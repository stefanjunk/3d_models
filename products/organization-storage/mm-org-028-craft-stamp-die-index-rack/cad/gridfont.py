"""Repository-owned geometric 5x7 glyph map and deterministic layout helpers."""
from __future__ import annotations

import unicodedata


FONT_ID = "MM-GRID-5X7-v1"
GLYPHS = {
    "A": ("01110", "10001", "10001", "11111", "10001", "10001", "10001"),
    "B": ("11110", "10001", "10001", "11110", "10001", "10001", "11110"),
    "C": ("01111", "10000", "10000", "10000", "10000", "10000", "01111"),
    "D": ("11110", "10001", "10001", "10001", "10001", "10001", "11110"),
    "E": ("11111", "10000", "10000", "11110", "10000", "10000", "11111"),
    "F": ("11111", "10000", "10000", "11110", "10000", "10000", "10000"),
    "G": ("01111", "10000", "10000", "10111", "10001", "10001", "01111"),
    "H": ("10001", "10001", "10001", "11111", "10001", "10001", "10001"),
    "I": ("11111", "00100", "00100", "00100", "00100", "00100", "11111"),
    "J": ("00111", "00010", "00010", "00010", "10010", "10010", "01100"),
    "K": ("10001", "10010", "10100", "11000", "10100", "10010", "10001"),
    "L": ("10000", "10000", "10000", "10000", "10000", "10000", "11111"),
    "M": ("10001", "11011", "10101", "10101", "10001", "10001", "10001"),
    "N": ("10001", "11001", "10101", "10011", "10001", "10001", "10001"),
    "O": ("01110", "10001", "10001", "10001", "10001", "10001", "01110"),
    "P": ("11110", "10001", "10001", "11110", "10000", "10000", "10000"),
    "Q": ("01110", "10001", "10001", "10001", "10101", "10010", "01101"),
    "R": ("11110", "10001", "10001", "11110", "10100", "10010", "10001"),
    "S": ("01111", "10000", "10000", "01110", "00001", "00001", "11110"),
    "T": ("11111", "00100", "00100", "00100", "00100", "00100", "00100"),
    "U": ("10001", "10001", "10001", "10001", "10001", "10001", "01110"),
    "V": ("10001", "10001", "10001", "10001", "10001", "01010", "00100"),
    "W": ("10001", "10001", "10001", "10101", "10101", "10101", "01010"),
    "X": ("10001", "10001", "01010", "00100", "01010", "10001", "10001"),
    "Y": ("10001", "10001", "01010", "00100", "00100", "00100", "00100"),
    "Z": ("11111", "00001", "00010", "00100", "01000", "10000", "11111"),
    "0": ("01110", "10001", "10011", "10101", "11001", "10001", "01110"),
    "1": ("00100", "01100", "00100", "00100", "00100", "00100", "01110"),
    "2": ("01110", "10001", "00001", "00010", "00100", "01000", "11111"),
    "3": ("11110", "00001", "00001", "01110", "00001", "00001", "11110"),
    "4": ("00010", "00110", "01010", "10010", "11111", "00010", "00010"),
    "5": ("11111", "10000", "10000", "11110", "00001", "00001", "11110"),
    "6": ("01110", "10000", "10000", "11110", "10001", "10001", "01110"),
    "7": ("11111", "00001", "00010", "00100", "01000", "01000", "01000"),
    "8": ("01110", "10001", "10001", "01110", "10001", "10001", "01110"),
    "9": ("01110", "10001", "10001", "01111", "00001", "00001", "01110"),
    "-": ("00000", "00000", "00000", "11111", "00000", "00000", "00000"),
    ".": ("00000", "00000", "00000", "00000", "00000", "00110", "00110"),
    "&": ("01100", "10010", "10100", "01000", "10101", "10010", "01101"),
    " ": ("000", "000", "000", "000", "000", "000", "000"),
}


def normalize_text(value: str, allowed_characters: str, maximum: int) -> str:
    replacements = {"Ä": "AE", "Ö": "OE", "Ü": "UE", "ä": "AE", "ö": "OE", "ü": "UE", "ẞ": "SS", "ß": "SS"}
    expanded = "".join(replacements.get(character, character) for character in value.strip())
    normalized = unicodedata.normalize("NFKD", expanded)
    ascii_value = "".join(character for character in normalized if not unicodedata.combining(character)).upper()
    result = " ".join(ascii_value.split())
    invalid = sorted(set(character for character in result if character not in set(allowed_characters)))
    if invalid:
        raise ValueError(f"unsupported personalization characters: {invalid}")
    if not result:
        raise ValueError("personalization must not be empty")
    if len(result) > maximum:
        raise ValueError(f"personalization exceeds {maximum} characters after transliteration")
    return result


def layout(text: str, available_width: float, target_height: float, maximum_pitch: float, minimum_pixel: float) -> dict:
    total_columns = sum(len(GLYPHS[character][0]) for character in text) + max(0, len(text) - 1)
    pitch = min(maximum_pitch, available_width / total_columns, target_height / 7.0)
    pixel = pitch * 0.78
    if pixel < minimum_pixel:
        raise ValueError("personalization would create sub-minimum printable pixels")
    return {"total_columns": total_columns, "pitch_mm": pitch, "pixel_width_mm": pixel, "text_width_mm": total_columns * pitch, "text_height_mm": 7.0 * pitch}


def pixel_rectangles(text: str, layout_data: dict, center_x: float, center_y: float) -> list[tuple[float, float, float]]:
    pitch = layout_data["pitch_mm"]
    pixel = layout_data["pixel_width_mm"]
    inset = (pitch - pixel) / 2.0
    start_x = center_x - layout_data["text_width_mm"] / 2.0
    start_y = center_y - layout_data["text_height_mm"] / 2.0
    cursor = 0
    rectangles = []
    for character in text:
        glyph = GLYPHS[character]
        for row_index, row in enumerate(glyph):
            for column_index, value in enumerate(row):
                if value == "1":
                    rectangles.append((start_x + (cursor + column_index) * pitch + inset, start_y + (6 - row_index) * pitch + inset, pixel))
        cursor += len(glyph[0]) + 1
    return rectangles
