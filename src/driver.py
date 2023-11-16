import signal
from streaming import UDPStreamer
from camera import Camera
import cv2
import numpy as np
import image_utils as iu

def cleanup():
    car.cleanup()
    streamer.stop()
    cam.stop()
    exit(0)

if __name__ == "__main__":
    from truck import Truck
    from gamepad import Gamepad, Inputs
    from data_client import DataClient
    # Trigger cleanup upon keyboard interrupt.
    def handler(signum: signal.Signals, stack_frame):
        global done
        print("\nKeyboard interrupt detected.")
        done = True
        # print(signum, signal.Signals(signum).name, stack_frame) 
        cleanup()
    signal.signal(signal.SIGINT, handler) # type: ignore



    g = Gamepad()
    cam = Camera().start()
    car = Truck()
    client = DataClient()
    streamer = UDPStreamer().start()

    def get_remap(image):
        filepath = './src/camera_calibration/calibrations/'
        camera_matrix =  np.load(filepath+"matrix800x600.npz")['arr_0']
        distortion_coefficients = np.load(filepath+"distortion800x600.npz")['arr_0']

        h, w = image.shape[:2]
        newcameramtx, roi = cv2.getOptimalNewCameraMatrix(camera_matrix, distortion_coefficients, (w,h), 1, (w,h))
        image_remap_x, image_remap_y = cv2.initUndistortRectifyMap(camera_matrix, distortion_coefficients, None, newcameramtx, (w,h), 5)
        return image_remap_x, image_remap_y, roi

    

    print("Starting Main Loop!")
    while True:
        steer = client.read_float_from_file("steering_angle.tbu")
        drive = client.read_float_from_file("drive_power.tbu")
        stream_state = client.read_bool_from_file("stream_state.tbu")
        image = cam.read()
        if stream_state:
            streamer.stream_image(iu.undistort(image, *get_remap(image)))
        else:
            streamer.stream_image(image)


        if steer is not None:
            car.phone_steer(steer)
        if drive is not None:
            car.set_drive_power(drive)
        