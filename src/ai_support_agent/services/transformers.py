"""Unit transformation and standardization tools."""

from typing import Dict, Optional, Any

# Unit types
UNIT_TYPES = {
    "temperature": "temperature",
    "resistance": "resistance",
    "voltage": "voltage",
    "current": "current",
    "power": "power",
    "time": "time",
    "frequency": "frequency",
    "capacitance": "capacitance",
    "inductance": "inductance",
    "volume": "volume",
    "magnetic": "magnetic"
}

# Standard unit mappings
STANDARD_UNITS = {
    # Temperature
    "°C": {"symbol": "°C", "display": "°C", "type": UNIT_TYPES["temperature"]},
    "°F": {"symbol": "°F", "display": "°F", "type": UNIT_TYPES["temperature"]},
    
    # Resistance
    "ohm": {"symbol": "Ω", "display": "Ω", "type": UNIT_TYPES["resistance"]},
    "ohms": {"symbol": "Ω", "display": "Ω", "type": UNIT_TYPES["resistance"]},
    "Ohm": {"symbol": "Ω", "display": "Ω", "type": UNIT_TYPES["resistance"]},
    "Ohms": {"symbol": "Ω", "display": "Ω", "type": UNIT_TYPES["resistance"]},
    
    # Voltage
    "V": {"symbol": "V", "display": "V", "type": UNIT_TYPES["voltage"]},
    "VDC": {"symbol": "VDC", "display": "VDC", "type": UNIT_TYPES["voltage"]},
    "VAC": {"symbol": "VAC", "display": "VAC", "type": UNIT_TYPES["voltage"]},
    "Volts": {"symbol": "V", "display": "V", "type": UNIT_TYPES["voltage"]},
    
    # Current
    "A": {"symbol": "A", "display": "A", "type": UNIT_TYPES["current"]},
    "Amp": {"symbol": "A", "display": "A", "type": UNIT_TYPES["current"]},
    "Amps": {"symbol": "A", "display": "A", "type": UNIT_TYPES["current"]},
    "mA": {"symbol": "mA", "display": "mA", "type": UNIT_TYPES["current"]},
    
    # Power
    "W": {"symbol": "W", "display": "W", "type": UNIT_TYPES["power"]},
    "Watt": {"symbol": "W", "display": "W", "type": UNIT_TYPES["power"]},
    "Watts": {"symbol": "W", "display": "W", "type": UNIT_TYPES["power"]},
    
    # Time
    "ms": {"symbol": "ms", "display": "ms", "type": UNIT_TYPES["time"]},
    "msec": {"symbol": "ms", "display": "ms", "type": UNIT_TYPES["time"]},
    "msecs": {"symbol": "ms", "display": "ms", "type": UNIT_TYPES["time"]},
    "mSeconds": {"symbol": "ms", "display": "ms", "type": UNIT_TYPES["time"]},
    "millisecond": {"symbol": "ms", "display": "ms", "type": UNIT_TYPES["time"]},
    "milliseconds": {"symbol": "ms", "display": "ms", "type": UNIT_TYPES["time"]},
    "Milliseconds": {"symbol": "ms", "display": "ms", "type": UNIT_TYPES["time"]},
    "MILLISECONDS": {"symbol": "ms", "display": "ms", "type": UNIT_TYPES["time"]},
    
    # Volume
    "CC": {"symbol": "cc", "display": "cc", "type": UNIT_TYPES["volume"]},
    "cc": {"symbol": "cc", "display": "cc", "type": UNIT_TYPES["volume"]},
    "cubic centimeter": {"symbol": "cc", "display": "cc", "type": UNIT_TYPES["volume"]},
    "cubic centimeters": {"symbol": "cc", "display": "cc", "type": UNIT_TYPES["volume"]},
    "CUBIC CENTIMETERS": {"symbol": "cc", "display": "cc", "type": UNIT_TYPES["volume"]},
    "Cubic Centimeters": {"symbol": "cc", "display": "cc", "type": UNIT_TYPES["volume"]},
    "Cubic centimeters": {"symbol": "cc", "display": "cc", "type": UNIT_TYPES["volume"]},
    
    # Capacitance
    "pF": {"symbol": "pF", "display": "pF", "type": UNIT_TYPES["capacitance"]},
    "picofarad": {"symbol": "pF", "display": "pF", "type": UNIT_TYPES["capacitance"]},
    "picofarads": {"symbol": "pF", "display": "pF", "type": UNIT_TYPES["capacitance"]},
    
    # Inductance
    "mH": {"symbol": "mH", "display": "mH", "type": UNIT_TYPES["inductance"]},
    "millihenry": {"symbol": "mH", "display": "mH", "type": UNIT_TYPES["inductance"]},
    "millihenries": {"symbol": "mH", "display": "mH", "type": UNIT_TYPES["inductance"]},
    
    # Magnetic
    "AT": {"symbol": "AT", "display": "AT", "type": UNIT_TYPES["magnetic"]},
    "Ampere Turn": {"symbol": "AT", "display": "AT", "type": UNIT_TYPES["magnetic"]},
    "Ampere Turns": {"symbol": "AT", "display": "AT", "type": UNIT_TYPES["magnetic"]},
    "ampere turn": {"symbol": "AT", "display": "AT", "type": UNIT_TYPES["magnetic"]},
    "ampere turns": {"symbol": "AT", "display": "AT", "type": UNIT_TYPES["magnetic"]},
    "AMPERE TURNS": {"symbol": "AT", "display": "AT", "type": UNIT_TYPES["magnetic"]}
}

# Standard suffixes
STANDARD_SUFFIXES = {
    "maximum": "max",
    "minimum": "min",
    "typical": "typ",
    "nominal": "nom"
}


def standardize_unit(unit: Optional[str]) -> Optional[Dict[str, str]]:
    """Standardize a unit string to its canonical form.
    
    Args:
        unit: Unit string to standardize
        
    Returns:
        Dict with standardized unit info or None if not found
    """
    if not unit:
        return None
        
    # Step 1: Split into unit and suffix
    parts = [p.strip() for p in unit.split("-", 1)]
    base_unit = parts[0].strip()
    suffix = parts[1].strip() if len(parts) > 1 else None
        
    # Step 2: Try direct lookup
    if base_unit in STANDARD_UNITS:
        std_unit = STANDARD_UNITS[base_unit]
    else:
        # Try case-insensitive lookup
        base_unit_lower = base_unit.lower()
        std_unit = None
        for key, value in STANDARD_UNITS.items():
            if key.lower() == base_unit_lower:
                std_unit = value
                break
                
    if not std_unit:
        return None
            
    # Step 3: Format with standardized suffix
    if suffix:
        suffix_lower = suffix.lower()
        # Always abbreviate standard suffixes
        if suffix_lower in STANDARD_SUFFIXES:
            abbrev = STANDARD_SUFFIXES[suffix_lower]
            std_unit = {**std_unit, "display": f"{std_unit['display']} - {abbrev}"}
        else:
            # For any other suffix, keep it as is
            std_unit = {**std_unit, "display": f"{std_unit['display']} - {suffix}"}
            
    return std_unit


def format_display_value(value: str, unit: Optional[str] = None) -> str:
    """Format a value with its unit for display.
    
    Args:
        value: The value to format
        unit: Optional unit to append
        
    Returns:
        Formatted display string
    """
    if not unit:
        return value
        
    # Handle special cases like temperature ranges
    if "to" in value:
        # For ranges like "-40 to +125"
        return f"{value} {unit}"
        
    std_unit = standardize_unit(unit)
    if not std_unit:
        return f"{value} {unit}"
        
    return f"{value} {std_unit['display']}" 