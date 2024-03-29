function renderCharts(data) {
    
    if (data.total_agent_alerts_bar_graph) {
        var jsonData = JSON.parse(data.total_agent_alerts_bar_graph);
        Plotly.react('total_agent_alerts_bar_graph', jsonData.data, jsonData.layout);
    } else {
        console.error('total_agent_alerts_bar_graph is undefined in the response');
    }

    if (data.alerts_per_agent_area_chart) {
        var jsonData = JSON.parse(data.alerts_per_agent_area_chart);
        Plotly.react('alerts_per_agent_area_chart', jsonData.data, jsonData.layout);
    } else {
        console.error('alerts_per_agent_area_chart is undefined in the response');
    }

    if (data.alert_severity_pie_chart) { 
        var jsonData = JSON.parse(data.alert_severity_pie_chart); 
        Plotly.react('alert_severity_pie_chart', jsonData.data, jsonData.layout)
    } else {
        console.error('alert_severity_pie_chart is undefined in the response');
    }

    if (data.distribution_alert_severity_line_graph) {
        var jsonData = JSON.parse(data.distribution_alert_severity_line_graph);
        Plotly.react('distribution_alert_severity_line_graph', jsonData.data, jsonData.layout);
    } else {
        console.error('distribution_alert_severity_line_graph is undefined in the response');
    }

    if (data.top_events_donut_chart) {
        var jsonData = JSON.parse(data.top_events_donut_chart); 
        Plotly.react('top_events_donut_chart', jsonData.data, jsonData.layout)
    } else {
        console.error('top_event_donut_chart is undefined in the response');
    }

    if (data.auth_failures_histogram) {
        var jsonData = JSON.parse(data.auth_failures_histogram);
        Plotly.react('auth_failures_histogram', jsonData.data, jsonData.layout);
    } else {
        console.error('auth_failures_histogram is undefined in the response');
    }

    if (data.mitre_attacks_donut_chart) {
        var jsonData = JSON.parse(data.mitre_attacks_donut_chart); 
        Plotly.react('mitre_attacks_donut_chart', jsonData.data, jsonData.layout)
    } else {
        console.error('mitre_attacks_donut_chart is undefined in the response');
    } 
}


function updateDashboardData() {
    fetch('/dashboard_data')
        .then(response => response.json())
        .then(data => {
            renderCharts(data);

            if (data.agent_info_table) {
                document.getElementById('agent_info_table').innerHTML = "<h2>Agent Information</h2>" + data.agent_info_table;
            } else {
                console.error('agent_info_table is undefined in the response');
            }

            if (data.event_logs_table) {
                document.getElementById('event_logs_table').innerHTML = "<h2>Event Logs</h2>" + data.event_logs_table;
            } else {
                console.error('event_logs_table is undefined in the response');
            }
        })
        .catch(error => console.error('Error fetching the dashboard data:', error));
}

updateDashboardData(); 
setInterval(updateDashboardData, 10000);
