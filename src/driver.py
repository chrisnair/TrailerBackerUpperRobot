from constants import ControlMode
from threading import Thread
from truck import Truck
from gamepad import Gamepad, Inputs
from mpc import Predicter
from state_informer import StateInformer
from control_signals import sendSuggestedAngle
import sys
import control_signals
import time
STOP = -1
MANUAL = 0
ASSISTED = 1
AUTOMATIC = 2
PHONE_CONTROL = 1
GAMEPAD_CONTROL = 0

g = Gamepad()
class Driver:
    def __init__(self):
        self.truck = Truck()
        self.input_in_auto_thread = Thread(target=self.input_in_auto)
        self.stopped = True
        self.exit_auto_flag = False
        self.state_informer = StateInformer().start()
        self.predicter = Predicter(self.state_informer)
        self.driving_mode = MANUAL
        self.transition_mode = -1
    def input_in_auto(self):
        while self.driving_mode == AUTOMATIC:
            try:
                g.update_input()
            except:
                pass
            
            if(g.was_pressed(Inputs.B)):
                self.driving_mode=MANUAL
                self.exit_auto_flag = True
                print("setting flag")
                self.truck.set_drive_power(0)
                self.truck.set_steering_angle(0)
                break
    def exit_auto(self):
        print("exiting auto")
        self.truck.set_drive_power(0)
        self.truck.set_steering_angle(0)
        self.driving_mode = MANUAL
        self.input_in_auto_thread.join()
    
    def cleanup(self):
        if self.input_in_auto_thread.is_alive():
            self.input_in_auto_thread.join()
        self.state_informer.stop()
        self.truck.cleanup()
        
    def manual(self):
        if self.driving_mode == MANUAL or self.driving_mode == ASSISTED:
            if ControlMode.CURRENT_CONTROL_MODE==GAMEPAD_CONTROL:

                try:
                    g.update_input()
                except:
                    print("NO CONTROLLER DETECTED. Change control mode in config.yml to use phone, or plug in a gamepad and restart to continue.")
                    return -1

                if g.was_pressed(Inputs.B):
                    self.stopped = True
                    return -1
                if g.was_pressed(Inputs.A):
                    self.transition_mode = AUTOMATIC
                    print("Press START to transition to AUTOMATIC MODE")
                if g.was_pressed(Inputs.START):
                    if self.transition_mode == AUTOMATIC:
                        self.driving_mode = self.transition_mode
                        self.input_in_auto_thread = Thread(target=self.input_in_auto)
                        self.exit_auto_flag=False
                        self.input_in_auto_thread.start()


                steer = g.get_stick_value(Inputs.LX)
                if steer is not None:
                    self.truck.gamepad_steer(steer)
                drive = g.get_trigger_value()
                if drive is not None:
                    self.truck.gamepad_drive(drive)

            elif ControlMode.CURRENT_CONTROL_MODE==PHONE_CONTROL:
                drive = control_signals.getDrivePower()
                self.truck.set_drive_power(drive)
                self.truck.phone_steer(control_signals.getSteeringAngle())
                   
                if self.driving_mode == ASSISTED:
                    t, y, f, angle ,steps = self.predicter.predict_fast()
                    sendSuggestedAngle(angle)
                

    def automatic(self):
        if self.exit_auto_flag:
            self.exit_auto()
            return -1
        if abs(self.truck.current_steering_angle>10):
            self.truck.set_drive_power(-.6)
        self.truck.set_drive_power(-.6)
        #now = time.time()
        t, y, f, angle ,steps = self.predicter.predict_fast()
        #future = time.time()
        #print(future-now)
        #print(angle)
        self.truck.set_steering_angle(-angle)
    def drive(self):
        #control_signals.startListening()
        self.stopped = False
        print("IO INITIATED")
        
      
        while not self.stopped:
            try:

                if ControlMode.CURRENT_CONTROL_MODE==PHONE_CONTROL:
                    control_signals.startListening()
                    self.driving_mode=control_signals.getControlState()
                    #print(self.driving_mode)
                if self.driving_mode==MANUAL or self.driving_mode==ASSISTED:
                    if self.manual() == -1:
                        break
                elif self.driving_mode ==AUTOMATIC:
                    if self.automatic() == -1:
                        break
            except Exception as e:
                self.driving_mode=MANUAL
                self.cleanup()
                raise e
                

                    
                
       
        self.cleanup()
        sys.exit(0)
        
