import socket
import json
from Request import Request
from Response import Response
from Crypto.Cipher import AES
import time

k3 = b'1111222233334444'

e_cipher = AES.new(k3, AES.MODE_ECB)
d_cipher = AES.new(k3, AES.MODE_ECB)

THE_READER = 1 
THE_WRITER = 2

server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
server.connect(('localhost',4001))

def pad64(len_bytes):
    padLen = 64-len(len_bytes)%64  
    padBytes = (' '*padLen).encode('utf-8')
    len_bytes += padBytes
    return len_bytes

def readMessage(server):
    try:
        message_length = int(server.recv(64))
        assert message_length > 0,"Connection Closed"
        #print("Message Length:", message_length)
        data = b''
        while message_length > 0:
            blob = server.recv(16)
            message_length -= 16
            data = data + blob
        return data
    except:
        print("Error when reading from client.")
        raise


def send(request):
    
    server.send(request.len())
    server.send(request._encrypt())

    response = Response(readMessage(server),e_cipher)
    return response


if __name__ == "__main__":
    
    # -----  SET MODE ----- #
    mode = input("Choose mode from: ECB, CFB \n -> ")
    #mode = "CFB"
    request = Request({
        "code": 1,
        "data":{
            "mode":mode
        }}, e_cipher)
    res = send(request)
    print("Preference set!")

    # -----  ASK CHOSEN MODE ----- #
    #input("Continue: ")
    request = Request({
        "code": 2
    },e_cipher)
    res = send(request)
    

    while res.body()["code"] == "Not Ready":
        time.sleep(1)
        res = send(request)

    chosenMode = res.body()["data"]["chosen_mode"]
    n_iv = res.body()["data"]["iv"]
    key = res.body()["data"]["key"]
    role = res.body()["data"]["comunication_role"]

    n_cipher = AES.new(key.encode('utf-8'),AES.MODE_ECB)
    
    # -----  START P2P COMUNICATION ----- #
    print("Second Response: CHOSEN MODE: {}\n IV: {}\n KEY: {}\n ROLE:{} ".format(chosenMode, n_iv, key, role))
    input("Start comunication, press a key and enter: ")

    if role == THE_READER: 
        listenerSocket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)  # prepare connection 
        listenerSocket.bind(('localhost',6000))                             #                
        listenerSocket.listen(1)                                            #    
        connection, addr = listenerSocket.accept()                          #                   

        nr_blocks = int(connection.recv(64).decode("utf-8"))                #read how many 8*16 size blocks are expected
        for i in range(nr_blocks+1):   
            big_blocks = connection.recv(8*16)                              #read a 8*16 block of message
            res = Response(big_blocks ,n_cipher, iv = n_iv, ctype = 'file') 
            print(i,"-->" ,res.body().strip(), end="\n\n", flush=True)

            req = Request({    #inform server you are done reading 8 blocks
                "code": 3
            }, e_cipher)
            res = send(req)


            req = Request({    #ask for permission to read again
                "code": 4
            }, e_cipher)
            res = send(req)
            while res.body()["code"] == "Not Ready":  # wait for permission to read again
                #time.sleep(1)
                res = send(req)
        print("Finished reading File.")

    elif role == THE_WRITER:
        callerSocket =socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        while(True):
            try:
                callerSocket.connect(('localhost',6000))
                break
            except Exception as e:
                print("Connection refused, Retrying.", flush=True)

        with open("FileToBeSent.txt", "rb") as f:
            plaintext = f.read()
        callerSocket.send( pad64(str(len(plaintext)//(8*16)).encode('utf-8')) )
        for i in range(len(plaintext)//(8*16)+1):
            plaintext_chunk = plaintext[8*16*i:8*16*(i+1)]
            req = Request(plaintext_chunk, n_cipher, iv = n_iv, ctype='file')
            callerSocket.send(req._encrypt())
            print("Sent block ", i)

            req = Request({  #inform you finished writing
                "code": 3
            }, e_cipher)
            res = send(req)

            req = Request({  #ask for permission to write again
                "code": 4   
            }, e_cipher)
            res = send(req)
            while res.body()["code"] == "Not Ready":  #wait for permission to write again
                time.sleep(1)
                res = send(req)
        print("Finished sending File.")

    input()
    send("Hello Tim!")

    send(DISCONNECT_MESSAGE)