#!/usr/bin/env python3
import socket
import sys

import config
from ev3dev2.motor import (OUTPUT_B, OUTPUT_C, OUTPUT_D, LargeMotor,
                           MediumMotor, MoveSteering, MoveTank, SpeedPercent)
from ev3dev2.sensor.lego import InfraredSensor
from ev3dev2.sound import Sound


DISTANCE_FACTOR = 36
ANGLE_FACTOR = 5.65
SCAN_POSITION_FACTOR = 3

SOUND_ON = False

sound = Sound()
if SOUND_ON:
    sound.speak('Initializing')

# Init motors
steer_pair = MoveSteering(OUTPUT_B, OUTPUT_C, motor_class=LargeMotor)
motor_sensor = MediumMotor(OUTPUT_D)

# Init sensor
ir_sensor = InfraredSensor()

if SOUND_ON:
    sound.speak('Ready to go!')


def establish_connection():
    serversocket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    serversocket.bind((socket.gethostname(), config.PORT))
    print("Hostname: " + socket.gethostname() +
            ", port:" + str(config.PORT))
    serversocket.listen(1)
    (clientsocket, address) = serversocket.accept()

    return clientsocket, address


def send_to_socket(socket, message):
    total = 0
    msg = message.encode()
    while total < len(msg):
        sent = socket.send(msg[total:])
        if sent == 0:
            raise RuntimeError("Socket connection broken")
        total += sent


def receive_from_socket(socket):
    msg = socket.recv(1024)
    return msg.decode()


def move_forward(distance):
    print("Move forward for " + str(distance))
    steer_pair.on_for_degrees(steering=0, speed=50,
                              degrees=DISTANCE_FACTOR * distance)


def rotate(angle):
    print("Rotate for " + str(angle))
    steer_pair.on_for_degrees(steering=100, speed=50,
                              degrees=ANGLE_FACTOR * angle)


def measure_and_send(angle):
    m = ir_sensor.proximity * 0.7
    print("Measured " + str(m) + " at " + str(angle))
    # TODO


def scan(precision, num_scans, increasing):
    print("Scan " + str(num_scans) + " times")
    total_rotation = (num_scans - 1) * precision
    if not increasing:
        total_rotation = -total_rotation

    start_motor_position = motor_sensor.position
    rotation_factor = 1 / motor_sensor.count_per_rot * 360
    next_scan_at = 0

    motor_sensor.on_for_degrees(speed=10,
                                degrees=SCAN_POSITION_FACTOR * total_rotation,
                                block=False)
    while motor_sensor.is_running:
        relative_motor_position = motor_sensor.position - start_motor_position
        if abs(relative_motor_position / SCAN_POSITION_FACTOR) >= next_scan_at:
            measure_and_send(next_scan_at)
            next_scan_at += precision

    # Check if the last measurement was made
    if next_scan_at <= total_rotation:
        measure_and_send(next_scan_at)


# print("Establishing connection")
# clientsocket, address = establish_connection()
# print("Connection established")

# with clientsocket:
#     while True:
#         c = receive_from_socket(clientsocket)
#         if not c:
#             break
#         command, amount = c.split(" ")
#         if command == "MOVE":
#             move_forward(float(amount))
#         elif command == "ROTATE":
#             rotate(float(amount))
#         else:
#             print("Unknown command: " + command)

# move_forward(30)
rotate(360 * 2)
# scan(45, 3, False)
