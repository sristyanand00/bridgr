import sys

def clean_file(path):
    with open(path, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # Replace non-ASCII characters with a space or appropriate tag
    cleaned = "".join([c if ord(c) < 128 else ' ' for c in content])
    
    with open(path, 'w', encoding='utf-8') as f:
        f.write(cleaned)
    print(f"Cleaned {path}")

if __name__ == "__main__":
    clean_file('models/bridgr_final.py')
    clean_file('ml/model_loader.py')
    clean_file('routes/analyze.py')
    clean_file('services/llm_service.py')
