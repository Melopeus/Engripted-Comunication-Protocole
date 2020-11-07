import json
from MyCryptography import ECB, CFB

class Request:
    def __init__(self, reqDict, cipher, **kwargs):
        #This function initialise the variables needed for encrypting a message
        
        if kwargs.get('iv') != None:
            CFB.init(cipher, kwargs.get('iv'))
            self.ENCMOD = CFB
        else:
            ECB.init(cipher)
            self.ENCMOD = ECB

        if kwargs.get('ctype','json') == 'file':
            self.reqDict = reqDict
        else:
            if type(reqDict) is dict:
                self.reqDict = reqDict
            elif type(reqDict) is bytes:
                self.reqDict = json.loads(self.ENCMOD._decrypt(reqDict))
            else:
                self.reqDict = dict()
            self.cipher = cipher  
        self.paddingLength = None
        
    def _encrypt(self):
        if type(self.reqDict) is dict:
            return self.ENCMOD._encrypt(json.dumps(self.reqDict))
        else:
            return self.ENCMOD._encrypt(self.reqDict)

    def _str(self):
        return str(self.reqDict)
    
    def body(self):
        return self.reqDict

    def len(self):
        return self.pad64(str(len(self._encrypt())).encode("utf-8"))

    def pad(self, request_bytes):
        padLen = 16-len(request_bytes)%16
        padBytes = (' '*padLen).encode('utf-8')
        request_bytes += padBytes

        self.paddingLength = padLen
        return request_bytes

    def pad64(self, len_bytes):
        padLen = 64-len(len_bytes)%64  
        padBytes = (' '*padLen).encode('utf-8')
        len_bytes += padBytes
        return len_bytes