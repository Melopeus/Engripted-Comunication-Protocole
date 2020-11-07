import json
from MyCryptography import ECB, CFB

class Response:
    def __init__(self, resDict, cipher, **kwargs):
        # This function sets all that is needed in order to decrypt the received mesage and make it a json like dictionary
        # The 2 most important functions are the initialization and the .body() to access the message

        if kwargs.get('iv') != None:
            CFB.init(cipher, kwargs.get('iv'))
            self.ENCMOD = CFB                  #ENCMOD is for ENCRYPTION MODE that can be eather ECB or CFB
        else:
            ECB.init(cipher)
            self.ENCMOD = ECB
        if kwargs.get('ctype','json') == 'file':
            self.resDict = self.ENCMOD._decrypt(resDict)
        else:
            if type(resDict) is dict:
                self.resDict = resDict
            elif type(resDict) is bytes:
                self.resDict = json.loads(self.ENCMOD._decrypt(resDict))
            else:
                self.resDict = dict()
        self.cipher = cipher

    def _encode(self):
        if type(self.resDict) is dict:
            return self.ENCMOD._encrypt(json.dumps(self.resDict))
        else:
            return self.ENCMOD._encrypt(self.resDict)
    
    def _str(self):
        return str(self.resDict)

    def len(self):
        return self.pad64(str(len(self._encode())).encode('utf-8'))

    def body(self):
        return self.resDict

    def pad(self, response_bytes):
        padLen = 16-len(response_bytes)%16
        padBytes = (' '*padLen).encode('utf-8')
        response_bytes += padBytes
        return response_bytes

    def pad64(self, len_bytes):
        padLen = 64-len(len_bytes)%64  
        padBytes = (' '*padLen).encode('utf-8')
        len_bytes += padBytes
        return len_bytes