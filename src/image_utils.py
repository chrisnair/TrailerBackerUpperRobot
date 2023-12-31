import cv2
import numpy as np








# Returns a black image with dimensions identical to that of the given image.
def zero_image(frame: cv2.Mat) -> cv2.Mat:
    return np.zeros_like(frame)

# cv2.putText except I added defaults to save me from typing
def put_text(image: cv2.Mat, message: str, pos = (25,25), font_scale = 1, color = (255, 255, 255), thickness = 2):
    cv2.putText(image, message, pos, cv2.FONT_HERSHEY_SIMPLEX, font_scale, color, thickness)

# Combines images together, where weight of each image can be adjusted.
# Images later in the list take z-axis priority.
def combine_images(pairs: list[tuple[cv2.Mat, float]]) -> cv2.Mat:
    # Throw exception if no images are provided.
    base = zero_image(pairs[0][0])
    for image, weight in pairs:
        # The last parameter is gamma, and is for adjusting the overall brightness.
        base = cv2.addWeighted(base, 1, image, weight, 0)
    return base

def generate_remapping_information(image):
    filepath = './src/camera_calibration/calibrations/'
    camera_matrix =  np.load(filepath+"matrix800x600.npz")['arr_0']
    distortion_coefficients = np.load(filepath+"distortion800x600.npz")['arr_0']

    h, w = image.shape[:2]
    newcameramtx, roi = cv2.getOptimalNewCameraMatrix(camera_matrix, distortion_coefficients, (w,h), 1, (w,h))
    image_remap_x, image_remap_y = cv2.initUndistortRectifyMap(camera_matrix, distortion_coefficients, None, newcameramtx, (w,h), 5)
    return image_remap_x, image_remap_y, roi

def undistort(distorted: cv2.Mat, remapping_information: tuple)-> cv2.Mat:
        image_remap_x, image_remap_y, roi = remapping_information
  
        undistorted = cv2.remap(distorted, image_remap_x, image_remap_y, cv2.INTER_LINEAR)
        # crop the image
        x, y, w, h = roi
        undistorted = undistorted[y:y+h, x:x+w]
        return undistorted



 
        


# Filters image for red by inverting image so red --> cyan. 
# Uses HSV format to be able to only include certain saturation and brightness of cyan.
def filter_red(img: cv2.Mat) -> cv2.Mat:
    
    
    # Bitwise complement operator. Flips each bit for each element in the matrix.
    invert = ~img
    hsv = cv2.cvtColor(invert, cv2.COLOR_BGR2HSV)
    lower_cyan = np.array([45, 150, 40]) # Lower bound of HSV values to include in mask
    upper_cyan = np.array([100, 255, 255]) # Upper bound of HSV values to include in mask
    # Clamp to certain cyan shades.
    mask = cv2.inRange(hsv, lower_cyan, upper_cyan)
    return mask

def filter_yellow(img: cv2.Mat) -> cv2.Mat:
    
    # Bitwise complement operator. Flips each bit for each element in the matrix.
    invert = ~img
    hsv = cv2.cvtColor(invert, cv2.COLOR_BGR2HSV)
    lower_cyan = np.array([115, 150, 40])
    upper_cyan = np.array([125, 255, 255])
    # Clamp to certain cyan shades.
    mask = cv2.inRange(hsv, lower_cyan, upper_cyan)
    return mask


# Finds the weighted center of the image. Images filtered for certain colors should be passed here to find the coordinates of colored markers.
def weighted_center(img: cv2.Mat) -> tuple[float, float]:

    # Contour: structural outlines.
    # Ignoring hierarchy (second return value).
    contours, _ = cv2.findContours(img, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
    if len(contours)>0:
        big_contour = max(contours, key=cv2.contourArea)
    else:
        return(img.shape[1] / 2, img.shape[0] / 2) #temp fix; bad

    # Moment: imagine the image is a 2D object of varying density. Find the "center of mass" / weighted center of the image.
    moments = cv2.moments(big_contour)
    if (moments["m00"] == 0) or (moments["m00"] == 0):
        return(img.shape[1] / 2, img.shape[0] / 2)
    cx = moments["m10"] / moments["m00"]
    cy = moments["m01"] / moments["m00"]
    return (cx, cy)


def cover_portion(image: cv2.Mat, portion: float, color: int) -> cv2.Mat:
    try:
        height, width, _  = image.shape
    except:
        height, width = image.shape
    mask = np.zeros_like(image)

    
    polygon = np.array(
        [
            [
                (0, height * portion), 
                (width, height * portion), 
                (width, height), 
                (0, height)
            ]
        ], 
        np.int32
    )
 
    cv2.fillPoly(mask, polygon, 255)
    cropped_edges = combine_images([(image, 1), (mask, 1)])
    return cropped_edges


def midpoint(point1: tuple[ float, float], point2: tuple[float, float]) -> tuple[ float, float]:
    x1, y1 = point1 
    x2, y2 = point2 

    return (x1 + x2) * 0.5 , (y1 + y2) * 0.5

def get_transformation_matrix(image):
    try:
        height, width, _ = image.shape
    except:
        height, width = image.shape

    tl = [width *2/9, height *.3]
    tr = [width * 7/9, height * .3]
    bl = [0, height* .45]
    br = [width, height* .45]


    src = np.float32([tl, tr, bl, br])

    tl = [0,0]
    tr = [image.shape[1], 0]
    bl = [0, image.shape[0]]
    br = [image.shape[1], image.shape[0]]

    dst = np.float32([tl, tr, bl, br])

    matrix = cv2.getPerspectiveTransform(src, dst)
    return matrix

def warp_perspective(image, transformation_matrix):
    res = cv2.warpPerspective(image, transformation_matrix, (image.shape[1], image.shape[0]) )
    return res

def slope(line):
    x1,y1,x2,y2=line
    return (y1-y2)/(x1-x2) if x1!=x2 else (y1-y2)/(x1-x2+1)