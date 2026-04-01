import os
import re

def revert_branding():
    base_dir = r"c:\Users\Pavan\OneDrive\Desktop\JARVIS"
    replacements = [
        (r"\bMark II\b", "JARVIS"),
        (r"\bMarkII\b", "Jarvis"),
        (r"\bmark_ii\b", "jarvis"),
        (r"\bmarkii\b", "jarvis"),
        (r"JarvisProjects", "JarvisProjects"),
        (r"jarvis_project", "jarvis_project"),
    ]
    
    extensions = (".py", ".txt", ".md", ".json")
    
    for root, dirs, files in os.walk(base_dir):
        if ".git" in dirs:
            dirs.remove(".git")
        if "__pycache__" in dirs:
            dirs.remove("__pycache__")
            
        for file in files:
            if file.endswith(extensions):
                path = os.path.join(root, file)
                try:
                    with open(path, "r", encoding="utf-8") as f:
                        content = f.read()
                    
                    new_content = content
                    for pattern, repl in replacements:
                        new_content = re.sub(pattern, repl, new_content)
                    
                    if new_content != content:
                        with open(path, "w", encoding="utf-8") as f:
                            f.write(new_content)
                        print(f"Reverted: {path}")
                except Exception as e:
                    print(f"Error processing {path}: {e}")

if __name__ == "__main__":
    revert_branding()
