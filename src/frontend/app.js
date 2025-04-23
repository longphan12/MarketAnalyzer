document.addEventListener('DOMContentLoaded', function() {
    const form = document.getElementById('uploadForm');
    const loading = document.getElementById('loading');
    const results = document.getElementById('results');
    let charts = {};

    form.addEventListener('submit', async (e) => {
        e.preventDefault();
        
        const fileInput = document.getElementById('pdfFile');
        if (!fileInput.files.length) {
            alert('Please select a PDF file');
            return;
        }

        const formData = new FormData();
        formData.append('file', fileInput.files[0]);

        loading.classList.remove('d-none');
        results.classList.add('d-none');

        try {
            console.log('Making API request...');
            const response = await fetch('/api/analyze', {
                method: 'POST',
                body: formData
            });
            console.log('Response status:', response.status);
            console.log('Response headers:', response.headers);

            if (!response.ok) {
                const errorText = await response.text();
                console.error('Response not OK:', errorText);
                throw new Error('Analysis failed');
            }

            console.log('Parsing response JSON...');
            const data = await response.json();
            console.log('Received data:', data);
            
            if (data.error) {
                if (data.error.includes('API quota')) {
                    alert('AI analysis is currently unavailable. The extracted data will still be displayed.');
                } else {
                    alert('Error analyzing the report. Please try again.');
                }
                if (data.housing_activity) {
                    displayResults(data);
                    updateCharts(data);
                }
                return;
            }
            
            displayResults(data);
            updateCharts(data);
            
        } catch (error) {
            console.error('Detailed error:', error);
            console.error('Error stack:', error.stack);
            alert('Failed to analyze the PDF. Please try again.');
        } finally {
            loading.classList.add('d-none');
            results.classList.remove('d-none');
        }
    });

    function displayResults(data) {
        // Display housing activity summary
        const housingActivity = document.getElementById('housingActivity');
        const housingData = data.housing_activity;
        let housingHtml = '<table class="table table-striped">';
        housingHtml += '<thead><tr><th>Metric</th><th>Current Quarter</th><th>Previous Quarter</th><th>QoQ Change</th></tr></thead>';
        housingHtml += '<tbody>';
        
        for (const [metric, values] of Object.entries(housingData)) {
            if (metric !== 'QOQ_CHANGE') {
                const currentQuarter = Object.keys(values)[1];
                const prevQuarter = Object.keys(values)[0];
                const qoqChange = values.QOQ_CHANGE || 0;
                
                housingHtml += `<tr>
                    <td>${metric.replace('_', ' ')}</td>
                    <td>${values[currentQuarter]}</td>
                    <td>${values[prevQuarter]}</td>
                    <td class="${qoqChange >= 0 ? 'text-success' : 'text-danger'}">${qoqChange}%</td>
                </tr>`;
            }
        }
        
        housingHtml += '</tbody></table>';
        housingActivity.innerHTML = housingHtml;

        // Display AI analysis if available
        if (data.ai_analysis) {
            const executiveSummary = document.getElementById('executiveSummary');
            executiveSummary.innerHTML = `
                <div class="analysis-text">
                    <p>${data.ai_analysis.executiveSummary.overview}</p>
                    <h5>Key Findings:</h5>
                    <ul>
                        ${data.ai_analysis.executiveSummary.keyFindings.map(finding => `<li>${finding}</li>`).join('')}
                    </ul>
                </div>
            `;

            const recommendations = document.getElementById('recommendations');
            recommendations.innerHTML = `
                <div class="analysis-text">
                    <h5>Market Opportunities:</h5>
                    <ul>
                        ${data.ai_analysis.recommendations.opportunities.map(opp => `<li>${opp}</li>`).join('')}
                    </ul>
                    <h5>Strategic Actions:</h5>
                    <ul>
                        ${data.ai_analysis.recommendations.actions.map(action => `<li>${action}</li>`).join('')}
                    </ul>
                </div>
            `;
        }

        // Update charts
        updateCharts(data);

        // Add PDF export button handler
        const exportButton = document.getElementById('exportPDF');
        exportButton.addEventListener('click', () => {
            // Create a print-specific stylesheet
            const printStyles = document.createElement('style');
            printStyles.textContent = `
                @media print {
                    body * {
                        visibility: hidden;
                    }
                    .container, .container * {
                        visibility: visible;
                    }
                    .container {
                        position: absolute;
                        left: 0;
                        top: 0;
                        width: 100%;
                        padding: 20px;
                    }
                    .upload-card {
                        display: none !important;
                        height: 0 !important;
                        margin: 0 !important;
                        padding: 0 !important;
                    }
                    .col-lg-6:has(.upload-card) {
                        display: none !important;
                        height: 0 !important;
                        margin: 0 !important;
                        padding: 0 !important;
                    }
                    .card {
                        border: none;
                        box-shadow: none;
                        page-break-inside: avoid;
                    }
                    .btn {
                        display: none;
                    }
                    .table {
                        width: 100%;
                    }
                    canvas {
                        max-width: 100%;
                        height: auto !important;
                    }
                    .hero-section, .navbar, .footer {
                        display: none;
                    }
                    h5 {
                        margin-top: 20px;
                        margin-bottom: 10px;
                    }
                    .chart-card {
                        margin-bottom: 30px;
                    }
                    @page {
                        size: letter;
                        margin: 1cm;
                    }
                }
            `;
            document.head.appendChild(printStyles);

            // Print the page
            window.print();

            // Remove the print styles after printing
            setTimeout(() => {
                document.head.removeChild(printStyles);
            }, 1000);
        });
    }

    function updateCharts(data) {
        // Housing Activity Chart
        const housingCtx = document.getElementById('housingActivityChart').getContext('2d');
        if (charts.housingActivity) {
            charts.housingActivity.destroy();
        }
        charts.housingActivity = new Chart(housingCtx, {
            type: 'bar',
            data: {
                labels: ['QTR_CLOS', 'QTR_STARTS', 'TOTAL_INV', 'TOTAL_SUPPLY'],
                datasets: [{
                    label: '3Q24',
                    data: Object.values(data.housing_activity).map(v => v['3Q24']),
                    backgroundColor: 'rgba(54, 162, 235, 0.5)',
                    borderColor: 'rgba(54, 162, 235, 1)',
                    borderWidth: 1
                }, {
                    label: '4Q24',
                    data: Object.values(data.housing_activity).map(v => v['4Q24']),
                    backgroundColor: 'rgba(255, 99, 132, 0.5)',
                    borderColor: 'rgba(255, 99, 132, 1)',
                    borderWidth: 1
                }]
            },
            options: {
                responsive: true,
                scales: {
                    y: {
                        beginAtZero: true
                    }
                }
            }
        });

        // Subdivision Chart
        const subdivisionCtx = document.getElementById('subdivisionChart').getContext('2d');
        if (charts.subdivision) {
            charts.subdivision.destroy();
        }
        charts.subdivision = new Chart(subdivisionCtx, {
            type: 'doughnut',
            data: {
                labels: ['Top 10', 'Top 25', 'Others'],
                datasets: [{
                    data: [
                        data.subdivisions.Top10_Percentage,
                        data.subdivisions.Top25_Percentage - data.subdivisions.Top10_Percentage,
                        100 - data.subdivisions.Top25_Percentage
                    ],
                    backgroundColor: [
                        'rgba(54, 162, 235, 0.5)',
                        'rgba(255, 99, 132, 0.5)',
                        'rgba(75, 192, 192, 0.5)'
                    ]
                }]
            },
            options: {
                responsive: true,
                plugins: {
                    legend: {
                        position: 'bottom'
                    }
                }
            }
        });

        // Builder Chart
        const builderCtx = document.getElementById('builderChart').getContext('2d');
        if (charts.builder) {
            charts.builder.destroy();
        }

        const builderData = data.builder_benchmark.Builder_Data;
        const builderNames = builderData.map(b => b.Builder);
        const annualClosings = builderData.map(b => b.Annual);

        // Create QoQ table
        const qoqTable = document.getElementById('builderQoQ');
        let tableHtml = '<table class="table table-striped">';
        tableHtml += '<thead><tr><th>Builder</th><th>QoQ Change (%)</th></tr></thead>';
        tableHtml += '<tbody>';
        
        builderData.forEach(builder => {
            const qoqChange = builder.QoQ_Change || 0;
            const changeClass = qoqChange >= 0 ? 'text-success' : 'text-danger';
            tableHtml += `<tr>
                <td>${builder.Builder}</td>
                <td class="${changeClass}">${qoqChange}%</td>
            </tr>`;
        });
        
        tableHtml += '</tbody></table>';
        qoqTable.innerHTML = tableHtml;

        // Create chart for annual closings only
        charts.builder = new Chart(builderCtx, {
            type: 'bar',
            data: {
                labels: builderNames,
                datasets: [{
                    label: 'Annual Closings',
                    data: annualClosings,
                    backgroundColor: 'rgba(75, 192, 192, 0.5)',
                    borderColor: 'rgba(75, 192, 192, 1)',
                    borderWidth: 1
                }]
            },
            options: {
                responsive: true,
                maintainAspectRatio: false,
                indexAxis: 'y',
                scales: {
                    x: {
                        beginAtZero: true,
                        title: {
                            display: true,
                            text: 'Annual Closings'
                        }
                    }
                }
            }
        });
    }
}); 