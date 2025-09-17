# lazypaper.py - Archivo principal
import tkinter as tk
import os
import sys
import time

# Función para manejar rutas
def resource_path(relative_path):
    try:
        base_path = sys._MEIPASS
    except Exception:
        base_path = os.path.abspath(".")
    return os.path.join(base_path, relative_path)

# Mostrar splash screen durante la carga
def show_splash():
    splash = tk.Tk()
    splash.title("Lazypaper")
    splash.overrideredirect(True)
    splash.geometry("300x200+500+300")
    
    # Intentar cargar imagen de splash
    try:
        from PIL import Image, ImageTk
        splash_image_path = resource_path("assets/images/icon.png")
        img = Image.open(splash_image_path)
        img = img.resize((64, 64), Image.LANCZOS)
        photo = ImageTk.PhotoImage(img)
        label = tk.Label(splash, image=photo)
        label.image = photo
        label.pack(pady=20)
    except:
        pass
    
    label = tk.Label(splash, text="Cargando Lazypaper...", font=("Arial", 12))
    label.pack(pady=10)
    
    progress = tk.Label(splash, text="Inicializando...")
    progress.pack(pady=5)
    
    splash.update()
    return splash, progress

# Carga diferida de modulos pesados
def load_heavy_modules(progress_callback=None):
    modules = {}
    if progress_callback:
        progress_callback("Cargando interfaz gráfica...")
    # Cargar GUI
    from gui import LazyPaper
    modules['LazyPaper'] = LazyPaper
    if progress_callback:
        progress_callback("Cargando temas...")
    # Cargar temas opcionalmente
    try:
        from ttkthemes import ThemedTk
        modules['ThemedTk'] = ThemedTk
        modules['THEMED'] = True
    except ImportError:
        modules['THEMED'] = False
    return modules

def main():
    # Mostrar splash screen
    splash, progress = show_splash()
    # Cargar módulos pesados en segundo plano
    def update_progress(message):
        progress.config(text=message)
        splash.update()
    modules = load_heavy_modules(update_progress)
    
    # Cerrar splash y crear ventana principal
    splash.destroy()
    
    # Crear ventana principal
    if modules['THEMED']:
        root = modules['ThemedTk'](theme="equilux")
    else:
        root = tk.Tk()
    root.title("Lazypaper - Generate my Wallpaper")
    
    # Establecer icono
    try:
        icon_path = resource_path("icons/icon.ico")
        root.iconbitmap(icon_path)
    except:
        pass
    
    # Crear aplicación
    app = modules['LazyPaper'](root)
    root.mainloop()

if __name__ == "__main__":
    main()