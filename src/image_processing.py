"""
Processes images with OpenCV for autonomous navigation.

IMPORTANT

All images are represented by OpenCV matrices, which are aliases of numpy arrays.
"""

import warnings
import math
import time

# Package Imports
import numpy as np
import cv2


# Local Imports
from constants import LaneBoundsRatio, ImageProcessingCalibrations
from image_utils import weighted_center, filter_red
from camera import Camera
#from streaming import UDPStreamer

# Global Configuration
warnings.simplefilter('ignore', np.RankWarning)
# Ignoring Polyfit warning because it's bothersome.
# Supposedly we can resolve it by decreasing the order (third argument), but it's already at 1 here...







# Returns an image filtered for edges.
def edge_detector(img: cv2.Mat) -> cv2.Mat:
    gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
    thresholded_image = cv2.threshold(gray,    200, 255, cv2.THRESH_BINARY)[1]
    filtered_image = cv2.bitwise_and(gray, thresholded_image)
    try:
        gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
    except:
        gray = img # already gray if it throws exception I think
    coeff = .25 # higher = ignore more stuff (noise filtering I think?)
    thresh = int(max(gray[0]) * coeff) 
    blur = cv2.GaussianBlur(filtered_image, (21, 21), 0)
    _, binary = cv2.threshold(blur, thresh, 255, cv2.THRESH_BINARY)
    edges = cv2.Canny(binary, 200, 400)
    return edges

# Replaces specified fraction of image with white.
"""
IMPORTANT

The y-axis coordinate starts from the top of the image, while the x-axis starts from the left as usual.
  1 2 3 4
0  ________
1 |
2 |
3 |
4 |

Leaving polygons embedded here for clarity.
"""
def region_of_interest(image: cv2.Mat) -> cv2.Mat:
    try:
        height, width, _  = image.shape
    except:
        height, width = image.shape
    crop = image[int(2*height/7):height, 0:width]
    return crop
       
def crop_emptyness(image: cv2.Mat) -> cv2.Mat:
    #crop = image[int(height):int(height/2), 0:int(width/2)]
    im = image
    na = np.array(im)

    lower_bound = np.array([200, 200, 200])  # Lower bound of the color range
    upper_bound = np.array([255, 255, 255])  # Upper bound of the color range

    #Find X,Y coordinates of pixels within the specified color range
    color_range = np.all((na >= lower_bound) & (na <= upper_bound), axis=2)
    whiteY, whiteX = np.where(color_range)
    hull = cv2.convexHull(np.column_stack((whiteX, whiteY)))
    pts = hull[:, 0]

    #Find the bounding box of the convex hull
    rect = cv2.boundingRect(pts)
    x, y, w, h = rect
    crop = image[y:int(.6*(y+h)), x:x+w]
    return crop

# Detect lines segments with hough lines using cropped image filtered for edges.
# (x1, y1, x2, y2) - the coordinates for each line segment.
"""
IMPORTANT

Return an array of the form:
line_segments [
    [[x1, y1, x2, y2]], 
    [[x1, y1, x2, y2]], 
    [[x1, y1, x2, y2]], 
    [[x1, y1, x2, y2]], 
    ...
]

"Singleton" arrays.
"""
def detect_line_segments(img: cv2.Mat) -> np.ndarray:
    rho = 1             # Distance precision in pixels, i.e. 1 pixel.
    angle = np.pi / 180 # Angular precision in radians, i.e. 1 degree (radians = degrees * pi / 180).
    min_threshold = 10  # Minimal of votes for a line to be counted.
    
    line_segments = cv2.HoughLinesP( # Detect lines using probabalistic Hough transform. More info: https://en.wikipedia.org/wiki/Hough_transform
        img, rho, angle, min_threshold, np.array([]), minLineLength=8, maxLineGap=4
    )
    return line_segments

# Extrapolates a line to its endpoints at the edges of the image. y is maxed at half the height.
# Used to determine deviation from lane.
def make_points(frame: cv2.Mat, line: np.ndarray) -> tuple[float, float, float, float]:
    height, width = frame.shape
    slope, intercept = line
    y1 = height # Bottom of the frame / image.
    y2 = y1 / 6 # Top quarter.

    # Extrapolate the line to a line segment with endpoints on the edges of the frame.
    x1 = max(-width, min(2 * width, ((y1 - intercept) / slope)))
    x2 = max(-width, min(2 * width, ((y2 - intercept) / slope)))
    return (x1, y1, x2, y2)

# Approximates the slope and intercept of each line segment, determines which side of the image it's on, 
# and then computes the average line for each side. Returns array of length 0 - 2 from `make_points`.
# The frame is the uncropped image.
def average_slope_intercept(frame: cv2.Mat, line_segments: np.ndarray) -> list[tuple[float, float, float, float]]:
    if line_segments is None:
        return []

    _, width = frame.shape
    left_fit = []
    right_fit = []
    x_values= []
    for line_segment in line_segments:
        x_values.append(line_segment[0][0])
    
    leftmost = min(x_values)
    rightmost = max(x_values)
    mid = (leftmost + rightmost)/2

  
        
    for line_segment in line_segments:
        x1, y1, x2, y2 = line_segment[0]
        if x1==x2: # if they are equal, there must be infinite slope, so we just subtract one to make a non-infinite slope
            x1-=1
        if (x1-x2 != 0):
            fit = np.polyfit((x1, x2), (y1, y2), 1)
            slope, intercept = fit
            if abs(slope-1) <.1:
                continue
            if ((slope < 0) and 
                (x1 < mid) and 
                (x2 < mid)):
                left_fit.append((slope, intercept))
            elif ((slope > 0) and 
                (x1 > mid) and 
                (x2 > mid)):
                right_fit.append((slope, intercept))

    left_fit_average = np.average(left_fit, axis=0) # Get averages going downward. Collapse into one array.
    right_fit_average = np.average(right_fit, axis=0)
    lane_lines = []
    if len(left_fit) > 0:
        lane_lines.append(make_points(frame, left_fit_average))
    if len(right_fit) > 0:
        lane_lines.append(make_points(frame, right_fit_average))

    # Because lane_lines will only ever have two values, we could return this as a tuple, but that would require unnecessary refactoring.
    return lane_lines



# Use lane lines to predict the steering angle in degrees.
# -90 --> left, 0 --> straight, 90 --> right
def compute_steering_angle(frame: cv2.Mat, lane_lines: list[tuple[float, float, float, float]]) -> float:
    if len(lane_lines) == 0:
        # Continue straight if no lines are present...
        return 0

    height, width, _ = frame.shape
    if len(lane_lines) == 1:
        # In the event only a left lane or right lane was detected, 
        # we calculate the x-offset based on the difference between the extrapolated x coordinates.
        x1, _, x2, _ = lane_lines[0]
        x_offset = x2 - x1
    else:
        # Otherwise, the offset is based on the average between the topmost (as in the y-coordinate is at the middle of the frame) 
        # x-coordinates and the measured camera position. Note that the camera position may have to be recalibrated.
        _, _, left_x2, _ = lane_lines[0]
        _, _, right_x2, _ = lane_lines[1]
        mid = width / 2 * (1 + ImageProcessingCalibrations.CAMERA_MID_OFFSET_PERCENT)
        x_offset = (left_x2 + right_x2) / 2 - mid

    """
    IMPORTANT

    How the steering angle is calculated:
    
      Car Front
        /| --> angle_to_mid_radian
       / |                       |
      /  | --> y_offset         V
     /   |                       Convert to degrees 
    /____|
   x_offset
    """
    y_offset = height / 2
    angle_to_mid_radian = math.atan(x_offset / y_offset)
    angle_to_mid_deg = math.degrees(angle_to_mid_radian)
    return angle_to_mid_deg



# Finds the angle between the bottom center point and middle of the detected red zone / tape.
def compute_hitch_angle(frame: cv2.Mat, cx: float, cy: float) -> float:
    origin_x, origin_y = frame.shape[1] / 2, frame.shape[0]
    x_offset, y_offset = cx - origin_x, origin_y - cy
    angle = math.atan(x_offset / y_offset)
    angle = math.degrees(angle)
    return angle

"""

Everything beneath this comment is for testing.
Run `quick_capture_module.py` for unit tests.

"""



# Adds lines to image. Color is in RGB format.
def display_lines(img: cv2.Mat, lines: list[tuple[float, float, float, float]], line_color=(255, 255, 255), line_width=2) -> cv2.Mat:
    line_image = img.copy()
    if lines is None:
        return line_image
    for line in lines:
        x1, y1, x2, y2 = line
        cv2.line(line_image, (int(x1), int(y1)), (int(x2), int(y2)), line_color, line_width)
    return line_image

# Returns the steering angle and lanes.
# Should be identical to the steps in main, but separate for testing.
def steering_info(img: cv2.Mat) -> tuple[float, list[tuple[float, float, float, float]]]:
    edges = edge_detector(img)
    cropped_edges = region_of_interest(edges)
    line_segments = detect_line_segments(cropped_edges)
    lane_lines = average_slope_intercept(img, line_segments)
    steering_angle_deg = compute_steering_angle(img, lane_lines)
    return (steering_angle_deg, lane_lines)

# Makes a reduced opacity image containing lane lines and the calculated path. 
def display_lanes_and_path(img: cv2.Mat, steering_angle_deg: float, lane_lines: list[tuple[float, float, float, float]]) -> cv2.Mat:
    try:
        height, width, _ = img.shape # CHANGE
    except:
        height, width = img.shape
    steering_angle_radians = math.radians(steering_angle_deg + 60)

    # Calculations for the center path.
    x1 = width / 2
    y1 = height
    x2 = x1 - height / 2 / math.tan(steering_angle_radians)
    y2 = height / 2

    final_image = display_lines(img, lane_lines, (255, 0, 0))
    final_image = display_lines(final_image, [(x1, y1, x2, y2)], (0, 255, 0))

    final_image = cv2.putText(final_image, f"Steering Angle: {steering_angle_deg}", 
                              (25, 25), cv2.FONT_HERSHEY_SIMPLEX, 1, (255, 255, 255), 2)

    return final_image



# `steering_info` but with the red angle and coordinates.
# Should be identical to the steps in main, but separate for testing.
def steering_info_reverse(img: cv2.Mat) -> tuple[float, tuple[float, float, float, float]]:
    origin_x, origin_y = img.shape[1] / 2, img.shape[0]
    filtered = filter_red(img)
    cropped = region_of_interest(filtered)
    cx, cy = weighted_center(cropped)
    angle = compute_hitch_angle(img, cx, cy)
    return (angle, (origin_x, origin_y, cx, cy))

# To be used in conjunction with `display_lanes_and_path`.
def display_trailer_info(img: cv2.Mat, 
                         hitch_angle: float, 
                         trailer_points: tuple[float, float, float, float]) -> cv2.Mat:
    final_image = display_lines(img, [trailer_points], (0, 0, 255))
    final_image = cv2.putText(final_image, f"Hitch Angle: {hitch_angle}", 
                              (25, 60), cv2.FONT_HERSHEY_SIMPLEX, 1, (255, 255, 255), 2)
    return final_image


    
if __name__ == "__main__":
    cam = Camera().start()

    i = 0
    while True:
        image = cam.read()
        
        
        # white = filter_white(image)
        edges = edge_detector(image)
        cropped_edges = region_of_interest(edges, True)
        line_segments = detect_line_segments(cropped_edges)
        lane_lines = average_slope_intercept(image, line_segments)
        num_lanes = len(lane_lines)
        steering_angle_lanes = compute_steering_angle(image, lane_lines)
        final = display_lanes_and_path(image,steering_angle_lanes, lane_lines)

        filtered = filter_red(image)
        cropped = region_of_interest(filtered, True)
        cx, cy = weighted_center(cropped)
        trailer_points = (image.shape[1] / 2, image.shape[0], cx, cy)
        hitch_angle = compute_hitch_angle(image, cx, cy)
        trailer_angle = hitch_angle - steering_angle_lanes # Angle of the trailer relative to the lane center.

        final_final = display_trailer_info(final, trailer_angle, trailer_points)
        
        
