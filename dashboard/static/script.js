// Netra-X Dashboard Client-Side Logic

let alertCount = 0;

// Connect to SSE
function connectSSE() {
    const eventSource = new EventSource('/api/alerts/stream');
    
    eventSource.onmessage = function(event) {
        try {
            const data = JSON.parse(event.data);
            
            if (data.type === 'heartbeat') {
                console.log('💓 Netra-X heartbeat');
                return;
            }
            
            console.log('🚨 Alert received:', data);
            handleAlert(data);
            
        } catch (e) {
            console.error('Error processing alert:', e);
        }
    };
    
    eventSource.onerror = function(error) {
        console.error('SSE connection error:', error);
        setTimeout(connectSSE, 5000);
    };
}

// Handle incoming alert
function handleAlert(alert) {
    // Increment counters
    alertCount++;
    
    // Update stats
    updateStats(alert);
    
    // Add to table
    addAlertToTable(alert);
    
    // Show banner for high severity
    if (alert.severity === 'HIGH' || alert.severity === 'CRITICAL') {
        showAlertBanner(alert);
    }
}

// Update stats in dashboard
function updateStats(alert) {
    // Update total alerts
    document.getElementById('totalAlerts').textContent = alertCount;
    
    // Update severity counts
    const stats = document.getElementById('highSeverity');
    const currentCount = parseInt(stats.textContent) || 0;
    if (alert.severity === 'HIGH' || alert.severity === 'CRITICAL') {
        stats.textContent = currentCount + 1;
    }
    
    // Update critical alerts
    if (alert.severity === 'CRITICAL') {
        const criticalEl = document.getElementById('criticalAlerts');
        const criticalCount = parseInt(criticalEl.textContent) || 0;
        criticalEl.textContent = criticalCount + 1;
    }
}

// Add alert to table
function addAlertToTable(alert) {
    const tbody = document.getElementById('alertsBody');
    const row = document.createElement('tr');
    
    const time = new Date(alert.timestamp).toLocaleTimeString();
    
    row.innerHTML = `
        <td>${time}</td>
        <td>${alert.source_ip || 'unknown'}</td>
        <td>${alert.dest_ip || 'unknown'}</td>
        <td>${alert.alert_type || 'Anomaly'}</td>
        <td class="severity-${alert.severity}">${alert.severity}</td>
        <td>${(alert.anomaly_score || 0).toFixed(2)}</td>
        <td>🔴 Active</td>
    `;
    
    // Add animation
    row.style.animation = 'fadeIn 0.5s';
    
    // Insert at top
    tbody.insertBefore(row, tbody.firstChild);
    
    // Limit table size
    while (tbody.children.length > 50) {
        tbody.removeChild(tbody.lastChild);
    }
}

// Show alert banner
function showAlertBanner(alert) {
    const banner = document.getElementById('alertBanner');
    const message = document.getElementById('alertMessage');
    const details = document.getElementById('alertDetails');
    
    // Update message
    message.textContent = `🚨 INTRUSION DETECTED - ${alert.severity}`;
    details.textContent = `${alert.source_ip} → ${alert.dest_ip} | ${alert.reason || 'Anomalous behavior detected'}`;
    
    // Show banner
    banner.style.display = 'block';
    
    // Update status indicator
    const statusDot = document.querySelector('.status-dot');
    const statusText = document.getElementById('statusText');
    statusDot.className = 'status-dot red';
    statusText.textContent = '🚨 INTRUSION';
    
    // Auto-hide after 10 seconds
    clearTimeout(window.alertTimeout);
    window.alertTimeout = setTimeout(() => {
        banner.style.display = 'none';
        const statusDot = document.querySelector('.status-dot');
        const statusText = document.getElementById('statusText');
        statusDot.className = 'status-dot green';
        statusText.textContent = 'SECURE';
    }, 10000);
}

// Fetch initial data
function fetchInitialData() {
    fetch('/api/stats')
        .then(response => response.json())
        .then(data => {
            if (data.total_alerts) {
                alertCount = data.total_alerts;
                document.getElementById('totalAlerts').textContent = data.total_alerts;
                document.getElementById('highSeverity').textContent = data.high_severity || 0;
            }
            
            // Populate table with existing alerts
            if (data.alerts) {
                data.alerts.forEach(alert => {
                    addAlertToTable(alert);
                });
            }
        })
        .catch(error => console.error('Error fetching initial data:', error));
}

// Add CSS animation
const style = document.createElement('style');
style.textContent = `
    @keyframes fadeIn {
        from { opacity: 0; transform: translateY(-10px); }
        to { opacity: 1; transform: translateY(0); }
    }
`;
document.head.appendChild(style);

// Initialize
console.log('🛡️ Netra-X Dashboard Online');
connectSSE();
fetchInitialData();

// Re-fetch stats periodically
setInterval(() => {
    fetch('/api/stats')
        .then(response => response.json())
        .then(data => {
            if (data.total_alerts !== alertCount) {
                alertCount = data.total_alerts;
                document.getElementById('totalAlerts').textContent = alertCount;
            }
        })
        .catch(() => {});
}, 10000);