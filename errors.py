class Error(Exception):
    pass

"""Error occurs when a key is present in multiple shards"""
class KeyPresentInMultipleShardsError(Error):
    def __init__(self, message):
        self.message = message

"""Error occurs when key is lost after add or remove"""
class KeyLostInTransitionError(Error):
    def __init__(self, message):
        self.message = message

"""Error occurs when value is wrong after add or remove"""
class ValueLostInTransitionError(Error):
    def __init__(self, message):
        self.message = message
