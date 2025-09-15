import os
import sys
import platform

def verificar_dependencias():
    """Verificar si las dependencias requeridas están instaladas"""
    paquetes_requeridos = {
        'PIL': 'Pillow',
        'numpy': 'numpy', 
        'ttkthemes': 'ttkthemes'
    }
    
    faltantes = []
    for import_name, package_name in paquetes_requeridos.items():
        try:
            __import__(import_name)
        except ImportError:
            faltantes.append(package_name)
    
    return faltantes
def setup_venv():
    """Configurar el entorno virtual si es necesario"""
    root_dir = os.path.dirname(os.path.abspath(__file__))
    lazypaper_dir = os.path.join(root_dir, "lazypaper")
    venv_dir = os.path.join(root_dir, "venv")
    requirements_path = os.path.join(root_dir, "requirements.txt")
    # Verificar que existe la carpeta lazypaper
    if not os.path.exists(lazypaper_dir):
        print(f"Error: No se encontró la carpeta 'lazypaper' en {root_dir}")
        print("Estructura esperada:")
        print("Proyecto/")
        print("├── lazypaper_launcher_esp.py")
        print("├── requirements.txt")
        print("└── lazypaper/")
        print("    ├── lazypaper.py")
        print("    ├── gui.py")
        print("    └── logic.py")
        return False
    
    # Verificar que el archivo principal existe
    if not os.path.exists(os.path.join(lazypaper_dir, "lazypaper.py")):
        print(f"Error: No se encontró lazypaper.py en {lazypaper_dir}")
        return False
    # Crear requirements.txt si no existe con versión actualizada
    if not os.path.exists(requirements_path):
        print("Creando archivo requirements.txt...")
        with open(requirements_path, "w") as f:
            f.write("""Pillow>=10.0.0
numpy>=1.24.0
ttkthemes>=3.2.2
rembg>=2.0.50
onnxruntime>=1.15.0
""")
    # Verificar dependencias básicas
    dependencias_faltantes = verificar_dependencias()
    if dependencias_faltantes:
        print(f"Dependencias faltantes: {', '.join(dependencias_faltantes)}")  
    # Verificar si estamos en un venv
    if hasattr(sys, 'real_prefix') or (hasattr(sys, 'base_prefix') and sys.base_prefix != sys.prefix):
        print("Ya tienes un entorno virtual.")
        return True
    # Si no estamos en un venv, sugerir crearlo
    if not os.path.exists(venv_dir):
        print(" No se encuentra entorno virtual. Para crearlo:")
        if platform.system() == "Windows":
            print(f"python -m venv {venv_dir}")
            print(f"{venv_dir}\\Scripts\\activate")
            print("pip install -r requirements.txt")
        else:
            print(f"python3 -m venv {venv_dir}")
            print(f"source {venv_dir}/bin/activate")
            print("pip install -r requirements.txt")
        print("\n Crear el entorno virtual, ejecuta este script nuevamente.")
        return False
    
    # Si el venv existe pero no estamos en él, activarlo
    print(" Entorno virtual encontrado pero no activado.")
    if platform.system() == "Windows":
        print(f"Para activar: {venv_dir}\\Scripts\\activate")
    else:
        print(f"Para activar: source {venv_dir}/bin/activate")
    print("Luego ejecuta este script nuevamente.")
    return False

def main():
    print("=" * 50)
    print("LazyPaper Launcher - Español")
    print("=" * 50)
    
    if not setup_venv():
        # Esperar entrada del usuario antes de salir
        input("\nPresiona Enter para salir...")
        return
    try:
        # Agregar la carpeta lazypaper al path
        lazypaper_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), "lazypaper")
        sys.path.insert(0, lazypaper_dir)
        
        print(" Iniciando LazyPaper...")
        # Importar y ejecutar lazypaper.py
        from lazypaper import main as run_app
        run_app()
        
    except ImportError as e:
        print(f"Error de importación: {e}")
        print("\n Solución de problemas:")
        print("1. Verifica que la carpeta 'lazypaper' contenga todos los archivos")
        print("2. Instala las dependencias: pip install -r requirements.txt")
        print("3. Asegúrate de estar en el directorio correcto")
        
    except Exception as e:
        print(f" Error inesperado: {e}")
        print("\nPor favor, verifica los archivos de la aplicación e intenta nuevamente.")
    input("\nPresiona Enter para salir...")
if __name__ == "__main__":
    main()