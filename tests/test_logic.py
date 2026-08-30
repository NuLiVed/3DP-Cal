import logic


def test_calculate_cost_short_print_under_100g():
    material = ("PLA", 120.0, 1.56)
    settings = (20.0, 50.0)

    total, rate_label = logic.calculate_cost(50.0, 2.0, material, settings)

    assert total == 228.8
    assert rate_label == "Short Print (0-4 hrs)"


def test_calculate_cost_long_print_uses_weight_multiplier_and_rate_tier():
    material = ("PETG", 140.0, 2.47)
    settings = (20.0, 50.0)

    total, rate_label = logic.calculate_cost(120.0, 12.0, material, settings)

    assert total == 383.6
    assert rate_label == "Long Print (10-20 hrs)"
