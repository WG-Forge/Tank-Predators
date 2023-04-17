from abc import ABC
from typing import Any, Callable
from Events.EventExceptions import HandlerNotInEvent
from Events.EventExceptions import HandlerArgumentMismatch
import inspect

class Event(ABC):
    """
    An abstract base class for events.
    """
    def __init__(self) -> None:
        self.__handlers = []

    def addHandler(self, handler: Callable[..., None]) -> None:
        """
        Adds a new handler to the event.

        :param handler: The handler to add.
        """
        self.__handlers.append(handler)

    def removeHandler(self, handler: Callable[..., None]) -> None:
        """
        Removes an existing handler from the event.

        :param handler: The handler to remove.
        """
        if handler in self.__handlers:
            self.__handlers.remove(handler)
        else:
            raise HandlerNotInEvent(handler.__name__)

    def trigger(self, *args: Any, **kwargs: Any) -> None:
        """
        Triggers the event, calling all registered handlers with the given arguments.

        :param args: The positional arguments to pass to the handlers.
        :param kwargs: The keyword arguments to pass to the handlers.
        """
        for handler in self.__handlers:
            signature = inspect.signature(handler)
            signatureParamCount = len(signature.parameters)
            passedParamCount = len(args) + len(kwargs)

            if signatureParamCount != passedParamCount:
                raise HandlerArgumentMismatch(f"Handler {handler.__name__} takes {signatureParamCount} arguments, but {passedParamCount} were passed to the event")
            
            handler(*args, **kwargs)