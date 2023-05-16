from abc import ABC


class Entity(ABC):
    __slots__ = ("__idx", "__name")

    def __init__(self, idx: int, name: str):
        self.__idx = idx
        self.__name = name

    def getId(self) -> int:
        return self.__idx

    def getName(self) -> str:
        return self.__name
