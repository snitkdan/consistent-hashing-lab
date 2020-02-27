class Error(Exception):
    pass

class KeyPresentInMultipleShardsError(Error):

    def __init__(self, message):
        self.message = message

class KeyLostInTransitionError(Error):

    def __init__(self, message):
        self.message = message

class ValueLostInTransitionError(Error):

    def __init__(self, message):
        self.message = message
