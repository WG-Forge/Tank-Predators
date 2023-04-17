from typing import Type, Callable

class EventNotInManager(Exception):
    def __init__(self, evenName: str):
        Exception.__init__(self, f"Event - {evenName} not in the event manager")

class HandlerNotInEvent(Exception):
    def __init__(self, handlerName: str):
        Exception.__init__(self, f"Handler - {handlerName} not in the event")

class HandlerArgumentMismatch(Exception):
    def __init__(self, message: str):
        Exception.__init__(self, message)