import os
import sys
import platform

def check_dependencies():
    """Check if required dependencies are installed"""
    required_packages = {
        'PIL': 'Pillow',
        'numpy': 'numpy',
        'ttkthemes': 'ttkthemes'
    }
    
    missing = []
    for import_name, package_name in required_packages.items():
        try:
            __import__(import_name)
        except ImportError:
            missing.append(package_name)

    return missing
def setup_venv():
    """Set up virtual environment if needed"""
    root_dir = os.path.dirname(os.path.abspath(__file__))
    lazypaper_dir = os.path.join(root_dir, "lazypaper")
    venv_dir = os.path.join(root_dir, "venv")
    requirements_path = os.path.join(root_dir, "requirements.txt")
    # Check if lazypaper folder exists
    if not os.path.exists(lazypaper_dir):
        print(f" Error: 'lazypaper' folder not found in {root_dir}")
        print("Expected structure:")
        print("Project/")
        print("├── lazypaper_launcher.py")
        print("├── requirements.txt")
        print("└── lazypaper/")
        print("    ├── lazypaper.py")
        print("    ├── gui.py")
        print("    └── logic.py")
        return False
    # Check if main file exists
    if not os.path.exists(os.path.join(lazypaper_dir, "lazypaper.py")):
        print(f"Error: lazypaper.py not found in {lazypaper_dir}")
        return False
    # Create requirements.txt if it doesn't exist with updated version
    if not os.path.exists(requirements_path):
        print("Creating requirements.txt file...")
        with open(requirements_path, "w") as f:
            f.write("""Pillow>=10.0.0
numpy>=1.24.0
ttkthemes>=3.2.2
rembg>=2.0.50
onnxruntime>=1.15.0
""")
    
    # Check basic dependencies
    missing_deps = check_dependencies()
    if missing_deps:
        print(f"Missing dependencies: {', '.join(missing_deps)}")
    
    # Check if we're already in a virtual environment
    if hasattr(sys, 'real_prefix') or (hasattr(sys, 'base_prefix') and sys.base_prefix != sys.prefix):
        print("Already in a virtual environment.")
        return True 
    # If not in a venv, suggest creating one
    if not os.path.exists(venv_dir):
        print("🔧 Virtual environment not found. To create it:")
        if platform.system() == "Windows":
            print(f"python -m venv {venv_dir}")
            print(f"{venv_dir}\\Scripts\\activate")
            print("pip install -r requirements.txt")
        else:
            print(f"python3 -m venv {venv_dir}")
            print(f"source {venv_dir}/bin/activate")
            print("pip install -r requirements.txt")
        print("\n After creating the virtual environment, run this script again.")
        return False
    # If venv exists but we're not in it, suggest activation
    print("Virtual environment found but not activated.")
    if platform.system() == "Windows":
        print(f"To activate: {venv_dir}\\Scripts\\activate")
    else:
        print(f"To activate: source {venv_dir}/bin/activate")
    print("Then run this script again.")
    return False
def main():
    print("=" * 50)
    print("LazyPaper Launcher - English")
    print("=" * 50)
    
    if not setup_venv():
        # Wait for user input before exiting
        input("\nPress Enter to exit...")
        return
    # Now we can import and run normally
    try:
        # Add the lazypaper folder to the path
        lazypaper_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), "lazypaper")
        sys.path.insert(0, lazypaper_dir)
        print("Starting LazyPaper...")
        # Import and run lazypaper.py
        from lazypaper import main as run_app
        run_app()   
    except ImportError as e:
        print(f"Import error: {e}")
        print("\nTroubleshooting steps:")
        print("1. Verify the 'lazypaper' folder contains all required files")
        print("2. Install dependencies: pip install -r requirements.txt")
        print("3. Ensure you're in the correct directory")      
    except Exception as e:
        print(f"Unexpected error: {e}")
        print("\nPlease check the application files and try again.")
    # Wait before closing (useful for seeing errors)
    input("\nPress Enter to exit...")

if __name__ == "__main__":
    main()