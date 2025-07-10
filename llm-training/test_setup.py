"""
Simple test to verify the pipeline setup
"""

def test_data_files():
    """Test that all data files exist and are valid"""
    import os
    import json
    
    # Check pretrain.txt
    assert os.path.exists("data/pretrain.txt"), "pretrain.txt not found"
    with open("data/pretrain.txt", "r") as f:
        lines = f.readlines()
        assert len(lines) > 0, "pretrain.txt is empty"
    
    # Check sft.jsonl
    assert os.path.exists("data/sft.jsonl"), "sft.jsonl not found"
    with open("data/sft.jsonl", "r") as f:
        for line in f:
            data = json.loads(line)
            assert "prompt" in data and "response" in data, "Invalid SFT format"
    
    # Check rag.jsonl
    assert os.path.exists("data/rag.jsonl"), "rag.jsonl not found"
    with open("data/rag.jsonl", "r") as f:
        for line in f:
            data = json.loads(line)
            assert "question" in data and "answer" in data, "Invalid RAG format"
    
    print("✅ All data files are valid")

def test_output_directories():
    """Test that output directories exist"""
    import os
    
    directories = ["output/cpt", "output/sft", "output/rag"]
    for dir_path in directories:
        assert os.path.exists(dir_path), f"Directory {dir_path} not found"
    
    print("✅ All output directories exist")

def test_python_files():
    """Test that all Python files have valid syntax"""
    import py_compile
    
    files = ["train_cpt.py", "train_sft.py", "train_rag.py", "main.py"]
    for file_path in files:
        try:
            py_compile.compile(file_path, doraise=True)
        except py_compile.PyCompileError as e:
            raise AssertionError(f"Syntax error in {file_path}: {e}")
    
    print("✅ All Python files have valid syntax")

if __name__ == "__main__":
    print("🔍 Testing LLM Training Pipeline Setup...")
    test_data_files()
    test_output_directories()
    test_python_files()
    print("🎉 All tests passed! The pipeline is ready to run.")
