import inspect

from Src.Core.common import Common
from Src.Core.exception import ValidationException
from Src.Models.dish_model import DishModel
from Src.Models.ingredient_model import IngredientModel
from Src.Models.measurement_unit_model import MeasurementUnitModel
from Src.Models.nomenclature_group_model import NomenclatureGroupModel
from Src.Models.nomenclature_model import NomenclatureModel
from Src.Models.organization_model import OrganizationModel
from Src.Models.premises_model import PremisesModel
from Src.Models.production_shop_model import ProductionShopModel
from Src.Models.restaurant_model import RestaurantModel
from Src.Models.settings_model import SettingsModel
from Src.Models.technological_map_model import TechnologicalMapModel
from Src.Models.warehouse_model import WarehouseModel


class DeserializeFactory:
    """Фабрика восстановления моделей из словарей и списков JSON."""

    def deserialize(self, source: object) -> object:
        """Рекурсивно восстанавливает модели и сохраняет их идентификаторы."""
        if isinstance(source, list):
            return [self.deserialize(item) for item in source]
        if not isinstance(source, dict):
            if source is None or isinstance(source, str | int | float):
                return source
            raise ValidationException("source", "Ожидаются данные из JSON")
        if "type" not in source:
            return {key: self.deserialize(value) for key, value in source.items()}

        mapping = {
            "DishModel": DishModel,
            "IngredientModel": IngredientModel,
            "MeasurementUnitModel": MeasurementUnitModel,
            "NomenclatureGroupModel": NomenclatureGroupModel,
            "NomenclatureModel": NomenclatureModel,
            "OrganizationModel": OrganizationModel,
            "PremisesModel": PremisesModel,
            "ProductionShopModel": ProductionShopModel,
            "RestaurantModel": RestaurantModel,
            "SettingsModel": SettingsModel,
            "TechnologicalMapModel": TechnologicalMapModel,
            "WarehouseModel": WarehouseModel,
        }

        type_name = source.get("type")
        if not isinstance(type_name, str) or type_name not in mapping:
            raise ValidationException("type", "Неизвестный тип модели")
        model_class = mapping[type_name]
        parameters = Common.get_constructor_parameters(model_class)
        arguments = {}
        for key, item in parameters.items():
            if key in source:
                arguments[key] = self.deserialize(source[key])
            elif item.default is inspect.Parameter.empty:
                raise ValidationException(key, "Отсутствует обязательный параметр")

        model = model_class(**arguments)
        if "id" in source:
            model.id = source["id"]
        return model
