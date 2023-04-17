from typing import Type, Any, Callable
from Events.Event import Event
from Events.EventExceptions import EventNotInManager
from Events.EventExceptions import EventAlreadyInManager

class EventManager:
    """
    A class that manages events.
    """
    def __init__(self) -> None:
        self.__events = {}

    def registerEvent(self, eventType: Type[Event]) -> None:
        """
        Registers an event with the type.

        :param eventType: The type of the event to register.
        """
        if eventType in self.__events:
            raise EventAlreadyInManager(eventType.__name__)

        self.__events[eventType] = eventType()

    def addHandler(self, eventType: Type[Event], handler: Callable[..., None]) -> None:
        """
        Adds a handler to the event with the given type.

        :param eventType: The type of the event to add the handler to.
        :param handler: The handler to add.
        """
        if eventType in self.__events:
            self.__events[eventType].addHandler(handler)
        else:
            raise EventNotInManager(eventType.__name__)

    def removeHandler(self, eventType: Type[Event], handler: Callable[..., None]) -> None:
        """
        Removes a handler from the event with the given type.

        :param eventName: The type of the event to remove the handler from.
        :param handler: The handler to remove.
        """
        if eventType in self.__events:
            self.__events[eventType].removeHandler(handler)
        else:
            raise EventNotInManager(eventType.__name__) 

    def triggerEvent(self, eventType: Type[Event], *args: Any, **kwargs: Any) -> None:
        """
        Triggers the event with the given name, calling all registered handlers with the given arguments.

        :param eventType: The type of the event to trigger.
        :param args: The positional arguments to pass to the handlers.
        :param kwargs: The keyword arguments to pass to the handlers.
        """
        if eventType in self.__events:
            self.__events[eventType].trigger(*args, **kwargs)
        else:
            raise EventNotInManager(eventType.__name__)
