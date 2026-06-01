"""Refrigerant metadata used by the simulator and recommendation engine."""

FLUIDS = {
    'R32': {
        'name': 'R32',
        'family': 'HFC',
        'Tc': 78.11,
        'Pc': 5.784,
        'omega': 0.2763,
        'M': 52.024,
        'gwp': 675,
        'safety': 'A2L',
        'eco_score': 62,
        'use_case': 'Residential and light commercial HVAC',
    },
    'R410A': {
        'name': 'R410A',
        'family': 'HFC blend',
        'Tc': 70.17,
        'Pc': 4.901,
        'omega': 0.2904,
        'M': 72.585,
        'gwp': 2088,
        'safety': 'A1',
        'eco_score': 34,
        'use_case': 'Legacy split and packaged systems',
    },
    'R290': {
        'name': 'R290 (Propane)',
        'family': 'Natural HC',
        'Tc': 96.68,
        'Pc': 4.251,
        'omega': 0.1523,
        'M': 44.096,
        'gwp': 3,
        'safety': 'A3',
        'eco_score': 96,
        'use_case': 'High-efficiency low-charge systems',
    },
    'R744': {
        'name': 'R744 (CO2)',
        'family': 'Natural',
        'Tc': 31.10,
        'Pc': 7.377,
        'omega': 0.2239,
        'M': 44.01,
        'gwp': 1,
        'safety': 'A1',
        'eco_score': 92,
        'use_case': 'Transcritical and commercial refrigeration',
    },
    'R134a': {
        'name': 'R134a',
        'family': 'HFC',
        'Tc': 101.06,
        'Pc': 4.059,
        'omega': 0.3272,
        'M': 102.032,
        'gwp': 1430,
        'safety': 'A1',
        'eco_score': 42,
        'use_case': 'Chillers and older refrigeration systems',
    },
    'NH3': {
        'name': 'NH3 (Ammonia)',
        'family': 'Natural',
        'Tc': 132.41,
        'Pc': 11.333,
        'omega': 0.2523,
        'M': 17.031,
        'gwp': 0,
        'safety': 'B2L',
        'eco_score': 98,
        'use_case': 'Industrial refrigeration',
    }
}


def get_fluid(fluid_name):
    return FLUIDS.get(fluid_name)


def all_fluids():
    return FLUIDS.copy()
