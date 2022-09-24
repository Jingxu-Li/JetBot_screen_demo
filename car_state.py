# -*- coding: utf-8 -*-
"""
Created on Sun Sep 11 16:33:48 2022

@author: dj079
"""

import cv2
import math
import numpy as np

dx = 240
dy = 270
end_task_index = 15

left_border = 2*dx
right_border = 14*dx


class car:
    
    # self properties
    ip = "0.0.0.0"
    port = 8888
    color_high = np.zeros(shape = (1,3))
    color_low = np.zeros(shape = (1,3))
    
    # motion properties
    x = 0 # central points (x,y)
    y = 0
    v = 0 # Updated by left and right wheel speed
    yaw = 0
    
    # properties for drawing line and planning
    central_point = []
    forward = "left" # This forward is used for drawing line
    front_middle_point = [] # Check the car border
    back_middle_point = []

    # target_points
    traces = []
    trace_forward = [] # left to right is forward
    trace_backward = [] # right to left is backward    
    dis_y = 0
    
    
    def __init__(self, ip, port, color_low, color_high, traces):
        self.ip = ip
        self.port = port
        self.color_low = color_low
        self.color_high = color_high
        self.traces = traces
        print(traces)
        self.trace_forward = traces[0]
        self.trace_backward = traces[1]
        self.task_trace = []
        self.state = ""
        self.contours = 0
        
    def print_msg(self):
        print("My points:")
        print(self.front_middle_point)
        print(self.back_middle_point)
        print(self.central_point)
        
        
    def calc_nearest_index(self):
        
        # calculate dx and dy of each point
        d_f = [(self.x,self.y) - point for point in self.trace_forward]
        d_b = [(self.x,self.y) - point for point in self.trace_backward]
        
        # calculate distance of each point
        d_f = [abs(math.sqrt(idx ** 2 + idy ** 2)) for (idx, idy) in d_f]
        d_b = [abs(math.sqrt(idx ** 2 + idy ** 2)) for (idx, idy) in d_b]
        
        mind_f = min(d_f)
        mind_b = min(d_b)
        
        ind = d_f.index(mind_f) if mind_f < mind_b else d_b.index(mind_b)
        self.forward = "left" if mind_f < mind_b else "right"
        self.task_trace = self.trace_forward if mind_f < mind_b else self.trace_backward
        if self.task_trace == self.trace_backward and ind == end_task_index:
            self.roll_back()
            
        self.goal = self.task_trace[ind + 1]
        return ind
    
    def calc_y_dis(self):
        y_line = self.traces[0][0][1] if self.forward == "left" else self.traces[1][0][1]
        if self.forward == "left":
            print("Current trace:",self.traces[0][0][1])
        else:
            print("Current trace:",self.traces[1][0][1])
        print("Current y:",self.y)
        print("Current dis:",y_line-self.y)
        self.dis_y = y_line - self.y
                     
    def update_point(self,img):
        
        # hsv select region of interest
        mask = cv2.inRange(img,self.color_low,self.color_high)
        
        # remove holes in the car surface
        kernel = cv2.getStructuringElement(cv2.MORPH_RECT, (5, 5))  # 矩形结构
        open_res = cv2.morphologyEx(mask, cv2.MORPH_CLOSE, kernel, iterations=2)
        
        # Find biggest contours
        _, contours, _ = cv2.findContours(open_res, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
        area = []
        print("Len of contours:",len(contours))
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
        # cv2.drawContours(trans_frame, [pts], 0, (255, 0, 0), 3)
    
        # find the first two points for the forward part
        if self.forward == "left":
            front = pts[0:2]
            back = pts[2:4]
        else:
            front = pts[2:4]
            back = pts[0:2]
        front_middle_point_float = [(front[0][0]+front[1][0])/2, (front[0][1]+front[1][1])/2]
        back_middle_point_float = [(back[0][0]+back[1][0])/2, (back[0][1]+back[1][1])/2]
        central_point_float = [(front_middle_point_float[0]+ back_middle_point_float[0])/2,\
                               (front_middle_point_float[1]+ back_middle_point_float[1])/2]
        self.front_middle_point = np.int0(front_middle_point_float)
        self.back_middle_point = np.int0(back_middle_point_float)
        self.central_point = np.int0(central_point_float)
        self.x = self.central_point[0]
        self.y = self.central_point[1]
        
    def update_state(self):
        if self.self.front_middle_point[0] < left_border:
            self.state = "turn_left" 
        elif self.self.front_middle_point[0] > right_border:
            self.state = "turn_right"
        else:
            self.state = "straight"
            
    def update(self, img):
        self.update_point(img)
        self.print_msg()
        self.calc_y_dis()
        

        
        # TODO: Update the distance to the goal
        
