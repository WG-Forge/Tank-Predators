class ServerException(Exception):
    def __init__(self, message):
        Exception.__init__(self, message)
        self.message = message 

class BadCommandException(ServerException):
    pass

class AccessDeniedException(ServerException):
    pass

class InappropriateGameStateException(ServerException):
    pass

class TimeoutException(ServerException):
    pass

class InternalServerErrorException(ServerException):
    pass

class InputException(Exception):
    def __init__(self, message):
        self.message = message
        Exception.__init__(self)