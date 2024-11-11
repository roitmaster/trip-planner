import unittest
from unittest.mock import patch, MagicMock
import json
from services.openai_helper import get_chatgpt_response

class TestChatGPTFunctions(unittest.TestCase):

    @patch('services.openai_helper.OpenAI')
    def test_get_chatgpt_response_successful_json(self, mock_openai):
        # Mock the OpenAI client response
        mock_response = MagicMock()
        mock_response.choices = [
            MagicMock(message=MagicMock(content='```json\n{"key": "value"}\n```'))
        ]
        mock_openai.return_value.chat.completions.create.return_value = mock_response

        # Call the function with a sample prompt
        prompt = "Provide a JSON response"
        result = get_chatgpt_response(prompt)
        
        # Check that the JSON data is correctly parsed
        expected_result = {"key": "value"}
        self.assertEqual(result, expected_result)

    @patch('services.openai_helper.OpenAI')
    def test_get_chatgpt_response_raw_json(self, mock_openai):
        # Mock the OpenAI client response with a plain JSON response
        mock_response = MagicMock()
        mock_response.choices = [
            MagicMock(message=MagicMock(content='{"key": "value"}'))
        ]
        mock_openai.return_value.chat.completions.create.return_value = mock_response

        # Call the function with a sample prompt
        prompt = "Provide a JSON response"
        result = get_chatgpt_response(prompt)

        # Check that the JSON data is correctly parsed
        expected_result = {"key": "value"}
        self.assertEqual(result, expected_result)

    @patch('services.openai_helper.OpenAI')
    def test_get_chatgpt_response_invalid_json(self, mock_openai):
        # Mock the OpenAI client response with malformed JSON
        mock_response = MagicMock()
        mock_response.choices = [
            MagicMock(message=MagicMock(content='```json\n{"key": "value"'))
        ]
        mock_openai.return_value.chat.completions.create.return_value = mock_response

        # Call the function with a sample prompt and check for JSONDecodeError
        prompt = "Provide a JSON response"
        with self.assertRaises(json.JSONDecodeError):
            get_chatgpt_response(prompt)

    @patch('services.openai_helper.OpenAI')
    def test_get_chatgpt_response_non_json_content(self, mock_openai):
        # Mock the OpenAI client response with non-JSON content
        mock_response = MagicMock()
        mock_response.choices = [
            MagicMock(message=MagicMock(content="I'm not a JSON object."))
        ]
        mock_openai.return_value.chat.completions.create.return_value = mock_response

        # Call the function and check that a JSONDecodeError is raised
        prompt = "Provide a JSON response"
        with self.assertRaises(json.JSONDecodeError):
            get_chatgpt_response(prompt)

if __name__ == '__main__':
    unittest.main()
