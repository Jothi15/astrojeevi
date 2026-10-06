from app.astrology import build_chart
from app.dignity import compute_dignities

SPEEDS = {name: 1.0 for name in ["Sun", "Moon", "Mars", "Mercury", "Jupiter", "Venus", "Saturn", "Rahu", "Ketu"]}
# Baseline placement with no planet in an exaltation/debilitation sign
# (everything in Sagittarius, Ketu in Gemini); tests override what they need.
NEUTRAL = {"Sun": 8, "Moon": 8, "Mars": 8, "Mercury": 8, "Jupiter": 8, "Venus": 8, "Saturn": 8, "Rahu": 8, "Ketu": 2}


def chart_with(placements: dict[str, tuple[int, float]]):
    """placements: planet -> (rasi index, degrees into the sign)."""
    positions = {**{p: r * 30 + 5.0 for p, r in NEUTRAL.items()}}
    for planet, (rasi, deg) in placements.items():
        positions[planet] = rasi * 30 + deg
    return build_chart(250.0, positions, SPEEDS)


def by_planet(entries):
    return {e.planet: e for e in entries}


def test_exalted_and_debilitated_are_detected():
    chart = chart_with({"Moon": (1, 5.75), "Saturn": (0, 8.79)})
    result = by_planet(compute_dignities(chart))
    assert result["Moon"].state == "ucham"
    assert result["Saturn"].state == "neecham"


def test_distance_from_deep_degree():
    chart = chart_with({"Moon": (1, 5.75), "Saturn": (0, 8.79)})
    result = by_planet(compute_dignities(chart))
    assert abs(result["Moon"].degrees_from_deep - 2.75) < 1e-6  # deep exaltation 3 deg
    assert abs(result["Saturn"].degrees_from_deep - 11.21) < 1e-6  # deep debilitation 20 deg
    assert result["Moon"].deep_degree == 3.0


def test_every_classical_planet_in_both_signs():
    table = {
        "Sun": (0, 6), "Moon": (1, 7), "Mars": (9, 3), "Mercury": (5, 11),
        "Jupiter": (3, 9), "Venus": (11, 5), "Saturn": (6, 0),
    }
    for planet, (exalt, debil) in table.items():
        up = by_planet(compute_dignities(chart_with({planet: (exalt, 10.0)})))
        down = by_planet(compute_dignities(chart_with({planet: (debil, 10.0)})))
        assert up[planet].state == "ucham", planet
        assert down[planet].state == "neecham", planet


def test_nodes_follow_bphs_convention_without_deep_degree():
    chart = chart_with({"Rahu": (1, 12.0), "Ketu": (7, 12.0)})
    result = by_planet(compute_dignities(chart))
    assert result["Rahu"].state == "ucham"  # Rahu exalted in Taurus
    assert result["Ketu"].state == "ucham"  # Ketu exalted in Scorpio
    assert result["Rahu"].degrees_from_deep is None
    swapped = by_planet(compute_dignities(chart_with({"Rahu": (7, 12.0), "Ketu": (1, 12.0)})))
    assert swapped["Rahu"].state == "neecham"
    assert swapped["Ketu"].state == "neecham"


def test_planets_in_ordinary_signs_are_not_listed():
    chart = chart_with({})
    assert compute_dignities(chart) == []


def test_krithika_chart_has_moon_ucham_and_saturn_neecham_only():
    longitudes = {
        "Sun": 245.59, "Moon": 35.76, "Mars": 310.65, "Mercury": 263.74, "Jupiter": 187.27,
        "Venus": 237.27, "Saturn": 8.79, "Rahu": 322.43, "Ketu": 142.43,
    }
    result = compute_dignities(build_chart(250.0, longitudes, SPEEDS))
    assert {(e.planet, e.state) for e in result} == {("Moon", "ucham"), ("Saturn", "neecham")}
