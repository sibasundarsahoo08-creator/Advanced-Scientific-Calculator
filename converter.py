"""
converter.py
Unit conversion logic. Temperature uses formulas; everything else
converts through a common base unit using multiplication factors.
"""

# category -> {unit_name: factor_to_base_unit}
LENGTH = {
    "Millimeters": 0.001,
    "Centimeters": 0.01,
    "Meters": 1.0,
    "Kilometers": 1000.0,
    "Inches": 0.0254,
    "Feet": 0.3048,
    "Yards": 0.9144,
    "Miles": 1609.344,
}

WEIGHT = {
    "Milligrams": 0.001,
    "Grams": 1.0,
    "Kilograms": 1000.0,
    "Ounces": 28.349523125,
    "Pounds": 453.59237,
    "Tonnes": 1_000_000.0,
}

VOLUME = {
    "Milliliters": 0.001,
    "Liters": 1.0,
    "Cubic Meters": 1000.0,
    "Teaspoons": 0.00492892,
    "Tablespoons": 0.0147868,
    "Cups": 0.24,
    "Fluid Ounces (US)": 0.0295735,
    "Gallons (US)": 3.78541,
}

SPEED = {
    "Meters/second": 1.0,
    "Kilometers/hour": 0.277778,
    "Miles/hour": 0.44704,
    "Knots": 0.514444,
    "Feet/second": 0.3048,
}

CATEGORIES = {
    "Length": LENGTH,
    "Weight": WEIGHT,
    "Volume": VOLUME,
    "Speed": SPEED,
    "Temperature": None,  # handled specially
}


class ConverterError(Exception):
    pass


def convert(category: str, from_unit: str, to_unit: str, value: float) -> float:
    if category == "Temperature":
        return _convert_temperature(from_unit, to_unit, value)

    table = CATEGORIES.get(category)
    if table is None:
        raise ConverterError(f"Unknown category: {category}")
    if from_unit not in table or to_unit not in table:
        raise ConverterError("Unknown unit")

    base_value = value * table[from_unit]
    return base_value / table[to_unit]


def _convert_temperature(from_unit: str, to_unit: str, value: float) -> float:
    # Normalize to Celsius first
    if from_unit == "Celsius":
        celsius = value
    elif from_unit == "Fahrenheit":
        celsius = (value - 32) * 5 / 9
    elif from_unit == "Kelvin":
        celsius = value - 273.15
    else:
        raise ConverterError("Unknown unit")

    if to_unit == "Celsius":
        return celsius
    elif to_unit == "Fahrenheit":
        return celsius * 9 / 5 + 32
    elif to_unit == "Kelvin":
        return celsius + 273.15
    else:
        raise ConverterError("Unknown unit")


TEMPERATURE_UNITS = ["Celsius", "Fahrenheit", "Kelvin"]


def units_for(category: str):
    if category == "Temperature":
        return TEMPERATURE_UNITS
    return list(CATEGORIES[category].keys())
