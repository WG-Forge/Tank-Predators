class HealthComponent:
    """
    Component for handling the health of an entity.
    """

    __slots__ = ("__currentHealth", "__maxHealth")

    def __init__(self, maxHealth: int, currentHealth: int = None) -> None:
        """
        Initializes a new instance of the HealthComponent class.

        :param maxHealth: The maximum health value.
        :param currentHealth: Optional. The current health value. Defaults to the maximum health value.
        """ 
        self.__maxHealth = maxHealth
        if currentHealth is not None:
            self.__currentHealth = currentHealth
        else:
            self.__currentHealth = maxHealth

    def receiveDamage(self, damageAmount: int) -> None:
        """
        Decreases the current health value by the specified amount.

        :param damageAmount: The amount of damage to be received.
        """
        self.__currentHealth -= damageAmount

    def isAlive(self) -> bool:
        """
        Checks whether the entity is alive or not.

        :return: True if the entity is alive, False otherwise.
        """
        if self.__currentHealth <= 0: 
            return False
        return True  
    
    def heal(self, healAmount: int = None) -> None:
        """
        Increases the current health value by the specified amount, but not above the maximum health.
        If no amount is specified, sets the current health value to the maximum health.

        :param healAmount: Optional. The amount of health to be healed.
        """
        if healAmount is None:
            self.__currentHealth = self.__maxHealth
        else:
            self.__currentHealth = min(self.__currentHealth + healAmount, self.__maxHealth)

    def getHealth(self) -> int:
        """
        Returns the current health value.

        :return: An integer representing the current health value.
        """
        return self.__currentHealth