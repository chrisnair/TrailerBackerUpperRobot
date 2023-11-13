import signal


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
    car = Truck()
    client = DataClient()

    def cleanup():
        car.cleanup()
        exit(0)
        
    while True:
        steer = client.read_float_from_file("steering_angle.tbu")
        drive = client.read_float_from_file("drive_power.tbu")

        if steer is not None:
            car.phone_steer(steer)
        if drive is not None:
            car.set_drive_power(drive)
        