"""Юнит-тесты для Src.Core.validation.Validation."""

import pytest

from Src.Core.exception import ValidationException
from Src.Core.position_type import PositionType
from Src.Core.validation import Validation


def test_validation__validate_instance__matching_type_returns_value():
    """Значение нужного типа возвращается без изменений."""
    # Подготовка
    value = [1, 2]

    # Действия
    result = Validation.validate_instance(value, list, "items", "Ошибка")

    # Проверки
    assert result is value


def test_validation__validate_instance__subclass_instance_is_accepted():
    """Экземпляр подкласса ожидаемого типа допустим."""
    # Подготовка
    value = True

    # Действия
    result = Validation.validate_instance(value, int, "flag", "Ошибка")

    # Проверки
    assert result is True


def test_validation__validate_instance__one_of_tuple_types_is_accepted():
    """Значение любого из типов кортежа допустимо."""
    # Подготовка
    value = "a"

    # Действия
    result = Validation.validate_instance(value, (int, str), "value", "Ошибка")

    # Проверки
    assert result == "a"


def test_validation__validate_instance__enum_member_is_accepted():
    """Член перечисления проходит проверку по типу перечисления."""
    # Подготовка
    value = PositionType.DISH

    # Действия
    result = Validation.validate_instance(
        value, PositionType, "position_type", "Ошибка"
    )

    # Проверки
    assert result is PositionType.DISH


@pytest.mark.parametrize("value", [None, "str", 1])
def test_validation__validate_instance__other_type_raises(value):
    """Значение другого типа (включая None) вызывает исключение валидации."""
    # Подготовка
    expected_type = list

    # Действия
    with pytest.raises(ValidationException) as exc_info:
        Validation.validate_instance(value, expected_type, "items", "Ошибка")

    # Проверки
    assert isinstance(exc_info.value, ValidationException)


def test_validation__validate_instance__error_carries_field_and_message():
    """Исключение хранит имя поля и переданное пояснение."""
    # Подготовка
    value = None

    # Действия
    with pytest.raises(ValidationException) as exc_info:
        Validation.validate_instance(value, list, "items", "Список указан неверно")

    # Проверки
    assert exc_info.value.field == "items"
    assert exc_info.value.message == "Список указан неверно"


def test_validation__validate_string__valid_value_is_returned():
    """Корректная строка возвращается как есть."""
    # Подготовка
    value = "Ромашка"
    field = "name"

    # Действия
    result = Validation.validate_string(value, field)

    # Проверки
    assert result == "Ромашка"


def test_validation__validate_string__surrounding_spaces_are_stripped():
    """Пробелы по краям строки удаляются."""
    # Подготовка
    value = "  Ромашка \n"
    field = "name"

    # Действия
    result = Validation.validate_string(value, field)

    # Проверки
    assert result == "Ромашка"


@pytest.mark.parametrize("value", ["", "   ", "\t\n"])
def test_validation__validate_string__empty_or_blank_raises(value):
    """Пустая строка и строка из одних пробелов вызывают исключение валидации."""
    # Подготовка
    field = "name"

    # Действия
    with pytest.raises(ValidationException) as exc_info:
        Validation.validate_string(value, field)

    # Проверки
    assert isinstance(exc_info.value, ValidationException)


@pytest.mark.parametrize("value", [None, 123, 1.5, ["а"], b"bytes"])
def test_validation__validate_string__non_string_raises(value):
    """Нестроковое значение вызывает исключение валидации."""
    # Подготовка
    field = "name"

    # Действия
    with pytest.raises(ValidationException) as exc_info:
        Validation.validate_string(value, field)

    # Проверки
    assert isinstance(exc_info.value, ValidationException)


def test_validation__validate_string__length_equal_to_max_is_accepted():
    """Строка длиной ровно max_length допустима."""
    # Подготовка
    value = "а" * 5
    field = "name"

    # Действия
    result = Validation.validate_string(value, field, max_length=5)

    # Проверки
    assert result == "а" * 5


def test_validation__validate_string__longer_than_max_raises():
    """Строка длиннее max_length вызывает исключение валидации."""
    # Подготовка
    value = "а" * 6
    field = "name"

    # Действия
    with pytest.raises(ValidationException) as exc_info:
        Validation.validate_string(value, field, max_length=5)

    # Проверки
    assert isinstance(exc_info.value, ValidationException)


def test_validation__validate_string__max_length_counts_stripped_value():
    """Длина считается после удаления пробелов по краям."""
    # Подготовка
    value = "  ааааа  "
    field = "name"

    # Действия
    result = Validation.validate_string(value, field, max_length=5)

    # Проверки
    assert result == "ааааа"


def test_validation__validate_string__length_equal_to_min_is_accepted():
    """Строка длиной ровно min_length допустима."""
    # Подготовка
    value = "ааа"
    field = "name"

    # Действия
    result = Validation.validate_string(value, field, min_length=3)

    # Проверки
    assert result == "ааа"


def test_validation__validate_string__shorter_than_min_raises():
    """Строка короче min_length вызывает исключение валидации."""
    # Подготовка
    value = "аа"
    field = "name"

    # Действия
    with pytest.raises(ValidationException) as exc_info:
        Validation.validate_string(value, field, min_length=3)

    # Проверки
    assert isinstance(exc_info.value, ValidationException)


def test_validation__validate_string__error_carries_field_name():
    """Исключение хранит имя проверяемого поля."""
    # Подготовка
    value = ""
    field = "full_name"

    # Действия
    with pytest.raises(ValidationException) as exc_info:
        Validation.validate_string(value, field)

    # Проверки
    assert exc_info.value.field == "full_name"


@pytest.mark.parametrize("value", [1, 0.001, 50.5, 10**9])
def test_validation__validate_positive_number__positive_value_is_returned(value):
    """Положительные int и float возвращаются без изменений."""
    # Подготовка
    field = "square"

    # Действия
    result = Validation.validate_positive_number(value, field)

    # Проверки
    assert result == value


@pytest.mark.parametrize("value", [0, 0.0, -1, -0.5])
def test_validation__validate_positive_number__zero_or_negative_raises(value):
    """Ноль и отрицательные числа вызывают исключение валидации."""
    # Подготовка
    field = "square"

    # Действия
    with pytest.raises(ValidationException) as exc_info:
        Validation.validate_positive_number(value, field)

    # Проверки
    assert isinstance(exc_info.value, ValidationException)


@pytest.mark.parametrize("value", [True, False])
def test_validation__validate_positive_number__bool_raises(value):
    """Значение bool не считается числом, хотя является подклассом int."""
    # Подготовка
    field = "square"

    # Действия
    with pytest.raises(ValidationException) as exc_info:
        Validation.validate_positive_number(value, field)

    # Проверки
    assert isinstance(exc_info.value, ValidationException)


@pytest.mark.parametrize("value", [float("nan"), float("inf"), float("-inf")])
def test_validation__validate_positive_number__non_finite_raises(value):
    """NaN и бесконечности вызывают исключение валидации."""
    # Подготовка
    field = "square"

    # Действия
    with pytest.raises(ValidationException) as exc_info:
        Validation.validate_positive_number(value, field)

    # Проверки
    assert isinstance(exc_info.value, ValidationException)


@pytest.mark.parametrize("value", [None, "50", [1], 1 + 2j])
def test_validation__validate_positive_number__non_number_raises(value):
    """Нечисловое значение вызывает исключение валидации."""
    # Подготовка
    field = "square"

    # Действия
    with pytest.raises(ValidationException) as exc_info:
        Validation.validate_positive_number(value, field)

    # Проверки
    assert isinstance(exc_info.value, ValidationException)


def test_validation__validate_digits__valid_value_is_returned():
    """Строка из ASCII-цифр без ограничений длины возвращается как есть."""
    # Подготовка
    value = "1234567890"
    field = "inn"

    # Действия
    result = Validation.validate_digits(value, field)

    # Проверки
    assert result == "1234567890"


def test_validation__validate_digits__leading_zeros_are_kept():
    """Ведущие нули сохраняются: значение остаётся строкой."""
    # Подготовка
    value = "0012345678"
    field = "inn"

    # Действия
    result = Validation.validate_digits(value, field)

    # Проверки
    assert result == "0012345678"


def test_validation__validate_digits__surrounding_spaces_are_stripped():
    """Пробелы по краям удаляются до проверки длины."""
    # Подготовка
    value = " 123456789 "
    field = "bic"

    # Действия
    result = Validation.validate_digits(value, field, min_length=9, max_length=9)

    # Проверки
    assert result == "123456789"


def test_validation__validate_digits__length_within_bounds_is_accepted():
    """Длина внутри границ min_length и max_length допустима."""
    # Подготовка
    value = "12345"
    field = "code"

    # Действия
    result = Validation.validate_digits(value, field, min_length=3, max_length=8)

    # Проверки
    assert result


def test_validation__validate_digits__shorter_than_min_raises():
    """Строка короче min_length вызывает исключение валидации."""
    # Подготовка
    value = "12"
    field = "code"

    # Действия
    with pytest.raises(ValidationException) as exc_info:
        Validation.validate_digits(value, field, min_length=3)

    # Проверки
    assert isinstance(exc_info.value, ValidationException)


def test_validation__validate_digits__longer_than_max_raises():
    """Строка длиннее max_length вызывает исключение валидации."""
    # Подготовка
    value = "123456789"
    field = "code"

    # Действия
    with pytest.raises(ValidationException) as exc_info:
        Validation.validate_digits(value, field, max_length=8)

    # Проверки
    assert isinstance(exc_info.value, ValidationException)


def test_validation__validate_digits__equal_bounds_exact_length_is_accepted():
    """При min_length == max_length строка ровно этой длины допустима."""
    # Подготовка
    value = "12345"
    field = "code"

    # Действия
    result = Validation.validate_digits(value, field, 5, 5)

    # Проверки
    assert result == "12345"


@pytest.mark.parametrize("value", ["1234", "123456"])
def test_validation__validate_digits__equal_bounds_other_length_raises(value):
    """При min_length == max_length строка другой длины вызывает исключение."""
    # Подготовка
    field = "code"

    # Действия
    with pytest.raises(ValidationException) as exc_info:
        Validation.validate_digits(value, field, 5, 5)

    # Проверки
    assert isinstance(exc_info.value, ValidationException)


@pytest.mark.parametrize(
    "value", ["12345abcde", "1234 56789", "1234-56789", "12345.6789"]
)
def test_validation__validate_digits__non_digit_characters_raise(value):
    """Строка нужной длины с нецифровыми символами вызывает исключение валидации."""
    # Подготовка
    field = "inn"

    # Действия
    with pytest.raises(ValidationException) as exc_info:
        Validation.validate_digits(value, field, min_length=10, max_length=10)

    # Проверки
    assert len(value) == 10
    assert isinstance(exc_info.value, ValidationException)


@pytest.mark.parametrize("value", ["²²²²²²²²²²", "١٢٣٤٥٦٧٨٩٠", "１２３４５６７８９０"])
def test_validation__validate_digits__non_ascii_digits_raise(value):
    """Unicode-цифры, для которых isdigit() истинен, отклоняются."""
    # Подготовка
    field = "inn"

    # Действия
    with pytest.raises(ValidationException) as exc_info:
        Validation.validate_digits(value, field, min_length=10, max_length=10)

    # Проверки
    assert value.isdigit()
    assert isinstance(exc_info.value, ValidationException)


@pytest.mark.parametrize("value", [None, 1234567890, "", "   "])
def test_validation__validate_digits__non_string_or_empty_raises(value):
    """Не строка (в том числе число) и пустая строка вызывают исключение валидации."""
    # Подготовка
    field = "inn"

    # Действия
    with pytest.raises(ValidationException) as exc_info:
        Validation.validate_digits(value, field)

    # Проверки
    assert isinstance(exc_info.value, ValidationException)
