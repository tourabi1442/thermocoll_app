const STEPS = [
    {
        tab: 0,
        infoClass: '',
        title: '① Compression — Vapeur BP → Vapeur HP',
        physics: 'Le compresseur aspire la vapeur froide du frigorigène (point 1) et la comprime mécaniquement. Le volume diminue → la pression et la température augmentent fortement. Le gaz passe de ~2–6 bar à ~15–25 bar.',
        mol: 'Molécules : très agitées, espacées, haute énergie cinétique. Phase vapeur surchauffée.',
        formula: 'W = h₂ − h₁',
        molState: 'Vapeur HP (sortie)',
        molDesc: 'T↑↑ P↑↑  Gaz surchauffé',
        molColor: '#ef4444',
        molDensity: 0.4,
        highlight: 'comp-box',
        arrowActive: 'arrow-top'
    },
    {
        tab: 1,
        infoClass: 'cond',
        title: '② Condensation — Vapeur HP → Liquide HP',
        physics: 'Le condenseur rejette la chaleur vers l\'extérieur. La vapeur chaude cède son énergie à l\'air ambiant et se condense progressivement. Pression quasi-constante (isobare).',
        mol: 'Molécules : ralentissent, se rapprochent, les forces attractives prennent le dessus → passage gaz → liquide.',
        formula: 'Q_cond = h₂ − h₃',
        molState: 'Liquide HP (sortie)',
        molDesc: 'T↓ P élevée  Liquide saturé',
        molColor: '#3b82f6',
        molDensity: 0.85,
        highlight: 'cond-box',
        arrowActive: 'arrow-right'
    },
    {
        tab: 2,
        infoClass: 'det',
        title: '③ Détente — Liquide HP → Mélange BP',
        physics: 'Le détendeur (ou valve d\'expansion) réduit brusquement la pression du liquide. Processus isenthalpique : la pression chute de ~15–25 bar à ~2–6 bar, provoquant une chute de température et une vaporisation partielle.',
        mol: 'Molécules : expansion soudaine → certaines passent en phase vapeur. Mélange liquide + vapeur (titre < 1).',
        formula: 'h₃ = h₄  (isenthalpique)',
        molState: 'Mélange BP (sortie)',
        molDesc: 'T↓↓ P↓↓  Liquide + vapeur',
        molColor: '#f59e0b',
        molDensity: 0.55,
        highlight: 'det-box',
        arrowActive: 'arrow-bottom'
    },
    {
        tab: 3,
        infoClass: 'evap',
        title: '④ Évaporation — Mélange BP → Vapeur BP',
        physics: 'L\'évaporateur absorbe la chaleur de l\'espace à refroidir. Le frigorigène à basse pression s\'évapore en absorbant l\'énergie thermique de l\'intérieur. Processus isobare à basse pression.',
        mol: 'Molécules : absorbent l\'énergie → passage liquide → vapeur. Extraction thermique de la pièce.',
        formula: 'Q_evap = h₁ − h₄',
        molState: 'Vapeur BP (entrée)',
        molDesc: 'T basse  P↓  Vapeur saturée',
        molColor: '#10b981',
        molDensity: 0.25,
        highlight: 'evap-box',
        arrowActive: 'arrow-left'
    }
];

let currentStep = 0;
let animFrame = null;
let molParticles = [];

// === STEP NAVIGATION ===
function goStep(idx) {
    currentStep = idx;
    document.querySelectorAll('.step-tab').forEach((t, i) => {
        t.classList.toggle('active', i === idx);
    });

    const step = STEPS[idx];

    // Highlight boxes
    ['comp-box', 'cond-box', 'det-box', 'evap-box'].forEach(id => {
        const el = document.getElementById(id);
        el.style.opacity = id === step.highlight ? '1' : '0.45';
    });

    // Highlight arrows
    ['arrow-top', 'arrow-right', 'arrow-bottom', 'arrow-left'].forEach(id => {
        const el = document.getElementById(id);
        el.style.opacity = id === step.arrowActive ? '1' : '0.2';
    });

    // Info card
    document.getElementById('infoTitle').textContent = step.title;
    document.getElementById('infoPhysics').textContent = '⚡ Physique : ' + step.physics;
    document.getElementById('infoMol').textContent = '🔬 ' + step.mol;
    document.getElementById('infoFormula').textContent = step.formula;

    const card = document.getElementById('infoCard');
    card.className = 'info-card ' + step.infoClass;

    // Molecular
    document.getElementById('molState').textContent = step.molState;
    document.getElementById('molDesc').textContent = step.molDesc;
    initMolecules(step.molColor, step.molDensity);
}

// === MOLECULAR ANIMATION ===
function initMolecules(color, density) {
    const canvas = document.getElementById('molCanvas');
    const ctx = canvas.getContext('2d');
    const W = canvas.width, H = canvas.height;

    const count = Math.round(density * 30);
    molParticles = Array.from({ length: count }, () => ({
        x: Math.random() * W,
        y: Math.random() * H,
        r: density > 0.7 ? 5 + Math.random() * 3 : 6 + Math.random() * 4,
        vx: (Math.random() - 0.5) * (1 + (1 - density) * 5),
        vy: (Math.random() - 0.5) * (1 + (1 - density) * 5),
        color
    }));

    if (animFrame) cancelAnimationFrame(animFrame);
    drawMolecules(ctx, W, H);
}

function drawMolecules(ctx, W, H) {
    ctx.clearRect(0, 0, W, H);

    for (const p of molParticles) {
        p.x += p.vx;
        p.y += p.vy;
        if (p.x < p.r || p.x > W - p.r) p.vx *= -1;
        if (p.y < p.r || p.y > H - p.r) p.vy *= -1;

        ctx.beginPath();
        ctx.arc(p.x, p.y, p.r, 0, Math.PI * 2);
        ctx.fillStyle = p.color + 'cc';
        ctx.fill();
        ctx.strokeStyle = p.color;
        ctx.lineWidth = 1.2;
        ctx.stroke();
    }

    animFrame = requestAnimationFrame(() => drawMolecules(ctx, W, H));
}

// === ARROW ANIMATION ===
function animateArrows() {
    let offset = 0;
    setInterval(() => {
        offset -= 1;
        ['arrow-top', 'arrow-bottom'].forEach(id => {
            const el = document.getElementById(id);
            if (el) el.setAttribute('stroke-dashoffset', offset);
        });
    }, 40);
}

// Init
goStep(0);
animateArrows();