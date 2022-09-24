# -*- coding: utf-8 -*-
"""
Created on Sun Sep 11 20:13:56 2022

@author: dj079
"""


def get_target():
    dx = 240
    dy = 270
    trace_x = [(i + 0.5)*dx for i in range(1, 15)]
    trace_y = [(i + 0.5)*dy for i in range(1, 7)]
    traces = []
    for y in trace_y:
        trace = []
        for x in trace_x:
            trace.append((int(x), int(y)))
        traces.append(trace)
    return traces
