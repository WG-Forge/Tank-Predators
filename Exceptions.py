class BadCommandException(Exception):
    def __init__(self, message):
        Exception.__init__(self, message)
        self.message = message

class AccessDeniedException(Exception):
    def __init__(self, message):
        Exception.__init__(self, message)
        self.message = message

class InappropriateGameStateException(Exception):
    def __init__(self, message):
        Exception.__init__(self, message)
        self.message = message

class TimeoutException(Exception):
    def __init__(self, message):
        Exception.__init__(self, message)
        self.message = message

class InternalServerErrorException(Exception):
    def __init__(self, message):
        Exception.__init__(self, message)
        self.message = message