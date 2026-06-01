import math
from .fluids import get_fluid

class PengRobinson:
    R = 8.314  # Gas constant (J/mol·K)
    
    def __init__(self, fluid_name):
        self.fluid = get_fluid(fluid_name)
        if not self.fluid:
            raise ValueError(f"Unknown fluid: {fluid_name}")
        
        self.Tc = self.fluid['Tc'] + 273.15  # Convert to Kelvin
        self.Pc = self.fluid['Pc'] * 1e6  # Convert to Pa
        self.omega = self.fluid['omega']
        self.M = self.fluid['M'] / 1000  # Convert to kg/mol
        
    def calculate_properties(self, T, P):
        """Calculate thermodynamic properties at given T and P"""
        T_k = T + 273.15  # Convert to Kelvin
        P_pa = P * 1e6  # Convert to Pa
        
        # Reduced properties
        Tr = T_k / self.Tc
        Pr = P_pa / self.Pc
        
        # Peng-Robinson coefficients
        a = 0.45724 * (self.R * self.Tc)**2 / self.Pc
        b = 0.07780 * self.R * self.Tc / self.Pc
        
        m = 0.37464 + 1.54226 * self.omega - 0.26992 * self.omega**2
        alpha = (1 + m * (1 - math.sqrt(Tr)))**2
        
        A = alpha * a * P_pa / (self.R * T_k)**2
        B = b * P_pa / (self.R * T_k)
        
        # Compressibility factor (Z)
        Z = Pr / Tr
        
        # Density
        density = P_pa / (Z * self.R * T_k) * self.M
        
        return {
            'T': T,
            'P': P,
            'Z': Z,
            'density': density,
            'Tr': Tr,
            'Pr': Pr
        }