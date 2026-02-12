import unittest
from unittest.mock import MagicMock, patch
import json
import base64
from paperbanana.client import OpenWebUIClient
from paperbanana.config import config
from PIL import Image
import io

class TestOpenWebUIClient(unittest.TestCase):
    def setUp(self):
        config.OPENWEBUI_BASE_URL = "http://mock-openwebui:3000/api"
        config.OPENWEBUI_MODEL = "gemma:12b"
        config.OPENWEBUI_IMAGE_MODEL = "flux-2-klein-4b"
        self.client = OpenWebUIClient()

    @patch('requests.post')
    def test_generate_text_simple(self, mock_post):
        # Mock Response
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.json.return_value = {
            "choices": [{"message": {"content": "Mocked Response"}}]
        }
        mock_post.return_value = mock_response

        response = self.client.generate_text("Hello")
        
        self.assertEqual(response, "Mocked Response")
        
        # Verify Request
        args, kwargs = mock_post.call_args
        self.assertEqual(args[0], "http://mock-openwebui:3000/api/chat/completions")
        self.assertEqual(kwargs['json']['model'], "gemma:12b")
        self.assertEqual(kwargs['json']['messages'][0]['content'], "Hello")

    @patch('requests.post')
    def test_generate_text_multimodal(self, mock_post):
        # Mock Response
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.json.return_value = {
            "choices": [{"message": {"content": "Image Analysis"}}]
        }
        mock_post.return_value = mock_response

        # input
        img = Image.new('RGB', (10, 10), color='red')
        prompt = ["Describe this:", img]
        
        response = self.client.generate_text(prompt)
        
        self.assertEqual(response, "Image Analysis")
        
        # Verify Request
        args, kwargs = mock_post.call_args
        json_body = kwargs['json']
        content = json_body['messages'][0]['content']
        self.assertEqual(len(content), 2)
        self.assertEqual(content[0]['type'], "text")
        self.assertEqual(content[1]['type'], "image_url")
        self.assertTrue(content[1]['image_url']['url'].startswith("data:image/png;base64,"))

    @patch('requests.post')
    def test_generate_image(self, mock_post):
        # Mock Response (b64_json)
        mock_response = MagicMock()
        mock_response.status_code = 200
        
        # Create a tiny valid png for mocking
        img_byte_arr = io.BytesIO()
        Image.new('RGB', (10, 10), color='blue').save(img_byte_arr, format='PNG')
        b64_str = base64.b64encode(img_byte_arr.getvalue()).decode('utf-8')
        
        mock_response.json.return_value = {
            "data": [{"b64_json": b64_str}]
        }
        mock_post.return_value = mock_response

        img = self.client.generate_image("A blue square")
        
        self.assertIsNotNone(img)
        self.assertIsInstance(img, Image.Image)
        
        # Verify Request
        args, kwargs = mock_post.call_args
        self.assertEqual(args[0], "http://mock-openwebui:3000/api/images/generations")
        self.assertEqual(kwargs['json']['model'], "flux-2-klein-4b")
        self.assertEqual(kwargs['json']['prompt'], "A blue square")

if __name__ == '__main__':
    unittest.main()
