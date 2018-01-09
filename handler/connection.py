#!usr/bin/python3
# -*- coding: utf-8 -*-

class Connection(object):

    """Docstring for Connection. """
    BUFFER = 8096

    def __init__(self,conn,ip,id,handler):
        """TODO: to be defined1. """
        self.handler = handler
        self.tcp = conn
        self.online = True
        self.ip = ip #TODO
        self.id = id

    def closeCon(self):
        self.tcp.close()
        self.online = False

    def recv(self,buffer=BUFFER):
        return self.tcp.recv(buffer).decode('utf8')
    
    def sendall(self,message):
        self.tcp.sendall(message.encode()) 
