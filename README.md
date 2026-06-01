# 🧊 ThermoCool Simulator

**Simulation Thermodynamique Interactive - Cycle Vapeur-Compression**

Une application web professionnelle pour simuler et analyser les cycles de réfrigération vapeur-compression avec visualisation P-h en temps réel.

---

## ✨ Caractéristiques

- 🔄 **Simulation du cycle thermodynamique complet** (Compression → Condensation → Détente → Évaporation)
- 📈 **Diagramme P-h interactif** avec Chart.js
- 🧪 **6 réfrigérants disponibles** (R32, R410A, R290, R744, R134a, NH₃)
- 📊 **Calculs précis** utilisant l'équation de Peng-Robinson
- 💾 **Sauvegarde automatique** des simulations en base de données
- 🎨 **Interface moderne et responsive** avec animations fluides
- 📱 **Compatible mobile et desktop**

---

## 🚀 Installation

### Prérequis
- Python 3.9+
- pip (gestionnaire de paquets Python)

### Étapes

1. **Cloner ou télécharger le projet**
```bash
   cd thermocool_app
```

2. **Créer un environnement virtuel**
```bash
   python -m venv venv
   venv\Scripts\activate  # Windows
   source venv/bin/activate  # Linux/Mac
```

3. **Installer les dépendances**
```bash
   pip install -r requirements.txt
```

4. **Lancer l'application**
```bash
   python app.py
```

5. **Accéder à l'application**
   - Ouvrir le navigateur
   - Aller à `http://localhost:5000`

---

## 📖 Utilisation

### Simulation
1. Sélectionner un réfrigérant
2. Ajuster les paramètres avec les sliders:
   - Température d'évaporation
   - Température de condensation
   - Puissance frigorifique
3. Cliquer sur **"Lancer la simulation"**
4. Consulter les résultats:
   - COP (Coefficient de Performance)
   - Puissance du compresseur
   - Diagramme P-h

### Historique
- Toutes les simulations sont sauvegardées automatiquement
- Consulter l'historique à `/results`

---

## 📁 Structure du Projet