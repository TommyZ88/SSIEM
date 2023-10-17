import unittest
from unittest.mock import Mock, patch
from Create_Pie import create_alert_severity_pie_chart
import json

class testCreateAlertSeverityPieChart(unittest.TestCase):

    @patch('Create_Pie.Elasticsearch')
    def test_chart_Agents(self, MockedElasticsearch):
        """
        Test Case 1 (Tests to check if there is 3 agents connected all with severty level 0 Alerts)
        """

        #Mock define expected data
        expected_data = {
            "aggregations": {
                "severity_count": {
                    "buckets": [
                        {"key": 1, "doc_count": 3},
                        {"key": 2, "doc_count": 0},
                        {"key": 3, "doc_count": 0},
                        {"key": 4, "doc_count": 0}
                    ]
                }
            }
        }

        # Mock the response from Elasticsearch
        mock_es_instance = MockedElasticsearch.return_value
        mock_es_instance.search.return_value = expected_data

        # Now call your function and test the result
        result = create_alert_severity_pie_chart(mock_es_instance)
        
        # Add your assertions based on the expected result

    @patch('Create_Pie.Elasticsearch')
    def test_Severity_Levels(self, MockedElasticsearch):
        """
        Test Case 2 (Tests with custom data: 10 High alerts, 5 Medium alerts, 2 Low alerts)
        """

        # Define expected data for this test
        expected_data = {
            "aggregations": {
                "severity_count": {
                    "buckets": [
                        {"key": "High", "doc_count": 10},
                        {"key": "Medium", "doc_count": 5},
                        {"key": "Low", "doc_count": 2},
                    ]
                }
            }
        }

        # Mock the response from Elasticsearch
        mock_es_instance = MockedElasticsearch.return_value
        mock_es_instance.search.return_value = expected_data

        # Call your function
        result = create_alert_severity_pie_chart(mock_es_instance)
        
        # Add your assertions based on the expected result
        # You can use assertions to check if the result contains the expected values.
    
    @patch('Create_Pie.Elasticsearch')
    def test_node_availability(self, MockedElasticsearch):
        """
        Test 3 (Testing Node data availability)
        """

        # Mock the response from Elasticsearch
        mock_es_instance = MockedElasticsearch.return_value
        mock_es_instance.nodes.info.return_value = {
            "_nodes": {
                "total": 1,
                "successful": 1,
                "failed": 0
            },
            # ... rest of the response
        }

        # Call your function
        result = create_alert_severity_pie_chart(mock_es_instance)
        
        # Add your assertions based on the expected result
        # You can use assertions to check if the result contains the expected values.
        self.assertEqual(mock_es_instance.nodes.info.call_count, 0)


if __name__ == "__main__":
    unittest.main(verbosity=2)

