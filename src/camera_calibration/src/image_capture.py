import numpy as np
import glob
import cv2
import sys
sys.path.insert(0,"./src/") # gamepad and camera are located in parent directory
from gamepad import Gamepad, Inputs
from camera import Camera
from streaming import UDPStreamer
from threading import Thread

# This module captures images from the camera when A is pressed on the controller.
# Images are saved to '.src/camera_calibration_calibration_images'
# The inteneded use of this module is to capture images for fisheye-correction calibration, but you could just use it to take pictures.

g = Gamepad()
streamer = UDPStreamer()
cam = Camera().start()
def stream():
    while not cam.stopped:
        streamer.stream_image(cam.read())


if __name__ == "__main__":
    stream_thread = Thread(target=stream)
    stream_thread.start()


    


    filepath = "./src/camera_calibration/calibration_images/"
    image_num = ord('r')
    print("STARTED")
    while True:
        g.update_input()

        if g.was_pressed(Inputs.A):
            
            filename = "sample_image_"+chr(image_num)+".jpg"
            
            cv2.imwrite(filepath + filename, cam.read())
            print("Saved file:", filepath + filename)

            image_num += 1
        elif g.was_pressed(Inputs.B):
            cam.stop()
            streamer.stop()
            stream_thread.join()
            break

    cam.stop()