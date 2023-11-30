import cv2
import image_processing as ip

image = cv2.imread("src/frames/frame174.jpg")
gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
thresholded_image = cv2.threshold(gray, 200, 255, cv2.THRESH_BINARY)[1]
filtered_image = cv2.bitwise_and(gray, thresholded_image)
edges = ip.edge_detector(filtered_image)


cv2.imshow("window",edges)
cv2.waitKey(5000)