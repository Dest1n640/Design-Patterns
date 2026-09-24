from Src.Core.named_entity import named_entity
from Src.models.premises_model import premises_model
from Src.models.restaurant_model import restaurant_model
from Src.models.production_shop_model import production_shop_model

class warehouse_model(named_entity):
    def __init__(self, premises: premises_model, warehouse_owner: restaurant_model | production_shop_model):
        super().__init__("Склад")
        self.premises = premises
        self.warehouse_owner = warehouse_owner

    @property
    def premises(self):
        return self.premises

    @property
    def warehouse_owner(self):
        return self.warehouse_owner
