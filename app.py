from flask import Flask, render_template, request, jsonify, redirect, url_for, session
from flask_sqlalchemy import SQLAlchemy
from flask_cors import CORS
from werkzeug.security import generate_password_hash, check_password_hash
from physics.cycle_solver import CycleSolver
from physics.fluids import all_fluids
import json
from datetime import datetime
from functools import wraps

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///thermocool.db'
app.config['SECRET_KEY'] = 'thermocool-secret-key-2024-production'

db = SQLAlchemy(app)
CORS(app)

# ==================== MODELS ====================

class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password = db.Column(db.String(255), nullable=False)
    full_name = db.Column(db.String(120))
    is_admin = db.Column(db.Boolean, default=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    simulations = db.relationship('Simulation', backref='user', lazy=True, cascade='all, delete-orphan')

    def set_password(self, password):
        self.password = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password, password)


class Simulation(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    sim_type = db.Column(db.String(20), default='thermocool')
    fluid = db.Column(db.String(50), nullable=False)
    temp_evap = db.Column(db.Float, nullable=False)
    temp_cond = db.Column(db.Float, nullable=False)
    power = db.Column(db.Float, nullable=False)
    cop = db.Column(db.Float, nullable=False)
    w_comp = db.Column(db.Float, nullable=False)
    efficiency = db.Column(db.Float, nullable=False)
    model_type = db.Column(db.String(50), default='Peng-Robinson')
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    results = db.Column(db.Text)

# ==================== AUTH ====================

def login_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'user_id' not in session:
            return redirect(url_for('login'))
        return f(*args, **kwargs)
    return decorated_function


def admin_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'user_id' not in session:
            return redirect(url_for('login'))
        if not session.get('is_admin'):
            return redirect(url_for('dashboard'))
        return f(*args, **kwargs)
    return decorated_function

# ==================== ROUTES ====================

@app.route('/')
def index():
    if 'user_id' not in session:
        return redirect(url_for('login'))
    return redirect(url_for('dashboard'))


@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        data = request.get_json()
        user = User.query.filter_by(username=data['username']).first()
        if user and user.check_password(data['password']):
            session['user_id'] = user.id
            session['username'] = user.username
            session['is_admin'] = user.is_admin
            return jsonify({'status': 'success'}), 200
        return jsonify({'status': 'error', 'message': 'Identifiants invalides'}), 401
    return render_template('login.html')


@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        data = request.get_json()
        if User.query.filter_by(username=data['username']).first():
            return jsonify({'status': 'error', 'message': "Nom d'utilisateur déjà utilisé"}), 400
        if User.query.filter_by(email=data['email']).first():
            return jsonify({'status': 'error', 'message': 'Email déjà utilisé'}), 400
        user = User(
            username=data['username'],
            email=data['email'],
            full_name=data.get('full_name', '')
        )
        user.set_password(data['password'])
        db.session.add(user)
        db.session.commit()
        return jsonify({'status': 'success'}), 201
    return render_template('register.html')


@app.route('/logout')
def logout():
    session.clear()
    return redirect(url_for('login'))


@app.route('/dashboard')
@login_required
def dashboard():
    return render_template('dashboard.html')


@app.route('/simulator')
@login_required
def simulator():
    return render_template('simulator.html')


@app.route('/learn')
@login_required
def learn():
    return render_template('learn.html')


@app.route('/climatisation')
@login_required
def climatisation():
    return render_template('climatisation.html')


@app.route('/results')
@login_required
def results():
    return render_template('results.html')


@app.route('/admin')
@admin_required
def admin():
    return render_template('admin.html')

# ==================== API ====================

def rounded_points(point):
    return {
        k: round(v, 2) if isinstance(v, float) else v
        for k, v in point.items()
    }


def serialize_cycle_result(res):
    return {
        'COP': round(res['COP'], 2),
        'COP_carnot': round(res['COP_carnot'], 2),
        'practical_factor': round(res['practical_factor'] * 100, 1),
        'W_comp': round(res['W_comp'], 2),
        'Q_evap': round(res['Q_evap'], 2),
        'Q_cond': round(res['Q_cond'], 2),
        'pressure_ratio': round(res['pressure_ratio'], 2),
        'temperature_lift': round(res['temperature_lift'], 1),
        'compressor_efficiency': round(res['compressor_efficiency'] * 100, 1),
        'monthly_kwh_index': round(res['monthly_kwh_index'], 1),
        'fluid_meta': res['fluid_meta'],
        'recommendation': res['recommendation'],
        'point1': rounded_points(res['point1']),
        'point2': rounded_points(res['point2']),
        'point3': rounded_points(res['point3']),
        'point4': rounded_points(res['point4']),
    }

@app.route('/api/calculate', methods=['POST'])
@login_required
def calculate():
    try:
        data = request.json
        user_id = session.get('user_id')

        solver = CycleSolver(
            fluid_name=data.get('refrigerant', 'R32'),
            T_evap=data.get('temp_evap', 5),
            T_cond=data.get('temp_cond', 45),
            Q_evap=data.get('power', 7800)
        )
        res = solver.solve()

        sim = Simulation(
            user_id=user_id,
            fluid=data.get('refrigerant', 'R32'),
            temp_evap=data.get('temp_evap', 5),
            temp_cond=data.get('temp_cond', 45),
            power=data.get('power', 7800),
            cop=res['COP'],
            w_comp=res['W_comp'],
            efficiency=min(res['COP'] / 6.0 * 100, 100),
            model_type=data.get('model_type', 'Peng-Robinson'),
            results=json.dumps(res)
        )
        db.session.add(sim)
        db.session.commit()

        payload = serialize_cycle_result(res)
        payload.update({
            'status': 'success',
            'simulation_id': sim.id,
            'efficiency': round(min(res['COP'] / 6.0 * 100, 100), 1),
        })
        return jsonify(payload)
    except Exception as e:
        return jsonify({'status': 'error', 'message': str(e)}), 400


@app.route('/api/compare', methods=['POST'])
@login_required
def compare_refrigerants():
    try:
        data = request.json or {}
        rows = []
        for fluid in all_fluids().keys():
            solver = CycleSolver(
                fluid_name=fluid,
                T_evap=data.get('temp_evap', 5),
                T_cond=data.get('temp_cond', 45),
                Q_evap=data.get('power', 7800)
            )
            res = solver.solve()
            meta = res['fluid_meta']
            score = (res['COP'] * 18) + (meta['eco_score'] * 0.35) - (res['pressure_ratio'] * 2.5)
            rows.append({
                'fluid': fluid,
                'name': meta['name'],
                'family': meta['family'],
                'cop': round(res['COP'], 2),
                'w_comp': round(res['W_comp'], 0),
                'pressure_ratio': round(res['pressure_ratio'], 2),
                'gwp': meta['gwp'],
                'safety': meta['safety'],
                'eco_score': meta['eco_score'],
                'score': round(score, 1),
                'recommendation': res['recommendation']
            })
        rows.sort(key=lambda item: item['score'], reverse=True)
        return jsonify({'status': 'success', 'rows': rows})
    except Exception as e:
        return jsonify({'status': 'error', 'message': str(e)}), 400


@app.route('/api/simulations', methods=['GET'])
@login_required
def get_simulations():
    user_id = session.get('user_id')
    sims = Simulation.query.filter_by(user_id=user_id).order_by(Simulation.created_at.desc()).limit(50).all()
    return jsonify([{
        'id': s.id,
        'fluid': s.fluid,
        'cop': round(s.cop, 2),
        'efficiency': round(s.efficiency, 1),
        'temp_evap': s.temp_evap,
        'temp_cond': s.temp_cond,
        'power': s.power,
        'w_comp': round(s.w_comp, 2),
        'model_type': s.model_type,
        'created_at': s.created_at.strftime('%d/%m/%Y %H:%M')
    } for s in sims])


@app.route('/api/simulation/<int:sim_id>', methods=['GET'])
@login_required
def get_simulation(sim_id):
    sim = Simulation.query.get_or_404(sim_id)
    if sim.user_id != session.get('user_id') and not session.get('is_admin'):
        return jsonify({'status': 'error'}), 403
    return jsonify({
        'id': sim.id,
        'fluid': sim.fluid,
        'cop': round(sim.cop, 2),
        'efficiency': round(sim.efficiency, 1),
        'temp_evap': sim.temp_evap,
        'temp_cond': sim.temp_cond,
        'power': sim.power,
        'w_comp': round(sim.w_comp, 2),
        'model_type': sim.model_type,
        'results': json.loads(sim.results) if sim.results else {},
        'created_at': sim.created_at.strftime('%d/%m/%Y %H:%M')
    })


@app.route('/api/simulation/<int:sim_id>', methods=['DELETE'])
@login_required
def delete_simulation(sim_id):
    sim = Simulation.query.get_or_404(sim_id)
    if sim.user_id != session.get('user_id') and not session.get('is_admin'):
        return jsonify({'status': 'error'}), 403
    db.session.delete(sim)
    db.session.commit()
    return jsonify({'status': 'success'})


@app.route('/api/user', methods=['GET'])
@login_required
def get_user_info():
    user = User.query.get(session.get('user_id'))
    return jsonify({
        'id': user.id,
        'username': user.username,
        'email': user.email,
        'full_name': user.full_name,
        'is_admin': user.is_admin,
        'simulations_count': len(user.simulations)
    })


@app.route('/api/users', methods=['GET'])
@admin_required
def get_users():
    users = User.query.order_by(User.created_at.desc()).all()
    return jsonify([{
        'id': u.id,
        'username': u.username,
        'email': u.email,
        'full_name': u.full_name,
        'is_admin': u.is_admin,
        'simulations_count': len(u.simulations),
        'created_at': u.created_at.strftime('%d/%m/%Y %H:%M')
    } for u in users])


@app.route('/api/users/<int:user_id>/toggle-admin', methods=['POST'])
@admin_required
def toggle_admin(user_id):
    user = User.query.get_or_404(user_id)
    if user.id == session.get('user_id'):
        return jsonify({'status': 'error', 'message': 'Cannot modify yourself'}), 400
    user.is_admin = not user.is_admin
    db.session.commit()
    return jsonify({'status': 'success', 'is_admin': user.is_admin})


@app.route('/api/users/<int:user_id>', methods=['DELETE'])
@admin_required
def delete_user(user_id):
    if user_id == session.get('user_id'):
        return jsonify({'status': 'error', 'message': 'Cannot delete yourself'}), 400
    user = User.query.get_or_404(user_id)
    db.session.delete(user)
    db.session.commit()
    return jsonify({'status': 'success'})


@app.route('/api/climatisation', methods=['POST'])
@login_required
def save_climatisation():
    data = request.json
    sim = Simulation(
        user_id=session.get('user_id'),
        sim_type='climatisation',
        fluid=data.get('type_clim', 'split_mural'),
        temp_evap=data.get('t_int', 24),
        temp_cond=data.get('t_ext', 38),
        power=data.get('power', 0),
        cop=data.get('cop', 0),
        w_comp=data.get('pelec', 0),
        efficiency=round(min(data.get('cop', 0) / 6.0 * 100, 100), 1),
        model_type='Climatisation-' + data.get('type_clim', 'split'),
        results=json.dumps(data)
    )
    db.session.add(sim)
    db.session.commit()
    return jsonify({'status': 'success', 'id': sim.id})


@app.route('/api/stats', methods=['GET'])
@admin_required
def get_stats():
    return jsonify({
        'total_users': User.query.count(),
        'total_simulations': Simulation.query.count(),
        'recent_simulations': Simulation.query.order_by(Simulation.created_at.desc()).limit(5).count()
    })


if __name__ == '__main__':
    with app.app_context():
        db.create_all()
    app.run(debug=True)
