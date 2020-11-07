import socket
import select
import sys
import json
from Request import Request
from Response import Response
from ClientClass import Client
from Crypto.Cipher import AES

k1 = b'1111222233334444'  #ECB
k2 = b'1111222233334444'  #CFB
k3 = b'1111222233334444'
iv = b'4444333322221111'

THE_READER = 1 
THE_WRITER = 2

cipher = AES.new(k3, AES.MODE_ECB)   
writingTurn = True

class ConnectionsManager:
    

    def __init__(self, server_listener):
        self.server_listener = server_listener
        self.clients_list = [] 

    def get_connections(self):
        connections = [client.connection for client in self.clients_list]
        connections.append(self.server_listener)
        return connections

    def add_connection(self,client):
        client.data.update({"comunication_role": len(self.clients_list) + 1})
        self.clients_list.append(client)

    def get_client_by_connection_id(self, connection):
        try:
            return [client for client in self.clients_list if client.connection == connection][0]
        except:
            return None
        
    def readMessage(self, client):
        try:
            message_length = int(client.connection.recv(64))
            assert message_length > 0,"Connection Closed"
            #print("Message Length:", message_length)
            data = b''
            while message_length > 0:
                blob = client.connection.recv(16)
                message_length -= 16
                data = data + blob
            return data
        except:
            print("Error when reading from client.")
            raise
        
    def all_clients_chose_preferred_mode(self):
        if len(self.clients_list) < 2:
            return False
        for client in self.clients_list:
            if client.data.get("preferred_mode") == None:
                return False
        return True

    def get_chosen_mode(self):
        pref_modes = [client.data["preferred_mode"] for client in self.clients_list]
        if pref_modes.count("ECB") == 2:
            return "ECB"
        elif pref_modes.count("ECV") == 0:
            return "CFB"
        else:
            return "ECV" ## SCHIMBA CU CEVA RANDOM

    def all_clients_have_finished(self):
        return all( [client.data["hasFinished"] for client in self.clients_list] )

    def manageClient(self, connection):
        global writingTurn
        client = self.get_client_by_connection_id(connection)             #identify client data
        try:
            request_bits = self.readMessage(client)         # read the cryptic message
            request = Request(request_bits, cipher)         # form the request object 
                                                            #(this processes the cryptic message and makes it a easy to read dictionary)
                                                            #the client/server comunicates using json format

            request_code = request.body()["code"]           #each action has a different code

            if request_code == 1: #set preferred_mode
                client.data.update({"preferred_mode" : request.body()["data"]["mode"]})
                client.data.update({"step": 1})
                res = Response({"code":"Ok"},cipher)
                client.connection.send(res.len())
                client.connection.send(res._encode())

            if request_code == 2: #ask for chosen mode
                if self.all_clients_chose_preferred_mode(): # if it's ready send KEY, IV, MODE, if not tell to wait and ask later
                    chosen_mode = self.get_chosen_mode()  
                    client_iv = None
                    key =       None
                    if chosen_mode == "CFB":
                        client_iv = iv.decode('utf-8')
                        key = k2.decode('utf-8')
                    else:
                        key = k1.decode('utf-8')

                    res =Response({"code":"Ready",          # create the response with all necessary data
                        "data":{
                            "chosen_mode":chosen_mode,
                            "iv": client_iv,
                            "key": key,
                            "comunication_role": client.data["comunication_role"]
                        }
                    },cipher)
                    client.connection.send(res.len())
                    client.connection.send(res._encode())
                else:
                    res = Response({"code":"Not Ready"},cipher)
                    client.connection.send(res.len())
                    client.connection.send(res._encode())

            if request_code == 3:    # client informs that it has finished it's job writing/reading 8 blocks

                client.data.update({"hasFinished":True})
                if self.all_clients_have_finished():
                    for cl in self.clients_list:
                        cl.data.update({"canContinue": True})
                res = Response({
                        "code": "Ok"
                    }, cipher)
                client.connection.send(res.len())
                client.connection.send(res._encode()) 

            if request_code == 4:     # client asks for permission to continue sending/reading next 8 blocks

                if client.data.get("comunication_role") == THE_READER:   #here I have implemented a sort of a semaphore
                    if writingTurn: 
                        res = Response({
                        "code": "Not Ready"
                        }, cipher)
                        client.connection.send(res.len())
                        client.connection.send(res._encode())
                        writingTurn = True
                        return
                    else:
                        if client.data.get("canContinue", None) == True:
                            client.data.update({"canContinue": False})
                            client.data.update({"hasFinished": False})
                            res = Response({
                                "code": "Yes"
                            }, cipher)
                            writingTurn = True
                            client.connection.send(res.len())
                            client.connection.send(res._encode())
                        else:
                            res = Response({
                                "code": "Not Ready"
                            }, cipher)
                            client.connection.send(res.len())
                            client.connection.send(res._encode())

                        
                if client.data.get("comunication_role") == THE_WRITER: 
                    if not writingTurn:
                        res = Response({
                        "code": "Not Ready"
                        }, cipher)
                        client.connection.send(res.len())
                        client.connection.send(res._encode())
                        return
                    else:
                        if client.data.get("canContinue", None) == True:
                            client.data.update({"canContinue": False})
                            client.data.update({"hasFinished": False})
                            res = Response({
                                "code": "Yes"
                            }, cipher)
                            writingTurn = False
                            client.connection.send(res.len())
                            client.connection.send(res._encode())
                        else:
                            res = Response({
                                "code": "Not Ready"
                            }, cipher)
                            client.connection.send(res.len())
                            client.connection.send(res._encode())


        except Exception as e:
            print(e)
            exit()
        


if __name__ == "__main__":

    server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)         # Create a socket object
    host = 'localhost' 
    port = 4001                 # Reserve a port for your service.
    server.bind((host, port))        # Bind to the port
    print('listening on', (host, port))

    CM = ConnectionsManager(server) 

    server.listen(2)  
    while True:
        conn = CM.get_connections()                                #get a list of all connections sockets
        readable, write, idk = select.select(conn, conn, conn, 1)  #see of the any of them can be read from
        for des in readable:
            if des == CM.server_listener:                      #server_listener listens for clients that want to connect
                connection, addr = server.accept()             #add the new connection
                newClient = Client(connection,{'addr': addr})
                CM.add_connection(newClient)                   
            else:
                CM.manageClient(des)                           #line 75

