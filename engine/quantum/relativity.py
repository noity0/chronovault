"""
ChronoVault Quantum Lab — Relativity Engine (REAL physics, exact math)
=====================================================================
The same equations GPS satellites use every day. Honest about scale:
effects are microscopic at everyday speeds, but the math is exact.
No API keys. Stdlib only.
"""
import json
import math

C = 299_792_458.0          # speed of light, m/s
G_EARTH = 9.80665          # m/s²
R_EARTH = 6_371_000.0      # m
GM_EARTH = 3.986004418e14  # m³/s² (standard gravitational parameter)
GPS_ALT = 20_200_000.0     # GPS satellite altitude, m


def lorentz_factor(v: float) -> float:
    """γ = 1/√(1−v²/c²). v in m/s. → infinity as v→c."""
    if v >= C:
        raise ValueError("v must be < c (no FTL — honest physics)")
    return 1.0 / math.sqrt(1.0 - (v / C) ** 2)


def velocity_dilation(proper_years: float, v: float) -> dict:
    """Twin paradox: traveler's proper time t0, speed v → Earth-elapsed time."""
    g = lorentz_factor(v)
    earth_years = proper_years * g
    return {"proper_years": proper_years, "lorentz_gamma": round(g, 6),
            "earth_years": round(earth_years, 6),
            "future_gain_years": round(earth_years - proper_years, 6),
            "earth_days": round(earth_years * 365.25, 2)}


def gravitational_dilation(altitude_m: float, duration_days: float) -> dict:
    """Exact Schwarzschild weak-field rate between surface and altitude:
       dτ/dt = GM/c² · (1/r_surface − 1/r_altitude)   [clock runs FASTER up there]
       (g·h/c² is only valid for h ≪ R; this form is exact for GPS too)."""
    rate = GM_EARTH / C ** 2 * (1.0 / R_EARTH - 1.0 / (R_EARTH + altitude_m))
    delta_per_day = rate * 86400  # seconds gained per day
    total = delta_per_day * duration_days
    return {"altitude_m": altitude_m, "seconds_gained_per_day": delta_per_day,
            "total_seconds_gained": total}


def gps_correction() -> dict:
    """The real GPS numbers — machine prints them like a physics textbook."""
    # velocity effect: orbital speed ~3.874 km/s
    v_orbit = math.sqrt(G_EARTH * R_EARTH ** 2 / (R_EARTH + GPS_ALT)) * 1.0
    g_orb = lorentz_factor(v_orbit)
    vel = -(1 - 1 / g_orb) * 86400  # seconds lost per day (negative = slower)
    grav = gravitational_dilation(GPS_ALT, 1.0)["seconds_gained_per_day"]
    return {
        "satellite_speed_ms": round(v_orbit, 1),
        "velocity_effect_us_per_day": round(vel * 1e6, 1),
        "gravitational_effect_us_per_day": round(grav * 1e6, 1),
        "net_us_per_day": round((vel + grav) * 1e6, 1),
        "note": "Net +38.6 μs/day — without this correction GPS drifts ~10 km/day. REAL forward time travel, flying overhead right now.",
    }


def examples() -> list:
    out = []
    for label, v, yrs in [
        ("ISS (7.66 km/s, 6 months)", 7_660.0, 0.5),
        ("0.1c rocket, 1 year", 0.1 * C, 1.0),
        ("0.9c rocket, 1 year", 0.9 * C, 1.0),
        ("0.999c rocket, 1 year", 0.999 * C, 1.0),
    ]:
        d = velocity_dilation(yrs, v)
        out.append({"case": label, **d})
    return out


if __name__ == "__main__":
    print(json.dumps({"gps": gps_correction(), "examples": examples()}, indent=1))
