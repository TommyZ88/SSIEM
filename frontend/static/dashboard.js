function updateDashboardData() {
    // Fetch the updated data from the server
    fetch('/dashboard_data')
        .then(response => response.json())
        .then(data => {
            // Replace the content of the plot and table container with the updated data
            document.getElementById('table-container').innerHTML = data.agent_table;
            // You can add more elements here as you add more visualizations to the dashboard_data route.
        });
    console.log('updateDashboardData is called'); // This will log to the console every time this function is called
}

// Set interval to call updateDashboardData every 10 seconds (10000 milliseconds)
setInterval(updateDashboardData, 10000);
