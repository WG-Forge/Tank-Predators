from Events.Event import Event

class TankAddedEvent(Event):
    pass

class TankMovedEvent(Event):
    pass

class TankShotEvent(Event):
    pass

class TankDestroyedEvent(Event):
    pass

class TankRespawnedEvent(Event):
    pass

class TankRangeBonusEvent(Event):
    pass

class TankRepairedEvent(Event):
    pass