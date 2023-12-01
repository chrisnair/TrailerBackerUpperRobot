from constants import ControlMode
from threading import Thread
from truck import Truck
from gamepad import Gamepad, Inputs
from mpc import Predicter
from state_informer import StateInformer
import sys
MANUAL = 0
ASSISTED = 1
AUTOMATIC = 2
PHONE_CONTROL = 1
GAMEPAD_CONTROL = 0

g = Gamepad()
class Controller:
    def __init__(self):
        self.truck = Truck()
        self.input_in_auto_thread = Thread(target=self.input_in_auto)
        self.stopped = True
        state_informer = StateInformer().start()
        self.predicter = Predicter(state_informer)
        self.driving_mode = MANUAL
    def input_in_auto(self):
        while self.driving_mode == AUTOMATIC:
            try:
                g.update_input()
            except:
                pass
            
            if(g.was_pressed(Inputs.B)):
                self.driving_mode=MANUAL
                break
        
    def manual(self):
        if self.driving_mode == MANUAL or self.driving_mode == ASSISTED:

            try:
                g.update_input()
            except:
                print("NO CONTROLLER DETECTED. Change control mode in config.yml to use phone, or plug in a gamepad and restart to continue.")
                return

            if g.was_pressed(Inputs.B):
                self.stopped = True
                return
            if g.was_pressed(Inputs.A):
                transition_mode = AUTOMATIC
                print("Press START to transition to AUTOMATIC MODE")
            if g.was_pressed(Inputs.START):
                self.driving_mode = transition_mode

            steer = g.get_stick_value(Inputs.LX)
            if steer is not None:
                self.truck.gamepad_steer(steer)
            drive = g.get_trigger_value()
            if drive is not None:
                self.truck.gamepad_drive(drive)

        if self.driving_mode == AUTOMATIC:
            self.input_in_auto_thread.start()
            self.truck.set_drive_power(-.6)
            t, y, f, angle ,steps = self.predicter.predict_fast()
            print(angle)
            self.truck.set_steering_angle(-angle)

            
    def drive(self):
       
        self.stopped = False
        print("IO INITIATED")
        transition_mode = MANUAL
        
        if ControlMode.CURRENT_CONTROL_MODE == GAMEPAD_CONTROL:
            while not self.stopped:
                if self.driving_mode == MANUAL or self.driving_mode == ASSISTED:

                    try:
                        g.update_input()
                    except:
                        print("NO CONTROLLER DETECTED. Change control mode in config.yml to use phone, or plug in a gamepad and restart to continue.")
                        break

                    if g.was_pressed(Inputs.B):
                        self.stopped = True
                        break
                    if g.was_pressed(Inputs.A):
                        transition_mode = AUTOMATIC
                        print("Press START to transition to AUTOMATIC MODE")
                    if g.was_pressed(Inputs.START):
                        self.driving_mode = transition_mode

                    steer = g.get_stick_value(Inputs.LX)
                    if steer is not None:
                        self.truck.gamepad_steer(steer)
                    drive = g.get_trigger_value()
                    if drive is not None:
                        self.truck.gamepad_drive(drive)

                if self.driving_mode == AUTOMATIC:
                    self.input_in_auto_thread.start()
                    self.truck.set_drive_power(-.6)
                    t, y, f, angle ,steps = self.predicter.predict_fast()
                    print(angle)
                    self.truck.set_steering_angle(-angle)
        elif ControlMode.CURRENT_CONTROL_MODE == PHONE_CONTROL:
            pass # wait for server to be up and good
            self.truck.cleanup()
        
