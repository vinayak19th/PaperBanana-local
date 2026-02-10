from paperbanana.pipeline import Pipeline
import sys

def test_pipeline():
    print("Initializing Pipeline...")
    p = Pipeline(iterations=1) # 1 iteration for speed
    
    print("Generating for 'A diagram of a distributed system'...")
    try:
        p.generate("A diagram of a distributed system")
        print("\n[SUCCESS] Pipeline generation completed without errors.")
    except Exception as e:
        print(f"\n[FAILURE] Pipeline generation failed: {e}")
        sys.exit(1)

if __name__ == "__main__":
    test_pipeline()
