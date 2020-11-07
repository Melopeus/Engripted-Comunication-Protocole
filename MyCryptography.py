from Crypto.Cipher import AES

class ECB:


    @staticmethod
    def init(newCipher):
        ECB.e_cipher = newCipher

    @staticmethod
    def _encrypt(b_text):
        if type(b_text) is str:
            b_text = b_text.encode('utf-8')
        b_text = ECB.pad(b_text)
        nr_blocks = len(b_text)//16
        cipherText = b''
        for i in range(nr_blocks):
            cipherText += ECB.e_cipher.encrypt(b_text[16*i:16*(i+1)])
        
        return cipherText

    @staticmethod
    def _decrypt(b_text):
        nr_blocks = len(b_text)//16
        plainText = b''
        for i in range(nr_blocks):
            plainText += ECB.e_cipher.decrypt(b_text[16*i:16*(i+1)])
        return plainText.decode('utf-8')
    
    @staticmethod
    def pad(b_text):
        padLen = 16-len(b_text)%16
        padBytes = (' '*padLen).encode('utf-8')
        b_text += padBytes
        return b_text

class CFB:
    lastBlock = None
    @staticmethod
    def init(cipher, newIV):
        CFB.e_cipher = cipher
        if type(newIV) is str:
            CFB.iv = newIV.encode('utf-8')
        else:
            CFB.iv = newIV

    @staticmethod
    def _encrypt(b_text):
        if type(b_text) is str:
            b_text = b_text.encode('utf-8')
        b_text = CFB.pad(b_text)
        nr_blocks = len(b_text)//16
        cipherText = b''
        encripted_iv = None
        if CFB.lastBlock != None:
            encripted_iv = CFB.lastBlock    # this is needed in case the plaintext is split in 8*16 chunks, and the function called on all the them
        else:                               # when we encrypt from the second on, the algorithm uses the correct IV(the last encrypted cipherTextBlock) not the original one
            encripted_iv = CFB.e_cipher.encrypt(CFB.iv)

        for i in range(nr_blocks):
            cipherTextBloc = bytes([a ^ b for a, b in zip(b_text[16*i:16*(i+1)], encripted_iv)])
            cipherText += cipherTextBloc
            encripted_iv = CFB.e_cipher.encrypt(cipherTextBloc)
        CFB.lastBlock = encripted_iv
        return cipherText

    @staticmethod
    def _decrypt(b_text):
        nr_blocks = len(b_text)//16
        plainText = b''
        encripted_iv = None
        if CFB.lastBlock != None:
            encripted_iv = CFB.lastBlock    # this is needed in case the crypertext is split in 8*16 chunks, and the function called on all the them
        else:                               # when we decrypt from the second on, the algorithm uses the correct IV(the last encrypted cipherTextBlock) not the original one
            encripted_iv = CFB.e_cipher.encrypt(CFB.iv)
        for i in range(nr_blocks): # iterate through all 16 bytes long blocks of cryptotext
            cipherTextBloc = b_text[16*i:16*(i+1)]
            plainTextBloc = bytes([a ^ b for a,b in zip(encripted_iv,cipherTextBloc)]) # xor operation
            plainText += plainTextBloc
            encripted_iv = CFB.e_cipher.encrypt(cipherTextBloc)
        CFB.lastBlock = encripted_iv
        return plainText.decode('utf-8')


    @staticmethod
    def pad(b_text):
        padLen = 16-len(b_text)%16
        padBytes = (' '*padLen).encode('utf-8')
        b_text += padBytes
        return b_text