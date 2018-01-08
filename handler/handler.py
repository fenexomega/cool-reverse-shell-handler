#!/usr/bin/python3
# -*- coding: utf-8 -*-
from jsonexposer import JsonExposer
import socket
from connection import Connection

MAX_CONNECTIONS = 1000
PORT = 8080
IP   = '0.0.0.0'

class Handler(object):

    """Docstring for Handler. """

    def __init__(self):
        """TODO: to be defined1. """
        self.conns = []
        self.exposer = JsonExposer(self.conns)
        self.exposer.start()
        self.tcp = socket.socket(socket.AF_INET,socket.SOCK_STREAM)
        self.tcp.bind((IP,PORT))
    def run(self):
        self.tcp.listen(MAX_CONNECTIONS)
        id = 1
        try:
            while True:
                con, ip = self.tcp.accept()
                print('IP {}'.format(ip))
                C = Connection(con,ip,id,self)
                id += 1
                self.conns.append(C)
                self.exposer.notify(C)
        except KeyboardInterrupt:
            print("Exiting")
        except Exception as e:
            print("EXCEPTION")
            print(e)
        finally:
            self.tcp.close()
            self.exposer.close_connection()
            self.exposer.join()

    def notifyOffline(connection):
        print("Offline: {}".format(connection.ip))
        self.exposer.notifyOffline(connection)
        

def main():
    handler = Handler()
    handler.run()

if __name__ == "__main__":
    main()


        
        
