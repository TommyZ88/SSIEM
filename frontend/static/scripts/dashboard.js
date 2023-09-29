function updateDashboardData() {
    fetch('/dashboard_data')
        .then(response => response.json())
        .then(data => {
            if (data.agent_table) {
                document.getElementById('agent-information').innerHTML = "<h2>Agent Information</h2>" + data.agent_table;
            } else {
                console.error('agent_table is undefined in the response');
            }

            if (data.alert_severity) {
                console.log('Alert Severity Data:', data.alert_severity);
                document.getElementById('pie-chart-container').innerHTML = data.alert_severity;
            } else {
                console.error('alert_pie_chart is undefined in the response');
            }

            if (data.event_logs_table) {
                document.getElementById('event-logs').innerHTML = "<h2>Event Logs</h2>" + data.event_logs_table;
            } else {
                console.error('event_logs_table is undefined in the response');
            }

        })
        .catch(error => console.error('Error fetching the dashboard data:', error));
}

// Set interval to call updateDashboardData every 10 seconds (10000 milliseconds)
setInterval(updateDashboardData, 10000);

