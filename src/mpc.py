import time
from state_informer import StateInformer
from trailer1 import func_eval
import numpy as np
from math import pi

"""
This module attemtps to implement grid search and newtons method search from src/trailer1.py for controlling of the car. WIP
"""

class Predicter:
    def __init__(self, state_informer: StateInformer):
        self.state_informer = state_informer
        self.trailer_deviation = state_informer.get_trailer_deviation()
        print(self.trailer_deviation)
        self.trailer_lane_angle = state_informer.get_trailer_lane_angle()
        self.hitch_angle = state_informer.get_hitch_angle()
        self.x = 0
        self.state_vector = [self.x, self.trailer_deviation, self.trailer_lane_angle * pi / 180, self.hitch_angle * pi / 180]

 
    # the same as Newton in trailer1.py
    def predict_fast(self):
        state_vector = [self.x, self.state_informer.get_trailer_deviation(), self.state_informer.get_trailer_lane_angle() * pi / 180, self.state_informer.get_hitch_angle() * pi / 180]

        str = 0
        v1 = 1.5
        t0=0

        y0=state_vector
        tstep=3
        
        steps = 0
        f_prev = 99999
        delta_str = 99999
        # Newton's method
        #print(self.state_informer.trailer_deviation)
        #print("newton")

        #print(y0)
        while True:
            u = [v1, str * pi / 180]
            [t, y, f, str_next] = func_eval(t0, y0, u, tstep)
            steps = steps + 1
            str_next = str_next * 180 / pi
            if abs(str_next - str) > 2.0 * delta_str:
                sgn = np.sign(str_next - str)
                str_next = str + sgn * min(2.0, 2.0 * delta_str)
            else:
                if steps > 1:
                    delta_str = abs(str_next - str)
            if f > f_prev:
                break
            str_prev = str
            str = str_next
            f_prev = f

        # the cost function may not intersect 0 which screws with Newton
        # use bisection to narrow in on the minimum
        # ignore new str_next return values for this part
        # print("bisection")
        strv = [str_prev, str]
        fv = [f_prev, f]
        while True:
            if abs(strv[1] - strv[0]) < 0.5:
                break
            str = 0.5 * (strv[0] + strv[1])
            strv.append(str)
            u = [v1, str * pi / 180]
            [t, y, f, str_next] = func_eval(t0, y0, u, tstep)
            steps = steps + 1
            fv.append(f)
            i = np.argmax(fv)
            if i == 2:
                break
            strv.pop(i)
            fv.pop(i)

        i = np.argmin(fv)
        str_next = strv[i]

        return t, y, f, str_next, steps
    
if __name__ == '__main__':
    informer = StateInformer()
    informer.update_state_and_inform()
    predicter = Predicter(informer)
    time.sleep(5)
    now = time.time()
    t,y,f,angle,steps = predicter.predict_fast()
    future = time.time()
    angle_slow, cost = predicter.predict()
    future_future = time.time()
    # print("t: ",t)
    # print("y: ",y)
    print("Generated steering angle: ", angle)
    print("Generation took " + str(future - now) + " seconds")
    print("Generated over "+ str(steps)+ " steps")
    # print("Slowly generated angle: ", angle_slow)
    # print("Generation took " + str(future_future - future) + " seconds")