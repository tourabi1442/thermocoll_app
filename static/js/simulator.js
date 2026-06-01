let selectedFluid = 'R32';
let selectedModel = 'Peng-Robinson';

function selectFluid(el, fluid) {
    document.querySelectorAll('.fluid-btn').forEach((b) => b.classList.remove('selected'));
    el.classList.add('selected');
    selectedFluid = fluid;
}

function selectModel(el, model) {
    document.querySelectorAll('.model-btn').forEach((b) => b.classList.remove('selected'));
    el.classList.add('selected');
    selectedModel = model;
}

function updateSlider(id, valId, value) {
    document.getElementById(valId).textContent = value;
}

function getPayload() {
    return {
        refrigerant: selectedFluid,
        temp_evap: parseFloat(document.getElementById('tempEvap').value),
        temp_cond: parseFloat(document.getElementById('tempCond').value),
        power: parseFloat(document.getElementById('power').value),
        model_type: selectedModel
    };
}

function validatePayload(payload) {
    if (payload.temp_cond <= payload.temp_evap + 3) {
        return "Le condenseur doit etre au moins 3 C au-dessus de l'evaporateur.";
    }
    if (payload.power <= 0) {
        return "La puissance frigorifique doit etre positive.";
    }
    return null;
}

async function runSimulation() {
    const btn = document.getElementById('runBtn');
    const icon = document.getElementById('runIcon');
    const text = document.getElementById('runText');
    const spinner = document.getElementById('runSpinner');
    const payload = getPayload();
    const error = validatePayload(payload);

    if (error) {
        showRecommendation(error, true);
        return;
    }

    btn.disabled = true;
    icon.style.display = 'none';
    spinner.style.display = 'block';
    text.textContent = 'Calcul en cours...';

    try {
        const res = await fetch('/api/calculate', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify(payload)
        });
        const data = await res.json();

        if (data.status === 'success') {
            showResults(data, payload);
            runComparison();
        } else {
            showRecommendation(data.message || 'Erreur de calcul.', true);
        }
    } catch (e) {
        showRecommendation('Erreur reseau: ' + e.message, true);
    } finally {
        btn.disabled = false;
        icon.style.display = '';
        spinner.style.display = 'none';
        text.textContent = 'Relancer la simulation';
    }
}

function showResults(data, payload) {
    document.getElementById('resCOP').textContent = data.COP;
    document.getElementById('resCompEff').textContent = data.compressor_efficiency;
    document.getElementById('resWcomp').textContent = Math.round(data.W_comp);
    document.getElementById('resRatio').textContent = data.pressure_ratio;
    document.getElementById('resSummary').textContent =
        `${payload.refrigerant} | ${payload.model_type} | Lift ${data.temperature_lift} C | Carnot ${data.COP_carnot}`;

    showRecommendation(
        `${data.recommendation} GWP: ${data.fluid_meta.gwp}, securite: ${data.fluid_meta.safety}, usage: ${data.fluid_meta.use_case}.`,
        false
    );

    const steps = ['Sortie evaporateur', 'Sortie compresseur', 'Sortie condenseur', 'Sortie detendeur'];
    const classes = ['p1', 'p2', 'p3', 'p4'];
    const points = [data.point1, data.point2, data.point3, data.point4];

    document.getElementById('pointsBody').innerHTML = points.map((p, i) => `
        <tr>
            <td><span class="point-badge ${classes[i]}">${i + 1}</span></td>
            <td><strong>${steps[i]}</strong><br><span class="muted">${p.state || '-'}</span></td>
            <td>${formatNumber(p.T)}</td>
            <td>${formatNumber(p.P)}</td>
            <td>${formatNumber(p.h)}</td>
            <td>${formatNumber(p.density)}</td>
        </tr>
    `).join('');

    document.getElementById('resultsArea').classList.add('visible');
    sessionStorage.setItem('lastSimulation', JSON.stringify(data));
}

function showRecommendation(message, isError) {
    const box = document.getElementById('recommendationBox');
    if (!box) return;
    box.textContent = message;
    box.classList.toggle('is-error', Boolean(isError));
}

async function runComparison() {
    const payload = getPayload();
    const error = validatePayload(payload);
    const body = document.getElementById('comparisonBody');

    if (error) {
        body.innerHTML = `<div class="comparison-empty">${error}</div>`;
        return;
    }

    body.innerHTML = '<div class="comparison-empty">Classement en cours...</div>';

    try {
        const res = await fetch('/api/compare', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify(payload)
        });
        const data = await res.json();

        if (data.status !== 'success') {
            body.innerHTML = `<div class="comparison-empty">${data.message || 'Erreur de comparaison.'}</div>`;
            return;
        }

        const rows = data.rows.map((row, index) => `
            <tr>
                <td><span class="rank-badge">${index + 1}</span></td>
                <td>
                    <strong>${row.fluid}</strong>
                    <div class="muted">${row.family}</div>
                </td>
                <td><span class="cop-pill ${copClass(row.cop)}">${row.cop}</span></td>
                <td>${Math.round(row.w_comp)} W</td>
                <td>${row.pressure_ratio}</td>
                <td>${row.gwp}</td>
                <td><span class="safety-pill">${row.safety}</span></td>
                <td>${row.score}</td>
            </tr>
        `).join('');

        body.innerHTML = `
            <div class="table-scroll">
                <table class="htable comparison-table">
                    <thead>
                        <tr>
                            <th>#</th><th>Fluide</th><th>COP</th><th>W comp</th>
                            <th>Ratio P</th><th>GWP</th><th>Securite</th><th>Score</th>
                        </tr>
                    </thead>
                    <tbody>${rows}</tbody>
                </table>
            </div>
        `;
    } catch (e) {
        body.innerHTML = `<div class="comparison-empty">Erreur reseau: ${e.message}</div>`;
    }
}

function formatNumber(value) {
    if (value === undefined || value === null || Number.isNaN(Number(value))) return '-';
    return Number(value).toFixed(2);
}

function copClass(cop) {
    if (cop >= 4) return 'cop-hi';
    if (cop >= 2.5) return 'cop-mid';
    return 'cop-lo';
}
