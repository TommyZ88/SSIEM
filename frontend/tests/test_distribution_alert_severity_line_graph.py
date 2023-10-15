import unittest
from unittest.mock import Mock
from elasticsearch import Elasticsearch
import json
from distribution_alert_severity_line_graph import create_distribution_alert_severity_line_graph

# Import the function to be tested here

class TestCreateDistributionAlertSeverityLineGraph(unittest.TestCase):

    def test_create_distribution_alert_severity_line_graph_with_valid_data(self):
        # Create a mock Elasticsearch instance
        es = Mock(spec=Elasticsearch)

        # Mock Elasticsearch search results
        fake_aggregations = {
            "severity_over_time": {
                "buckets": [
                    {
                        "key_as_string": "2023-10-14T00:00:00",
                        "severity_levels": {
                            "buckets": [
                                {"key": "low", "doc_count": 10},
                                {"key": "medium", "doc_count": 20},
                            ]
                        }
                    },
                    {
                        "key_as_string": "2023-10-14T00:05:00",
                        "severity_levels": {
                            "buckets": [
                                {"key": "medium", "doc_count": 15},
                                {"key": "high", "doc_count": 5},
                            ]
                        }
                    }
                ]
            }
        }
        es.search.return_value = {"aggregations": fake_aggregations}

        # Call the function to be tested
        result = create_distribution_alert_severity_line_graph(es)

        # Verify that the result is a JSON string
        self.assertIsInstance(result, str)

        # Parse the JSON and check its structure
        result_data = json.loads(result)
        self.assertIsInstance(result_data, dict)
        self.assertIn("data", result_data)
        self.assertIn("layout", result_data)

    def test_create_distribution_alert_severity_line_graph_with_no_data(self):
        # Create a mock Elasticsearch instance
        es = Mock(spec=Elasticsearch);

        # Mock Elasticsearch search results with no buckets
        es.search.return_value = {"aggregations": {"severity_over_time": {"buckets": []}}};

        # Call the function to be tested
        result = create_distribution_alert_severity_line_graph(es);

        # Verify that the result is "No data available"
        self.assertEqual(result, "No data available");

if __name__ == '__main__':
    unittest.main()