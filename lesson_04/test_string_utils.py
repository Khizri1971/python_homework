import pytest


class StringUtils:
    """Класс с полезными утилитами для обработки и анализа строк."""

    @staticmethod
    def capitalize(text: str) -> str:
        """Делает первую букву строки заглавной, не изменяя регистр остальных букв."""
        if not text:
            return text
        return text[0].upper() + text[1:]

    @staticmethod
    def trim(text: str) -> str:
        """Удаляет пробельные символы с начала и конца строки."""
        if text is None:
            raise ValueError("Входное значение не может быть None")
        return text.strip()

    @staticmethod
    def contains(text: str, substring: str) -> bool:
        """Проверяет, содержится ли подстрока в строке (чувствительно к регистру)."""
        if text is None or substring is None:
            raise ValueError("Аргументы не могут быть None")
        return substring in text

    @staticmethod
    def delete_symbol(text: str, symbol: str) -> str:
        """Удаляет все вхождения указанного символа из строки."""
        if text is None or symbol is None:
            raise ValueError("Аргументы не могут быть None")
        return text.replace(symbol, "")


# =====================================================================
# ТЕСТЫ (pytest)
# =====================================================================

# --- Тесты для метода capitalize ---
@pytest.mark.parametrize("input_str, expected", [
    ("тест", "Тест"),
    ("привет мир", "Привет мир"),
    ("123 тест", "123 тест"),
    ("", ""),
])
def test_capitalize_positive(input_str, expected):
    assert StringUtils.capitalize(input_str) == expected


# --- Тесты для метода trim ---
@pytest.mark.parametrize("input_str, expected", [
    ("  привет  ", "привет"),
    ("\n\t тест \t\n", "тест"),
    ("без_пробелов", "без_пробелов"),
    (" ", ""),
    ("", ""),
])
def test_trim_positive(input_str, expected):
    assert StringUtils.trim(input_str) == expected


def test_trim_negative_none():
    with pytest.raises(ValueError, match="Входное значение не может быть None"):
        StringUtils.trim(None)


# --- Тесты для метода contains ---
@pytest.mark.parametrize("text, substring, expected", [
    ("04 апреля 2023", "апреля", True),
    ("123", "2", True),
    ("Тест", "тест", False),  # Регистрозависимость
    ("Привет", "мир", False),
])
def test_contains_positive(text, substring, expected):
    assert StringUtils.contains(text, substring) == expected


@pytest.mark.parametrize("text, substring", [
    (None, "тест"),
    ("тест", None),
    (None, None)
])
def test_contains_negative_none(text, substring):
    with pytest.raises(ValueError, match="Аргументы не могут быть None"):
        StringUtils.contains(text, substring)


# --- Тесты для метода delete_symbol ---
@pytest.mark.parametrize("text, symbol, expected", [
    ("04 апреля 2023", " ", "04апреля2023"),  # Удаление пробелов
    ("тест", "т", "ес"),
    ("123", "4", "123"),  # Символа нет в строке
    ("", "а", ""),
])
def test_delete_symbol_positive(text, symbol, expected):
    assert StringUtils.delete_symbol(text, symbol) == expected


def test_delete_symbol_negative_none():
    with pytest.raises(ValueError, match="Аргументы не могут быть None"):
        StringUtils.delete_symbol(None, "а")
