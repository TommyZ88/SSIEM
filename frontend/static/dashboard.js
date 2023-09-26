function updateDashboardData() {
    fetch('/dashboard_data')
        .then(response => response.json())
        .then(data => {
            if (data.agent_table) {
                document.getElementById('table-container').innerHTML = data.agent_table;
            } else {
                console.error('agent_table is undefined in the response');
            }
        })
        .catch(error => console.error('Error fetching the dashboard data:', error));
}

// Set interval to call updateDashboardData every 10 seconds (10000 milliseconds)
setInterval(updateDashboardData, 10000);
