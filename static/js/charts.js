let phChart = null;

function drawPhDiagram(point1, point2, point3, point4) {
    const ctx = document.getElementById('phChart');
    
    if (!ctx) {
        console.error('Chart canvas not found');
        return;
    }

    // Destroy old chart if exists
    if (phChart) {
        phChart.destroy();
    }

    // Create P-h diagram points
    // Simplified calculation based on density and temperature
    const points = [
        {
            x: (point1.density * 100 + point1.T * 5),
            y: point1.P * 10 + 5,
            label: 'Point 1 (Évaporation)'
        },
        {
            x: (point2.density * 120 + point2.T * 8),
            y: point2.P * 10 + 15,
            label: 'Point 2 (Compression)'
        },
        {
            x: (point3.density * 80 + point3.T * 4),
            y: point3.P * 10 + 15,
            label: 'Point 3 (Détente)'
        },
        {
            x: (point4.density * 90 + point4.T * 5),
            y: point4.P * 10 + 5,
            label: 'Point 4 (Expansion)'
        }
    ];

    phChart = new Chart(ctx, {
        type: 'scatter',
        data: {
            datasets: [
                {
                    label: 'Cycle Thermodynamique',
                    data: points,
                    borderColor: '#667eea',
                    backgroundColor: ['#ff6b6b', '#4ecdc4', '#f9ca24', '#6c5ce7'],
                    borderWidth: 3,
                    showLine: true,
                    fill: false,
                    pointRadius: 10,
                    pointHoverRadius: 12,
                    pointBorderWidth: 2,
                    pointBorderColor: '#333',
                    tension: 0.4,
                    spanGaps: true
                }
            ]
        },
        options: {
            responsive: true,
            maintainAspectRatio: true,
            interaction: {
                intersect: false,
                mode: 'index'
            },
            plugins: {
                legend: {
                    display: true,
                    labels: {
                        font: { size: 12, weight: 'bold' },
                        color: '#333',
                        padding: 15
                    }
                },
                title: {
                    display: true,
                    text: 'Diagramme P-h (Pression-Enthalpie)',
                    font: { size: 16, weight: 'bold' },
                    color: '#333',
                    padding: 20
                },
                tooltip: {
                    backgroundColor: 'rgba(0,0,0,0.8)',
                    padding: 12,
                    titleFont: { size: 12, weight: 'bold' },
                    bodyFont: { size: 11 },
                    callbacks: {
                        label: function(context) {
                            return [
                                'h: ' + context.parsed.x.toFixed(1) + ' kJ/kg',
                                'P: ' + (context.parsed.y / 10).toFixed(2) + ' bar'
                            ];
                        },
                        title: function(context) {
                            const labels = ['Point 1 (Évaporation)', 'Point 2 (Compression)', 'Point 3 (Détente)', 'Point 4 (Expansion)'];
                            return labels[context[0].dataIndex];
                        }
                    }
                }
            },
            scales: {
                x: {
                    type: 'linear',
                    position: 'bottom',
                    title: {
                        display: true,
                        text: 'Enthalpie h (kJ/kg)',
                        font: { size: 13, weight: 'bold' },
                        color: '#333'
                    },
                    grid: {
                        color: 'rgba(0,0,0,0.1)'
                    },
                    ticks: {
                        color: '#666'
                    }
                },
                y: {
                    title: {
                        display: true,
                        text: 'Pression P (bar)',
                        font: { size: 13, weight: 'bold' },
                        color: '#333'
                    },
                    grid: {
                        color: 'rgba(0,0,0,0.1)'
                    },
                    ticks: {
                        color: '#666'
                    }
                }
            }
        }
    });
}