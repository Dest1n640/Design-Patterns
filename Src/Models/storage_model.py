from Src.Core import abstract_model
from Src.Models.warehouse_model import WarehouseModel
from Src.Models.measurement_unit_model import MeasurementUnitModel
from Src.Models.nomenclature_model import NomenclatureModel
from Src.Core.validation import Validation


class StorageModel(abstract_model):
  def __init__(self, warehouse: WarehouseModel, measurement_unit: MeasurementUnitModel, nomenclature: NomenclatureModel):
    self.warehouse = warehouse
    self.measurement_unit = measurement_unit
    self.nomenclature = nomenclature

  @property
  def warehouse(self) -> WarehouseModel:
    return self.__warehouse

  @property
  def measurement_unit(self) -> MeasurementUnitModel:
    return self.__mewsurement_unit

  @property
  def nomenclature(self) -> NomenclatureModel:
    return self.__nomenclature

  @warehouse.setter
  def warehouse(self, other: WarehouseModel) -> None:
    Validation.validate_instance(other, WarehouseModel, "Warehouse", "Склад указан неверно")
    self.__warehouse = other

  @measurement_unit.setter
  def measurement_unit(self, other: MeasurementUnitModel) -> None:
    Validation.validate_instance(other, MeasurementUnitModel, "MeasurementUnit", "Единицы измерения указанны неверно")
    self.__measurement_unit = other

  @nomenclature.setter
  def nomenclature(self, other: NomenclatureModel) -> None:
    Validation.validate_instance(other, NomenclatureModel, "Nomenclature", "Номенклатура указанна неверно")
    self.__nomenclature = other
