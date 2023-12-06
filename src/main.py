import signal
from truck import Truck
from camera import Camera
from driver import Driver

def handler(signum: signal.Signals, stack_frame):
    global done
    print("\nKeyboard interrupt detected.")
    done = True
    # print(signum, signal.Signals(signum).name, stack_frame) 
    cleanup()
    signal.signal(signal.SIGINT, handler) # type: ignore

if __name__ == '__main__':
    driver = Driver().drive()

   