from truck import Truck
from camera import Camera
from state_informer import StateInformer

if __name__ == '__main__':
    cam = Camera().start()
    truck = Truck()
    truck.start()