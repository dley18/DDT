"""Incident configurations."""

INCIDENT_TYPE = {
    "event": {"J_INCIDENT_EVENT", 2},
    "warning": {"J_INCIDENT_WARNING", 3},
    "alarm": {"J_INCIDENT_ALARM", 4},
}

INCIDENT_STATE = {
    "one_shot": {"J_INCIDENT_ONE_SHOT", 3},
    "set": {"J_INCIDENT_SET", 2},
    "clear": {"J_INCIDENT_CLEAR", 1},
}



INCIDENT_ARGUMENTS = {
    "d": "longValue",
    "s": "stringTidxValue",
    "f": "realValue",
}

INCIDENT_ARGUMENTS_V2 = {
    "d": 858993459,
    "s": 572662306,
    "f": 1145324612,
}

INCIDENT_COLORS = {
    "clear": "#77797d",
    "event": "#05e81b",
    "warning": "#e88605",
    "alarm": "#e80505",
    "black_text": "#000000",
}
