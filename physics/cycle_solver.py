from .peng_robinson import PengRobinson

class CycleSolver:
    def __init__(self, fluid_name, T_evap, T_cond, Q_evap):
        self.fluid_name = fluid_name
        self.T_evap = T_evap  # Evaporator temperature (°C)
        self.T_cond = T_cond  # Condenser temperature (°C)
        self.Q_evap = Q_evap  # Evaporator power (W)
        
        self.pr = PengRobinson(fluid_name)
        
    def solve(self):
        """Solve the 4-point refrigeration cycle"""
        
        # Point 1: Evaporator outlet (saturated vapor)
        P1 = self.get_saturation_pressure(self.T_evap)
        props1 = self.pr.calculate_properties(self.T_evap, P1)
        
        # Point 2: Compressor outlet (high pressure)
        P2 = self.get_saturation_pressure(self.T_cond)
        T2_isentropic = self.T_evap + (self.T_cond - self.T_evap) * 1.2
        props2 = self.pr.calculate_properties(T2_isentropic, P2)
        
        # Point 3: Condenser outlet (saturated liquid)
        props3 = self.pr.calculate_properties(self.T_cond, P2)
        
        # Point 4: Evaporator inlet (after expansion)
        props4 = self.pr.calculate_properties(self.T_evap, P1)
        
        # Calculate COP
        COP = self.calculate_cop(props1, props2, props3, props4)
        
        return {
            'point1': props1,
            'point2': props2,
            'point3': props3,
            'point4': props4,
            'COP': COP,
            'Q_evap': self.Q_evap,
            'W_comp': self.Q_evap / COP if COP > 0 else 0
        }
    
    def get_saturation_pressure(self, T):
        """Simplified saturation pressure (bar)"""
        return 1 + T * 0.1
    
    def calculate_cop(self, p1, p2, p3, p4):
        """Calculate Coefficient of Performance"""
        T1 = p1['T'] + 273.15
        T2 = p2['T'] + 273.15
        
        if T2 == T1:
            return 5.0
        
        COP = T1 / (T2 - T1)
        return max(COP, 1.0)