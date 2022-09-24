# -*- coding: utf-8 -*-
"""
Created on Sun Sep 11 16:29:44 2022

@author: dj079
"""
import cv2
import math
import matplotlib.pyplot as plt
import numpy as np
import time

import image_utils as iu
from car_state import car
import trace_target as trace_t
from test_udp_server import mainServer

debug_mode = False
dx = 240
dy = 270
end_task_index = 15

left_border = 2*dx
right_border = 14*dx

def fix_straight(car, th):
    # return if car is needed to turn
    if abs(car.dis_y) >= th:
        if car.dis_y < 0:
            return "l" if car.forward == "left" else "r"
        elif car.dis_y > 0:
            return "r" if car.forward == "left" else "l"
    else:
        return "n"
    

if __name__ == "__main__":

    HOST, PORT = "192.168.43.2", 8888
    main_server = mainServer(HOST,PORT)
    
    traces = trace_t.get_target()                
    car_red = car(ip="192.168.43.229", port = 23, color_low = np.array([15,220,240]), \
                  color_high = np.array([30,245,255]), traces = traces[2:4])
        
    # Step1: Straight line - left to right
    
    car_red.forward = "left"
    cap = iu.initial_cap()
    
    for i in range(0,10):
        print("count :",i)
        main_server.go_straight((car_red.ip,car_red.port),0.25,0.5)
        time.sleep(0.5)
        img = iu.get_image(cap,debug_mode)
        img1 = iu.image_undistort(img)
        
        car_red.update(img1)
        while car_red.contours == 0:
            img = iu.get_image(cap,debug_mode)
            img1 = iu.image_undistort(img)
            car_red.update(img1)
            
        act_ch = fix_straight(car_red,100)
        cv2.imwrite("./logs/{}-{}.jpg".format(i,car_red.dis_y), img1)
        print("Current fix is:",act_ch)
        if act_ch == "l":
            main_server.turn_left_little((car_red.ip,car_red.port),abs(car_red.dis_y),0.8)
            # main_server.turn_right_little((car_red.ip,car_red.port),abs(car_red.dis_y),0.1)
        elif act_ch == "r":
            main_server.turn_right_little((car_red.ip,car_red.port),abs(car_red.dis_y),0.8)
            # main_server.turn_left_little((car_red.ip,car_red.port),abs(car_red.dis_y),0.1)
        time.sleep(0.8)
    
    # Step2: First turn
    main_server.set_speed((car_red.ip,car_red.port),0,0)
    time.sleep(5)
    main_server.set_speed((car_red.ip,car_red.port),0.3,0.001)   
    time.sleep(2)
    main_server.set_speed((car_red.ip,car_red.port),0,0)
    
    # Step3: right to left
    # car_red.forward = "right"
    
    # for i in range(8,16):
    #     print("count :",i)
        
    #     img = iu.get_image(cap,debug_mode)
    #     img1 = iu.image_undistort(img)
        
    #     car_red.update(img1)
    #     while car_red.contours == 0:
    #         img = iu.get_image(cap,debug_mode)
    #         img1 = iu.image_undistort(img)
    #         car_red.update(img1)
            
    #     act_ch = fix_straight(car_red,30)
    #     cv2.imwrite("./logs/{}-{}.jpg".format(i,car_red.dis_y), img1)
    #     print("Current fix is:",act_ch)
        
    #     if act_ch == "l":
    #         main_server.turn_left_little((car_red.ip,car_red.port),abs(car_red.dis_y),0.2)
    #         main_server.turn_right_little((car_red.ip,car_red.port),abs(car_red.dis_y),0.1)
    #     elif act_ch == "r":
    #         main_server.turn_right_little((car_red.ip,car_red.port),abs(car_red.dis_y),0.2)
    #         main_server.turn_left_little((car_red.ip,car_red.port),abs(car_red.dis_y),0.1)
            
    #     time.sleep(0.3)
        
    #     main_server.go_straight((car_red.ip,car_red.port),0.25,0.5)
    #     time.sleep(0.4)
        
    # Step4: second turn
    # main_server.set_speed((car_red.ip,car_red.port),0,0)
    # time.sleep(5)
    # main_server.set_speed((car_red.ip,car_red.port),0.001,0.3)   
    # time.sleep(2.5)
    main_server.set_speed((car_red.ip,car_red.port),0,0)
    main_server.receive_close()
        
            