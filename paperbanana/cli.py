import argparse
import sys
from .pipeline import Pipeline
from .config import config

def main():
    parser = argparse.ArgumentParser(description="PaperBanana: Automated Academic Illustration")
    parser.add_argument("--input", required=True, help="Path to input text file containing methodology description.")
    parser.add_argument("--caption", required=False, help="Caption for the diagram.")
    parser.add_argument("--output", required=True, help="Path to save the final output image.")
    parser.add_argument("--iterations", type=int, default=config.DEFAULT_ITERATIONS, help="Number of refinement iterations.")
    
    args = parser.parse_args()
    
    try:
        with open(args.input, "r") as f:
            input_text = f.read()
    except FileNotFoundError:
        print(f"Error: Input file '{args.input}' not found.")
        sys.exit(1)
        
    if args.caption:
        input_text += f"\n\nCaption: {args.caption}"
        
    pipeline = Pipeline(iterations=args.iterations)
    pipeline.generate(input_text)

if __name__ == "__main__":
    main()
