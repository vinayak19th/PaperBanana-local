from .agents import Retriever, Planner, Stylist, Visualizer, Critic, SketchGenerator, DrawIOBuilder, Renderer, DiagramCritic
from .config import config
import os

class Pipeline:
    def __init__(self, iterations=config.DEFAULT_ITERATIONS):
        self.iterations = iterations
        self.retriever = Retriever()
        self.planner = Planner()
        self.stylist = Stylist()
        # Initialize agents
        self.visualizer = Visualizer()
        self.critic = Critic()
        self.sketch_generator = SketchGenerator()
        self.drawio_builder = DrawIOBuilder()
        self.renderer = Renderer()
        self.diagram_critic = DiagramCritic()

    def generate(self, input_text: str) -> None:
        """
        Orchestrates the generation process:
        1. Retrieval
        2. Planning
        3. Styling
        4. Visualization (Image or Draw.io)
        5. Iterative Refinement
        """
        print("Gathering reference examples...")
        examples = self.retriever.retrieve(input_text)
        
        print("Generating initial plan...")
        initial_plan = self.planner.plan(input_text, examples)
        
        print("Styling the plan...")
        styled_plan = self.stylist.style(initial_plan)
        
        current_description = styled_plan
        
        # Branch based on output format
        if config.OUTPUT_FORMAT == 'drawio':
            self._generate_drawio(input_text, current_description)
        else:
            self._generate_image(input_text, current_description)

    def _generate_image(self, input_text: str, current_description: str):
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
            
        print("Generation complete (Image).")

    def _generate_drawio(self, input_text: str, current_description: str):
        print("Starting Draw.io generation workflow...")
        
        # 1. Generate Sketch (Prototype)
        print("Generating prototype sketch...")
        sketch = self.sketch_generator.sketch(current_description)
        if sketch:
            sketch.save(f"{config.OUTPUT_DIR}/sketch_prototype.png")
            print("Saved sketch_prototype.png")
        else:
            print("Failed to generate sketch.")
            # Continue anyway, relying on text description
        
        # 2. Critique Sketch (Visual Concept)
        print("Critiquing sketch...")
        # We use the standard Critic here to refine the description based on the sketch
        if sketch:
            critique_result = self.critic.critique(sketch, input_text, current_description)
            current_description = critique_result.get("revised_description", current_description)
            print(f"Refined description based on sketch: {critique_result.get('critic_suggestions')}")

        # 3. Build Draw.io XML
        print("Building Draw.io XML...")
        xml_content = self.drawio_builder.build(current_description)
        
        # Save initial XML
        with open(f"{config.OUTPUT_DIR}/diagram_v0.drawio", "w") as f:
            f.write(xml_content)
            
        # 4. Iterative Refinement of XML
        for i in range(self.iterations):
            print(f"Draw.io Iteration {i+1}/{self.iterations}...")
            
            # Render XML to Image for Critique
            render_path = f"{config.OUTPUT_DIR}/drawio_render_{i}.png"
            xml_path = f"{config.OUTPUT_DIR}/diagram_v{i}.drawio"
            
            # Save current XML for rendering
            with open(xml_path, "w") as f:
                f.write(xml_content)
                
            success = self.renderer.render(xml_path, render_path)
            
            if not success:
               print("Rendering failed. Aborting critique loop.")
               break
               
            print(f"Rendered preview to {render_path}")
            
            # Load rendered image for critique
            from PIL import Image
            try:
                rendered_image = Image.open(render_path)
            except Exception as e:
                print(f"Failed to open rendered image: {e}")
                break
                
            # Critique Diagram (Technical/LaTeX check)
            print("Critiquing diagram...")
            suggestions = self.diagram_critic.critique(rendered_image, input_text)
            print(f"Critique Suggestions: {suggestions}")
            
            if "No changes needed" in suggestions or "no changes needed" in suggestions.lower():
                print("Critic implies diagram is good. Stopping.")
                break
                
            # Refine XML
            print("Refining XML...")
            xml_content = self.drawio_builder.build(current_description, critique_suggestions=suggestions)
            
        # Save Final
        final_path = f"{config.OUTPUT_DIR}/final_diagram.drawio"
        with open(final_path, "w") as f:
            f.write(xml_content)
        print(f"Generation complete. Saved to {final_path}")

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
