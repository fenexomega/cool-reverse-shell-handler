#!/usr/bin/python3
# -*- coding: utf-8 -*-

from select import select
import socket 
import threading
import json
import time
PORT            = 6969
HOST            = '0.0.0.0'
MAX_CONNECTIONS = 10
TIMEOUT         = 5.0 # IN SECONDS
BUFFER          = 8096
TIME_TO_WAIT    = 0.1 

connected_clients = []


class ClientThread(threading.Thread):
    """Thread que envia input e output do shell para o cliente"""
    def __init__(self,conn,ip,shells):
        super().__init__()
        self.out_queue  =   []
        self.conn       =   conn
        self.ip         =   ip
        self.online     =   True
        self.shells     =   shells
    
    def execute_cmd(self,cmd):
        #EXECUTE COMMAND
        try:
            cmd = json.loads(cmd)
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
            while self.online:
                time.sleep(TIME_TO_WAIT)
                senders,receivers, errors_rec = \
                        select(con_list,con_list,[],TIMEOUT)
                for r in receivers:
                    for msg in self.out_queue:
                        r.sendall(msg.encode())
                    self.out_queue.clear()
                for s in senders:
                        msg = s.recv(BUFFER).decode('utf8')
                        if msg:
                            self.execute_cmd(msg)
        except Exception as e:
            print("Connection Closed")
            print(e)
        finally:
            if self.online:
                self.stop_connection()
            self.remove_itself()
    
    def stop_connection(self):
        self.conn.shutdown(socket.SHUT_RD)
        self.online = False
        self.conn.close()

    def remove_itself(self):
        global connected_clients
        connected_clients.remove(self) 


#ORGANIZE THIS IN ANOTHER THREAD
class JsonExposer(threading.Thread):

    """Docstring for JsonExposer. """

    def __init__(self,shells):
        """TODO: to be defined1. """
        super().__init__()
        self.shells = shells
        self.tcp = socket.socket(socket.AF_INET,socket.SOCK_STREAM)
        self.tcp.bind((HOST,PORT))
        self.tcp.listen(MAX_CONNECTIONS)
        self.online = True

    def send_shell_list(self,ct):
        # TODO
        l = []
        for shell in self.shells:
            if shell.online:
                obj = {'id':self.shells.index(shell), \
                        'ip': shell.ip}
                l.append(obj)
        obj = {'type':'info','title':'connected_clients','content':l}
        ct.send_in_json(obj)

    def run(self):
        try:
            while True:
                connection, ip = self.tcp.accept()
                print('Received Connection from {}'.format(ip))
                connection.setblocking(False)
                ct = ClientThread(connection,ip,self.shells)
                ct.start()
                connected_clients.append(ct)
                self.send_shell_list(ct) 
            #TODO CONDITION TO EXIT?
        except Exception as e:
            #TODO
            #MOSTRAR MELHOR E FAZER LOG
            print(e)
        finally:
            self.close_connection()

    def close_connection(self):
        for ct in connected_clients:
            ct.stop_connection()
        for ct in connected_clients:
            ct.join()
        self.tcp.shutdown(socket.SHUT_WR)
        self.tcp.close()
        self.online = False
         
    def notify(self,connection):
        for client in connected_clients:
            client.notify(connection)

    def notifyOffline(self,connection):
        pass
        
