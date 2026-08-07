/**
 * Choptyuk Spinor Monograph - Interactive UI JavaScript
 *
 * Provides AJAX calls to the REST API endpoints and interactive
 * parameter configuration for all verification/simulation operations.
 */

const API_BASE = '/api';

// ============================================================
// API Client
// ============================================================

const ChoptyukAPI = {
    /**
     * Run verification with optional custom parameters.
     */
    async verify(params = {}) {
        const response = await fetch(`${API_BASE}/verify`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify(params)
        });
        if (!response.ok) throw new Error(`Verification failed: ${response.statusText}`);
        return response.json();
    },

    /**
     * Run simulation with parameter sweep configuration.
     */
    async simulate(params = {}) {
        const response = await fetch(`${API_BASE}/simulate`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify(params)
        });
        if (!response.ok) throw new Error(`Simulation failed: ${response.statusText}`);
        return response.json();
    },

    /**
     * Test a custom hypothesis.
     */
    async hypothesis(params) {
        const response = await fetch(`${API_BASE}/hypothesis`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify(params)
        });
        if (!response.ok) throw new Error(`Hypothesis test failed: ${response.statusText}`);
        return response.json();
    },

    /**
     * Download a report in the specified format.
     */
    getReportUrl(format) {
        return `${API_BASE}/reports/${format}`;
    },

    /**
     * List available report files.
     */
    async listReports() {
        const response = await fetch(`${API_BASE}/reports/list`);
        if (!response.ok) throw new Error(`List reports failed: ${response.statusText}`);
        return response.json();
    }
};

// ============================================================
// Formatting Utilities
// ============================================================

const Format = {
    number(val, digits = 6) {
        if (val === null || val === undefined) return 'N/A';
        return Number(val).toFixed(digits);
    },

    percent(val, digits = 4) {
        if (val === null || val === undefined) return 'N/A';
        return (Number(val) * 100).toFixed(digits) + '%';
    },

    scientific(val, digits = 4) {
        if (val === null || val === undefined) return 'N/A';
        return Number(val).toExponential(digits);
    }
};

// ============================================================
// UI Components
// ============================================================

const UI = {
    /**
     * Show a loading state on an element.
     */
    setLoading(elementId, loading = true) {
        const el = document.getElementById(elementId);
        if (!el) return;
        if (loading) {
            el.dataset.originalContent = el.innerHTML;
            el.innerHTML = '<div class="spinner"></div> Loading...';
            el.style.opacity = '0.6';
        } else {
            el.style.opacity = '1';
        }
    },

    /**
     * Show an alert message.
     */
    showAlert(containerId, message, type = 'info') {
        const container = document.getElementById(containerId);
        if (!container) return;
        const alert = document.createElement('div');
        alert.className = `alert alert-${type} fade-in`;
        alert.textContent = message;
        container.prepend(alert);
        setTimeout(() => alert.remove(), 5000);
    },

    /**
     * Create a status badge.
     */
    statusBadge(passed) {
        return `<span class="badge ${passed ? 'badge-success' : 'badge-danger'}">${passed ? 'PASS' : 'FAIL'}</span>`;
    },

    /**
     * Create a value display with label.
     */
    valueDisplay(label, value, unit = '') {
        return `<div class="card">
            <div class="card-title">${label}</div>
            <div class="card-value">${value}</div>
            ${unit ? `<div class="card-label">${unit}</div>` : ''}
        </div>`;
    }
};

// ============================================================
// Verification Page Logic
// ============================================================

const VerifyPage = {
    async runVerification() {
        const params = {
            deltaA: parseFloat(document.getElementById('input-deltaA')?.value || (Math.PI / 2)),
            deltaB: parseFloat(document.getElementById('input-deltaB')?.value || (Math.PI / 3)),
            deltaC: parseFloat(document.getElementById('input-deltaC')?.value || (Math.PI / 7)),
            lambda1: parseFloat(document.getElementById('input-lambda1')?.value || 3.838),
            scalarCurvature: parseFloat(document.getElementById('input-scalarCurvature')?.value || -2.0),
            deltaObserved: parseFloat(document.getElementById('input-deltaObserved')?.value || 3.443)
        };

        UI.setLoading('verify-results', true);
        UI.showAlert('verify-alerts', 'Running verification...', 'info');

        try {
            const result = await ChoptyukAPI.verify(params);
            this.displayResults(result);
            UI.showAlert('verify-alerts', 'Verification complete!', 'success');
        } catch (err) {
            UI.showAlert('verify-alerts', `Error: ${err.message}`, 'error');
        } finally {
            UI.setLoading('verify-results', false);
        }
    },

    displayResults(result) {
        const container = document.getElementById('verify-results');
        if (!container) return;

        let html = '<div class="results-panel fade-in">';
        html += '<h3>Summary</h3>';
        html += `<p>${UI.statusBadge(result.allPassed)} ${result.passedChecks}/${result.totalChecks} checks passed</p>`;

        // Key values
        html += '<div class="grid grid-4" style="margin-top:1rem">';
        html += UI.valueDisplay('Delta_Ch (base)', Format.number(result.choptyukFormula.deltaChBase));
        html += UI.valueDisplay('Delta_Ch (higher)', Format.number(result.choptyukFormula.deltaChHigher));
        html += UI.valueDisplay('Delta_obs', Format.number(result.choptyukFormula.deltaObserved));
        html += UI.valueDisplay('Deviation', Format.number(result.choptyukFormula.deviationBase));
        html += '</div></div>';

        // Checks table
        html += '<div class="results-panel fade-in"><h3>Verification Checks</h3>';
        html += '<div class="table-container"><table>';
        html += '<tr><th>Check</th><th>Expected</th><th>Actual</th><th>Status</th><th>Message</th></tr>';

        for (const check of result.checks) {
            html += `<tr>
                <td>${check.name}</td>
                <td class="mono">${Format.number(check.expected)}</td>
                <td class="mono">${Format.number(check.actual)}</td>
                <td>${UI.statusBadge(check.passed)}</td>
                <td>${check.message}</td>
            </tr>`;
        }
        html += '</table></div></div>';

        // QNM events
        if (result.qnmEvents) {
            html += '<div class="results-panel fade-in"><h3>LIGO QNM Predictions</h3>';
            html += '<div class="table-container"><table>';
            html += '<tr><th>Event</th><th>Date</th><th>Mass (M☉)</th><th>f_obs (Hz)</th><th>f_pred (Hz)</th><th>Error</th><th>SNR</th></tr>';
            for (const evt of result.qnmEvents) {
                html += `<tr>
                    <td>${evt.eventName}</td>
                    <td>${evt.date}</td>
                    <td class="mono">${Format.number(evt.remnantMassSolar, 1)}</td>
                    <td class="mono">${Format.number(evt.observedFreqHz, 1)}</td>
                    <td class="mono">${Format.number(evt.predictedFreqHz, 1)}</td>
                    <td class="mono">${Format.percent(evt.relativeError)}</td>
                    <td class="mono">${Format.number(evt.snr, 1)}</td>
                </tr>`;
            }
            html += '</table></div></div>';
        }

        container.innerHTML = html;
    },

    resetToCanonical() {
        const defaults = {
            'input-deltaA': (Math.PI / 2).toFixed(10),
            'input-deltaB': (Math.PI / 3).toFixed(10),
            'input-deltaC': (Math.PI / 7).toFixed(10),
            'input-lambda1': '3.838',
            'input-scalarCurvature': '-2.0',
            'input-deltaObserved': '3.443'
        };
        for (const [id, val] of Object.entries(defaults)) {
            const el = document.getElementById(id);
            if (el) el.value = val;
        }
    }
};

// ============================================================
// Simulation Page Logic
// ============================================================

const SimulatePage = {
    async runSimulation() {
        const params = {
            deltaCMin: parseFloat(document.getElementById('sim-dcMin')?.value || 0.5),
            deltaCMax: parseFloat(document.getElementById('sim-dcMax')?.value || 1.5),
            lambda1Min: parseFloat(document.getElementById('sim-l1Min')?.value || 3.0),
            lambda1Max: parseFloat(document.getElementById('sim-l1Max')?.value || 5.0),
            curvatureMin: parseFloat(document.getElementById('sim-rMin')?.value || -4.0),
            curvatureMax: parseFloat(document.getElementById('sim-rMax')?.value || 0.0),
            numPoints: parseInt(document.getElementById('sim-nPts')?.value || 100),
            maxOrder: parseInt(document.getElementById('sim-maxOrd')?.value || 8)
        };

        UI.setLoading('sim-results', true);
        UI.showAlert('sim-alerts', 'Running simulation...', 'info');

        try {
            const result = await ChoptyukAPI.simulate(params);
            this.displayResults(result);
            UI.showAlert('sim-alerts', 'Simulation complete!', 'success');
        } catch (err) {
            UI.showAlert('sim-alerts', `Error: ${err.message}`, 'error');
        } finally {
            UI.setLoading('sim-results', false);
        }
    },

    displayResults(result) {
        const container = document.getElementById('sim-results');
        if (!container) return;

        let html = '<div class="results-panel fade-in"><h3>Simulation Results</h3>';
        html += '<div class="grid grid-3">';

        // Sweep results
        if (result.deltaCSweep) {
            html += UI.valueDisplay('Optimal delta_C', Format.number(result.deltaCSweep.optimalValue));
            html += UI.valueDisplay('Min deviation', Format.number(result.deltaCSweep.minDeviation));
            html += UI.valueDisplay('Delta_Ch at opt', Format.number(result.deltaCSweep.optimalDeltaCh));
        }
        html += '</div>';

        // Convergence
        if (result.convergence) {
            html += '<div style="margin-top:1rem">';
            html += `<p>Converged: ${UI.statusBadge(result.convergence.converged)}</p>`;
            html += `<p>Convergence rate: <span class="mono">${Format.number(result.convergence.convergenceRate)}</span></p>`;
            html += `<p>Limit estimate: <span class="value-highlight">${Format.number(result.convergence.limitEstimate)}</span></p>`;
            html += '</div>';
        }

        // Sensitivity
        if (result.sensitivity) {
            html += '<div style="margin-top:1rem"><h4>Sensitivity Analysis</h4>';
            html += `<p>Most sensitive: <span class="value-highlight">${result.sensitivity.mostSensitiveParameter}</span></p>`;
            html += '<div class="table-container"><table>';
            html += '<tr><th>Parameter</th><th>Abs. Sensitivity</th><th>Rel. Sensitivity</th></tr>';
            for (const [key, val] of Object.entries(result.sensitivity.sensitivities || {})) {
                const relVal = result.sensitivity.relativeSensitivities?.[key] || 0;
                html += `<tr><td>${key}</td><td class="mono">${Format.number(val)}</td><td class="mono">${Format.number(relVal)}</td></tr>`;
            }
            html += '</table></div></div>';
        }

        html += '</div>';
        container.innerHTML = html;
    }
};

// ============================================================
// Hypothesis Page Logic
// ============================================================

const HypothesisPage = {
    async testHypothesis() {
        const params = {
            name: document.getElementById('hyp-name')?.value || 'Custom',
            deltaA: parseFloat(document.getElementById('hyp-deltaA')?.value || (Math.PI / 2)),
            deltaB: parseFloat(document.getElementById('hyp-deltaB')?.value || (Math.PI / 3)),
            deltaC: parseFloat(document.getElementById('hyp-deltaC')?.value || (Math.PI / 7)),
            lambda1: parseFloat(document.getElementById('hyp-lambda1')?.value || 3.838),
            scalarCurvature: parseFloat(document.getElementById('hyp-scalarCurvature')?.value || -2.0),
            genus: parseInt(document.getElementById('hyp-genus')?.value || 3),
            pslOrder: parseInt(document.getElementById('hyp-pslOrder')?.value || 168),
            deltaObserved: parseFloat(document.getElementById('hyp-deltaObserved')?.value || 3.443),
            maxOrder: parseInt(document.getElementById('hyp-maxOrder')?.value || 6)
        };

        UI.setLoading('hyp-results', true);
        UI.showAlert('hyp-alerts', 'Testing hypothesis...', 'info');

        try {
            const result = await ChoptyukAPI.hypothesis(params);
            this.displayResults(result, params);
            UI.showAlert('hyp-alerts', 'Hypothesis test complete!', 'success');
        } catch (err) {
            UI.showAlert('hyp-alerts', `Error: ${err.message}`, 'error');
        } finally {
            UI.setLoading('hyp-results', false);
        }
    },

    displayResults(result, params) {
        const container = document.getElementById('hyp-results');
        if (!container) return;

        let html = '<div class="results-panel fade-in"><h3>Hypothesis: ' + (params.name || 'Custom') + '</h3>';
        html += '<div class="grid grid-3">';
        html += UI.valueDisplay('Delta_Ch', Format.number(result.choptyukValue));
        html += UI.valueDisplay('Deviation', Format.number(result.deviation));
        html += UI.valueDisplay('Rel. deviation', Format.percent(result.relativeDeviation));
        html += '</div></div>';

        container.innerHTML = html;
    }
};

// ============================================================
// Reports Page Logic
// ============================================================

const ReportsPage = {
    download(format) {
        window.location.href = ChoptyukAPI.getReportUrl(format);
    },

    async refreshList() {
        try {
            const reports = await ChoptyukAPI.listReports();
            const container = document.getElementById('reports-list');
            if (!container) return;

            if (reports.length === 0) {
                container.innerHTML = '<p class="text-muted">No reports generated yet.</p>';
                return;
            }

            let html = '<div class="table-container"><table>';
            html += '<tr><th>Filename</th><th>Format</th><th>Size</th></tr>';
            for (const r of reports) {
                html += `<tr><td>${r.filename}</td><td><span class="badge badge-info">${r.format}</span></td><td>${(r.sizeBytes / 1024).toFixed(1)} KB</td></tr>`;
            }
            html += '</table></div>';
            container.innerHTML = html;
        } catch (err) {
            console.error('Error listing reports:', err);
        }
    }
};

// ============================================================
// Initialization
// ============================================================

document.addEventListener('DOMContentLoaded', () => {
    console.log('Choptyuk Spinor Monograph UI initialized');

    // Auto-run verification on dashboard
    const dashVerify = document.getElementById('dashboard-verify');
    if (dashVerify) {
        VerifyPage.runVerification();
    }
});
