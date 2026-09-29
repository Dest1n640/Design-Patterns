from Src.Logics.setting_manager import SettingsManager
from Src.Core.exception import ValidationException

def test_not_raise_settings_manager_load():
  manager = SettingsManager()
  try:
    manager.load()
    assert True
  except ValidationException:
    assert False
  except:
    assert False

def test_not_empty_settings_manager_load():
  manager = SettingsManager()
  try:
    manager.load()
  except:
    assert False 
  assert manager.settings is not None

def test_equals_settings_manager_create():
  manager1 = SettingsManager()
  manager2 = SettingsManager()

  assert manager1 == manager2

def test_is_loaded_settings_manager_true():
  manager = SettingsManager()
  try:
    manager.load()
  except:
    assert False

  assert manager.is_loaded

def test_is_settinga_eq():
  manager1 = SettingsManager()
  manager2 = SettingsManager()

  assert manager1.settings == manager2.settings

