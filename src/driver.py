if __name__ == "__main__":
    from truck import Truck
    from gamepad import Gamepad, Inputs
    from data_client import DataClient
    g = Gamepad()
    car = Truck()
    client = DataClient()
    while True:
        try:
            steer = client.read_float_from_file("steering_angle.tbu")
            drive = client.read_float_from_file("drive_power.tbu")

            if steer is not None:
                car.phone_steer(steer)
            if drive is not None:
                car.set_drive_power(drive)
        
        except KeyboardInterrupt:
           car.cleanup()