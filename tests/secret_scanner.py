import subprocess
import os
import re

SECRETS_PATTERNS = [
    r"API_KEY",
    r"SECRET",
    r"TOKEN",
    r"PASSWORD",
    r"SERPAPI",
    r"Authorization",
    r"Bearer",
    r"Cookie",
    r"session",
    r"sk-",
    r"key="
]

def scan_files():
    # Get all git tracked files
    result = subprocess.run(["git", "ls-files"], capture_output=True, text=True, shell=True)
    if result.returncode != 0:
        print("Git ls-files failed")
        return
        
    files = result.stdout.strip().split("\n")
    found_secrets = []
    
    for filepath in files:
        if not os.path.exists(filepath):
            continue
        # Skip binary files or cache files we just untracked
        if filepath.endswith(".pyc") or "__pycache__" in filepath:
            continue
            
        try:
            with open(filepath, "r", encoding="utf-8", errors="ignore") as f:
                for line_num, line in enumerate(f, 1):
                    for pattern in SECRETS_PATTERNS:
                        if re.search(pattern, line, re.IGNORECASE):
                            # Classify it
                            classification = "suspected_keyword"
                            # If it matches sk- or key= with something after it, or SERPAPI_API_KEY
                            # Check if it has a hardcoded secret value (e.g. key="xyz" where xyz is not empty/example)
                            # We must NOT print the value in the report, only path, line, and classification.
                            # Skip common config template names like config.example.json or comments
                            if "example" in filepath.lower() or "template" in filepath.lower():
                                continue
                            if "api_key = os.environ" in line or "os.getenv" in line:
                                continue
                            # Avoid flagging standard class/model definitions or imports
                            if "import" in line or "class" in line or "def " in line:
                                continue
                                
                            found_secrets.append({
                                "file": filepath,
                                "line": line_num,
                                "pattern": pattern,
                                "classification": classification
                            })
        except Exception as e:
            print(f"Error reading {filepath}: {e}")
            
    print("=== SECRET SCAN RESULTS ===")
    if not found_secrets:
        print("No suspected secrets found.")
    else:
        for secret in found_secrets:
            print(f"File: {secret['file']} | Line: {secret['line']} | Pattern: {secret['pattern']} | Classification: {secret['classification']}")

if __name__ == "__main__":
    scan_files()
