from .fluids import get_fluid
from .peng_robinson import PengRobinson


class CycleSolver:
    """Educational vapor-compression cycle solver.

    The project does not use a full refrigerant property library, so these
    calculations remain simplified. The outputs are structured to support a
    credible engineering comparison: temperature lift, pressure ratio, Carnot
    reference, practical COP, compressor power, and environmental metadata.
    """

    def __init__(self, fluid_name, T_evap, T_cond, Q_evap):
        self.fluid_name = fluid_name
        self.T_evap = float(T_evap)
        self.T_cond = float(T_cond)
        self.Q_evap = float(Q_evap)
        self.fluid = get_fluid(fluid_name)

        if not self.fluid:
            raise ValueError(f"Fluide inconnu: {fluid_name}")
        if self.T_cond <= self.T_evap + 3:
            raise ValueError("La temperature du condenseur doit etre au moins 3 C au-dessus de l'evaporateur.")
        if self.Q_evap <= 0:
            raise ValueError("La puissance frigorifique doit etre positive.")

        self.pr = PengRobinson(fluid_name)

    def solve(self):
        P1 = self.get_saturation_pressure(self.T_evap)
        P2 = self.get_saturation_pressure(self.T_cond)
        pressure_ratio = P2 / P1 if P1 > 0 else 0
        lift = self.T_cond - self.T_evap
        eta_comp = self.estimate_compressor_efficiency(pressure_ratio, lift)

        props1 = self.with_state(
            self.pr.calculate_properties(self.T_evap + 5, P1),
            "Vapeur basse pression",
            self.estimate_enthalpy(self.T_evap + 5, vapor=True),
        )

        T2 = self.T_evap + lift / max(eta_comp, 0.45)
        props2 = self.with_state(
            self.pr.calculate_properties(T2, P2),
            "Vapeur haute pression",
            self.estimate_enthalpy(T2, vapor=True),
        )

        props3 = self.with_state(
            self.pr.calculate_properties(self.T_cond - 3, P2),
            "Liquide haute pression",
            self.estimate_enthalpy(self.T_cond - 3, vapor=False),
        )

        props4 = self.with_state(
            self.pr.calculate_properties(self.T_evap, P1),
            "Melange liquide-vapeur",
            props3["h"],
        )

        carnot_cop = self.calculate_carnot_cop()
        practical_factor = self.estimate_practical_factor(eta_comp, pressure_ratio)
        cop = max(1.0, carnot_cop * practical_factor)
        w_comp = self.Q_evap / cop
        q_cond = self.Q_evap + w_comp
        seasonal_cost_index = w_comp / 1000 * 8 * 30

        return {
            "point1": props1,
            "point2": props2,
            "point3": props3,
            "point4": props4,
            "COP": cop,
            "COP_carnot": carnot_cop,
            "practical_factor": practical_factor,
            "Q_evap": self.Q_evap,
            "Q_cond": q_cond,
            "W_comp": w_comp,
            "pressure_ratio": pressure_ratio,
            "temperature_lift": lift,
            "compressor_efficiency": eta_comp,
            "monthly_kwh_index": seasonal_cost_index,
            "fluid_meta": {
                "name": self.fluid["name"],
                "family": self.fluid["family"],
                "gwp": self.fluid["gwp"],
                "safety": self.fluid["safety"],
                "eco_score": self.fluid["eco_score"],
                "use_case": self.fluid["use_case"],
            },
            "recommendation": self.recommendation(cop, pressure_ratio),
        }

    def with_state(self, props, state, h):
        props["state"] = state
        props["h"] = h
        return props

    def get_saturation_pressure(self, T):
        tc = self.fluid["Tc"]
        pc_bar = self.fluid["Pc"] * 10
        reduced = max(0.08, min(0.98, (T + 273.15) / (tc + 273.15)))
        return max(0.35, pc_bar * reduced ** 4.2)

    def estimate_enthalpy(self, T, vapor):
        base = 180 if vapor else 70
        heat_capacity = 1.05 if vapor else 0.72
        fluid_shift = (self.fluid["M"] - 50) * 0.18
        return base + heat_capacity * (T + 40) + fluid_shift

    def calculate_carnot_cop(self):
        cold_k = self.T_evap + 273.15
        hot_k = self.T_cond + 273.15
        return cold_k / (hot_k - cold_k)

    def estimate_compressor_efficiency(self, pressure_ratio, lift):
        ratio_penalty = min(0.18, max(0, pressure_ratio - 2.5) * 0.025)
        lift_penalty = min(0.12, max(0, lift - 35) * 0.004)
        return max(0.58, min(0.82, 0.78 - ratio_penalty - lift_penalty))

    def estimate_practical_factor(self, eta_comp, pressure_ratio):
        eos_factor = 0.52
        pressure_penalty = max(0, pressure_ratio - 3) * 0.018
        return max(0.32, min(0.62, eos_factor * eta_comp - pressure_penalty + 0.18))

    def recommendation(self, cop, pressure_ratio):
        if cop >= 4 and self.fluid["eco_score"] >= 80:
            return "Excellent choix: rendement eleve et impact environnemental faible."
        if pressure_ratio > 5:
            return "Attention: rapport de pression eleve. Reduire l'ecart de temperature ameliorerait le COP."
        if self.fluid["gwp"] > 1000:
            return "Performance correcte, mais GWP eleve. Comparer avec R32, R290 ou R744."
        return "Configuration acceptable. Optimiser le pincement thermique peut encore ameliorer la performance."
