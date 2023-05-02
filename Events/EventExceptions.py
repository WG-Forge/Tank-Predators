class EventNotInManager(Exception):
    """
    Exception raised when an event is not registered in an EventManager instance.
    """
    def __init__(self, eventName: str):
        """
        Initializes the EventNotInManager exception.

        :param eventName: The name of the event that was not found in the event manager.
        """
        Exception.__init__(self, f"Event - {eventName} not in the event manager")

class EventAlreadyInManager(Exception):
    """
    Exception raised when an event is already registered in an EventManager instance.
    """
    def __init__(self, eventName: str):
        """
        Initializes the EventAlreadyInManager exception.

        :param eventName: The name of the event that was already in the event manager.
        """
        Exception.__init__(self, f"Event - {eventName} is already in the event manager")

class HandlerNotInEvent(Exception):
    """
    Exception raised when a handler is not registered in an event.
    """
    def __init__(self, handlerName: str):
        """
        Initializes the HandlerNotInEvent exception.

        :param handlerName: The name of the handler that was not found in the event.
        """
        Exception.__init__(self, f"Handler - {handlerName} not in the event")

class HandlerArgumentMismatch(Exception):
    """
    Exception raised when there is a mismatch in the number of arguments between a handler and an event.
    """
    def __init__(self, message: str):
        """
        Initializes the HandlerArgumentMismatch exception.

        :param message: The message explaining the cause of the exception.
        """
        Exception.__init__(self, message)
