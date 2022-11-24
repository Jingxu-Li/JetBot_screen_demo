# -*- coding: utf-8 -*-
"""
Created on Sun Sep 11 16:33:48 2022

@author: dj079
"""

import cv2
import math
import numpy as np

import image_utils as iu

dx = 240
dy = 270
end_task_index = 15

left_border = 2*dx
right_border = 14*dx


class car:

    # self properties
    ip = "0.0.0.0"
    port = 8888
    color_high = np.zeros(shape=(1, 3))
    color_low = np.zeros(shape=(1, 3))

    l = 120
    r = 30
    
    # control period
    delta_t = 0.1
    
    # motion properties
    x = 0                       # central points (x,y)
    y = 0
    v = 0                       # Updated by left and right wheel speed
    yaw = 0                     # angle of car

    vc = 200                    # mm/s -- vp = vl = vr = 0.1

    # kinematics
    vl = 0
    vr = 0

    # properties for drawing line and planning
    central_point = ()
    forward = "go"              # go: x++ back: x--
    ey = 0                      # distance point to line
    ld = 0                      # distance to next point
    e = 0

    # target_points
    traces = []
    previous_target = 0
    next_target = 1
    number = 0

    def __init__(self, ip, port, color_low, color_high, traces, vc=None):
        self.ip = ip
        self.port = port
        self.color_low = color_low
        self.color_high = color_high
        self.traces = traces
        print(traces)
        self.contours = 0
        if vc:
            self.vc = vc

    def print_msg(self):
        print("My points:")
        print(self.central_point)

    def calc_y_dis(self):
        point1 = self.traces[self.previous_target]
        point2 = self.traces[self.next_target]
        if point1[0] == point2[0]:
            return self.x - point1[0]
        # y = (y2-y1)/(x2-x1)*(x-x1) + y1
        # A = (point2[1] - point1[1])/(point2[0] - point1[0])
        # B = -1
        # C = point1[0]**2*(point1[1]-point2[1])*(point2[0]-point1[0]) + point1[1]
        # self.ey = abs(A*self.x + B*self.y + C)/(math.sqrt(A**2 + B**2))
        self.ey = self.y - point2[1]
        print("ey:", self.ey)

    def calc_target(self, th):
        # Calculate previous target and next target
        target = self.traces[self.previous_target]
        self.ld = math.sqrt((self.x-target[0])**2 + (self.y-target[1])**2)
        # if self.ld < th:
        #     self.previous_target += 1
        #     self.next_target += 1
        #     if self.next_target == len(self.traces):
        #         self.next_target = 0
        # while self.x > self.traces[self.previous_target][0]:
        #     self.previous_target += 1
        #     self.next_target += 1
        for index, point in enumerate(self.traces):
            if point[0] > self.x:
                self.next_target = index
                break
        print("next target value:", self.traces[self.next_target])

    def update_point_simulate(self):
        self.v = (self.vl + self.vr) / 2
        self.delta_yaw = abs(self.vl - self.vr) / self.l
        self.x = self.x + self.v * math.cos(self.yaw) * self.delta_t
        self.y = self.y + self.v * math.sin(self.yaw) * self.delta_t
        self.yaw = self.yaw + self.delta_yaw * self.delta_t

    def update_point(self, img):

        # hsv select region of interest
        mask = cv2.inRange(img, self.color_low, self.color_high)

        # remove holes in the car surface
        kernel = cv2.getStructuringElement(cv2.MORPH_RECT, (5, 5))  # 矩形结构
        open_res = cv2.morphologyEx(mask, cv2.MORPH_CLOSE, kernel, iterations=2)

        # Find biggest contours
        _, contours, _ = cv2.findContours(open_res, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
        area = []
        print("Len of contours:", len(contours))
        self.contours = len(contours)
        if len(contours) != 0:
            for i in range(len(contours)):
                area.append(cv2.contourArea(contours[i]))
            max_idx = np.argmax(area)
        else:
            return
        # Find a min box containing the max contour
        min_box = cv2.minAreaRect(contours[max_idx])
        pts = np.int0(cv2.boxPoints(min_box))
        cv2.drawContours(open_res, [pts], 0, (255, 0, 0), 3)
        cv2.imwrite("pics/{}_{}_{}.jpg".format(self.number, self.x, self.y), open_res)
        self.number += 1
        # find the first two points for the forward part
        if self.forward == "left":
            front = pts[0:2]
            back = pts[2:4]
        else:
            front = pts[2:4]
            back = pts[0:2]
        front_middle_point_float = [(front[0][0]+front[1][0])/2, (front[0][1] + front[1][1])/2]
        back_middle_point_float = [(back[0][0]+back[1][0])/2, (back[0][1] + back[1][1])/2]
        central_point_float = ((front_middle_point_float[0] + back_middle_point_float[0])/2,
                               (front_middle_point_float[1] + back_middle_point_float[1])/2)

        self.central_point = iu.unitPixelToDis(central_point_float)
        self.x = self.central_point[0]
        self.y = self.central_point[1]

    def update(self, img):
        self.update_point(img)
        self.print_msg()
        self.calc_y_dis()
        self.calc_target(50)
        self.purely_pursuit(self.next_target, 100)

    def inverse_kine_v(self, vm):
        vp = (vm - 111.8)/878
        return vp

    def purely_pursuit(self, target_index, th):
        # Calculate target velocity of each wheel
        # target: next point need to pursuit, (x,y)
        target = self.traces[target_index]
        self.ld = math.sqrt((self.x-target[0])**2 + (self.y-target[1])**2)
        turn = ""
        if abs(self.ey) < th:
            self.vl = self.inverse_kine_v(self.vc)
            self.vr = self.inverse_kine_v(self.vc)
            return
        if self.forward == "go":
            if self.y - target[1] > 0:
                turn = "left"
            elif self.y - target[1] < 0:
                turn = "right"
            else:
                turn = "straight"
        else:
            if self.y - target[1] < 0:
                turn = "left"
            elif self.y - target[1] > 0:
                turn = "right"
            else:
                turn = "straight"
        delta = self.l * abs(self.ey) * self.vc / self.ld**2
        print("Current turn:", turn)
        print("Current ld:", self.ld)
        if turn == "left":
            self.vl = self.inverse_kine_v(self.vc - delta)
            self.vr = self.inverse_kine_v(self.vc + delta)
        elif turn == "right":
            self.vl = self.inverse_kine_v(self.vc + delta)
            self.vr = self.inverse_kine_v(self.vc - delta)
        else:
            self.vl = self.inverse_kine_v(self.vc)
            self.vr = self.inverse_kine_v(self.vc)
        if self.vl < 0:
            self.vl = 0.01
        if self.vr < 0:
            self.vr = 0.01
        if self.vl > self.inverse_kine_v(self.vc):
            self.vl = self.inverse_kine_v(self.vc)
        if self.vr > self.inverse_kine_v(self.vc):
            self.vr = self.inverse_kine_v(self.vc)
