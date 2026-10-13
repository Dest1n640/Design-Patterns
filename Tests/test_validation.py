"""Юнит-тесты для Src.Core.validation.Validation."""

import pytest

from Src.Core.exception import ValidationException
from Src.Core.position_type import PositionType
from Src.Core.validation import Validation


def test_validation__validate_instance__matching_type_returns_value():
    """Значение нужного типа возвращается без изменений."""
    value = [1, 2]
    assert Validation.validate_instance(value, list, "items", "Ошибка") is value


def test_validation__validate_instance__subclass_instance_is_accepted():
    """Экземпляр подкласса ожидаемого типа допустим."""
    assert Validation.validate_instance(True, int, "flag", "Ошибка") is True


def test_validation__validate_instance__one_of_tuple_types_is_accepted():
    """Значение любого из типов кортежа допустимо."""
    assert Validation.validate_instance("a", (int, str), "value", "Ошибка") == "a"


def test_validation__validate_instance__enum_member_is_accepted():
    """Член перечисления проходит проверку по типу перечисления."""
    result = Validation.validate_instance(
        PositionType.DISH, PositionType, "position_type", "Ошибка"
    )
    assert result is PositionType.DISH


@pytest.mark.parametrize("value", [None, "str", 1])
def test_validation__validate_instance__other_type_raises(value):
    """Значение другого типа (включая None) вызывает исключение валидации."""
    with pytest.raises(ValidationException):
        Validation.validate_instance(value, list, "items", "Ошибка")


def test_validation__validate_instance__error_carries_field_and_message():
    """Исключение хранит имя поля и переданное пояснение."""
    with pytest.raises(ValidationException) as exc_info:
        Validation.validate_instance(None, list, "items", "Список указан неверно")
    assert exc_info.value.field == "items"
    assert exc_info.value.message == "Список указан неверно"


def test_validation__validate_string__valid_value_is_returned():
    """Корректная строка возвращается как есть."""
    assert Validation.validate_string("Ромашка", "name") == "Ромашка"


def test_validation__validate_string__surrounding_spaces_are_stripped():
    """Пробелы по краям строки удаляются."""
    assert Validation.validate_string("  Ромашка \n", "name") == "Ромашка"


@pytest.mark.parametrize("value", ["", "   ", "\t\n"])
def test_validation__validate_string__empty_or_blank_raises(value):
    """Пустая строка и строка из одних пробелов вызывают исключение валидации."""
    with pytest.raises(ValidationException):
        Validation.validate_string(value, "name")


@pytest.mark.parametrize("value", [None, 123, 1.5, ["а"], b"bytes"])
def test_validation__validate_string__non_string_raises(value):
    """Нестроковое значение вызывает исключение валидации."""
    with pytest.raises(ValidationException):
        Validation.validate_string(value, "name")


def test_validation__validate_string__length_equal_to_max_is_accepted():
    """Строка длиной ровно max_length допустима."""
    assert Validation.validate_string("а" * 5, "name", max_length=5) == "а" * 5


def test_validation__validate_string__longer_than_max_raises():
    """Строка длиннее max_length вызывает исключение валидации."""
    with pytest.raises(ValidationException):
        Validation.validate_string("а" * 6, "name", max_length=5)


def test_validation__validate_string__max_length_counts_stripped_value():
    """Длина считается после удаления пробелов по краям."""
    assert Validation.validate_string("  ааааа  ", "name", max_length=5) == "ааааа"


def test_validation__validate_string__length_equal_to_min_is_accepted():
    """Строка длиной ровно min_length допустима."""
    assert Validation.validate_string("ааа", "name", min_length=3) == "ааа"


def test_validation__validate_string__shorter_than_min_raises():
    """Строка короче min_length вызывает исключение валидации."""
    with pytest.raises(ValidationException):
        Validation.validate_string("аа", "name", min_length=3)


def test_validation__validate_string__error_carries_field_name():
    """Исключение хранит имя проверяемого поля."""
    with pytest.raises(ValidationException) as exc_info:
        Validation.validate_string("", "full_name")
    assert exc_info.value.field == "full_name"


@pytest.mark.parametrize("value", [1, 0.001, 50.5, 10**9])
def test_validation__validate_positive_number__positive_value_is_returned(value):
    """Положительные int и float возвращаются без изменений."""
    assert Validation.validate_positive_number(value, "square") == value


@pytest.mark.parametrize("value", [0, 0.0, -1, -0.5])
def test_validation__validate_positive_number__zero_or_negative_raises(value):
    """Ноль и отрицательные числа вызывают исключение валидации."""
    with pytest.raises(ValidationException):
        Validation.validate_positive_number(value, "square")


@pytest.mark.parametrize("value", [True, False])
def test_validation__validate_positive_number__bool_raises(value):
    """Значение bool не считается числом, хотя является подклассом int."""
    with pytest.raises(ValidationException):
        Validation.validate_positive_number(value, "square")


@pytest.mark.parametrize("value", [float("nan"), float("inf"), float("-inf")])
def test_validation__validate_positive_number__non_finite_raises(value):
    """NaN и бесконечности вызывают исключение валидации."""
    with pytest.raises(ValidationException):
        Validation.validate_positive_number(value, "square")


@pytest.mark.parametrize("value", [None, "50", [1], 1 + 2j])
def test_validation__validate_positive_number__non_number_raises(value):
    """Нечисловое значение вызывает исключение валидации."""
    with pytest.raises(ValidationException):
        Validation.validate_positive_number(value, "square")


def test_validation__validate_digits__valid_value_is_returned():
    """Строка из ASCII-цифр без ограничений длины возвращается как есть."""
    assert Validation.validate_digits("1234567890", "inn") == "1234567890"


def test_validation__validate_digits__leading_zeros_are_kept():
    """Ведущие нули сохраняются: значение остаётся строкой."""
    assert Validation.validate_digits("0012345678", "inn") == "0012345678"


def test_validation__validate_digits__surrounding_spaces_are_stripped():
    """Пробелы по краям удаляются до проверки длины."""
    result = Validation.validate_digits(
        " 123456789 ", "bic", min_length=9, max_length=9
    )
    assert result == "123456789"


def test_validation__validate_digits__length_within_bounds_is_accepted():
    """Длина внутри границ min_length и max_length допустима."""
    assert Validation.validate_digits("12345", "code", min_length=3, max_length=8)


def test_validation__validate_digits__shorter_than_min_raises():
    """Строка короче min_length вызывает исключение валидации."""
    with pytest.raises(ValidationException):
        Validation.validate_digits("12", "code", min_length=3)


def test_validation__validate_digits__longer_than_max_raises():
    """Строка длиннее max_length вызывает исключение валидации."""
    with pytest.raises(ValidationException):
        Validation.validate_digits("123456789", "code", max_length=8)


def test_validation__validate_digits__equal_bounds_exact_length_is_accepted():
    """При min_length == max_length строка ровно этой длины допустима."""
    assert Validation.validate_digits("12345", "code", 5, 5) == "12345"


@pytest.mark.parametrize("value", ["1234", "123456"])
def test_validation__validate_digits__equal_bounds_other_length_raises(value):
    """При min_length == max_length строка другой длины вызывает исключение."""
    with pytest.raises(ValidationException):
        Validation.validate_digits(value, "code", 5, 5)


@pytest.mark.parametrize(
    "value", ["12345abcde", "1234 56789", "1234-56789", "12345.6789"]
)
def test_validation__validate_digits__non_digit_characters_raise(value):
    """Строка нужной длины с нецифровыми символами вызывает исключение валидации."""
    assert len(value) == 10
    with pytest.raises(ValidationException):
        Validation.validate_digits(value, "inn", min_length=10, max_length=10)


@pytest.mark.parametrize("value", ["²²²²²²²²²²", "١٢٣٤٥٦٧٨٩٠", "１２３４５６７８９０"])
def test_validation__validate_digits__non_ascii_digits_raise(value):
    """Unicode-цифры, для которых isdigit() истинен, отклоняются."""
    assert value.isdigit()
    with pytest.raises(ValidationException):
        Validation.validate_digits(value, "inn", min_length=10, max_length=10)


@pytest.mark.parametrize("value", [None, 1234567890, "", "   "])
def test_validation__validate_digits__non_string_or_empty_raises(value):
    """Не строка (в том числе число) и пустая строка вызывают исключение валидации."""
    with pytest.raises(ValidationException):
        Validation.validate_digits(value, "inn")
