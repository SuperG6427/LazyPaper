# main.py - Archivo principal para ejecutar la aplicación
import tkinter as tk

# Importar temas y rembg opcionalmente
try:
    from ttkthemes import ThemedTk
    THEMED = True
except ImportError:
    THEMED = False
    print("ttkthemes no se encuentra instalado. Usando tema por defecto.")

from gui import LazyPaper

def main():
    if THEMED:
        root = ThemedTk(theme="equilux")  # Puedes usar: "arc", "equilux", "black", etc.
    else:
        root = tk.Tk()
    app = LazyPaper(root)
    root.mainloop()

if __name__ == "__main__":
    main()