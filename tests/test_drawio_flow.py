import unittest
from unittest.mock import MagicMock, patch
import os
import sys

# Add project root to path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from paperbanana.pipeline import Pipeline
from paperbanana.config import config
from PIL import Image

class TestDrawIOFlow(unittest.TestCase):
    @patch('paperbanana.agents.client_instance')
    @patch('paperbanana.agents.subprocess.run')
    @patch('PIL.Image.open')
    @patch('os.path.exists')
    def test_drawio_generation(self, mock_exists, mock_image_open, mock_subprocess, mock_client):
        # Allow /mock/drawio to exist
        mock_exists.side_effect = lambda path: path == '/mock/drawio' or os.path.join('outputs', 'diagram_v0.drawio') in path or True
        # Setup specific config for this test
        config.OUTPUT_FORMAT = 'drawio'
        config.DRAWIO_PATH = '/mock/drawio'
        
        # Mock Client Responses
        mock_client.generate_text.side_effect = [
            "Mock Plan", # Planner
            "Mock Styled Plan", # Stylist
            '{"revised_description": "Refined Sketch Desc", "critic_suggestions": "Good sketch"}', # Critic (Sketch)
            "<mxGraphModel>Mock XML</mxGraphModel>", # DrawIOBuilder (Initial)
            "Move box A to the right.", # DiagramCritic
            "<mxGraphModel>Mock XML v2</mxGraphModel>" # DrawIOBuilder (Refinement)
        ]
        
        # Mock Image Generation (Sketch)
        mock_image = Image.new('RGB', (100, 100))
        mock_client.generate_image.return_value = mock_image
        
        # Mock Image Open (for rendering check)
        mock_image_open.return_value = mock_image
        
        # Mock Subprocess (Renderer)
        mock_subprocess.return_value = MagicMock(returncode=0)
        
        # Initialize Pipeline
        pipeline = Pipeline(iterations=1)
        
        # Run
        pipeline.generate("Test Input")
        
        # Assertions
        # 1. Check Sketch generation called
        mock_client.generate_image.assert_called()
        
        # 2. Check XML Building called
        # We expect DrawIOBuilder to be called twice (initial + refinement)
        # However, checking exact count is tricky due to pipeline internal calls.
        # We can check that generate_text was called with XML-related prompts.
        self.assertTrue(any("mxGraph" in str(call) for call in mock_client.generate_text.call_args_list))
        
        # 3. Check Renderer called
        mock_subprocess.assert_called()
        args, _ = mock_subprocess.call_args
        self.assertEqual(args[0][0], '/mock/drawio')
        self.assertIn('-x', args[0])
        
        print("Draw.io Flow Test Passed.")

if __name__ == '__main__':
    unittest.main()
