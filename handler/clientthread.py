#!/usr/bin/python3
# -*- coding: utf-8 -*-

import time
import json
import socket
import threading
import select

BUFFER          = 8096
TIMEOUT         = 5.0 # IN SECONDS
TIME_TO_WAIT    = 0.1
class ClientThread(threading.Thread):
    """Thread que envia input e output do shell para o cliente"""
    def __init__(self,conn,ip,shells,conn_clients):
        super().__init__()
        self.out_queue  =   []
        self.conn       =   conn
        self.ip         =   ip
        self.online     =   True
        self.shells     =   shells
        self.connected_clients = conn_clients
        self.conn.setblocking(False)

    def parse_msg(self,msg):
        msg = json.loads(msg)
        print(msg)
        if(msg['messageType'] == 'cmd'):
            self.execute_cmd(msg['content'])

    def execute_cmd(self,cmd):
        #EXECUTE COMMAND
        try:
            print(cmd)
            self.shell_id = cmd['id']
            shell = self.shells[self.shell_id]
            if not shell.online:
                self.send_in_json('Error: That connection is closed')
                return
            shell.sendall(cmd['cmd'])
            output = shell.recv()
            self.send_in_json(output)
        except IndexError:
            self.send_in_json('Error: That connection doesn\'t exist')

    def send_in_json(self,message):
        obj = {'message' : message }
        print(obj)
        message = json.dumps(obj)
        self.out_queue.append(message)

    def notify(self,message):
       msg = json.dumps(message)
       self.send_in_json(msg)

    def run(self):
        con_list = [self.conn]
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
                                self.parse_msg(msg)
                            else:
                                loop = False
        except Exception as e:
            print(e)
        finally:
            if self.online:
                self.stop_connection()
            self.remove_itself()

    def stop_connection(self):
        self.conn.shutdown(socket.SHUT_RD)
        self.online = False
        self.conn.close()
        print("Client {} desconnected ".format(self.ip))

    def remove_itself(self):
        self.connected_clients.remove(self)
