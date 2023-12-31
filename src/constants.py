from enum import Enum
import yaml

"""
This module stores constants used throughout the project. The majority of these constants can be configured via `config.yml`.
Descriptions of these constants can be found in the config file as well.
"""

def read_yaml(filename):
    with open(f'{filename}.yml','r') as f:
        output = yaml.safe_load(f)
    return output
    

config = read_yaml('../TrailerBackerUpperRobot/config')
del yaml

settings = config['settings']

driving = settings['driving']

steering = settings['steering rack']

camera = settings['camera']

streaming = settings['streaming']

control = settings['control']

gpio = settings['gpio']

class MainMode(Enum):
    """
    Enumeration for the different driving modes
    """
    MANUAL       = 0
    AUTO_FORWARD = 1
    AUTO_REVERSE = 2
    STOPPED = 3

class ControlMode():
    CURRENT_CONTROL_MODE = control["control mode"]


class DriveParams:
    STEERING_RACK_CENTER       = steering["center"]




class GPIO:
    SERVO_MOTOR_PIN         = gpio["servo motor"]
    DRIVE_MOTOR_POWER_PIN   = gpio["drive motor power"]
    DRIVE_MOTOR_FORWARD_PIN = gpio["drive motor forward"]
    DRIVE_MOTOR_REVERSE_PIN = gpio["drive motor reverse"]



class CameraSettings:

    RESOLUTION: tuple[int, int] = (camera["resolution width"], camera["resolution height"])
    FRAMERATE: int              = camera["framerate"]


class OpenCVSettings:
    RECORDING_FRAMERATE: int = camera["framerate"] # Arbitrary (this number does affect the frame rate, but the number you put here is not the true framerate and we don't know why).



class Streaming:
    DESTINATION_ADDRESS = streaming["destination ip"]
    DESTINATION_PORT    = streaming["destination port"]
    ENABLED: bool             = streaming["enabled"]

if __name__ == "__main__":
    print(settings)