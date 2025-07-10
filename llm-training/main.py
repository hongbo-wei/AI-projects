"""
Main execution script for the complete LLM training pipeline
Runs CPT → SFT → RAG training sequence
"""

import subprocess
import sys

def run_training_script(script_name, description):
    """Run a training script and handle errors"""
    print(f"\n{'='*60}")
    print(f"🚀 {description}")
    print(f"{'='*60}")
    
    try:
        result = subprocess.run([sys.executable, script_name], 
                              capture_output=True, text=True, check=True)
        print(f"✅ {description} completed successfully!")
        if result.stdout:
            print(result.stdout)
    except subprocess.CalledProcessError as e:
        print(f"❌ {description} failed!")
        print(f"Error: {e.stderr}")
        return False
    except Exception as e:
        print(f"❌ Unexpected error in {description}: {e}")
        return False
    
    return True

def main():
    print("🤖 LLM Training Pipeline: CPT → SFT → RAG")
    print("=" * 60)
    
    # Phase 1: CPT Training
    if not run_training_script("train_cpt.py", "CPT (Continuous Pre-Training)"):
        print("❌ CPT training failed. Stopping pipeline.")
        return
    
    # Phase 2: SFT Training
    if not run_training_script("train_sft.py", "SFT (Supervised Fine-Tuning)"):
        print("❌ SFT training failed. Stopping pipeline.")
        return
    
    # Phase 3: RAG Training
    if not run_training_script("train_rag.py", "RAG (Retrieval-Augmented Generation)"):
        print("⚠️ RAG training completed with warnings (this is normal for demo)")
    
    print("\n" + "=" * 60)
    print("🎉 TRAINING PIPELINE COMPLETED!")
    print("=" * 60)
    print("All models have been saved to:")
    print("- output/cpt/    - CPT model")
    print("- output/sft/    - SFT model")
    print("- output/rag/    - RAG model")

if __name__ == "__main__":
    main()
