from flask import Flask, render_template, request, redirect, url_for, session, jsonify
from flask_sqlalchemy import SQLAlchemy
from werkzeug.security import generate_password_hash, check_password_hash
from datetime import datetime, date
from functools import wraps

app = Flask(__name__)
app.secret_key = 'myeyes-secret-2024'
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///myeyes.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)

class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    password = db.Column(db.String(200), nullable=False)
    nom = db.Column(db.String(100))
    role = db.Column(db.String(20), default='opticien')

class Patient(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    nom = db.Column(db.String(100), nullable=False)
    prenom = db.Column(db.String(100), nullable=False)
    date_naissance = db.Column(db.String(20))
    telephone = db.Column(db.String(20))
    email = db.Column(db.String(120))
    adresse = db.Column(db.String(200))
    date_creation = db.Column(db.DateTime, default=datetime.utcnow)
    consultations = db.relationship('Consultation', backref='patient', lazy=True)
    commandes = db.relationship('Commande', backref='patient', lazy=True)

class Consultation(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    patient_id = db.Column(db.Integer, db.ForeignKey('patient.id'), nullable=False)
    date = db.Column(db.DateTime, default=datetime.utcnow)
    od_sphere = db.Column(db.Float)
    od_cylindre = db.Column(db.Float)
    od_axe = db.Column(db.Integer)
    og_sphere = db.Column(db.Float)
    og_cylindre = db.Column(db.Float)
    og_axe = db.Column(db.Integer)
    ecart_pupillaire = db.Column(db.Float)
    notes = db.Column(db.Text)
    opticien = db.Column(db.String(100))

class Commande(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    patient_id = db.Column(db.Integer, db.ForeignKey('patient.id'), nullable=False)
    date_commande = db.Column(db.DateTime, default=datetime.utcnow)
    type_monture = db.Column(db.String(100))
    marque_monture = db.Column(db.String(100))
    type_verre = db.Column(db.String(100))
    traitement = db.Column(db.String(100))
    montant_total = db.Column(db.Float)
    acompte = db.Column(db.Float, default=0)
    statut = db.Column(db.String(30), default='En cours')
    date_livraison = db.Column(db.String(20))

class Stock(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    reference = db.Column(db.String(50), unique=True)
    designation = db.Column(db.String(200))
    categorie = db.Column(db.String(50))
    marque = db.Column(db.String(100))
    quantite = db.Column(db.Integer, default=0)
    prix_achat = db.Column(db.Float)
    prix_vente = db.Column(db.Float)
    seuil_alerte = db.Column(db.Integer, default=5)

class RendezVous(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    patient_id = db.Column(db.Integer, db.ForeignKey('patient.id'), nullable=False)
    date_heure = db.Column(db.DateTime, nullable=False)
    motif = db.Column(db.String(200))
    statut = db.Column(db.String(30), default='Planifie')
    patient_rel = db.relationship('Patient', backref='rendez_vous')

def login_required(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        if 'user_id' not in session:
            return redirect(url_for('login'))
        return f(*args, **kwargs)
    return decorated

@app.route('/')
def index():
    if 'user_id' not in session:
        return redirect(url_for('login'))
    return redirect(url_for('dashboard'))

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        data = request.get_json()
        user = User.query.filter_by(username=data.get('username')).first()
        if user and check_password_hash(user.password, data.get('password')):
            session['user_id'] = user.id
            session['user_nom'] = user.nom
            session['user_role'] = user.role
            return jsonify({'success': True})
        return jsonify({'success': False, 'message': 'Identifiants incorrects'})
    return render_template('login.html')

@app.route('/logout')
def logout():
    session.clear()
    return redirect(url_for('login'))

@app.route('/dashboard')
@login_required
def dashboard():
    return render_template('app.html', page='dashboard')

@app.route('/patients')
@login_required
def patients():
    return render_template('app.html', page='patients')

@app.route('/consultations')
@login_required
def consultations():
    return render_template('app.html', page='consultations')

@app.route('/commandes')
@login_required
def commandes():
    return render_template('app.html', page='commandes')

@app.route('/stock')
@login_required
def stock():
    return render_template('app.html', page='stock')

@app.route('/agenda')
@login_required
def agenda():
    return render_template('app.html', page='agenda')

@app.route('/api/stats')
@login_required
def api_stats():
    total_patients = Patient.query.count()
    commandes_en_cours = Commande.query.filter_by(statut='En cours').count()
    stock_alerte = Stock.query.filter(Stock.quantite <= Stock.seuil_alerte).count()
    ca = db.session.query(db.func.sum(Commande.montant_total)).scalar() or 0
    return jsonify({'total_patients': total_patients, 'commandes_en_cours': commandes_en_cours,
                    'stock_alerte': stock_alerte, 'ca_total': ca})

@app.route('/api/patients', methods=['GET', 'POST'])
@login_required
def api_patients():
    if request.method == 'GET':
        q = request.args.get('q', '')
        query = Patient.query
        if q:
            query = query.filter(db.or_(Patient.nom.ilike(f'%{q}%'), Patient.prenom.ilike(f'%{q}%')))
        ps = query.order_by(Patient.date_creation.desc()).all()
        return jsonify([{'id': p.id, 'nom': p.nom, 'prenom': p.prenom, 'telephone': p.telephone,
                         'email': p.email, 'date_naissance': p.date_naissance, 'adresse': p.adresse,
                         'date_creation': p.date_creation.strftime('%d/%m/%Y'),
                         'nb_consultations': len(p.consultations), 'nb_commandes': len(p.commandes)} for p in ps])
    data = request.get_json()
    p = Patient(nom=data['nom'], prenom=data['prenom'], telephone=data.get('telephone'),
                email=data.get('email'), adresse=data.get('adresse'), date_naissance=data.get('date_naissance'))
    db.session.add(p)
    db.session.commit()
    return jsonify({'success': True, 'id': p.id})

@app.route('/api/patients/<int:pid>', methods=['PUT', 'DELETE'])
@login_required
def api_patient(pid):
    p = Patient.query.get_or_404(pid)
    if request.method == 'DELETE':
        db.session.delete(p)
        db.session.commit()
        return jsonify({'success': True})
    data = request.get_json()
    for k, v in data.items():
        setattr(p, k, v)
    db.session.commit()
    return jsonify({'success': True})

@app.route('/api/consultations', methods=['GET', 'POST'])
@login_required
def api_consultations():
    if request.method == 'GET':
        pid = request.args.get('patient_id')
        query = Consultation.query
        if pid:
            query = query.filter_by(patient_id=pid)
        cs = query.order_by(Consultation.date.desc()).all()
        result = []
        for c in cs:
            p = Patient.query.get(c.patient_id)
            result.append({'id': c.id, 'patient_id': c.patient_id,
                           'patient_nom': f"{p.nom} {p.prenom}" if p else '',
                           'date': c.date.strftime('%d/%m/%Y %H:%M'),
                           'od_sphere': c.od_sphere, 'od_cylindre': c.od_cylindre, 'od_axe': c.od_axe,
                           'og_sphere': c.og_sphere, 'og_cylindre': c.og_cylindre, 'og_axe': c.og_axe,
                           'ecart_pupillaire': c.ecart_pupillaire, 'notes': c.notes, 'opticien': c.opticien})
        return jsonify(result)
    data = request.get_json()
    c = Consultation(patient_id=data['patient_id'], od_sphere=data.get('od_sphere'),
                     od_cylindre=data.get('od_cylindre'), od_axe=data.get('od_axe'),
                     og_sphere=data.get('og_sphere'), og_cylindre=data.get('og_cylindre'),
                     og_axe=data.get('og_axe'), ecart_pupillaire=data.get('ecart_pupillaire'),
                     notes=data.get('notes'), opticien=session.get('user_nom', ''))
    db.session.add(c)
    db.session.commit()
    return jsonify({'success': True})

@app.route('/api/commandes', methods=['GET', 'POST'])
@login_required
def api_commandes():
    if request.method == 'GET':
        cs = Commande.query.order_by(Commande.date_commande.desc()).all()
        result = []
        for c in cs:
            p = Patient.query.get(c.patient_id)
            result.append({'id': c.id, 'patient_id': c.patient_id,
                           'patient_nom': f"{p.nom} {p.prenom}" if p else '',
                           'date_commande': c.date_commande.strftime('%d/%m/%Y'),
                           'type_monture': c.type_monture, 'marque_monture': c.marque_monture,
                           'type_verre': c.type_verre, 'traitement': c.traitement,
                           'montant_total': c.montant_total, 'acompte': c.acompte,
                           'statut': c.statut, 'date_livraison': c.date_livraison,
                           'reste': (c.montant_total or 0) - (c.acompte or 0)})
        return jsonify(result)
    data = request.get_json()
    c = Commande(patient_id=data['patient_id'], type_monture=data.get('type_monture'),
                 marque_monture=data.get('marque_monture'), type_verre=data.get('type_verre'),
                 traitement=data.get('traitement'), montant_total=data.get('montant_total'),
                 acompte=data.get('acompte', 0), statut=data.get('statut', 'En cours'),
                 date_livraison=data.get('date_livraison'))
    db.session.add(c)
    db.session.commit()
    return jsonify({'success': True})

@app.route('/api/commandes/<int:cid>', methods=['PUT'])
@login_required
def api_commande(cid):
    c = Commande.query.get_or_404(cid)
    data = request.get_json()
    for k, v in data.items():
        setattr(c, k, v)
    db.session.commit()
    return jsonify({'success': True})

@app.route('/api/stock', methods=['GET', 'POST'])
@login_required
def api_stock():
    if request.method == 'GET':
        items = Stock.query.order_by(Stock.categorie, Stock.designation).all()
        return jsonify([{'id': s.id, 'reference': s.reference, 'designation': s.designation,
                         'categorie': s.categorie, 'marque': s.marque, 'quantite': s.quantite,
                         'prix_achat': s.prix_achat, 'prix_vente': s.prix_vente,
                         'seuil_alerte': s.seuil_alerte, 'alerte': s.quantite <= s.seuil_alerte} for s in items])
    data = request.get_json()
    s = Stock(**data)
    db.session.add(s)
    db.session.commit()
    return jsonify({'success': True})

@app.route('/api/stock/<int:sid>', methods=['PUT', 'DELETE'])
@login_required
def api_stock_item(sid):
    s = Stock.query.get_or_404(sid)
    if request.method == 'DELETE':
        db.session.delete(s)
        db.session.commit()
        return jsonify({'success': True})
    data = request.get_json()
    for k, v in data.items():
        setattr(s, k, v)
    db.session.commit()
    return jsonify({'success': True})

@app.route('/api/agenda', methods=['GET', 'POST'])
@login_required
def api_agenda():
    if request.method == 'GET':
        rdvs = RendezVous.query.order_by(RendezVous.date_heure).all()
        return jsonify([{'id': r.id, 'patient_id': r.patient_id,
                         'patient_nom': f"{r.patient_rel.nom} {r.patient_rel.prenom}",
                         'date_heure': r.date_heure.strftime('%Y-%m-%dT%H:%M'),
                         'motif': r.motif, 'statut': r.statut} for r in rdvs])
    data = request.get_json()
    r = RendezVous(patient_id=data['patient_id'],
                   date_heure=datetime.strptime(data['date_heure'], '%Y-%m-%dT%H:%M'),
                   motif=data.get('motif'), statut='Planifie')
    db.session.add(r)
    db.session.commit()
    return jsonify({'success': True})

@app.route('/api/patients_list')
@login_required
def api_patients_list():
    ps = Patient.query.order_by(Patient.nom).all()
    return jsonify([{'id': p.id, 'nom': f"{p.nom} {p.prenom}"} for p in ps])

def init_db():
    with app.app_context():
        db.create_all()
        if not User.query.filter_by(username='admin').first():
            db.session.add(User(username='admin', password=generate_password_hash('admin123'), nom='Dr. Martin', role='admin'))
        if not Patient.query.first():
            ps = [
                Patient(nom='Mbarga', prenom='Jean-Paul', telephone='699001122', email='jp.mbarga@gmail.com', date_naissance='1985-03-15', adresse='Bastos, Yaounde'),
                Patient(nom='Atangana', prenom='Marie', telephone='677334455', email='marie.a@yahoo.fr', date_naissance='1992-07-22', adresse='Mvan, Yaounde'),
                Patient(nom='Nkolo', prenom='Eric', telephone='655667788', email='eric.nkolo@gmail.com', date_naissance='1978-11-08', adresse='Ekie, Yaounde'),
                Patient(nom='Fouda', prenom='Sylvie', telephone='698112233', email='sylvie.f@gmail.com', date_naissance='2001-04-30', adresse='Nlongkak, Yaounde'),
            ]
            for p in ps: db.session.add(p)
            db.session.flush()
            db.session.add(Consultation(patient_id=1, od_sphere=-2.5, od_cylindre=-0.75, od_axe=180, og_sphere=-3.0, og_cylindre=-1.0, og_axe=175, ecart_pupillaire=64, notes='Vision de loin reduite', opticien='Dr. Martin'))
            db.session.add(Consultation(patient_id=2, od_sphere=1.5, og_sphere=1.75, ecart_pupillaire=62, notes='Hypermetropie legere', opticien='Dr. Martin'))
            db.session.add(Commande(patient_id=1, type_monture='Acetate', marque_monture='Ray-Ban', type_verre='Progressif', traitement='Anti-reflet', montant_total=185000, acompte=90000, statut='En cours', date_livraison='2024-02-15'))
            db.session.add(Commande(patient_id=2, type_monture='Metal', marque_monture='Silhouette', type_verre='Unifocal', traitement='Anti-reflet', montant_total=120000, acompte=120000, statut='Livre', date_livraison='2024-01-20'))
            stocks = [
                Stock(reference='MON-001', designation='Monture Acetate Premium', categorie='Monture', marque='Ray-Ban', quantite=12, prix_achat=25000, prix_vente=55000, seuil_alerte=5),
                Stock(reference='MON-002', designation='Monture Metal Fine', categorie='Monture', marque='Silhouette', quantite=3, prix_achat=35000, prix_vente=75000, seuil_alerte=5),
                Stock(reference='VER-001', designation='Verre Progressif Ind. 1.67', categorie='Verre', marque='Essilor', quantite=20, prix_achat=30000, prix_vente=65000, seuil_alerte=8),
                Stock(reference='VER-002', designation='Verre Unifocal Ind. 1.5', categorie='Verre', marque='Hoya', quantite=45, prix_achat=8000, prix_vente=18000, seuil_alerte=10),
                Stock(reference='SOL-001', designation='Solution nettoyante 100ml', categorie='Accessoire', marque='Zeiss', quantite=4, prix_achat=2500, prix_vente=6000, seuil_alerte=10),
            ]
            for s in stocks: db.session.add(s)
            db.session.add(RendezVous(patient_id=3, date_heure=datetime(2024, 2, 12, 10, 0), motif='Controle annuel', statut='Planifie'))
        db.session.commit()

if __name__ == '__main__':
    init_db()
    app.run(debug=True, port=5000)
