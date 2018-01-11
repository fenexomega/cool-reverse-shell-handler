#!/usr/bin/python3
# -*- coding: utf-8 -*-

import socket
import threading
import time

TIME_TO_WAIT = 0.1

class simplesocket(threading.Thread):

    def __init__(self,ip,port,conn,observers):
        super().__init__()
        self.ip = ip
        self.port = port
        self.observers = observers
        self.tcp = conn
        self.online = True

    def sendall(self,message):
        self.tcp.sendall(message.encode())

    def run(self):
        con_list = [self.tcp]
        i = 0
        try:
            loop = True
            while loop:
                print("WAITING INPUT")
                time.sleep(TIME_TO_WAIT)
                if self.conn.fileno() == -1 or not self.online:
                    break
                else:
                    senders,receivers, errors_rec = \
                        select.select(con_list,con_list,[],TIMEOUT)
                    for r in receivers:
                        for msg in self.out_queue:
                            r.sendall(msg.encode())
                        self.out_queue.clear()
                    for s in senders:
                            msg = s.recv(BUFFER).decode('utf8')
                            if msg:
                                self.execute_cmd(msg)
                            else:
                                loop = False
        except Exception as e:
            print(e)
        finally:
            if self.online:
                self.stop_connection()
            self.remove_itself()


    def close(self):

        self.join()
        pass




