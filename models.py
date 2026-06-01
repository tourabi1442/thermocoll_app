from app import db
from datetime import datetime

class Simulation(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    fluid = db.Column(db.String(50), nullable=False)
    temp_evap = db.Column(db.Float, nullable=False)
    temp_cond = db.Column(db.Float, nullable=False)
    power = db.Column(db.Float, nullable=False)
    cop = db.Column(db.Float, nullable=False)
    w_comp = db.Column(db.Float, nullable=False)
    efficiency = db.Column(db.Float, nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    results = db.Column(db.Text)

    def __repr__(self):
        return f'<Simulation {self.id}: {self.fluid} COP={self.cop}>'

    def to_dict(self):
        return {
            'id': self.id,
            'fluid': self.fluid,
            'temp_evap': self.temp_evap,
            'temp_cond': self.temp_cond,
            'power': self.power,
            'cop': self.cop,
            'w_comp': self.w_comp,
            'efficiency': self.efficiency,
            'created_at': self.created_at.strftime('%Y-%m-%d %H:%M:%S')
        }