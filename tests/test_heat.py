from app import heat


def hrs(t, rh, solar=0, wind=1.5):
    return [{"time": f"2026-10-06T{h:02d}:00", "temp": t, "rh": rh, "solar": solar, "wind": wind} for h in range(24)]


def test_wet_bulb_known_value():  # Stull's paper example: 20°C, 50% RH -> ~13.7°C
    assert abs(heat.wet_bulb(20, 50) - 13.7) < 0.3


def test_humidity_raises_wbgt():
    assert heat.wbgt(36, 70) > heat.wbgt(36, 30)


def test_sun_raises_and_wind_lowers_wbgt():
    assert heat.wbgt(33, 50, 900) > heat.wbgt(33, 50, 0)
    assert heat.wbgt(33, 50, 900, wind=4) < heat.wbgt(33, 50, 900, wind=0.5)


def test_heavy_work_is_stricter():
    w = heat.wbgt(33, 55, 600)
    assert heat.classify(w, "heavy") >= heat.classify(w, "light")


def test_cool_day_is_low_risk():
    p = heat.build_plan(hrs(22, 50), "construction")
    assert p["level"] == 0 and p["work"] == 60 and p["peak"] == "-"


def test_hot_day_has_peak_and_rest():
    p = heat.build_plan(hrs(40, 60, 800), "construction")
    assert p["level"] == 3 and p["rest"] > 0 and p["peak"] != "-"


def test_personal_shift_never_lowers_risk():
    base = heat.build_plan(hrs(33, 55, 500), "delivery")
    shifted = heat.build_plan(hrs(33, 55, 500), "delivery", heat.risk_shift(True, True))
    assert shifted["level"] >= base["level"] and heat.risk_shift(True, True) == 3.0


def test_calibration_offset_applies():
    raw = heat.wbgt(30, 50, calibrated=False)
    heat.set_offset(1.5)
    try:
        assert abs(heat.wbgt(30, 50) - raw - 1.5) < 1e-9
    finally:
        heat.set_offset(0.0)
