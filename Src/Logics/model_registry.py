"""Единый реестр коллекций доменных моделей приложения."""

from Src.Core.abstract_model import AbstractModel
from Src.Models.dish_model import DishModel
from Src.Models.ingredient_model import IngredientModel
from Src.Models.measurement_unit_model import MeasurementUnitModel
from Src.Models.nomenclature_group_model import NomenclatureGroupModel
from Src.Models.nomenclature_model import NomenclatureModel
from Src.Models.organization_model import OrganizationModel
from Src.Models.premises_model import PremisesModel
from Src.Models.production_shop_model import ProductionShopModel
from Src.Models.restaurant_model import RestaurantModel
from Src.Models.technological_map_model import TechnologicalMapModel
from Src.Models.warehouse_model import WarehouseModel

ENTITY_TYPES: dict[str, type[AbstractModel]] = {
    "measurement_units": MeasurementUnitModel,
    "nomenclature_groups": NomenclatureGroupModel,
    "nomenclature": NomenclatureModel,
    "restaurants": RestaurantModel,
    "production_shops": ProductionShopModel,
    "warehouses": WarehouseModel,
    "technological_maps": TechnologicalMapModel,
    "organizations": OrganizationModel,
    "premises": PremisesModel,
    "dishes": DishModel,
    "ingredients": IngredientModel,
}
