# ThermoСool — Amélioration de la page Climatisation

## Contexte du projet

Application Flask (Python) appelée **ThermoСool** — simulateur thermodynamique pour cycles vapeur-compression.  
Chemin du projet : `C:\python\thermocool_app`

Stack : Flask · SQLAlchemy (SQLite) · Jinja2 templates · CSS pur (`static/css/main.css`) · JS vanilla

---

## Objectif

Améliorer la page **`/climatisation`** pour qu'elle soit présentable devant un jury universitaire (PFE).  
Deux axes : **fonctionnel** (ajout du type de climatisation) et **visuel** (styling soigné).

---

## Fichiers à modifier

| Fichier | Rôle |
|---|---|
| `templates/climatisation.html` | Page principale à améliorer |
| `static/css/main.css` | Ajouter les styles manquants |
| `app.py` | Optionnel : sauvegarder les calculs climatisation en DB |

---

## 1. Ajouter « Type de Climatisation »

### Nouvelle carte à insérer dans `.clim-grid` (après la carte Pièce, avant Usage & Coût)

Ajouter un champ `<select id="typeClim">` avec les options suivantes. Chaque type influe sur le COP et la formule de puissance.

```html
<div class="clim-card clim-card--type">
    <div class="clim-card-title">❄️ Type de Climatisation</div>
    <div class="clim-field">
        <div class="clim-label">Type d'installation</div>
        <select class="clim-select" id="typeClim" onchange="updateTypeInfo()">
            <option value="split_mural">Split Mural (monosplit)</option>
            <option value="multi_split">Multi-Split</option>
            <option value="cassette">Cassette (plafond)</option>
            <option value="gainable">Gainable (conduit)</option>
            <option value="console">Console / Colonne</option>
            <option value="armoire">Armoire (précision)</option>
        </select>
    </div>
    <!-- Info dynamique selon le type choisi -->
    <div class="clim-type-info" id="typeInfo"></div>
</div>
```

### Données par type (à intégrer dans le JS)

```js
const TYPE_DATA = {
    split_mural: {
        label: "Split Mural",
        cop_factor: 1.0,        // facteur multiplicatif sur le COP calculé
        power_margin: 1.10,     // marge de puissance (+10%)
        icon: "🏠",
        desc: "Installation murale standard. Idéal pour pièces jusqu'à ~50 m². COP typique : 3.5–5.0.",
        fluides: ["R32", "R410A"],
        norm: "EN 14511"
    },
    multi_split: {
        label: "Multi-Split",
        cop_factor: 0.92,       // légère perte liée aux longueurs de circuit
        power_margin: 1.15,
        icon: "🏢",
        desc: "Un groupe extérieur, plusieurs unités intérieures. COP légèrement réduit par les pertes de charge.",
        fluides: ["R32", "R410A"],
        norm: "EN 14511"
    },
    cassette: {
        label: "Cassette Plafond",
        cop_factor: 0.95,
        power_margin: 1.12,
        icon: "⬜",
        desc: "Diffusion 4 sens encastrée au plafond. Convient aux espaces commerciaux (50–150 m²).",
        fluides: ["R32", "R410A", "R290"],
        norm: "EN 14511"
    },
    gainable: {
        label: "Gainable (conduit)",
        cop_factor: 0.88,
        power_margin: 1.20,
        icon: "📦",
        desc: "Distribution par réseau de gaines. Confort uniforme, esthétique discrète. Perte COP par friction.",
        fluides: ["R32", "R410A"],
        norm: "EN 14511"
    },
    console: {
        label: "Console / Colonne",
        cop_factor: 0.97,
        power_margin: 1.10,
        icon: "🗄️",
        desc: "Unité posée au sol ou en colonne. Simple à installer, sans travaux de maçonnerie.",
        fluides: ["R32", "R410A", "R290"],
        norm: "EN 14511"
    },
    armoire: {
        label: "Armoire de Précision",
        cop_factor: 0.85,
        power_margin: 1.25,
        icon: "🖥️",
        desc: "Refroidissement de précision (salles serveurs, laboratoires). Contrôle hygrométrique intégré.",
        fluides: ["R134a", "R32"],
        norm: "EN 14511 / ASHRAE"
    }
};
```

### Fonction `updateTypeInfo()` à ajouter

```js
function updateTypeInfo() {
    const type = document.getElementById('typeClim').value;
    const d = TYPE_DATA[type];
    document.getElementById('typeInfo').innerHTML = `
        <div class="type-badge">${d.icon} ${d.label}</div>
        <p class="type-desc">${d.desc}</p>
        <div class="type-meta">
            <span>Fluides recommandés : <strong>${d.fluides.join(', ')}</strong></span>
            <span>Norme : <strong>${d.norm}</strong></span>
        </div>
    `;
}
// Appeler au chargement
updateTypeInfo();
```

### Modifier `runClimatisation()` pour intégrer le type

Dans la fonction existante, récupérer le type et appliquer les facteurs :

```js
const typeClim = document.getElementById('typeClim').value;
const td = TYPE_DATA[typeClim];

// Appliquer la marge de puissance selon le type
const Qfinal = Qneed * td.power_margin;

// Appliquer le facteur COP selon le type  
const COPfinal = COP * td.cop_factor;

// Recalculer avec les valeurs corrigées
const Pelec = Qfinal / COPfinal;
const kwhMonth = (Pelec / 1000) * heures * jours;
const costMonth = kwhMonth * prix;

// Afficher la puissance corrigée
document.getElementById('crPower').textContent = Math.round(Qfinal) + ' W';
document.getElementById('crCOP').textContent   = COPfinal.toFixed(2);
```

### Ajouter une ligne de résultat : type d'installation recommandé

Ajouter dans `.clim-results-grid` un 5e carte :

```html
<div class="clim-res-card clim-res-card--wide">
    <div class="clim-res-val" id="crType" style="font-size:1rem;">—</div>
    <div class="clim-res-lbl">Type d'installation sélectionné</div>
</div>
```

Et dans le JS : `document.getElementById('crType').textContent = td.icon + ' ' + td.label;`

---

## 2. Sauvegarder les calculs climatisation (optionnel mais apprécié)

### Dans `app.py`

Ajouter un nouveau modèle `ClimatisationSim` ou simplement une nouvelle route API :

```python
@app.route('/api/climatisation', methods=['POST'])
@login_required
def save_climatisation():
    data = request.json
    # Sauvegarder dans la table Simulation avec sim_type='climatisation'
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
```

Appeler cette route à la fin de `runClimatisation()` en JS avec un `fetch('/api/climatisation', {...})`.

---

## 3. Améliorations de style

### Dans `static/css/main.css` — ajouter à la fin du fichier

```css
/* ===== CLIMATISATION PAGE ===== */

/* Grid 3 colonnes → 4 colonnes quand type ajouté */
.clim-grid {
    display: grid;
    grid-template-columns: repeat(auto-fit, minmax(240px, 1fr));
    gap: 16px;
    margin-bottom: 20px;
}

/* Carte type de climatisation */
.clim-card--type {
    border-top: 3px solid #2563eb;
}

.type-badge {
    display: inline-flex;
    align-items: center;
    gap: 6px;
    background: #eff6ff;
    color: #1d4ed8;
    border-radius: 8px;
    padding: 5px 12px;
    font-size: 0.82rem;
    font-weight: 600;
    margin: 8px 0 6px;
}

.type-desc {
    font-size: 0.8rem;
    color: #6b7280;
    line-height: 1.5;
    margin: 4px 0 8px;
}

.type-meta {
    display: flex;
    flex-direction: column;
    gap: 3px;
    font-size: 0.78rem;
    color: #374151;
    border-top: 1px solid #f3f4f6;
    padding-top: 8px;
    margin-top: 4px;
}

/* Carte résultat large (type d'installation) */
.clim-res-card--wide {
    grid-column: span 2;
    background: linear-gradient(135deg, #eff6ff 0%, #dbeafe 100%);
    border: 1px solid #bfdbfe;
}

/* Bouton simulation — style amélioré */
.btn-clim-run {
    display: block;
    width: 100%;
    margin-top: 16px;
    padding: 14px 28px;
    background: linear-gradient(135deg, #2563eb 0%, #1d4ed8 100%);
    color: white;
    border: none;
    border-radius: 12px;
    font-size: 1rem;
    font-weight: 700;
    letter-spacing: 0.3px;
    cursor: pointer;
    transition: transform 0.15s, box-shadow 0.15s;
    box-shadow: 0 4px 14px rgba(37, 99, 235, 0.35);
}

.btn-clim-run:hover {
    transform: translateY(-2px);
    box-shadow: 0 6px 20px rgba(37, 99, 235, 0.45);
}

.btn-clim-run:active {
    transform: translateY(0);
}

/* Priority buttons — améliorer le selected state */
.priority-btn {
    flex: 1;
    min-width: 130px;
    padding: 10px 14px;
    border: 2px solid #e5e7eb;
    border-radius: 10px;
    background: white;
    cursor: pointer;
    font-size: 0.82rem;
    font-weight: 600;
    color: #374151;
    transition: all 0.2s;
    display: flex;
    flex-direction: column;
    align-items: center;
    gap: 2px;
    text-align: center;
}

.priority-btn.selected {
    border-color: #2563eb;
    background: #eff6ff;
    color: #1d4ed8;
    box-shadow: 0 0 0 3px rgba(37,99,235,0.12);
}

.priority-btn:hover:not(.selected) {
    border-color: #93c5fd;
    background: #f8faff;
}

/* Résultats cards — animation d'entrée */
.clim-results {
    display: none;
    animation: slideUp 0.4s ease;
}

.clim-results.visible {
    display: block;
}

@keyframes slideUp {
    from { opacity: 0; transform: translateY(20px); }
    to   { opacity: 1; transform: translateY(0); }
}

/* Valeurs numériques résultats */
.clim-res-val {
    font-size: 1.75rem;
    font-weight: 800;
    color: #1d4ed8;
    letter-spacing: -0.5px;
}

.clim-res-lbl {
    font-size: 0.75rem;
    color: #6b7280;
    margin-top: 2px;
    font-weight: 500;
}

/* Recommendation block */
.clim-rec {
    background: #f0fdf4;
    border: 1px solid #bbf7d0;
    border-radius: 12px;
    padding: 14px 18px;
}

.clim-rec-title {
    font-weight: 700;
    color: #15803d;
    font-size: 0.88rem;
    margin-bottom: 6px;
}

.clim-rec-text {
    color: #374151;
    font-size: 0.85rem;
    line-height: 1.6;
}

/* Responsive */
@media (max-width: 768px) {
    .clim-grid { grid-template-columns: 1fr; }
    .priority-row { flex-wrap: wrap; gap: 8px; }
    .priority-btn { min-width: calc(50% - 4px); }
    .clim-res-card--wide { grid-column: span 1; }
}
```

### Amélioration du header de la page

Remplacer le header actuel par une version plus impactante :

```html
<div class="clim-header">
    <div class="clim-header-badge">❄️ Module Climatisation</div>
    <h1 class="clim-title">Simulation & Dimensionnement</h1>
    <p class="clim-sub">Estimez la puissance nécessaire, choisissez le type d'installation adapté et optimisez votre consommation énergétique.</p>
</div>
```

Et le CSS correspondant :

```css
.clim-header {
    text-align: center;
    margin-bottom: 28px;
    padding: 32px 20px;
    background: linear-gradient(135deg, #eff6ff 0%, #dbeafe 100%);
    border-radius: 16px;
    border: 1px solid #bfdbfe;
}

.clim-header-badge {
    display: inline-block;
    background: #2563eb;
    color: white;
    border-radius: 20px;
    padding: 4px 16px;
    font-size: 0.78rem;
    font-weight: 600;
    letter-spacing: 0.5px;
    margin-bottom: 10px;
    text-transform: uppercase;
}

.clim-title {
    font-size: 1.8rem;
    font-weight: 800;
    color: #111827;
    letter-spacing: -0.5px;
    margin-bottom: 8px;
}

.clim-sub {
    color: #4b5563;
    font-size: 0.9rem;
    max-width: 540px;
    margin: 0 auto;
    line-height: 1.6;
}
```

---

## Ordre d'exécution recommandé

1. **`static/css/main.css`** — ajouter tous les styles CSS en fin de fichier
2. **`templates/climatisation.html`** — restructurer le HTML :
   - Nouveau header
   - Ajouter la carte "Type de Climatisation" dans `.clim-grid`
   - Ajouter la carte résultat wide dans `.clim-results-grid`
   - Mettre à jour le JS (`TYPE_DATA`, `updateTypeInfo`, modifier `runClimatisation`)
3. **`app.py`** — ajouter la route `/api/climatisation` (POST)
4. Tester : `python app.py` et naviguer vers `/climatisation`

---

## Notes importantes

- Ne pas casser les routes existantes ni les autres templates
- Garder la compatibilité avec `base.html` (blocs `{% block content %}` et `{% block extra_js %}`)
- La DB SQLite est dans `thermocool.db` — pas besoin de migration si on réutilise la table `Simulation` existante avec `sim_type='climatisation'`
- Tout le JS est en vanilla (pas de framework) — garder la même approche
