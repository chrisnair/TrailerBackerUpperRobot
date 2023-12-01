from threading import Thread
import numpy as np
import math
import cv2

# LOCAL IMPORTS
from constants import ImageProcessingCalibrations as Calibrations
#from speedometer import Speedometer
import image_processing as ip
import image_utils as iu
from camera import Camera
from truck import Truck
from streaming import UDPStreamer

# TODO: Come up with a nice name for this module and class
# Working name: StateInformer get it like state informer like a spy? It's so funny.

"""This module tracks all relevant vehicle state information needed for implemeneting model predictive control
as described in http://liu.diva-portal.org/smash/get/diva2:1279885/FULLTEXT01.pdf (pdf available in ../literature)"""


class StateInformer:
    def __init__(self):
        # "pos" refers to coordinates in image of the form (x-pixel, y-pixel)
        self.thread: Thread = Thread(target = self.update_continuosly)
        #self.speedometer: Speedometer = Speedometer().start()
        self.cam: Camera = Camera()

        self.lane_center_pos: tuple[int, int] = (0,0)
        self.lanes: list[tuple[float, float, float, float]] = []

        #self.frame: cv2.Mat = self.cam.read() # ensure frame is non-None at start
        self.frame = self.cam.read()
        self.remapping_information = iu.generate_remapping_information(self.frame)
        self.frame = iu.undistort(self.frame, self.remapping_information)

        self.truck = Truck()
        
        self.steering_angle: float = 0 # alpha
        self.car_lane_angle: float = 0 # theta1
        self.car_deviation: float = 0 # y1; inches
        self.vel: float = 0 #v (assuming that car and trailer velocities are the same) (not how the paper does it)

        self.trailer_lane_angle: float = 0 # theta2
        self.hitch_angle: float = 0 # beta 
        self.trailer_pos: tuple[float, float] = (0, 0)
        self.trailer_deviation: float = 0 # y2; inches

        self.CAMERA_LOCATION = self.frame.shape[1] / 2, self.frame.shape[0]
        self.HITCH_TO_TRAILER_AXLE_DIST = 8 # inches
        print(self.frame.shape)

        self.stopped: bool = False
        
        # image correction
       

        self.streamer = UDPStreamer()

        
    # def update_vel(self):
    #     self.vel = self.speedometer.read()
    
    def get_vel(self):
        return self.vel

    def update_hitch_angle(self):
        # Relies on: update_trailer_pos()
        trailer_x, trailer_y = self.trailer_pos                                 
        cam_x, cam_y = self.CAMERA_LOCATION
        trailer_to_cam_line = math.dist(self.trailer_pos, self.CAMERA_LOCATION)
        trailer_to_frame_bottom_line = cam_y - trailer_y
        rad = math.acos(trailer_to_frame_bottom_line / trailer_to_cam_line)
        deg = -math.degrees(rad)
        if self._is_on_left(self.trailer_pos):
            deg *= -1 # angles on left are  represetned with negative
        self.hitch_angle = deg
        """
                 C    Point C: Camera Location (Car rear)
                /|    Point A: Trailer axle location (red marker)
               / |    Point B: Point defined by coordinates (x-coordiante of camera, y-coordinate of trailer) to ensure right triangle angle at all times.               
              /  |        
             /   |    Lengths of CA and CB are calculated. arccos(CB/CA) = angle C                 
            /____|        
           A      B   NOTE: arccos(1) = 0 so there is no problem when len(CA) = len(CB)
        """
    def get_hitch_angle(self):
        return self.hitch_angle
    
    def update_trailer_pos(self):
        # Relies on: update_frame()
        img = self.frame
        red = iu.filter_red(img)
        self.trailer_pos = iu.weighted_center(red)
        
    def get_trailer_pos(self):
        return self.trailer_pos
    
    def update_trailer_lane_angle(self):
        # Relies on: update_hitch_angle, update_car_lane_angle()
        trailer_x, _ = self.trailer_pos
        center_x, _ = self.lane_center_pos

        angle = abs(self.hitch_angle) - abs(self.car_lane_angle)

        if trailer_x < center_x:
            angle *= -1 # if the trailer is to the left, angle is negative

        self.trailer_lane_angle = angle 

        # I don't feel like drawing the triangle for this but trust me

    def get_trailer_lane_angle(self):
        return self.trailer_lane_angle

    
    def update_trailer_deviation(self):
        # Relies on: self.update_trailer_lane_angle()

        rad = math.radians(self.trailer_lane_angle)
        self.trailer_deviation = math.sin(rad) * self.HITCH_TO_TRAILER_AXLE_DIST
        """
                 C    Point C: Camera Location (Car rear)
                /|    Point A: The trailer axle (red marker)
               / |    Point B: Defined by coordinate (x-coordinate of lane_center, y-coordinate of the trailer).                    
              /  |     
             /   |                      
            /____|    A and B share the same y-coordinate so a right triangle is maintained 
           A      B   
                      Length of line AB is the horizontal displacement of the trailer from the lane center.
                      
                      Known values are:
                      - Angle C (self.trailer_lane_angle)
                      - Length of CA (the physical distance from the hitch to the trailer axle)
        
                      Desired value:
                      - Length of AB
                      
                      sin(C) = BA/CA 
                      CA * sin(C) = BA
        
        """
    def get_trailer_deviation(self):
        return self.trailer_deviation

   

    def update_car_lane_angle(self):
        # Relies on: update_lane_center_pos()
        
        cam_x, cam_y = self.CAMERA_LOCATION
        
        lane_center_x, lane_center_y = self.lane_center_pos
        

        central_line = math.dist(self.CAMERA_LOCATION, self.lane_center_pos)
        heading_line = cam_y - lane_center_y

        angle = math.degrees(math.acos(heading_line / central_line))

        if not self._is_on_left(self.lane_center_pos): # if the lane center is on the RIGHT, then the car must be on the left.
            angle *= -1

        self.car_lane_angle = angle
        """
                 C    Point C: Camera Location (Car rear)
                /|    Point A: The center of the lane
               / |    Point B: Defined by coordinate (x-coordinate of lane_center, y-coordinate of the trailer).                  
              /  |    Therefore the line CB is the line from the camera  
             /   |                      
            /____|    A and B share the same y-coordinate so a right triangle is maintained 
           A      B   
                      Finally, arccos(CB/CA) = angle C
        """
    def get_car_lane_angle(self):
        return self.car_lane_angle
    
    def update_car_deviation(self):
        # Relies on: update_trailer_deviation(), update_car_lane_angle()

        # represent left and right both as positive numbers?
        true_distance_to_center = math.sqrt (self.HITCH_TO_TRAILER_AXLE_DIST**2 + self.trailer_deviation**2) # inches
        horizontal_distance_to_center = true_distance_to_center * math.sin(math.radians(self.car_lane_angle)) # inches
        self.car_deviation = horizontal_distance_to_center # inches

        """
                  C
                 / \           Point C: Camera Location
                / | \          Point B: Point defined by (x-coordinate of lane center, y-coordinate of trailer)
               /  |  \         Point A: Trailer axle location (red marker)                     
              /   |   \        Point D: Point defining heading line of camera (CD) such that it intersects with AB
             /    |    \                  
            /_____|_____\      NOTE: Triangle CBD is right; triangle ABC is a triangle. 
           A      D      B 
                      
                              Known values are:
                              - Length of CA (HITCH_TO_AXLE_DISTANCE)
                              - Length of AB (self.trailer_deviation)
                              - Angle DCB (self.car_lane_angle)
                                
                               
                              Desired value:
                              - length of DB
                      
                              
        
                              By pythagorean theorem, length of CB = sqrt(HITCH_TO_AXLE_DISTANCE^2 + self.trailer_deviation^2)
                              
                              CBD is a right triangle (I'm like 99% sure but I'm not gonna prove it)
        
                              If CB is the distance between the car and lane center (the x-cooordinate of point B is the lane center x-coordinate),
                              then the x component of CB is the horizontal distance of the car from the center
        
                              sin(DCB) = length DB / length CB
                              length CB * sin(DCB) = length DB
                              
        """
    def get_car_deviation(self):
        return self.car_deviation


    def update_steering_angle(self):
        #Relies on: car.set_steering_angle()
        self.steering_angle = self.truck.current_steering_angle
    
    def get_steering_angle(self):
        return self.steering_angle
    
    def update_lanes(self):
        # Relies on: update_frame()
        img = self.frame
        edges = ip.edge_detector(img)
        cropped_edges = ip.region_of_interest(edges,True)
        line_segments = ip.detect_line_segments(cropped_edges)
        lane_lines = ip.average_slope_intercept(img, line_segments)
        self.lanes = lane_lines
    
    def get_lanes(self):
        return self.lanes
    
    def update_lane_center_pos(self):
        #Relies on: update_lanes()
        if len(self.lanes) == 2:

            lane1 = self.lanes[0]
            lane1_x1, lane1_y1, lane1_x2, lane1_y2 = lane1
            # lane1_midpoint = iu.midpoint((lane1_x1, lane1_y1), (lane1_x2, lane1_y2))

            lane2 = self.lanes[1]
            lane2_x1, lane2_y1, lane2_x2, lane2_y2 = lane2
            # lane2_midpoint = iu.midpoint((lane2_x1, lane2_y1),(lane2_x2, lane2_y2))

            # #self.lane_center_pos = ((lane1_midpoint[0]+lane2_midpoint[0])/2, 240)
            # self.lane_center_pos = iu.midpoint(lane1_midpoint, lane2_midpoint)

            lane1_upper_point = (lane1_x1, lane1_y1) if lane1_y1 < lane1_y2 else (lane1_x2, lane1_y2)
            lane2_upper_point = (lane2_x1, lane2_y1) if lane2_y1 < lane2_y2 else (lane2_x2, lane2_y2)

            self.lane_center_pos = iu.midpoint(lane1_upper_point, lane2_upper_point)

            

        elif len(self.lanes) == 1:
            pass
        """
        Here's what I'd like to do if there is one lane:
        Whenever there are two lanes, we record the distance from the left lane to the center, and the distance from the right lane to the center.
        When two lanes are no longer visible, we check whether the visible lane is on the left or on the right.
        We use the corresponding previously saved distance to estimate a new lane center. In vertical (not actually considered due to infinite slope)
        or near-vertical lane conditions,
        A line can simply be drawn from the midpoint of the lane to the left or right. However, in a curve, a line like this would not allign with the true center.
        A better approximation would be a line perpendicular to the drawn lane line.
        I'll get around to this eventually, for now I'll see how well (probably not very well) it works when only updating the lane center when two lanes are visible.
        TODO (maybe): I think it would be beneficial if the center of the lanes was the refernce point (perhaps implemented as cartesian origin) for other positions.
        """

    def get_lane_center_pos(self):
        return self.lane_center_pos

    def update_state(self):
        self.update_frame() # This one needs to be first; the others rely on it.

        #self.update_vel()

        self.update_trailer_pos()
        
        self.update_lanes()
        self.update_lane_center_pos()


        self.update_steering_angle()
        self.update_car_lane_angle()
        self.update_hitch_angle()
        self.update_trailer_lane_angle()

        self.update_trailer_deviation()
        self.update_car_deviation()
        red = iu.filter_red(self.frame)
        x,y = self.trailer_pos
        camera_x, camera_y = self.CAMERA_LOCATION
        trailer = ip.display_trailer_info(self.frame, self.hitch_angle,[camera_x,camera_y,x,y])
        #self.streamer.stream_image(ip.display_lanes_and_path(self.frame, self.hitch_angle, self.lanes))
        edges = ip.edge_detector(self.frame)
        cropped_edges = ip.region_of_interest(edges,True)
        combined = ip.display_lanes_and_path(trailer, self.steering_angle,self.lanes)
        self.streamer.stream_image(combined)
        

    def update_frame(self):
        img = self.cam.read()
        self.frame = iu.undistort(img, self.remapping_information)
        self.frame = self.frame
    
    def get_frame(self):
        return self.frame

    def update_continuosly(self):
        while not self.stopped:
            self.update_state()
            
    
    def start(self):
        print("starting thread")
        self.thread.start()
        return self

    def stop(self):
        #self.speedometer.stop()
        print("Releasing state informer resources... ", end="")
        self.stopped = True
        self.thread.join()
        print("DONE")




    def _is_on_left(self, pos: tuple[int, int]):
        x, y = pos
        cam_x, cam_y = self.CAMERA_LOCATION
        if x < cam_x: # cam x is the middle of the frame
            return True
        return False
    

        
if __name__ == "__main__":
    s = StateInformer()