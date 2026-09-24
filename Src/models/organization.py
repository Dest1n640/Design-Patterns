from Src.Core.named_entity import named_entity


class organization(named_entity):
    """Класс сущности - организация"""
    _instance = None

    def __new__(cls, *args, **kwargs):
        """Реализация singleton для класса"""
        if cls._instance is None:
            cls._instance = super().__new__(cls)
        return cls._instance

    def __init__(self):
      """Констуктор с присваением именни ООО Ромашка"""
      super().__init__("ООО Ромашка")
