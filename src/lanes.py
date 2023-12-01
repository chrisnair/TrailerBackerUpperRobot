import cv2
import image_processing as ip
from streaming import UDPStreamer

image = cv2.imread("src/frames/transformed_image_a.jpg")
edges = ip.edge_detector(image)
cropped = ip.region_of_interest(edges, True)
ip.detect_line_segments(edges)
line_segments = ip.detect_line_segments(cropped)
lane_lines = ip.average_slope_intercept(image, line_segments)
final = ip.display_lanes_and_path(cropped,0, lane_lines)


cv2.imwrite("edges.jpg",final)

