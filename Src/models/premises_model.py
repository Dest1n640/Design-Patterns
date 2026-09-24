from Src.Core.named_entity import named_entity

class premises_model(named_entity):
  def __init__(self, address: str, square: int | float):
    super().__init__("Помещение")
    self.address = address
    self.square = square

  @property
  def address(self):
    return self.address

  @property
  def square(self):
    return self.square

