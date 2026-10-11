"""
tools.py - the ONLY file teammates need to edit.

The chatbot calls these three functions. Each teammate replaces the body of
their function with a call into their own module, keeping the same name,
arguments, and returning a plain dict (JSON-serialisable). On failure, return
{"error": "message"} instead of raising.

    get_planet_data              -> Planetary Analysis owner
    compare_planets              -> Comparison owner
    predict_mission_feasibility  -> ML Feasibility owner

Until they do, the placeholder data below keeps the chatbot working for testing.
"""

# --------------------------------------------------------------------------
# 1. WIRE YOUR EXISTING MODULES HERE
#    The functions below use a small placeholder dataset so the chatbot runs
#    out of the box. Replace the bodies with calls into your real modules.
# --------------------------------------------------------------------------

_PLACEHOLDER_DATA = {
    "mercury": {"gravity_ms2": 3.7, "mean_temp_c": 167, "distance_au": 0.39, "atmosphere": "negligible"},
    "venus": {"gravity_ms2": 8.87, "mean_temp_c": 464, "distance_au": 0.72, "atmosphere": "CO2, very dense"},
    "earth": {"gravity_ms2": 9.81, "mean_temp_c": 15, "distance_au": 1.0, "atmosphere": "N2/O2"},
    "mars": {"gravity_ms2": 3.71, "mean_temp_c": -63, "distance_au": 1.52, "atmosphere": "CO2, very thin"},
    "jupiter": {"gravity_ms2": 24.79, "mean_temp_c": -110, "distance_au": 5.2, "atmosphere": "H2/He, no surface"},
    "saturn": {"gravity_ms2": 10.44, "mean_temp_c": -140, "distance_au": 9.58, "atmosphere": "H2/He, no solid surface"},
    "uranus": {"gravity_ms2": 8.69, "mean_temp_c": -195, "distance_au": 19.2, "atmosphere": "H2/He/CH4, no solid surface"},
    "neptune": {"gravity_ms2": 11.15, "mean_temp_c": -200, "distance_au": 30.05, "atmosphere": "H2/He/CH4, no solid surface"},
    "moon": {"gravity_ms2": 1.62, "mean_temp_c": -53, "distance_au": 1.0, "atmosphere": "negligible"},
    "titan": {"gravity_ms2": 1.35, "mean_temp_c": -179, "distance_au": 9.58, "atmosphere": "N2, dense"},
    "pluto": {"gravity_ms2": 0.62, "mean_temp_c": -229, "distance_au": 39.5, "atmosphere": "N2, very thin"},
}


def get_planet_data(planet: str) -> dict:
    # TODO: replace with your Planetary Analysis module, e.g.
    #   from planetary_analysis import analyze_planet
    #   return analyze_planet(planet)
    data = _PLACEHOLDER_DATA.get(planet.strip().lower())
    if not data:
        return {"error": f"No data for '{planet}'. Known: {', '.join(_PLACEHOLDER_DATA)}"}
    return {"planet": planet.title(), **data}


def compare_planets(planet_a: str, planet_b: str) -> dict:
    # TODO: replace with your Comparison module.
    a, b = get_planet_data(planet_a), get_planet_data(planet_b)
    if "error" in a or "error" in b:
        return {"error": a.get("error") or b.get("error")}
    return {"a": a, "b": b}


def predict_mission_feasibility(planet: str, mission_type: str = "orbiter") -> dict:
    # TODO: replace with your trained model, e.g.
    #   model = joblib.load("feasibility_model.pkl")   (load once, cache it)
    #   score = model.predict_proba([features])[0][1]
    d = get_planet_data(planet)
    if "error" in d:
        return d
    # Placeholder heuristic only - NOT your ML model.
    score = 1.0
    score -= min(abs(d["mean_temp_c"] - 15) / 600, 0.5)
    score -= min(d["distance_au"] / 20, 0.3)
    if mission_type == "lander":
        score -= min(abs(d["gravity_ms2"] - 9.81) / 40, 0.2)
    return {
        "planet": d["planet"],
        "mission_type": mission_type,
        "feasibility_score": round(max(score, 0.0), 2),
        "note": "placeholder heuristic, replace with ML model",
    }


TOOL_FUNCTIONS = {
    "get_planet_data": get_planet_data,
    "compare_planets": compare_planets,
    "predict_mission_feasibility": predict_mission_feasibility,
}

TOOLS = [
    {
        "name": "get_planet_data",
        "description": "Get physical and environmental data for one planet.",
        "input_schema": {
            "type": "object",
            "properties": {"planet": {"type": "string", "description": "Planet name, e.g. Mars"}},
            "required": ["planet"],
        },
    },
    {
        "name": "compare_planets",
        "description": "Compare two planets side by side.",
        "input_schema": {
            "type": "object",
            "properties": {
                "planet_a": {"type": "string"},
                "planet_b": {"type": "string"},
            },
            "required": ["planet_a", "planet_b"],
        },
    },
    {
        "name": "predict_mission_feasibility",
        "description": "Run the ML mission feasibility model for a planet and mission type.",
        "input_schema": {
            "type": "object",
            "properties": {
                "planet": {"type": "string"},
                "mission_type": {"type": "string", "enum": ["flyby", "orbiter", "lander", "crewed"]},
            },
            "required": ["planet"],
        },
    },
]

