"""Юнит-тесты для Src.Logics.settings_manager.SettingsManager."""

import json
from pathlib import Path

import pytest

from Src.Core.exception import ApplicationException, ValidationException
from Src.Logics.settings_manager import SettingsManager


def _write_json(directory: Path, data: object) -> str:
    """Записывает данные во временный json-файл и возвращает путь к нему."""
    path = directory / "settings.json"
    path.write_text(json.dumps(data, ensure_ascii=False), encoding="utf-8")
    return str(path)


def _build_loaded_manager() -> SettingsManager:
    """Возвращает менеджер настроек, загруженный из файла по умолчанию."""
    manager = SettingsManager()
    manager.load()
    return manager


def test_settings_manager__load_default_file__does_not_raise():
    """Загрузка настроек из файла по умолчанию проходит без исключений."""
    SettingsManager().load()


def test_settings_manager__load_default_file__settings_not_empty():
    """После загрузки модель настроек заполнена организацией."""
    manager = _build_loaded_manager()
    assert manager.settings is not None
    assert manager.settings.organization is not None


def test_settings_manager__two_instances__same_object():
    """Повторное создание менеджера возвращает тот же экземпляр (singleton)."""
    assert SettingsManager() is SettingsManager()


def test_settings_manager__load_default_file__is_loaded_true():
    """После успешной загрузки признак is_loaded равен True."""
    assert _build_loaded_manager().is_loaded


def test_settings_manager__two_instances__share_settings():
    """Настройки, загруженные через один экземпляр, видны через другой."""
    manager = _build_loaded_manager()
    assert SettingsManager().settings is manager.settings


def test_settings_manager__load_default_file__organization_matches_json(
    settings_data,
):
    """Реквизиты организации совпадают с разделом company в settings.json."""
    company = settings_data["company"]
    organization = _build_loaded_manager().settings.organization
    assert organization.name == company["name"]
    assert organization.inn == company["inn"]
    assert organization.bic == company["bic"]
    assert organization.curr_account == company["curr_account"]
    assert organization.legal_form == company["legal_form"]


def test_settings_manager__load_default_file__names_match_json(settings_data):
    """ФИО руководителя и главного бухгалтера совпадают с settings.json."""
    settings = _build_loaded_manager().settings
    assert settings.boss_name == settings_data["company"]["boss_name"]
    assert settings.accountant_name == settings_data["company"]["accountant_name"]


def test_settings_manager__load_default_file__first_start_matches_json(
    settings_data,
):
    """Признак первого запуска совпадает с settings.json."""
    settings = _build_loaded_manager().settings
    assert settings.first_start is settings_data["first_start"]


def test_settings_manager__load_without_company__raises_validation_exception(
    settings_data, tmp_path
):
    """Файл настроек без раздела company вызывает исключение валидации."""
    settings_data.pop("company")
    with pytest.raises(ValidationException):
        SettingsManager().load(_write_json(tmp_path, settings_data))


def test_settings_manager__load_not_object__raises_validation_exception(tmp_path):
    """Файл, в котором лежит не json-объект, вызывает исключение валидации."""
    with pytest.raises(ValidationException):
        SettingsManager().load(_write_json(tmp_path, [1, 2, 3]))


def test_settings_manager__load_non_string_file_name__raises_validation_exception():
    """Имя файла не строкой вызывает исключение валидации."""
    with pytest.raises(ValidationException):
        SettingsManager().load(None)


def test_settings_manager__load_missing_file__raises_application_exception(
    tmp_path,
):
    """Отсутствующий файл вызывает исключение приложения."""
    with pytest.raises(ApplicationException) as exc_info:
        SettingsManager().load(str(tmp_path / "missing.json"))
    assert type(exc_info.value) is ApplicationException


def test_settings_manager__load_broken_json__raises_application_exception(tmp_path):
    """Файл с синтаксической ошибкой json вызывает исключение приложения."""
    path = tmp_path / "broken.json"
    path.write_text("{не json", encoding="utf-8")
    with pytest.raises(ApplicationException) as exc_info:
        SettingsManager().load(str(path))
    assert type(exc_info.value) is ApplicationException


def test_settings_manager__load_invalid_after_success__keeps_previous_settings(
    settings_data, tmp_path
):
    """Неудачная загрузка не сбрасывает is_loaded и настройки прошлой загрузки."""
    manager = _build_loaded_manager()
    settings = manager.settings
    settings_data["company"]["inn"] = "abc"

    with pytest.raises(ValidationException):
        manager.load(_write_json(tmp_path, settings_data))

    assert manager.is_loaded
    assert manager.settings is settings


def test_settings_manager__load_from_other_directory__reads_default_file(
    tmp_path, monkeypatch
):
    """Файл по умолчанию ищется от корня проекта, а не от текущего каталога."""
    monkeypatch.chdir(tmp_path)
    assert _build_loaded_manager().is_loaded
