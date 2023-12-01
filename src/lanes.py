import cv2
import image_processing as ip
from streaming import UDPStreamer

image = cv2.imread("src/frames/frame999.jpg")
gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
thresholded_image = cv2.threshold(gray,    220, 255, cv2.THRESH_BINARY)[1]
filtered_image = cv2.bitwise_and(gray, thresholded_image)
edges = ip.edge_detector(filtered_image)
cropped = ip.region_of_interest(edges)

cv2.imwrite("edges.jpg",cropped)

