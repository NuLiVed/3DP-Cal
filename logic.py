import math # For Math functions (Decimal Round-UP to 2nd Place)

def calculate_cost(weight, hours, material_data, global_settings):
    """ Calculate the total cost of a 3D print job based on weight, hours, material data, and global settings.
        Parameters:
        material_data: Tuple containing material name, wattage, and price per gram.
        global_settings: Tuple containing Meralco Rate and Setup Fee. 
    """
    
    # Unpack Material Data and Global Settings
    _, wattage, price_per_g = material_data
    m_rate, setup_fee = global_settings
    
    # 10 minutes buffer for print time estimation
    buffer = 10/60
    
    # Filament Cost
    # Multiplier based on weight: 2.0 for <100g, 1.5 for >=100g
    multiplier = 2.0 if weight < 100 else 1.5
    filament_cost = weight * (price_per_g * multiplier)
    
    # Machine Rate based on hours
    match hours:
        case h if h <= (4 + buffer):
            machine_rate, rate_label = 70, "Short Print (0-4 hrs)"
        case h if h <= (10 + buffer):
            machine_rate, rate_label = 90, "Short Print (5-10 hrs)"
        case h if h <= (20 + buffer):
            machine_rate, rate_label = 120, "Short Print (10-20 hrs)"
        case _:
            machine_rate, rate_label = 150, "Short Print (20+ hrs)"    
            
    # Electricity Cost
    electricity_cost = (wattage / 1000) * m_rate * hours
    
    # Total Cost
    raw_total = filament_cost + machine_rate + electricity_cost + setup_fee
    
    # Round up raw total to 2 decimal places
    total_rounded = math.ceil(raw_total * 100) / 100
    
    # Return Total Cost and Rate Label for Receipt Generation
    return total_rounded, rate_label