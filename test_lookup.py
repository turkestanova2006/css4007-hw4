
from tools_hw4 import lookup

def test_population():
    r = lookup("Brightwater", "population_2025")
    assert r["value"] == 44675
    assert r["source"] == "NR-05"

def test_correction():
    r = lookup("Brightwater", "area_km2")
    assert r["value"] == 921.4
    assert r["source"] == "NR-16"

def test_similar_names():
    a = lookup("Ossbridge", "population_2025")
    b = lookup("Ossford", "population_2025")
    assert a["value"] == 52904
    assert b["value"] == 30982

def test_misspelled_name():
    r = lookup("Ossbrige", "population_2025")
    assert "error" in r
    assert "Ossbridge" in r["suggestions"]

def test_archived_profile():
    r = lookup("Tarnvale", "population_2025")
    assert r["value"] == 71388
    assert r["source"] == "NR-03"

def test_water_conversion():
    r = lookup("Lindenmoor", "water_2025")
    assert r["value"] == 2151.4
    assert r["source"] == "NR-08"

def test_unknown_field():
    r = lookup("Brightwater", "unknown_field")
    assert "error" in r
