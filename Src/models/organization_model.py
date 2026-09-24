from Src.Core.named_entity import named_entity


class organization(named_entity):
    """Класс сущности - организация"""
    _instance = None

    def __new__(cls, *args, **kwargs):
        """Реализация singleton для класса"""
        if cls._instance is None:
            cls._instance = super().__new__(cls)
        return cls._instance

    def __init__(self, INN: str, BIC: str, curr_account: str, legal_form: str):
      """Констуктор с присваением именни ООО Ромашка"""
      super().__init__("Ромашка")
      self.INN = INN
      self.BIC = BIC
      self.curr_account = curr_account
      self.legal_form = legal_form

