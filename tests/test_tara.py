from app.constants import TARA_CATEGORIES
from app.tara import compute_tara_balam


def test_birth_nakshatra_is_janma():
    for birth_nak in range(27):
        entries = compute_tara_balam(birth_nak)
        own = entries[birth_nak]
        assert own.count == 1
        assert own.category == "Janma"


def test_categories_cycle_correctly():
    entries = compute_tara_balam(5)
    for entry in entries:
        expected_category = TARA_CATEGORIES[(entry.count - 1) % 9]
        assert entry.category == expected_category


def test_wraparound_at_end_of_cycle():
    entries = compute_tara_balam(26)
    # nakshatra 0 is one past the birth star (26) -> wraps -> count 2 -> Sampat
    assert entries[0].count == 2
    assert entries[0].category == "Sampat"
    # nakshatra 25 is one before 26 -> count 27 -> category (27-1)%9=8 -> Ati-Mitra
    assert entries[25].count == 27
    assert entries[25].category == "Ati-Mitra"


def test_all_27_nakshatras_covered_exactly_once():
    entries = compute_tara_balam(0)
    assert sorted(e.nakshatra for e in entries) == list(range(27))
    assert sorted(e.count for e in entries) == list(range(1, 28))
