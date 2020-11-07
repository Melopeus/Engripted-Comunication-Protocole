# Tema 1 Securitatea Informatiei
## Contents
1. [Requirements](#requirements)
2. [How to use it](#how-to-use-it)
3. [Algorithm presentation](#algorithm-presentation)

## Requirements
I have used python 3.8.3 and `pycryptodome`.
I had some issues with installing it so if there are any issues you can try installing it this way:
```py
pip uninstall crypto
pip uninstall pycryptodome
pip install pycryptodome
```
A way to easily access 3 command lines like `gitBash`.
## How to use it
Open 3 command lines.
The first step is to turn on the server application called `KM.py`.
```
python KM.py
```
In the other 2 command lines run the client apps.
```
python Client.py
```
Now you will play the role of both clients and choose the wanted encryption mode (ECB or CFB) by writing in the command your choice.

After this you need to confirm the continuation of communication.
The results will be printed on the screen.

## Algorithm presentation
### The crypting modes
These modes were implemented in the `MyCryptography.py` module. There are 2 classes called `ECB` and `CFB`. Each class has these methods:
>* init()     
> initializes the block cipher used (AES) 

>* _encrypt()   
> encrypts a message implementing the mode procedure

>* _decrypt()   
> decrypt a message implementing the mode procedure

>* pad()   
> adds padding bytes to the end of the message

There are comments in the code that will explain each step for each function. They simply implement the diagrams shown in the laboratory and are not very complex.

These modes are initialized and used when the program sends messages via sockets. This happens mostly in the Request/Response objects also defined by me.


### Communication
The communication happens via sockets. It mostly follows a client-server model. I think the best way to explain the flow of the communication is by commenting the code itself so there are comments that guide and explain what happens. For the KM the process starts at line 195 `if __name__ == "__main__":`
Requests between client/server follow this form:
```py
request = Request({
    "code": int,
    "data": dict
}, cipher, iv)
```
`cipher` and `iv` are used to determine the encryption mode

The flow of the app goes like this:
> Server: 
>* listen, accept and remember all connections with clients
>* manage client requests by their `code`

These are the codes I used:
> Codes:
> * 1 : Request set client preference
> * 2 : Ask for the chosen communication mode
> * 3 : Declare finished operation
> * 4 : Ask permission to continue writing

This is what the server does when he receives the codes:
> * 1 -> Sets in the client object the specified mode.
> * 2 -> Checks if all clients have set their preferences. If yes, he sends the chosen mode, if not he sends a message that tells the clients to wait and ask later.
> * 3 -> Sets a flag to identify that the client has does his job
> * 4 -> Checks if every client has done his job(to write/ to read) and direct the writer to write first and then the reader to read.

The clients have a much easier flow, they follow these steps:
>* Connect to the server
>* Specify their preferred mode
>* Ask for the mode until they receive it and the rest of the information like keys, what job they have, 
>* Start communication with one another
>* Communicate with the server and ask for permission to continue until all data was sent/received