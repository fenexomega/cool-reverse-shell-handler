#!/usr/bin/python3
# -*- coding: utf-8 -*-

from clientthread import ClientThread
from select import select
import socket
import threading
import time

TIMEOUT         = 5.0 # IN SECONDS
PORT            = 6969
HOST            = '0.0.0.0'
MAX_CONNECTIONS = 10


####https://docs.python.org/3/library/selectors.html



#ORGANIZE THIS IN ANOTHER THREAD
class JsonExposer(threading.Thread):

    """Docstring for JsonExposer. """

    def __init__(self,shells):
        """TODO: to be defined1. """
        super().__init__()
        self.connected_clients = []
        self.shells = shells
        self.tcp = socket.socket(socket.AF_INET,socket.SOCK_STREAM)
        self.tcp.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
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
        obj = {'messageType':4,'content':{'title':'connected_clients','content':l}}
        ct.send_in_json(obj)

    def run(self):
        try:
            while self.online:
                print("Waiting accept()")
                r,w,e = select([self.tcp],[self.tcp],[],TIMEOUT)
                if r:
                    connection, ip = self.tcp.accept()
                    print('Received Connection from {}'.format(ip))
                    ct = ClientThread(connection,ip,self.shells,self.connected_clients)
                    ct.start()
                    self.connected_clients.append(ct)
                    self.send_shell_list(ct)
            #TODO CONDITION TO EXIT?
        #except Exception as e:
        #    #TODO
        #    #MOSTRAR MELHOR E FAZER LOG
        #    print("Exception in exposer:")
        #    print(e)
        finally:
            print("Exiting Thread")
            if self.online:
                self.close_connection()

    def close_connection(self):
        for ct in self.connected_clients:
            ct.stop_connection()
        for ct in self.connected_clients:
            ct.join()
        print("closing exposer")
        self.tcp.shutdown(socket.SHUT_RDWR)
        self.tcp.close()
        self.online = False
        print("exposer closed")

    def notify(self,connection):
        for client in self.connected_clients:
            client.notify(connection)

    def notifyOffline(self,connection):
        pass

