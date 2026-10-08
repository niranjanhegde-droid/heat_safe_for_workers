"""Heat engine v2: Stull wet-bulb + radiation/wind-aware WBGT, personal risk shift, field calibration.

IMPORTANT: THRESHOLDS, WORK_REST and the sun/wind coefficients are starting values inspired by
ISO 7243 / ACGIH / NIOSH. Calibrate with a real WBGT meter (admin panel) and have an
occupational-health expert verify them before real-world use.
"""
import math

LEVELS = ["low", "moderate", "high", "extreme"]
THRESHOLDS = {"light": (28, 30, 32), "moderate": (26, 28, 31), "heavy": (25, 27, 29)}
JOB_LOAD = {"delivery": "moderate", "construction": "heavy", "farm": "heavy", "vendor": "light"}
WORK_REST = [(60, 0), (50, 10), (40, 20), (15, 45)]  # (work, rest) minutes per hour
OFFSET = 0.0  # field-calibration bias in °C, set from admin meter readings


def set_offset(x: float) -> None:
    global OFFSET
    OFFSET = x


def wet_bulb(t: float, rh: float) -> float:
    """Stull (2011) wet-bulb approximation, valid roughly RH 5-99%, T -20..50°C."""
    rh = min(max(rh, 5.0), 99.0)
    return (t * math.atan(0.151977 * (rh + 8.313659) ** 0.5) + math.atan(t + rh)
            - math.atan(rh - 1.676331) + 0.00391838 * rh ** 1.5 * math.atan(0.023101 * rh) - 4.686035)


def wbgt(t: float, rh: float, solar: float = 0.0, wind: float = 1.5, calibrated: bool = True) -> float:
    """Outdoor WBGT = 0.7*Tnwb + 0.2*Tg + 0.1*Ta.
    Tnwb and globe temp Tg are estimated from wet-bulb, air temp, solar (W/m²) and wind (m/s at worker height)."""
    s, damp = min(max(solar, 0), 1000), 1 + 0.15 * max(wind, 0)
    tnwb = wet_bulb(t, rh) + 0.0028 * s / damp
    tg = t + 0.018 * s / damp
    return 0.7 * tnwb + 0.2 * tg + 0.1 * t + (OFFSET if calibrated else 0)


def risk_shift(new_to_heat, high_risk) -> float:
    """°C added to effective WBGT: unacclimatized workers and 45+/chronic-condition workers get stricter limits."""
    return 2.0 * bool(new_to_heat) + 1.0 * bool(high_risk)


def classify(w: float, load: str) -> int:
    return sum(w >= c for c in THRESHOLDS[load])


def fmt_hour(h: int) -> str:
    return f"{h % 12 or 12} {'AM' if h < 12 else 'PM'}"


def span(hours: list[int]) -> str:
    return f"{fmt_hour(min(hours))}–{fmt_hour(max(hours) + 1)}" if hours else "-"


def build_plan(hours: list[dict], job: str, shift: float = 0.0) -> dict:
    load = JOB_LOAD.get(job, "moderate")
    rows = []
    for h in hours:
        hr = int(h["time"][11:13])
        if 6 <= hr <= 20:
            w = wbgt(h["temp"], h["rh"], h["solar"], h.get("wind", 1.5))
            rows.append({"hour": hr, "wbgt": round(w, 1), "level": classify(w + shift, load)})
    worst = max((r["level"] for r in rows), default=0)
    return {"load": load, "rows": rows, "level": worst, "shift": shift,
            "peak": span([r["hour"] for r in rows if r["level"] >= 2]),
            "safe": span([r["hour"] for r in rows if r["level"] <= 1]),
            "work": WORK_REST[worst][0], "rest": WORK_REST[worst][1]}


def level_at(plan: dict, hour: int) -> int:
    return next((r["level"] for r in plan["rows"] if r["hour"] == hour), 0)
