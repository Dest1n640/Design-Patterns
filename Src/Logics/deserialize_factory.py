import inspect
from typing import get_type_hints

from Src.Core.abstract_convertor import AbstractConvertor
from Src.Core.common import Common
from Src.Core.exception import ValidationException
from Src.Logics.Convertors.basic_deserialize import BasicDeserialize
from Src.Logics.Convertors.collection_deserialize import CollectionDeserialize
from Src.Logics.Convertors.datetime_deserialize import DatetimeDeserialize
from Src.Logics.Convertors.enum_deserialize import EnumDeserialize
from Src.Logics.Convertors.reference_deserialize import ReferenceDeserialize
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


class DeserializeFactory(AbstractConvertor):
    """Фабрика восстановления моделей из словарей и списков JSON."""

    def convert(self, source: object) -> object:
        """Рекурсивно восстанавливает модели и сохраняет их идентификаторы."""
        if isinstance(source, list):
            return CollectionDeserialize(self.convert).convert(source)
        if not isinstance(source, dict):
            if source is None or isinstance(source, str | int | float):
                return source
            raise ValidationException("source", "Ожидаются данные из JSON")
        if "type" not in source:
            return CollectionDeserialize(self.convert).convert(source)

        type_name = source.get("type")
        if not isinstance(type_name, str) or type_name not in mapping:
            raise ValidationException("type", "Неизвестный тип модели")
        model_class = mapping[type_name]
        parameters = Common.get_constructor_parameters(model_class)
        field_types = get_type_hints(model_class.__init__)
        convertors: list[AbstractConvertor] = [
            BasicDeserialize(),
            DatetimeDeserialize(field_types),
            EnumDeserialize(field_types),
            ReferenceDeserialize(self.convert),
            CollectionDeserialize(self.convert),
        ]
        fields = {}
        for convertor in convertors:
            fields.update(convertor.convert(source))

        arguments = {}
        for key, item in parameters.items():
            if key in source:
                if key not in fields:
                    raise ValidationException(key, "Ожидаются данные из JSON")
                arguments[key] = fields[key]
            elif item.default is inspect.Parameter.empty:
                raise ValidationException(key, "Отсутствует обязательный параметр")

        model = model_class(**arguments)
        if "id" in source:
            model.id = source["id"]
        return model
