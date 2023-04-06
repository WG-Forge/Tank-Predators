from Tank import Tank


class MediumTank(Tank):
    """
        Abstract tank class\n
        HP - health points\n
        SP - speed points\n
        Damage - damage it causes on hitting other tank\n
        FireRange - Distance from another tank needed to fire a shot
    """
    def __init__(self):
        self.hp = 2
        self.sp = 2
        self.damage = 1
        self.destructionPoints = 2
        self.fireRange = 2
