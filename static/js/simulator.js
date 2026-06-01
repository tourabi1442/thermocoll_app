let selectedFluid = 'R32';
let selectedModel = 'Peng-Robinson';

function selectFluid(el, fluid) {
    document.querySelectorAll('.fluid-btn').forEach(b => b.classList.remove('selected'));
    el.classList.add('selected');
    selectedFluid = fluid;
}

function selectModel(el, model) {
    document.querySelectorAll('.model-btn').forEach(b => b.classList.remove('selected'));
    el.classList.add('selected');
    selectedModel = model;
}

function updateSlider(id, valId, value, unit) {
    document.getElementById(valId).textContent = value;
}

async function runSimulation() {
    const btn = document.getElementById('runBtn');
    const icon = document.getElementById('runIcon');
    const text = document.getElementById('runText');
    const spinner = document.getElementById('runSpinner');

    btn.disabled = true;
    icon.style.display = 'none';
    spinner.style.display = 'block';
    text.textContent = 'Calcul en cours...';

    const payload = {
        refrigerant: selectedFluid,
        temp_evap: parseFloat(document.getElementById('tempEvap').value),
        temp_cond: parseFloat(document.getElementById('tempCond').value),
        power: parseFloat(document.getElementById('power').value),
        model_type: selectedModel
    };

    try {
        const res = await fetch('/api/calculate', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify(payload)
        });
        const data = await res.json();

        if (data.status === 'success') {
            showResults(data, payload);
        } else {
            alert('Erreur: ' + data.message);
        }
    } catch (e) {
        alert('Erreur réseau: ' + e.message);
    } finally {
        btn.disabled = false;
        icon.style.display = '';
        spinner.style.display = 'none';
        text.textContent = 'Relancer la simulation';
    }
}

function showResults(data, payload) {
    document.getElementById('resCOP').textContent = data.COP;
    document.getElementById('resEff').textContent = data.efficiency;
    document.getElementById('resQevap').textContent = Math.round(data.Q_evap);
    document.getElementById('resWcomp').textContent = Math.round(data.W_comp);
    document.getElementById('resSummary').textContent =
        `${payload.refrigerant} · ${payload.model_type} · #${data.simulation_id}`;

    const steps = ['Sortie évaporateur', 'Sortie compresseur', 'Sortie condenseur', 'Sortie détendeur'];
    const classes = ['p1', 'p2', 'p3', 'p4'];
    const points = [data.point1, data.point2, data.point3, data.point4];

    document.getElementById('pointsBody').innerHTML = points.map((p, i) => `
        <tr>
            <td><span class="point-badge ${classes[i]}">${i + 1}</span></td>
            <td>${steps[i]}</td>
            <td>${p.T ?? '—'}</td>
            <td>${p.P ?? '—'}</td>
            <td>${p.density ?? '—'}</td>
        </tr>
    `).join('');

    const area = document.getElementById('resultsArea');
    area.classList.add('visible');
    area.scrollIntoView({ behavior: 'smooth', block: 'start' });

    // Save to sessionStorage for results page
    sessionStorage.setItem('lastSimulation', JSON.stringify(data));
}