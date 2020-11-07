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

There are comments in the code that will explain each step for each function.

These modes are initialized and used when the program sends messages via sockets. This happens mostly in the Request/Response objects also defined by me.


### Communication
The communication happens via sockets. It mostly follows a client-server model. I think the best way to explain the flow of the communication is by commenting the code itself so there are comments that guide and explain what happens. For the KM the process starts at line 195 `if __name__ == "__main__":`
