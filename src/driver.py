import signal
import time


if __name__ == "__main__":
    from truck import Truck
    from gamepad import Gamepad, Inputs
    from data_client import DataClient
    import ControlSignals
    # Trigger cleanup upon keyboard interrupt.
    def handler(signum: signal.Signals, stack_frame):
        global done
        print("\nKeyboard interrupt detected.")
        done = True
        # print(signum, signal.Signals(signum).name, stack_frame) 
        cleanup()
    signal.signal(signal.SIGINT, handler) # type: ignore



    g = Gamepad()
    car = Truck()
    client = DataClient()
    ControlSignals.startListening()

    def cleanup():
        car.cleanup()
        exit(0)
        
    while True:
        steer = ControlSignals.getSteeringAngle()
        drive = ControlSignals.getDrivePower()

        if steer is not None:
            car.phone_steer(steer)
        if drive is not None:
            car.set_drive_power(drive)

        time.sleep(1/60)
        