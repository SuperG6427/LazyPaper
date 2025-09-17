# build_optimized.py - Script optimizado para construir el ejecutable
import os
import subprocess
import sys
import shutil
import zipfile
from datetime import datetime

def build_executable():
    print("=== CONSTRUYENDO LAZYPAPER OPTIMIZADO ===")
    
    # Verificar si PyInstaller está instalado
    try:
        import PyInstaller
        print("✓ PyInstaller está instalado")
    except ImportError:
        print("Instalando PyInstaller...")
        subprocess.check_call([sys.executable, "-m", "pip", "install", "pyinstaller"])
    
    # Obtener la ruta al requirements.txt (que está fuera de la carpeta lazypaper)
    requirements_path = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "requirements.txt"))
    
    # Instalar dependencias desde el requirements.txt correcto
    print("Instalando dependencias desde requirements.txt...")
    subprocess.check_call([sys.executable, "-m", "pip", "install", "-r", requirements_path])
    
    # Limpiar builds anteriores
    if os.path.exists("build"):
        shutil.rmtree("build")
    if os.path.exists("dist"):
        shutil.rmtree("dist")
    
    # Comando para construir el ejecutable optimizado
    # NOTA: No excluir el módulo 'email' ya que es necesario para pkg_resources
    cmd = [
        "pyinstaller",
        "--name=Lazypaper",
        "--onefile",
        "--windowed",
        "--icon=icons/icon.ico",
        "--add-data=assets/images;assets/images",
        "--add-data=icons;icons",
        "--exclude-module=matplotlib",
        "--exclude-module=scipy",
        "--exclude-module=pandas",
        "--exclude-module=tensorflow",
        "--exclude-module=keras",
        "--exclude-module=sklearn",
        "--exclude-module=test",
        "--exclude-module=unittest",
        "--hidden-import=PIL._tkinter_finder",
        "--hidden-import=numpy.core._multiarray_umath",
        "--hidden-import=packaging.specifiers",
        "--hidden-import=packaging.requirements",
        "--hidden-import=pkg_resources",
        "--hidden-import=email",
        "--hidden-import=email.mime",
        "--hidden-import=email.mime.text",
        "--hidden-import=email.mime.multipart",
        "--hidden-import=email.mime.base",
        "--hidden-import=email.mime.image",
        "--hidden-import=email.mime.application",
        "--hidden-import=email.utils",
        "--hidden-import=email.encoders",
        "--hidden-import=email.header",
        "--hidden-import=email.charset",
        "--hidden-import=email.policy",
        "--hidden-import=email.generator",
        "--hidden-import=email.iterators",
        "--hidden-import=email.parser",
        "--hidden-import=email.feedparser",
        "--optimize=2",
        "lazypaper.py"
    ]
    
    print("Ejecutando PyInstaller con configuración optimizada...")
    subprocess.check_call(cmd)
    
    print("✓ Ejecutable creado exitosamente!")
    
    # Crear paquete ZIP
    create_distribution_package()
    
    print("✓ Paquete de distribución creado en la carpeta 'package'")

def create_distribution_package():
    """Crear un paquete ZIP con el ejecutable y archivos necesarios"""
    package_dir = "package"
    if os.path.exists(package_dir):
        shutil.rmtree(package_dir)
    os.makedirs(package_dir)
    
    # Copiar ejecutable
    exe_source = os.path.join("dist", "Lazypaper.exe")
    exe_dest = os.path.join(package_dir, "Lazypaper.exe")
    shutil.copy2(exe_source, exe_dest)
    
    # Crear README
    create_readme(package_dir)
    
    # Crear archivo ZIP
    zip_filename = f"Lazypaper_Portable_{datetime.now().strftime('%Y%m%d_%H%M')}.zip"
    with zipfile.ZipFile(zip_filename, 'w', zipfile.ZIP_DEFLATED) as zipf:
        for root, dirs, files in os.walk(package_dir):
            for file in files:
                file_path = os.path.join(root, file)
                arcname = os.path.relpath(file_path, package_dir)
                zipf.write(file_path, arcname)
    
    print(f"✓ Paquete creado: {zip_filename}")
    print(f"Tamaño: {os.path.getsize(zip_filename) / (1024*1024):.2f} MB")

def create_readme(package_dir):
    """Crear archivo README.txt"""
    readme_content = """LAZYPAPER - Generador de Wallpapers Portable

Descripción:
Lazypaper es una aplicación para crear wallpapers personalizados con opciones de:
- Eliminación de fondos (usando IA)
- Ajuste de posición y tamaño
- Diferentes colores de fondo
- Efectos de contorno y desenfoque

Requisitos del sistema:
- Windows 7 o superior
- 4GB de RAM recomendados
- 200MB de espacio libre en disco

Instrucciones de uso:
1. Extraer todo el contenido del ZIP en una carpeta
2. Ejecutar "Lazypaper.exe"
3. Cargar una imagen con el botón "Cargar Imagen"
4. Ajustar las opciones deseadas
5. Hacer clic en "Generar Wallpaper"
6. Guardar el resultado con "Guardar"

Notas:
- La primera ejecución puede tardar unos segundos mientras se inicializan los componentes
- Para mejores resultados con la eliminación de fondos, use imágenes con fondos contrastados

Soporte:
Para reportar problemas o sugerencias, contacte al desarrollador.

Versión: 1.3
Fecha: {date}
""".format(date=datetime.now().strftime("%Y-%m-%d"))
    
    with open(os.path.join(package_dir, "README.txt"), "w", encoding="utf-8") as f:
        f.write(readme_content)

if __name__ == "__main__":
    build_executable()