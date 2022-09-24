from jetbot import Robot

import socket
import sys
import time


robot = Robot()
sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
sock.bind(('',23))
host = ('192.168.43.2',8888)

def close_loop_straight(speed, t):
    counts = 10*t
    robot.set_motors(speed,speed)
    factor = 2
    for count in range(1,int(counts)+1):
        left_motor_speed, right_motor_speed = robot.get_motors()
        print("Count and speed:",count,left_motor_speed, right_motor_speed)
        if left_motor_speed < right_motor_speed:
            rate = (right_motor_speed - left_motor_speed)/left_motor_speed
            robot.set_motors((1+factor*rate)*speed,speed)
            print("left small speed:",(1+factor*rate)*speed, speed)
        elif left_motor_speed > right_motor_speed:
            rate = (left_motor_speed - right_motor_speed)/right_motor_speed
            robot.set_motors(speed,(1+factor*rate)*speed)
            print("right small speed:",speed,(1+factor*rate)*speed)
        else:
            robot.set_motors(speed,speed)
        time.sleep(0.1)

scale_factor = 0.001
while True:
    try:
        received = str(sock.recv(1024), "utf-8")
        data = received.split('-')
        if data[0] == 'g':
            left_motor_speed, right_motor_speed = robot.get_motors()
            data = "gr-{}-{}".format(left_motor_speed,right_motor_speed)
            print(data)
            sock.sendto(data.encode('utf-8'),host)
        elif data[0] == 's':
            print("set speed:",data)
            robot.set_motors(float(data[1]), float(data[2]))
        elif data[0] == 'st':
            print("go straight:",data)
            close_loop_straight(float(data[1]), float(data[2]))
        elif data[0] == 'l':
            print("turn_left:",data)
            add_rate = scale_factor*float(data[1])
            if add_rate>0.1:
                add_rate = 0.1
            robot.set_motors(0.01, 0.6)
            time.sleep(float(data[2]))
        elif data[0] == 'r':
            print("turn_right:",data)
            add_rate = scale_factor*float(data[1])
            if add_rate>0.1:
                add_rate = 0.1
            robot.set_motors(0.6, 0.01)
            time.sleep(float(data[2]))
            
    except Exception as e:
        print(e)