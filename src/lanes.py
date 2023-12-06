import cv2
import image_processing as ip
import numpy as np
import time
from streaming import UDPStreamer
from PIL import Image, ImageFilter



if __name__ == '__main__':
    image = cv2.imread("src/frames/transformed_image_a.jpg")
    now = time.time()
    remove_bad = ip.region_of_interest(image)
    edges = ip.edge_detector(remove_bad)
    cv2.imwrite("edges.jpg",edges)
    cropped = ip.region_of_interest(edges, True)
    line_segments = ip.detect_line_segments(cropped)
    lane_lines = ip.average_slope_intercept(cropped, line_segments)
    fone = time.time()
    final = ip.display_lanes_and_path(cropped,0, lane_lines)
    print(lane_lines)
    cv2.imwrite("edges1.jpg",cropped)

