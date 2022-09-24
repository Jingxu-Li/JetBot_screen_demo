# -*- coding: utf-8 -*-
"""
Created on Sun Sep 11 16:29:44 2022

@author: dj079
"""
import cv2
import numpy as np
import time

import image_utils as iu
from car_state import car
import trace_target as trace_t
from test_udp_server import mainServer

debug_mode = False

if __name__ == "__main__":

    HOST, PORT = "192.168.43.2", 8888
    main_server = mainServer(HOST, PORT)

    traces = trace_t.get_target()
    car_red = car(ip="192.168.43.229", port=23, color_low=np.array([15, 220, 240]),
                  color_high=np.array([30, 245, 255]), traces=traces[2:4])
    cap = iu.initial_cap()
    folder = "{}".format(time.time())
    count = 0

    while True:
        print("====================")
        img = iu.get_image(cap, debug_mode)
        img1 = iu.image_undistort(img)
        cv2.imwrite("./{}/{}.jpg".format(folder, count), img1)
        car_red.update(img1)
        main_server.set_speed((car_red.ip, car_red.port), car_red.vl, car_red.vr)

    main_server.set_speed((car_red.ip, car_red.port), 0, 0)
    main_server.receive_close()
