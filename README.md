# TrailerBackerUpperRobot

This project aims to develop an autonomous robotic system capable of driving backward while maneuvering a trailer using Model Predictive Control (MPC) algorithms. Traditional autonomous driving systems primarily focus on forward motion, but this project aims to enable a robot to navigate in reverse, a crucial skill for various real-world scenarios.


## Installation
In order to install this code, one would need all technologies used listed below. 

## Structure
The online folder contains Java code which allows for communication between the app part of our project and this robot portion. It sets up a connection and allows for packets to be sent to and from the phone.

Within the src:
The `camera.py` folder creates a camera object, which is what is used to take frames which are used in calculations.

`constants.py` is meant to store variables in the code which do not change. 

`control_signals.py` receives control signals from the server on the java side and updates state variables which can be accessed from anywhere. 

`driver.py` is the file that is to be run when starting the robot, it allows for gamepad control and control using the trailerbackerupper app. 

`gamepad.py` is used when a controller is plugged into the robot when one wants to control it using the controller. 

`gpio.py` is used in controlling the motors located on the robot. 

`image_processing.py` and `image_utils.py` are both used in taking the images captured by our camera and transforming them to be used in calculations. 

`main.py` is the file to run when dribing. 

`mpc.py` is where the calculations are done, this takes in a hitch angle, trailer deviation from lane, and trailer anglle compared to lane angle and outputs a value for the front wheels to turn to. 

`state_informer.py` tracks and updates relevant vehicle state information needed for implementing MPC. 

`streaming.py` is used mostly for testing, changing the ip in config.yml to the desired streaming location and running client.py on that machine will allow for a live view of the images. 

In `trailer1.py`, the main calculations for MPC are done. 

`truck.py` controls the driving and steering of the car.



## Running the code
The code in Online is responsible for running the server by which the app and Raspberry Pi communicate.

Run `ServerStarter.java` to start the server. To start the truck/trailer control software, run `main.py`.

Settings can be configured in `config.yml`.

A client for video streaming from the onboard camera is provided in `client.py`.

## Technologies Used
Seeed Studio vehicle chassis.
Raspberry Pi 4 Model B.
Raspberry Pi Camera
Python 3.9.2.
Java 8
