import logic


def test_calculate_cost_short_print_under_100g():
    material = ("PLA", 120.0, 1.56)
    settings = (20.0, 50.0)

    total, rate_label = logic.calculate_cost(50.0, 2, 0, material, settings)

    assert total == 228.8
    assert rate_label == "Short Print (0-4 hrs)"


def test_calculate_cost_long_print_uses_weight_multiplier_and_rate_tier():
    material = ("PETG", 140.0, 2.47)
    settings = (20.0, 50.0)

    total, rate_label = logic.calculate_cost(120.0, 12, 0, material, settings)

    assert total == 383.6
    assert rate_label == "Long Print (10-20 hrs)"


def test_to_decimal_hours_combines_hours_and_minutes():
    assert logic.to_decimal_hours(2, 30) == 2.5


def test_split_duration_restores_hours_and_minutes():
    assert logic.split_duration(2.5) == (2, 30)


def test_format_duration_uses_singular_and_plural_units():
    assert logic.format_duration(1, 1) == "1 hr 1 min"
    assert logic.format_duration(2, 30) == "2 hrs 30 mins"
