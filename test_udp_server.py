# -*- coding: utf-8 -*-
"""
Created on Sun Sep 11 18:08:09 2022

@author: dj079
"""

import socketserver, threading, time
import socket
import sys

class ThreadedUDPRequestHandler(socketserver.BaseRequestHandler):
    
    def handle(self):
        data = self.request[0].strip()
        socket = self.request[1]
        current_thread = threading.current_thread()
        print("{}: client: {}, wrote: {}".format(current_thread.name, self.client_address, data))
        res = data.decode('utf-8').split('-')
        if res[0] == "gr":
            left_speed = res[1]
            right_speed = res[2]
            print("res from car: left_speed:{}, right_speed:{}".format(left_speed,right_speed))
        

class ThreadedUDPServer(socketserver.ThreadingMixIn, socketserver.UDPServer):
    pass

class mainServer():
    
    host = "0.0.0.0"
    port = 1234
    server = None
    server_thread = None
    server_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    main_thread = None
    def __init__(self,host,port):
        self.server = ThreadedUDPServer((host, port), ThreadedUDPRequestHandler)
        self.server_thread = threading.Thread(target=self.server.serve_forever)
        self.server_thread.daemon = True
        self.host = host
        self.port = port
        self.main_thread = threading.Thread(target=self.receive_begin)
        
        self.main_thread.start()
        
        
    def request_speed(self, addr):
        data = "g"
        self.server_socket.sendto(data.encode("utf-8"), addr)
        
    def set_speed(self, addr, left_speed, right_speed):
        data = "s-{}-{}".format(left_speed,right_speed)
        self.server_socket.sendto(data.encode("utf-8"), addr)
    
    def turn_right_little(self, addr, dis, time):
        data = "r-{}-{}".format(dis,time)
        self.server_socket.sendto(data.encode("utf-8"), addr)
        
    def turn_left_little(self, addr, dis, time):
        data = "l-{}-{}".format(dis,time)
        self.server_socket.sendto(data.encode("utf-8"), addr)
    
    def go_straight(self, addr, speed, t):
        data = "st-{}-{}".format(speed,t)
        self.server_socket.sendto(data.encode("utf-8"), addr)
    
    def receive_close(self):
        self.server.shutdown()
        self.server.server_close()
        self.server_socket.close()
        sys.exit()
    
    def receive_begin(self):
        try:
            self.server_thread.start()
            print("Server started at {} port {}".format(self.host, self.port))
            while True: time.sleep(100)
        except (KeyboardInterrupt, SystemExit):
            self.server.shutdown()
            self.server.server_close()
            sys.exit()
    
if __name__ == "__main__":
    
    HOST, PORT = "192.168.43.2", 8888
    server = ThreadedUDPServer((HOST, PORT), ThreadedUDPRequestHandler)

    server_thread = threading.Thread(target=server.serve_forever)
    server_thread.daemon = True
    try:
        server_thread.start()
        print("Server started at {} port {}".format(HOST, PORT))
        while True: time.sleep(100)
    except (KeyboardInterrupt, SystemExit):
        server.shutdown()
        server.server_close()
        exit()