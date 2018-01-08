#!/usr/bin/python3
# -*- coding: utf-8 -*-

from select import select
import socket 
import threading
import json
PORT            = 6969
HOST            = '0.0.0.0'
MAX_CONNECTIONS = 10
TIMEOUT         = 5.0 # IN SECONDS
BUFFER          = 8096

connected_clients = []


class ClientThread(threading.Thread):
    """Thread que envia input e output do shell para o cliente"""
    def __init__(self,conn,ip):
        super().__init__()
        self.in_queue   =   []
        self.out_queue  =   []
        self.conn       =   conn
        self.ip         =   ip
        self.online     =   True
    
    def execute_cmd(self,cmd):
        #EXECUTE COMMAND
        try:
            cmd = json.dumps(cmd)
            self.shell_id = cmd['id']
            shell = self.server.conns[shell_id]
            if not conn.online:
                send_in_json('Error: That connection is closed')
                return
            shell.sendall(cmd['cmd'])
            output = shell.recv()
            send_in_json(output)
        except IndexError:
            send_in_json('Error: That connection doesn\'t exist')
    
    def send_in_json(self,message):
        obj = {'message' : message }
        message = json.dumps(obj)
        self.out_queue.append(message)

    def notify(self,message):
       msg = json.dumps({'message':message})
       send_in_json(msg)

    def run(self):
        con_list = [self.conn]
        try:
            while True:
                receivers, senders, errors_rec = \
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
        self.conn.shutdown(socket.SHUT_RDWR)
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
#                connection.setblocking(False)
                ct = ClientThread(connection,ip)
                ct.start()
                connected_clients.append(ct)
                self.send_shell_list(ct) 
            #TODO CONDITION TO EXIT?
        except Exception as e:
            #TODO
            #MOSTRAR MELHOR E FAZER LOG
            print(e)
        finally:
            if self.online:
                self.close_connection()

    def close_connection(self):
        for ct in connected_clients:
            ct.stop_connection()
        for ct in connected_clients:
            ct.join()
        self.tcp.shutdown(socket.SHUT_RDWR)
        self.tcp.close()
        self.online = False
         
    def notify(self,connection):
        for client in connected_clients:
            client.notify(connection)
        
