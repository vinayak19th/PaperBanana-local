import unittest
from unittest.mock import MagicMock, patch
from paperbanana.pipeline import Pipeline
from PIL import Image
import io

class TestPipeline(unittest.TestCase):
    @patch("paperbanana.agents.client_instance")
    def test_pipeline_flow(self, mock_client_instance):
        # Mock responses
        # Planner response -> Stylist response -> Critic response (text part)
        mock_client_instance.generate_text.side_effect = [
            "Mock Initial Plan",   # Planner
            "Mock Styled Plan",    # Stylist
            '{"critic_suggestions": "Add labels", "revised_description": "Refined Plan"}' # Critic
        ]
        
        # Visualizer response
        mock_image = Image.new('RGB', (1, 1), color='red')
        mock_client_instance.generate_image.return_value = mock_image
        
        # Run Pipeline
        pipeline = Pipeline(iterations=1)
        pipeline.generate("Test Input")
        
        # Verify calls
        # We expect at least 3 calls to generate_text (Plan, Style, Critic)
        self.assertTrue(mock_client_instance.generate_text.call_count >= 3)
        
        # Visualizer called?
        mock_client_instance.generate_image.assert_called()

    @patch("paperbanana.agents.client_instance")
    def test_pipeline_batch_flow(self, mock_client_instance):
        # Setup mocks for batch execution
        # For 2 inputs, each with 1 iteration:
        # Each input needs: Plan, Style, Image, Critic
        # Total text calls per input: 3
        # Total image calls per input: 1
        
        # We need to provide enough side effects for all threads
        # Since threads run in parallel, order is not guaranteed between threads, 
        # but within a thread it should be Plan -> Style -> Critic
        
        # Simulating responses
        def side_effect_text(prompt, model=None):
            if "scientific illustrator" in str(prompt):
                return "Mock Initial Plan"
            elif "design expert" in str(prompt):
                return "Mock Styled Plan"
            elif "Visual Designer" in str(prompt):
                return '{"critic_suggestions": "Nice", "revised_description": "Final"}'
            return "Generic Response"

        mock_client_instance.generate_text.side_effect = side_effect_text
        mock_client_instance.generate_image.return_value = Image.new('RGB', (1, 1), color='blue')

        pipeline = Pipeline(iterations=1)
        inputs = ["Input 1", "Input 2"]
        pipeline.generate_batch(inputs)
        
        # Verify that we had calls corresponding to 2 inputs
        # 2 inputs * 3 text calls (Plan, Style, Critic) = 6 text calls minimum
        self.assertTrue(mock_client_instance.generate_text.call_count >= 6)
        
        # 2 inputs * 1 image call = 2 image calls
        self.assertEqual(mock_client_instance.generate_image.call_count, 2)

if __name__ == "__main__":
    unittest.main()
