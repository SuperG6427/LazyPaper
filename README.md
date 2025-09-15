
<img alt="LazyPaper_Banner" src= "https://github.com/SuperG6427/LazyPaper/blob/main/lazypaper/assets/images/banner_lazypaper.png?raw=true" width="100%">

### ENG: 
Convert your images into **custom wallpapers** automatically with an easy-to-use Python tool.  

### ESP: 
Convierte tus imágenes en **fondos de pantalla personalizados** de manera automática con una herramienta sencilla en Python.  

---

## ⚙️ Requirements / Requerimientos 

###  Python
- **Python ≥ 3.8** (recommended / recomendado: **3.11+**)  
- Works on / Funciona en **Linux, macOS, Windows**  

###  Core Dependencies / Dependencias Principales
- [Pillow](https://pillow.readthedocs.io/en/stable/) `>=10.0.0`
- [NumPy](https://numpy.org/) `>=1.24.0`
- `tkinter` (usually included with Python / Usualmente viene con Python)  
- [ttkthemes](https://github.com/RedFantom/ttkthemes) `>=3.2.2`  

###  Optional / Opcional (AI features / Funciones de IA )
- [rembg](https://github.com/danielgatis/rembg) `>=2.0.50` → Background removal / Removedor de Fondos  
- [onnxruntime](https://onnxruntime.ai/) `>=1.15.0`  
- GPU acceleration: `onnxruntime-gpu` (requires CUDA + NVIDIA drivers) 

---

## 💻 System dependencies / Dependencias del Sistema

- **Linux:**  
  ```bash
  sudo apt-get install python3-tk python3-pil.imagetk libglib2.0-0 libsm6 libxext6 libxrender-dev libgomp1

- **macOS:**
  ```bash
  brew install python-tk

- **Windows:**  
 Usually included with Python installation / Usualmente viene incluido instalado con Python.

---

## Features / Características

- ✅ Easy-to-use GUI (Tkinter + ttk themes) / Interfaz gráfica de usuario fácil de usar (Tkinter + temas ttk)

- ✅ Multiplatform launchers (Windows/Linux/macOS) / Lanzadores multiplataforma (Windows/Linux/MacOS)

- ✅ Automatic dependency setup / Configuración automática de dependencias

- ✅ Optional AI background removal (rembg + onnxruntime) / Eliminación de fondo con IA opcional (rembg + onnxruntime)


---

## How to Run / Como ejecutarlo
1. Clone the repository / Clona el repositorio 
```bash
git clone git@github.com:SuperG6427/LazyPaper.git
cd LazyPaper
```
2. Install dependencies / Instalar dependencias
```bash
pip install -r requirements.txt
```
3. Run with launcher (auto-detects OS) / Ejecutar con Launcher (auto-detecta SO)
- English:  
```bash
python lazypaper_launcher.py
```
- Español:  
```bash
python lazypaper_launcher_esp.py
```

