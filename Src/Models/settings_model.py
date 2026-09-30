from Src.Core.abstract_model import AbstractModel
from Src.Models.organization_model import OrganizationModel

class SettingModel(AbstractModel):
  """Модель настроект"""
  __organization: OrganizationModel = None
  __boss_name: str = ""
  __account_name: str = ""

  @property
  def organization(self) -> OrganizationModel:
    self._validation_organization()
    return self.__company

  @organization.setter
  def organization(self, value: OrganizationModel) -> None:
    self._validation_organization()

  @property
  def boss_name(self) -> str:
    return self.boss_name

  @boss_name.setter
  def boss_name(self, value: str) -> None:
    self._validation_boss_name()
    self.boss_name = value.strip()

  @property
  def account_name(self) -> str:
    return self.account_name

  @account_name.setter
  def account_name(self, value: str) -> None:
    self._validation_account_name()
    self.account_name = value.strip()
    
  def _validation_organization(self):
    pass

  def _validation_boss_name(self):
    pass

  def _validation_account_name(self):
    pass
