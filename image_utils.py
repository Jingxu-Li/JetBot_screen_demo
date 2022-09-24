# -*- coding: utf-8 -*-
"""
Created on Sun Sep 11 17:01:44 2022

@author: dj079
"""

import cv2
import numpy as np
import matplotlib.pyplot as plt

camera_matrix = np.array([[2274.70044231214, 0, 0],
                          [0, 2277.47577542350, 0],
                          [1891.36869963620, 1068.40034012363, 1]])
camera_matrix = camera_matrix.T

# k1,k2
radial_distortion = np.array([0.155441871929529,-0.274063403031581])
# p1,p2
tangential_distortion = np.array([0,0])
# Here I modified the parameters to get better performance
# distortion = np.array([0.155441871929529,-0.274063403031581,0,0])
distortion = np.array([0.1,-0.12,0,0])


# image size: 3840*2160
# 变换前的四个角点(左上、右上、左下、右下)
pts1 = np.float32([[172,227], [3712,244], [91,2022], [3765,2053]])
# 变换后的四个角点(左上、右上、左下、右下)
pts2 = np.float32([[0, 0],[3840, 0],[0, 2160],[3840,2160]])
# 生成透视变换矩阵；进行透视变换
P_Matrix = cv2.getPerspectiveTransform(pts1, pts2)

def initial_cap():
    
    cap = cv2.VideoCapture(1 + cv2.CAP_DSHOW)
    
    width = 3840  #定义摄像头获取图像宽度
    height = 2160   #定义摄像头获取图像长度
    
    cap.set(cv2.CAP_PROP_FRAME_WIDTH, width)  #设置宽度
    cap.set(cv2.CAP_PROP_FRAME_HEIGHT, height)  #设置长度
    
    flag = cap.isOpened()
    if not flag:
        print("Camera is not opened")
    else:
        print("Camera opened")
        return cap

def get_image(cap,debug_mode):
    
    frame = None
    if debug_mode:    
        frame = cv2.imread('WIN_20220824_21_56_18_Pro.jpg')
    else:
        try:
            ret, frame = cap.read() 
            # plt.imshow(frame)
            # plt.show()
        except Exception as e:
            print(e)
    return frame

def image_undistort(img):
    
    # get undistorted image, return HSV converted image
    img_undistored = cv2.undistort(img, camera_matrix, distortion)

    trans_frame = cv2.warpPerspective(img_undistored, P_Matrix, (3840,2160))
    trans_frame = cv2.cvtColor(trans_frame,cv2.COLOR_BGR2HSV)
    return trans_frame