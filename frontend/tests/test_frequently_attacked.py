import unittest
from unittest.mock import Mock, patch
from frequently_attacked import create_frequently_attacked_agents_bar_graph
import json
from elasticsearch import Elasticsearch


class testFrequentlyAttackedAgents(unittest.TestCase):

    @patch('frequently_attacked.Elasticsearch')
    def test_chart_Agents(self, MockedElasticsearch):
        """
        Test Case 1 (3 agents available)
        """

        #Mock define expected data
        expected_data = {
            "aggregations": {
                "hosts": {
                    "buckets": [
                        {"key": "agent1", "doc_count": 3},
                        {"key": "agent2", "doc_count": 0},
                        {"key": "agent3", "doc_count": 0},
                        {"key": "agent4", "doc_count": 0}
                    ]
                }
            }
        }

        # Mock the response from Elasticsearch
        mock_es_instance = MockedElasticsearch.return_value
        mock_es_instance.search.return_value = expected_data

        # Now call your function and test the result
        result = create_frequently_attacked_agents_bar_graph(mock_es_instance)
        
        # Add your assertions based on the expected result

    @patch('frequently_attacked.Elasticsearch')
    def test_attack_count(self, MockedElasticsearch):
        """
        Test Case 2 (Tests to check the attack count)
        """

        # Mock define expected data
        expected_data = {
            "aggregations": {
                "hosts": {
                    "buckets": [
                        {"key": "agent1", "doc_count": 5},
                        {"key": "agent2", "doc_count": 10},
                        {"key": "agent3", "doc_count": 15},
                        {"key": "agent4", "doc_count": 20}
                    ]
                }
            }
        }

        # Mock the response from Elasticsearch
        mock_es_instance = MockedElasticsearch.return_value
        mock_es_instance.search.return_value = expected_data

        # Now call your function and test the result
        result = create_frequently_attacked_agents_bar_graph(mock_es_instance)

        # Parse the result JSON
        result_json = json.loads(result)

        # Check the attack count for each agent
        for i, bucket in enumerate(expected_data['aggregations']['hosts']['buckets']):
            self.assertEqual(result_json['data'][i]['y'], [bucket['doc_count']])

    @patch('frequently_attacked.Elasticsearch')
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
            
        }

        # Call your function
        result = create_frequently_attacked_agents_bar_graph(mock_es_instance)
        
        # Add your assertions based on the expected result
        # You can use assertions to check if the result contains the expected values.
        self.assertEqual(mock_es_instance.nodes.info.call_count, 0)

    @patch('frequently_attacked.Elasticsearch')
    def test_empty_data(self, MockedElasticsearch):
        """
        Test Case 4 (empty data test)
        """

        # Mock define expected data
        expected_data = {
            "aggregations": {
                "hosts": {
                    "buckets": []
                }
            }
        }

        # Mock the response from Elasticsearch
        mock_es_instance = MockedElasticsearch.return_value
        mock_es_instance.search.return_value = expected_data

        # Now call your function and test the result
        result = create_frequently_attacked_agents_bar_graph(mock_es_instance)
        

        # Parse the result JSON
        result_json = json.loads(result)

        # Check if the result is an empty graph
        self.assertEqual(len(result_json['data']), 0)

if __name__ == "__main__":
    unittest.main(verbosity=2)

