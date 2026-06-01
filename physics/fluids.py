# Refrigerant properties (critical temperature, critical pressure, acentric factor)
FLUIDS = {
    'R32': {
        'name': 'R32',
        'Tc': 78.11,  # Critical temperature (°C)
        'Pc': 5.784,  # Critical pressure (MPa)
        'omega': 0.2763,  # Acentric factor
        'M': 52.024,  # Molar mass (g/mol)
    },
    'R410A': {
        'name': 'R410A',
        'Tc': 70.17,
        'Pc': 4.901,
        'omega': 0.2904,
        'M': 72.585,
    },
    'R290': {
        'name': 'R290 (Propane)',
        'Tc': 96.68,
        'Pc': 4.251,
        'omega': 0.1523,
        'M': 44.096,
    },
    'R744': {
        'name': 'R744 (CO2)',
        'Tc': 31.10,
        'Pc': 7.377,
        'omega': 0.2239,
        'M': 44.01,
    },
    'R134a': {
        'name': 'R134a',
        'Tc': 101.06,
        'Pc': 4.059,
        'omega': 0.3272,
        'M': 102.032,
    },
    'NH3': {
        'name': 'NH3 (Ammonia)',
        'Tc': 132.41,
        'Pc': 11.333,
        'omega': 0.2523,
        'M': 17.031,
    }
}

def get_fluid(fluid_name):
    return FLUIDS.get(fluid_name, None)