from Entity import Entity


class Observer(Entity):
    def __init__(self, idx: int, name: str):
        super().__init__(idx, name)
