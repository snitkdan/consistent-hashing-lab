class Error(Exception):
    pass

class KeyPresentInMultipleShards(Error):

    def __init__(self, message):
        self.message = message