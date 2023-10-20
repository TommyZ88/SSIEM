# Author: Rhyanna Arisya Zaharom

import unittest
from unittest.mock import Mock, patch
from event_logs_table import create_event_logs_table

class TestCreateEventLogsTable(unittest.TestCase):

    @patch('event_logs_table.Elasticsearch')
    def test_create_event_logs_table(self, MockedElasticsearch):
        """
        Test Case 1
        Test if the function correctly processes and returns an HTML table with event logs
        when provided with valid Elasticsearch search results.
        """
        # Mocking the response from Elasticsearch
        mock_es_instance = MockedElasticsearch.return_value
        mock_es_instance.search.return_value = {
            'hits': {
                'hits': [
                    {
                        "_source": {
                            "@timestamp": "2023-10-13T12:00:00.000Z",
                            "agent": {"name": "TestAgent", "ip": "192.168.1.1"},
                            "rule": {"description": "TestEvent", "level": "High"}
                        }
                    }
                ]
            }
        }

        result = create_event_logs_table(mock_es_instance)
        expected_string = "<th>Timestamp</th>"

        # Assert that the expected string (part of the HTML table) is present in the result
        self.assertIn(expected_string, result)

    @patch('event_logs_table.Elasticsearch')
    def test_empty_event_logs(self, MockedElasticsearch):
        """
        Test Case 2
        Test if the function correctly handles and returns an HTML table with headers only
        when there are no event logs in the Elasticsearch search results.
        """
        # Mocking an empty response from Elasticsearch
        mock_es_instance = MockedElasticsearch.return_value
        mock_es_instance.search.return_value = {
            'hits': {
                'hits': []
            }
        }

        result = create_event_logs_table(mock_es_instance)

        # Expected HTML table headers
        expected_headers = ["<th>Timestamp</th>", "<th>Agent Name</th>", "<th>IP Address</th>", "<th>Event</th>", "<th>Severity</th>"]

        # Assert that the expected headers are present in the result
        for header in expected_headers:
            self.assertIn(header, result)

        # Assert that there are no table rows in the result
        self.assertNotIn("<tr>", result.split("</thead>")[-1])  # Checking only after the table headers


    @patch('event_logs_table.Elasticsearch')
    def test_invalid_data_structure(self, MockedElasticsearch):
        """
        Test Case 3
        Test if the function raises an exception when provided with an invalid data structure from Elasticsearch.
        """
        # Mocking an invalid response structure from Elasticsearch
        mock_es_instance = MockedElasticsearch.return_value
        mock_es_instance.search.return_value = {
            'invalid_key': {}
        }

        # Call the function and expect an exception
        with self.assertRaises(Exception):
            create_event_logs_table(mock_es_instance)

    @patch('event_logs_table.Elasticsearch')
    def test_elasticsearch_search_exception(self, MockedElasticsearch):
        """
        Test Case 4
        Test if the function raises an exception when there's an error while searching with Elasticsearch.
        """
        # Mock an exception when trying to search with Elasticsearch
        mock_es_instance = MockedElasticsearch.return_value
        mock_es_instance.search.side_effect = Exception("Elasticsearch search error")

        # Call the function and expect an exception
        with self.assertRaises(Exception):
            create_event_logs_table(mock_es_instance)

if __name__ == '__main__':
    unittest.main(verbosity=2)
