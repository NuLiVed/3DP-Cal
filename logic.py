import math # For Math functions (Decimal Round-UP to 2nd Place)

def to_decimal_hours(hours, minutes):
    """ Combine separate hour and minute inputs into a single decimal hour value for computation.
        Example: (2, 30) -> 2.5
    """
    return hours + (minutes / 60)

def split_duration(total_hours):
    """ Split a stored decimal hour value back into whole hours and minutes.
        Example: 2.5 -> (2, 30)
    """
    total_minutes = round(total_hours * 60)
    return total_minutes // 60, total_minutes % 60

def format_duration(hours, minutes):
    """ Format print time the same way it was entered, for receipts and previews.
        Example: (2, 30) -> "2 hrs 30 mins"
    """
    hr_word = "hr" if hours == 1 else "hrs"
    min_word = "min" if minutes == 1 else "mins"
    return f"{hours} {hr_word} {minutes} {min_word}"

def calculate_cost(weight, hours, minutes, material_data, global_settings):
    """ Calculate the total cost of a 3D print job based on weight, print time, material data, and global settings.
        Parameters:
        hours, minutes: Print time as entered by the user (whole hours plus minutes).
        material_data: Tuple containing material name, wattage, and price per gram.
        global_settings: Tuple containing Meralco Rate and Setup Fee.
    """

    # Unpack Material Data and Global Settings
    _, wattage, price_per_g = material_data
    m_rate, setup_fee = global_settings

    # Total print time in decimal hours for rate tiering and electricity usage
    total_hours = to_decimal_hours(hours, minutes)

    # 10 minutes buffer for print time estimation
    buffer = 10/60

    # Filament Cost
    # Multiplier based on weight: 2.0 for <100g, 1.5 for >=100g
    multiplier = 2.0 if weight < 100 else 1.5
    filament_cost = weight * multiplier
    
    # Machine Rate based on total print time
    match total_hours:
        case h if h <= (4 + buffer):
            machine_rate, rate_label = 74, "Short Print (0-4 hrs)"
        case h if h <= (10 + buffer):
            machine_rate, rate_label = 90, "Medium Print (5-10 hrs)"
        case h if h <= (20 + buffer):
            machine_rate, rate_label = 120, "Long Print (10-20 hrs)"
        case _:
            machine_rate, rate_label = 150, "Extra Long Print (20+ hrs)"    
            
    # Electricity Cost
    electricity_cost = (wattage / 1000) * m_rate * total_hours
    
    # Total Cost
    raw_total = filament_cost + machine_rate + electricity_cost + setup_fee
    
    # Round up raw total to 2 decimal places
    total_rounded = math.ceil(raw_total * 100) / 100
    
    # Return Total Cost and Rate Label for Receipt Generation
    return total_rounded, rate_label