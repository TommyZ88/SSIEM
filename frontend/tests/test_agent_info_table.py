import unittest
from unittest.mock import Mock
from elasticsearch import Elasticsearch
from pandas import DataFrame
from datetime import datetime
from agent_info_table import create_agent_info_table


class TestCreateAgentInfoTable(unittest.TestCase):

    def test_create_agent_info_table_with_valid_data(self):
        # Create a mock Elasticsearch instance
        es = Mock(spec=Elasticsearch)

        # Mock Elasticsearch search results
        fake_hits = {
            "hits": {
                "hits": [
                    {
                        "_source": {
                            "id": "agent1",
                            "name": "Agent 1",
                            "ip": "192.168.1.1",
                            "status": "active",
                            "timestamp": "2023-10-14T10:00:00.000Z"
                        }
                    },
                    {
                        "_source": {
                            "id": "agent2",
                            "name": "Agent 2",
                            "ip": "192.168.1.2",
                            "status": "inactive",
                            "timestamp": "2023-10-14T09:30:00.000Z"
                        }
                    }
                ]
            }
        }
        es.search.return_value = fake_hits

        # Call the function to be tested
        result = create_agent_info_table(es)

        # Verify that the result contains expected data
        expected_result = DataFrame([
            ("agent1", "Agent 1", "192.168.1.1", "active"),
            ("agent2", "Agent 2", "192.168.1.2", "inactive")
        ], columns=["Agent ID", "Name", "IP", "Status"]).to_html(index=False, classes='table table-striped')
        self.assertEqual(result, expected_result)

    def test_create_agent_info_table_with_empty_data(self):
        # Create a mock Elasticsearch instance
        es = Mock(spec=Elasticsearch)

        # Mock Elasticsearch search results with no hits
        fake_hits = {"hits": {"hits": []}}
        es.search.return_value = fake_hits

        # Call the function to be tested
        result = create_agent_info_table(es)

        # Verify that the result is an empty DataFrame in HTML format
        expected_result = DataFrame(columns=["Agent ID", "Name", "IP", "Status"]).to_html(index=False, classes='table table-striped')
        self.assertEqual(result, expected_result)

    def test_create_agent_info_table_with_invalid_timestamp(self):
        # Create a mock Elasticsearch instance
        es = Mock(spec=Elasticsearch)

        # Mock Elasticsearch search results with an entry containing an invalid timestamp
        fake_hits = {
            "hits": {
                "hits": [
                    {
                        "_source": {
                            "id": "agent1",
                            "name": "Agent 1",
                            "ip": "192.168.1.1",
                            "status": "active",
                            "timestamp": "invalid_timestamp"
                        }
                    }
                ]
            }
        }
        es.search.return_value = fake_hits

        # Call the function to be tested
        result = create_agent_info_table(es)

        # Verify that the result is an empty DataFrame in HTML format (due to invalid timestamp)
        expected_result = DataFrame(columns=["Agent ID", "Name", "IP", "Status"]).to_html(index=False, classes='table table-striped')
        self.assertEqual(result, expected_result)

if __name__ == '__main__':
    unittest.main()
