import subprocess
import sys
import shutil

def run_setup():
    # Use 'uv' if available for much faster installs
    has_uv = shutil.which("uv") is not None
    pkg_manager = ["uv", "pip"] if has_uv else [sys.executable, "-m", "pip"]
    
    print(f"Installing requirements using {'uv' if has_uv else 'pip'}...")
    try:
        subprocess.run([*pkg_manager, "install", "-r", "requirements.txt"], check=True)
    except Exception as e:
        print(f"Error during requirements install: {e}")
        sys.exit(1)

    print("Installing Playwright browsers...")
    try:
        subprocess.run([sys.executable, "-m", "playwright", "install"], check=True)
    except Exception as e:
        print(f"Error during Playwright install: {e}")

    mgr_name = "uv" if has_uv else "pip"
    print(f"\n✅ Setup complete! Systems ready via {mgr_name}.")
    print("Run 'python main.py' to bring JARVIS online, sir.")

if __name__ == "__main__":
    run_setup()

