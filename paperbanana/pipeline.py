from .agents import Retriever, Planner, Stylist, Visualizer, Critic
from .config import config

class Pipeline:
    def __init__(self, iterations=config.DEFAULT_ITERATIONS):
        self.iterations = iterations
        self.retriever = Retriever()
        self.planner = Planner()
        self.stylist = Stylist()
        self.visualizer = Visualizer()
        self.critic = Critic()

    def generate(self, input_text: str) -> None:
        """
        Orchestrates the generation process:
        1. Retrieval
        2. Planning
        3. Styling
        4. Visualization
        5. Iterative Refinement
        """
        print("Gathering reference examples...")
        examples = self.retriever.retrieve(input_text)
        
        print("Generating initial plan...")
        initial_plan = self.planner.plan(input_text, examples)
        
        print("Styling the plan...")
        styled_plan = self.stylist.style(initial_plan)
        
        current_description = styled_plan
        
        for i in range(self.iterations):
            print(f"Iteration {i+1}/{self.iterations}...")
            
            # Generate Image
            image = self.visualizer.visualize(current_description)
            if image:
                image.save(f"{config.OUTPUT_DIR}/iteration_{i+1}.png")
                print(f"Saved iteration_{i+1}.png")
            else:
                print("Failed to generate image.")
                break
            
            # Critique
            print("Critiquing...")
            critique_result = self.critic.critique(image, input_text, current_description)
            
            suggestions = critique_result.get("critic_suggestions", "No suggestions")
            refined_description = critique_result.get("revised_description", current_description)
            
            print(f"Critique: {suggestions}")
            
            # Update Plan
            current_description = refined_description
            
        print("Generation complete.")

    def generate_batch(self, inputs: list[str]) -> None:
        """
        Runs generation for multiple inputs in parallel.
        """
        import concurrent.futures
        
        print(f"Starting batch generation for {len(inputs)} inputs...")
        
        with concurrent.futures.ThreadPoolExecutor() as executor:
            # map inputs to the generate method
            futures = [executor.submit(self.generate, input_text) for input_text in inputs]
            
            # Wait for all to complete
            for future in concurrent.futures.as_completed(futures):
                try:
                    future.result()
                except Exception as e:
                    print(f"Error in batch generation: {e}")
                    
        print("Batch generation complete.")
