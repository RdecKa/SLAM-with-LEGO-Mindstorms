#!/usr/bin/env python3
import socket

import config
from ev3dev2.motor import (OUTPUT_B, OUTPUT_C, OUTPUT_D, LargeMotor,
                           MediumMotor, MoveSteering)
from ev3dev2.sensor.lego import InfraredSensor
from ev3dev2.sound import Sound


DISTANCE_FACTOR = 36
ANGLE_FACTOR = 5.65
SCAN_POSITION_FACTOR = 3

# Actual maximal valid value is 99, but more distant mesurements are more noisy
MAX_VALID_MEASUREMENT = 99 * 2 / 3

SOUND_ON = False

recv_buffer = b""
end_char = b"\0"

sound = Sound()
if SOUND_ON:
    sound.speak('Initializing')

# Init motors
steer_pair = MoveSteering(OUTPUT_B, OUTPUT_C, motor_class=LargeMotor)
motor_sensor = MediumMotor(OUTPUT_D)

# Init sensor
ir_sensor = InfraredSensor()
sensor_orientation = 0


def establish_connection():
    serversocket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    try:
        serversocket.bind((socket.gethostname(), config.PORT))
    except OSError:
        msg = "Could not open a socket"
        print(msg)
        if SOUND_ON:
            sound.speak(msg)
        exit(1)
    print("Hostname: " + socket.gethostname() + ", port:" + str(config.PORT))
    serversocket.listen(1)

    if SOUND_ON:
        sound.speak('Ready to connect!')

    (clientsocket, address) = serversocket.accept()
    return clientsocket, address


print("Establishing connection")
clientsocket, address = establish_connection()
print("Connection established")


def send_to_socket(socket, message):
    total = 0
    msg = message.encode() + end_char
    while total < len(msg):
        sent = socket.send(msg[total:])
        if sent == 0:
            raise RuntimeError("Socket connection broken")
        total += sent


def receive_from_socket(socket):
    global recv_buffer
    while end_char not in recv_buffer:
        chunk = socket.recv(1024)
        if chunk == b"":
            raise RuntimeError("Socket connection broken")
        recv_buffer += chunk
    end_char_loc = recv_buffer.index(end_char)
    msg = recv_buffer[:end_char_loc]
    recv_buffer = recv_buffer[end_char_loc + 1:]
    return msg.decode()


def move_forward(distance):
    print("Move forward for " + str(distance))
    steer_pair.on_for_degrees(steering=0, speed=30,
                              degrees=DISTANCE_FACTOR * distance)


def rotate(angle):
    print("Rotate for " + str(angle))
    steer_pair.on_for_degrees(steering=-100, speed=30,
                              degrees=ANGLE_FACTOR * angle)


def rotate_sensor(angle, block=True, speed=5):
    angle_scaled = angle * SCAN_POSITION_FACTOR
    motor_sensor.on_for_degrees(speed=speed,
                                degrees=angle_scaled,
                                block=block)
    global sensor_orientation
    sensor_orientation += angle_scaled


def rotate_sensor_to_zero_position():
    rotate_sensor(-sensor_orientation / SCAN_POSITION_FACTOR)


def measure_and_send(angle):
    m = ir_sensor.proximity
    if m > MAX_VALID_MEASUREMENT:
        print("Looking at infinity")
        return
    m_cm = m * 0.7
    print("Measured " + str(m_cm) + " at " + str(angle))
    msg = str(angle) + " " + str(m_cm)
    send_to_socket(clientsocket, msg)


def scan(precision, num_scans, increasing):
    total_rotation = (num_scans - 1) * precision
    if not increasing:
        total_rotation = -total_rotation

    start_motor_position = motor_sensor.position
    next_scan_at = 0

    rotate_sensor(total_rotation, block=False)

    while motor_sensor.is_running:
        relative_motor_position = motor_sensor.position - start_motor_position
        if abs(relative_motor_position / SCAN_POSITION_FACTOR) >= next_scan_at:
            measure_and_send(next_scan_at)
            next_scan_at += precision

    # Check if the last measurement was made
    if next_scan_at <= total_rotation:
        measure_and_send(next_scan_at)

    send_to_socket(clientsocket, "END")


with clientsocket:
    try:
        while True:
            c = receive_from_socket(clientsocket)
            if not c:
                break
            command, *params = c.split(" ")
            if command == "MOVE":
                move_forward(float(params[0]))
            elif command == "ROTATE":
                rotate(float(params[0]))
            elif command == "SCAN":
                precision = float(params[0])
                num_scans = float(params[1])
                increasing = params[2] == "True"
                scan(precision, num_scans, increasing)
            elif command == "ROTATESENSOR":
                rotate_sensor(float(params[0]))
            else:
                print("Unknown command: " + command)
    except (KeyboardInterrupt, RuntimeError):
        if SOUND_ON:
            sound.speak("Shut down.")
        print("Shut down")
        rotate_sensor_to_zero_position()
