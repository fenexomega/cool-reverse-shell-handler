#!/usr/bin/python3
# -*- coding: utf-8 -*-

import socket
import threading
import time

TIME_TO_WAIT = 0.1

class simplesocket(threading.Thread):
    def __init__(self,id,ip,port,conn,observers,conns_list):
        super().__init__()
        self.ip         = ip
        self.port       = port
        self.observers  = observers
        self.tcp        = conn
        self.online     = True
        self.conns_list = conns_list
        self.id         = id 
        self.out_queue  = []

    def sendall(self,message):
        self.tcp.sendall(message.encode())

    def notify(message):
        for o in self.observers:
            o.notify(id,message)

    def notify_offline():
        for o in self.observers:
            o.notify_offline(self)

    def sendall(message):
        self.out_queue.append(message)

    def run(self):
        con_list = [self.tcp]
        try:
            while self.online:
                print("WAITING INPUT")
                time.sleep(TIME_TO_WAIT)
                if  not self.online:
                    break
                else:
                    r,s,e = \
                        select.select(con_list,con_list,[],TIMEOUT)
                    for c in s:
                        for msg in self.out_queue:
                            c.sendall(msg.encode())
                        self.out_queue.clear()
                    for c in r:
                            msg = c.recv(BUFFER).decode('utf8')
                            if msg:
                                self.notify(msg)
                            else:
                                self.shutdown()
                                self.online = False
                                break
        except Exception as e:
            print(e)
        finally:
            if self.online:
                self.shutdown()
            self.remove_itself()
    
    def shutdown(self):
        self.online = False
        self.tcp.shutdown(socket.SHUT_RDWR)
        self.tcp.close()
        self.notify_offline()

    def close(self):
        if self.online:
            self.shutdown()
        self.join()
        pass




