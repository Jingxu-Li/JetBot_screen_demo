# -*- coding: utf-8 -*-
"""
Created on Thu Oct  6 22:46:55 2022

@author: dj079
"""
from car_state import car
import math


class car_s(car):
    ''' Setup as clockwise to be omega positive position
    '''
    theta = 0
    omega = 0
    velocity = 0

    def update(self):
        self.omega = (self.vl - self.vr) / self.l
        self.velocity = (self.vl + self.vr) / 2
        delta_t = 0.1
        self.x += self.velocity * math.cos(self.theta) * delta_t
        self.y += self.velocity * math.sin(self.theta) * delta_t
        self.theta += self.omega * delta_t
