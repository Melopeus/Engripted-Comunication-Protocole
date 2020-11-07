class Client:
    def __init__(self, connection, data):
        self.data =data
        self.data.update({"step" : 0 , "hasFinished":False, "canContinue": False})
        
        self.connection = connection
