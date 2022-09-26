# -*- coding: utf-8 -*-
"""
Created on Sun Sep 11 16:29:44 2022

@author: dj079
"""
import cv2
import numpy as np
import os
import time

import image_utils as iu
from car_state import car
import trace_target as trace_t
from test_udp_server import mainServer
import car_logger

debug_mode = False

del_list = os.listdir("pics")
for f in del_list:
    file_path = os.path.join("pics", f)
    if os.path.isfile(file_path):
        os.remove(file_path)

if __name__ == "__main__":

    HOST, PORT = "192.168.43.2", 8888
    main_server = mainServer(HOST, PORT)

    traces = trace_t.get_target()
    car_red = car(ip="192.168.43.229", port=23, color_low=np.array([15, 240, 195]),
                  color_high=np.array([30, 255, 205]), traces=traces[2]) # +traces[3][-1::]
    cap = iu.initial_cap()
    # folder = "{}".format(time.time())
    # car_logger.logger.info("folder:", folder)
    count = 0

    while True:
        try:
            print("====================")
            img = iu.get_image(cap, debug_mode)
            img1 = iu.image_undistort(img)
            cv2.imwrite("pics/{}.jpg".format(count), img1)
            count += 1
            car_red.update(img1)

            while car_red.contours == 0:
                img = iu.get_image(cap, debug_mode)
                img1 = iu.image_undistort(img)
                car_red.update(img1)
            print("Current car speed: {},{}".format(car_red.vl, car_red.vr))
            main_server.set_speed((car_red.ip, car_red.port), car_red.vl, car_red.vr)
            # time.sleep(1)
        except KeyboardInterrupt:
            main_server.set_speed((car_red.ip, car_red.port), 0, 0)
            main_server.receive_close()
