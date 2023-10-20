# Author: Rhyanna Arisya Zaharom

import unittest
from unittest.mock import Mock, patch
from elasticsearch import Elasticsearch
from mitre_attacks_donut_chart import create_top_mitre_attacks_donut_chart

class TestMitreAttacksDonutChart(unittest.TestCase):

    @patch('mitre_attacks_donut_chart.Elasticsearch')
    def test_create_top_mitre_attacks_donut_chart(self, mock_es):
        """
        Test Case 1
        Test if the function correctly processes and returns the top MITRE attacks
        based on the provided Elasticsearch search results.
        """
        # Mock Elasticsearch search results
        mock_search_result = {
            'aggregations': {
                'top_attacks': {
                    'buckets': [
                        {
                            'key': 'T1234',
                            'attack_name': {'buckets': [{'key': 'Initial Access'}]},
                            'doc_count': 5
                        },
                        {
                            'key': 'T5678',
                            'attack_name': {'buckets': [{'key': 'Execution'}]},
                            'doc_count': 3
                        }
                    ]
                }
            }
        }

        # Configure the mock Elasticsearch instance to return the mock search results
        mock_es.search.return_value = mock_search_result

        # Call the function
        result = create_top_mitre_attacks_donut_chart(mock_es)

        # Check if the result contains the expected values
        self.assertIn('T1234', result)
        self.assertIn('T5678', result)


    @patch('mitre_attacks_donut_chart.Elasticsearch')
    def test_no_data_available(self, mock_es):
        """
        Test Case 2
        Test if the function returns the appropriate message when there are no MITRE attacks
        in the Elasticsearch search results.
        """
        # Mock Elasticsearch search results with no data
        mock_search_result = {
            'aggregations': {
                'top_attacks': {
                    'buckets': []
                }
            }
        }

        # Configure the mock Elasticsearch instance to return the mock search results
        mock_es.search.return_value = mock_search_result

        # Call the function
        result = create_top_mitre_attacks_donut_chart(mock_es)

        # Check if the result is "No data available"
        self.assertEqual(result, "No data available")

    @patch('mitre_attacks_donut_chart.Elasticsearch')
    def test_single_attack_technique(self, mock_es):
        """
        Test Case 3
        Test if the function correctly processes and returns a single MITRE attack
        based on the provided Elasticsearch search results.
        """
        # Mock Elasticsearch search results with a single attack technique
        mock_search_result = {
            'aggregations': {
                'top_attacks': {
                    'buckets': [
                        {
                            'key': 'T9999',
                            'attack_name': {'buckets': [{'key': 'Persistence'}]},
                            'doc_count': 7
                        }
                    ]
                }
            }
        }

        # Configure the mock Elasticsearch instance to return the mock search results
        mock_es.search.return_value = mock_search_result

        # Call the function
        result = create_top_mitre_attacks_donut_chart(mock_es)

        # Check if the result contains the expected values
        self.assertIn('T9999', result)


    @patch('mitre_attacks_donut_chart.Elasticsearch')
    def test_invalid_data_structure(self, mock_es):
        """
        Test Case 4
        Test if the function raises an exception when provided with an invalid data structure
        from the Elasticsearch search results.
        """
        # Mock Elasticsearch search results with an invalid data structure
        mock_search_result = {
            'invalid_key': {}
        }

        # Configure the mock Elasticsearch instance to return the mock search results
        mock_es.search.return_value = mock_search_result

        # Call the function and expect an exception or a specific behavior
        with self.assertRaises(Exception):
            create_top_mitre_attacks_donut_chart(mock_es)


    @patch('mitre_attacks_donut_chart.Elasticsearch')
    def test_elasticsearch_search_exception(self, mock_es):
        """
        Test Case 5
        Test if the function raises an exception when there's an error while searching
        with Elasticsearch.
        """
        # Mock an exception when trying to search with Elasticsearch
        mock_es.search.side_effect = Exception("Elasticsearch search error")

        # Call the function and expect an exception
        with self.assertRaises(Exception):
            create_top_mitre_attacks_donut_chart(mock_es)


if __name__ == '__main__':
    unittest.main(verbosity=2)
