function renderCharts(data) {
    if (data.alert_severity_pie_chart) {  // This should match the key used in the JSON returned by the server
        var layout = {
            // Define layout properties here if needed
        };
        Plotly.newPlot('alert_severity_pie_chart', [data.alert_severity_pie_chart], layout);  // 'pie-chart-container' is the id of the div where the Pie chart will be rendered
    } else {
        console.error('alert_severity_pie_chart is undefined in the response');
    }

    if (data.top_events_donut_chart) {
        var trace = {
            ...data.top_events_donut_chart,  // Spread the existing chart data
            hole: .5  // Set the size of the hole to create a donut chart
        };
        var layout = {
            // Define layout properties here if needed
        };
        Plotly.newPlot('top_events_donut_chart', [trace], layout);
    } else {
        console.error('top_event_donut_chart is undefined in the response');
    }

    if (data.mitre_attacks_donut_chart) {
        var trace = {
            ...data.mitre_attacks_donut_chart,  // Spread the existing chart data
            hole: .5  // Set the size of the hole to create a donut chart
        };
        var layout = {
            // Define layout properties here if needed
        };
        Plotly.newPlot('mitre_attacks_donut_chart', [trace], layout);
    } else {
        console.error('mitre_attacks_donut_chart is undefined in the response');
    }
}


function updateDashboardData() {
    fetch('/dashboard_data')
        .then(response => response.json())
        .then(data => {
            // Render the charts with the data received from the server
            renderCharts(data);

            // For non-chart elements like tables, you can continue to update the innerHTML as before
            if (data.agent_table) {
                document.getElementById('agent-information').innerHTML = "<h2>Agent Information</h2>" + data.agent_table;
            } else {
                console.error('agent_table is undefined in the response');
            }

            if (data.event_logs_table) {
                document.getElementById('event-logs').innerHTML = "<h2>Event Logs</h2>" + data.event_logs_table;
            } else {
                console.error('event_logs_table is undefined in the response');
            }
        })
        .catch(error => console.error('Error fetching the dashboard data:', error));
}

updateDashboardData(); // Call once initially when the page loads.
// Set interval to call updateDashboardData every 10 seconds (10000 milliseconds)
setInterval(updateDashboardData, 10000);
