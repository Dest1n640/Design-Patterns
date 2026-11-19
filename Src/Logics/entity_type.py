from enum import Enum, unique

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


@unique
class EntityType(Enum):
    """Доменные модели; имена элементов в нижнем регистре задают ключи коллекций."""

    MEASUREMENT_UNITS = MeasurementUnitModel
    NOMENCLATURE_GROUPS = NomenclatureGroupModel
    NOMENCLATURE = NomenclatureModel
    RESTAURANTS = RestaurantModel
    PRODUCTION_SHOPS = ProductionShopModel
    WAREHOUSES = WarehouseModel
    TECHNOLOGICAL_MAPS = TechnologicalMapModel
    ORGANIZATIONS = OrganizationModel
    PREMISES = PremisesModel
    DISHES = DishModel
    INGREDIENTS = IngredientModel
