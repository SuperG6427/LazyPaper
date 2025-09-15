# gui.py - Interfaz gráfica de usuario
import tkinter as tk
from tkinter import ttk, filedialog, messagebox, colorchooser
import tkinter.font as tkfont
from PIL import Image, ImageTk, ImageDraw
import os
import threading

from logic import LazyPaperLogic

class LazyPaper:
    def __init__(self, root):
        self.root = root
        self.root.title("LazyPaper - Generador de Wallpapers")
        self.root.geometry("1500x800") # tamaño inicial
        self.root.minsize(1200, 700) # tamaño minimo
        
        # Inicializar la lógica
        self.logic = LazyPaperLogic()
        
        # Variables y estado
        self.preview_tk_image = None
        self.status_var = tk.StringVar(value="Listo")
        self.drag_data = {"x": 0, "y": 0, "item": None}
        self.icon_photo = None  # Para guardar referencia al icono
        self.resolution_var = tk.StringVar(value="Desktop FHD (1920x1080)")
        self.image_info = tk.StringVar(value="No hay imagen cargada")
        self.zoom_info = tk.StringVar(value="Vista previa")
        
        # Configurar icono y fuente
        self.set_window_icon()
        self.set_default_font()
        
        # UI
        self.setup_ui()
    
    def set_window_icon(self):
        """Solución robusta para cargar el icono de la ventana"""
        icon_paths = [
            # Buscar en la raíz del proyecto
            os.path.join(os.path.dirname(os.path.abspath(__file__)), "icon.png"),
            # Buscar en la carpeta assets
            os.path.join(os.path.dirname(os.path.abspath(__file__)), "assets", "icon.png"),
            # Buscar en el directorio padre (si los archivos están en una subcarpeta)
            os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "icon.png"),
            # Buscar en assets del directorio padre
            os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "assets", "icon.png"),
        ]
        
        icon_found = False
        for icon_path in icon_paths:
            if os.path.exists(icon_path):
                try:
                    img = Image.open(icon_path)
                    img = img.resize((64, 64), Image.LANCZOS)
                    photo = ImageTk.PhotoImage(img)
                    self.root.iconphoto(True, photo)
                    print(f"Icono cargado desde: {icon_path}")
                    icon_found = True
                    # Guardar referencia para evitar garbage collection
                    self.icon_photo = photo
                    break
                except Exception as e:
                    print(f"Error al cargar icono desde {icon_path}: {e}")
        
        if not icon_found:
            print("No se encontró icon.png en ninguna ubicación esperada")
            # Crear un icono básico como fallback
            try:
                # Crear un icono simple en memoria
                img = Image.new('RGB', (64, 64), color='red')
                draw = ImageDraw.Draw(img)
                draw.rectangle([16, 16, 48, 48], fill='blue')
                photo = ImageTk.PhotoImage(img)
                self.root.iconphoto(True, photo)
                self.icon_photo = photo
                print("Usando icono de fallback")
            except Exception as e:
                print(f"No se pudo crear icono de fallback: {e}")
    
    def set_default_font(self):
        """Configurar la fuente por defecto con alternativas"""
        # Lista de fuentes preferidas en orden de prioridad
        preferred_fonts = [
            "Helvetica", 
            "Arial", 
            "Liberation Sans", 
            "DejaVu Sans",
            "Tahoma",
            "Verdana"
        ]
        available_font = "Helvetica"  # Valor por defecto
        test_label = ttk.Label(self.root, text="Test")
        try:
            test_font = tkfont.Font(font=test_label.cget("font"))
            for font in preferred_fonts:
                try:
                    test_font.config(family=font)
                    # Si no hay error, la fuente está disponible
                    available_font = font
                    break
                except:
                    continue
        except:
            available_font = "TkDefaultFont"
        finally:
            test_label.destroy()
        
        print(f"Usando fuente: {available_font}")
        
        # Fuente para widgets ttk
        style = ttk.Style()
        # Configurar fuente para diferentes elementos de ttk
        style.configure(".", font=("Helvetica", 12))
        style.configure("TButton", font=("Helvetica", 12))
        style.configure("TLabel", font=("Helvetica", 12))
        style.configure("TEntry", font=("Helvetica", 12))
        style.configure("TCombobox", font=("Helvetica", 12))
        style.configure("TCheckbutton", font=("Helvetica", 12))
        style.configure("TRadiobutton", font=("Helvetica", 12))
        style.configure("TSpinbox", font=("Helvetica", 12))
        style.configure("TLabelFrame", font=("Helvetica", 12, "bold"))
        style.configure("TFrame", font=("Helvetica", 12))   
        # Configurar fuente para los botones de nudges
        style.configure("Nudge.TButton", font=(available_font, 10, "bold"))
        # Configurar fuente para widgets tkinter estándar
        default_font = (available_font, 10)
        self.root.option_add("*Font", default_font)
        self.root.option_add("*Label.Font", default_font)
        self.root.option_add("*Button.Font", default_font)
        self.root.option_add("*Entry.Font", default_font)
        self.root.option_add("*Listbox.Font", default_font)
        self.root.option_add("*Menu.Font", default_font)

    def setup_ui(self):
        # Configurar pesos para redimensionamiento
        self.root.columnconfigure(0, weight=1)
        self.root.rowconfigure(0, weight=1)
        
        # Frame principal
        main_frame = ttk.Frame(self.root, padding="10")
        main_frame.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        main_frame.columnconfigure(1, weight=1)
        main_frame.rowconfigure(0, weight=1)

        # Panel controles - Ahora con scrollbar
        controls_container = ttk.Frame(main_frame)
        controls_container.grid(row=0, column=0, sticky=(tk.N, tk.S, tk.W, tk.E), padx=(0, 10))
        controls_container.columnconfigure(0, weight=1)
        controls_container.rowconfigure(0, weight=1)
        
        # Crear canvas y scrollbar para el panel de controles
        controls_canvas = tk.Canvas(controls_container, highlightthickness=0)
        controls_scrollbar = ttk.Scrollbar(controls_container, orient="vertical", command=controls_canvas.yview)
        controls_scrollable_frame = ttk.Frame(controls_canvas)
        
        # Configurar el sistema de scroll
        controls_scrollable_frame.bind(
            "<Configure>",
            lambda e: controls_canvas.configure(scrollregion=controls_canvas.bbox("all"))
        )
        
        controls_canvas.create_window((0, 0), window=controls_scrollable_frame, anchor="nw")
        controls_canvas.configure(yscrollcommand=controls_scrollbar.set)
        
        # Empaquetar canvas y scrollbar
        controls_canvas.grid(row=0, column=0, sticky=(tk.N, tk.S, tk.W, tk.E))
        controls_scrollbar.grid(row=0, column=1, sticky=(tk.N, tk.S))
        
        # Configurar el frame desplazable para expandirse
        controls_container.columnconfigure(0, weight=1)
        controls_container.rowconfigure(0, weight=1)
        
        # Ahora el controls_frame va dentro del frame desplazable
        controls_frame = ttk.LabelFrame(controls_scrollable_frame, text="Controles", padding="8")
        controls_frame.grid(row=0, column=0, sticky=(tk.N, tk.S, tk.W, tk.E))
        controls_frame.columnconfigure(0, weight=1)
        
        # Añadir esta línea para que los controles se expandan verticalmente
        controls_frame.rowconfigure(22, weight=1)

        # Botones carga / info imagen
        ttk.Button(controls_frame, text="Cargar Imagen", command=self.load_image).grid(row=0, column=0, sticky=(tk.W, tk.E), pady=4)
        
        # Visualizar informacion de la imagen
        info_frame = ttk.Frame(controls_frame)
        info_frame.grid(row=1, column=0, sticky=(tk.W, tk.E), pady=(0,8))
        ttk.Label(info_frame, text="Información:", font=("Helvetica", 10, "bold")).grid(row=0, column=0, sticky=tk.W)
        self.image_info = tk.StringVar(value="No hay imagen cargada")
        ttk.Label(info_frame, textvariable=self.image_info, wraplength=220, justify=tk.LEFT).grid(row=1, column=0, sticky=tk.W)
        ttk.Separator(controls_frame, orient="horizontal").grid(row=2, column=0, sticky=(tk.W, tk.E), pady=6)

        # Boton de acciones 
        ttk.Button(controls_frame, text="Generar Wallpaper", command=self.generate_wallpaper).grid(row=2, column=0, sticky=(tk.W, tk.E), pady=4)
        ttk.Button(controls_frame, text="Guardar", command=self.save_wallpaper).grid(row=3, column=0, sticky=(tk.W, tk.E), pady=4)
        
        ttk.Separator(controls_frame, orient="horizontal").grid(row=4, column=0, sticky=(tk.W, tk.E), pady=6)

        # Opciones de procesamiento
        ttk.Label(controls_frame, text="Opciones de procesamiento:").grid(row=5, column=0, sticky=tk.W)
        self.remove_bg_var = tk.BooleanVar(value=False)
        remove_cb = ttk.Checkbutton(controls_frame, text="Eliminar fondo (rembg)", variable=self.remove_bg_var, command=self.update_options)
        remove_cb.grid(row=6, column=0, sticky=tk.W, pady=2)
        if not self.logic.REMBG_AVAILABLE:
            remove_cb.config(state="disabled", text="Eliminar fondo (rembg) — rembg no instalado")
        
        self.add_outline_var = tk.BooleanVar()
        self.outline_check = ttk.Checkbutton(controls_frame, text="Agregar contorno blanco", variable=self.add_outline_var)
        self.outline_check.grid(row=7, column=0, sticky=tk.W, pady=2)
        self.blur_bg_var = tk.BooleanVar()
        ttk.Checkbutton(controls_frame, text="Fondo con blur", variable=self.blur_bg_var).grid(row=8, column=0, sticky=tk.W, pady=2)
        ttk.Separator(controls_frame, orient="horizontal").grid(row=9, column=0, sticky=(tk.W, tk.E), pady=6)

        # Resoluciones
        ttk.Label(controls_frame, text="Resolución:").grid(row=10, column=0, sticky=tk.W)
        # Valor que existe
        resolution_combo = ttk.Combobox(controls_frame, textvariable=self.resolution_var, 
        values=list(self.logic.resolutions.keys()), state="readonly")
        resolution_combo.grid(row=11, column=0, sticky=(tk.W, tk.E), pady=2)
        resolution_combo.bind("<<ComboboxSelected>>", self.on_resolution_change)

        # Configuracion de Personalizacion
        self.custom_frame = ttk.Frame(controls_frame)
        self.custom_frame.grid(row=12, column=0, sticky=(tk.W, tk.E), pady=2)
        self.custom_width = tk.StringVar(value="1920")
        self.custom_height = tk.StringVar(value="1080")
        ttk.Label(self.custom_frame, text="Ancho:").grid(row=0, column=0, sticky=tk.W)
        ttk.Entry(self.custom_frame, textvariable=self.custom_width, width=8).grid(row=0, column=1, padx=2)
        ttk.Label(self.custom_frame, text="Alto:").grid(row=0, column=2, sticky=tk.W, padx=(8,0))
        ttk.Entry(self.custom_frame, textvariable=self.custom_height, width=8).grid(row=0, column=3, padx=2)
        self.custom_frame.grid_remove()

        ttk.Separator(controls_frame, orient="horizontal").grid(row=13, column=0, sticky=(tk.W, tk.E), pady=6)

        # Color de fondo
        ttk.Label(controls_frame, text="Color de fondo:").grid(row=14, column=0, sticky=tk.W)
        color_frame = ttk.Frame(controls_frame)
        color_frame.grid(row=15, column=0, sticky=(tk.W, tk.E))
        self.color_option = tk.StringVar(value="auto")
        ttk.Radiobutton(color_frame, text="Automático", variable=self.color_option, value="auto").grid(row=0, column=0, sticky=tk.W)
        ttk.Radiobutton(color_frame, text="Blanco", variable=self.color_option, value="white").grid(row=1, column=0, sticky=tk.W)
        ttk.Radiobutton(color_frame, text="Negro", variable=self.color_option, value="black").grid(row=2, column=0, sticky=tk.W)
        ttk.Radiobutton(color_frame, text="Personalizado", variable=self.color_option, value="custom").grid(row=3, column=0, sticky=tk.W)
        self.custom_color = "#FFFFFF"
        ttk.Button(color_frame, text="Elegir color", command=self.choose_color).grid(row=4, column=0, sticky=tk.W, pady=4)
        ttk.Separator(controls_frame, orient="horizontal").grid(row=16, column=0, sticky=(tk.W, tk.E), pady=6)

        # Posicionamiento y offsets
        ttk.Label(controls_frame, text="Posición de la imagen:").grid(row=17, column=0, sticky=tk.W)
        pos_frame = ttk.Frame(controls_frame)
        pos_frame.grid(row=18, column=0, sticky=(tk.W, tk.E), pady=2)
        ttk.Radiobutton(pos_frame, text="Izquierda", variable=self.logic.position_var, value="left", command=self.update_preview).grid(row=0, column=0, sticky=tk.W)
        ttk.Radiobutton(pos_frame, text="Centro", variable=self.logic.position_var, value="center", command=self.update_preview).grid(row=0, column=1, sticky=tk.W)
        ttk.Radiobutton(pos_frame, text="Derecha", variable=self.logic.position_var, value="right", command=self.update_preview).grid(row=0, column=2, sticky=tk.W)

        # Offsets y botones de ajuste
        offset_frame = ttk.Frame(controls_frame)
        offset_frame.grid(row=19, column=0, sticky=(tk.W, tk.E), pady=4)
        ttk.Label(offset_frame, text="Offset X:").grid(row=0, column=0, sticky=tk.W)
        ttk.Spinbox(offset_frame, from_=-5000, to=5000, textvariable=self.logic.offset_x_var, width=7, command=self.update_preview).grid(row=0, column=1, padx=4)
        ttk.Label(offset_frame, text="Offset Y:").grid(row=0, column=2, sticky=tk.W, padx=(8,0))
        ttk.Spinbox(offset_frame, from_=-5000, to=5000, textvariable=self.logic.offset_y_var, width=7, command=self.update_preview).grid(row=0, column=3, padx=4)

        # Botones para ajustar con flechas
        nudges = ttk.Frame(controls_frame)
        nudges.grid(row=20, column=0, sticky=(tk.W, tk.E), pady=(4,6))
        nudges.columnconfigure([0,1,2], weight=1)

        # Creacion de botones
        style = ttk.Style()
        style.configure("Nudge.TButton", font=("Helvetica", 10, "bold"))
        ttk.Button(nudges, text="↖", width=3, style="Nudge.TButton", 
                   command=lambda: self.nudge(-10, -10)).grid(row=0, column=0, padx=2, pady=2)
        ttk.Button(nudges, text="↑", width=3, style="Nudge.TButton", 
                   command=lambda: self.nudge(0, -10)).grid(row=0, column=1, padx=2, pady=2)
        ttk.Button(nudges, text="↗", width=3, style="Nudge.TButton", 
                   command=lambda: self.nudge(10, -10)).grid(row=0, column=2, padx=2, pady=2)
        ttk.Button(nudges, text="←", width=3, style="Nudge.TButton", 
                   command=lambda: self.nudge(-10, 0)).grid(row=1, column=0, padx=2, pady=2)
        ttk.Button(nudges, text="•", width=3, style="Nudge.TButton", 
                   command=lambda: self.nudge(0, 0)).grid(row=1, column=1, padx=2, pady=2)
        ttk.Button(nudges, text="→", width=3, style="Nudge.TButton", 
                   command=lambda: self.nudge(10, 0)).grid(row=1, column=2, padx=2, pady=2)    
        ttk.Button(nudges, text="↙", width=3, style="Nudge.TButton", 
                   command=lambda: self.nudge(-10, 10)).grid(row=2, column=0, padx=2, pady=2)
        ttk.Button(nudges, text="↓", width=3, style="Nudge.TButton", 
                   command=lambda: self.nudge(0, 10)).grid(row=2, column=1, padx=2, pady=2)
        ttk.Button(nudges, text="↘", width=3, style="Nudge.TButton", 
                   command=lambda: self.nudge(10, 10)).grid(row=2, column=2, padx=2, pady=2)

        # Configurar el evento de redimensionamiento para ajustar el canvas
        def configure_canvas(event):
            controls_canvas.configure(scrollregion=controls_canvas.bbox("all"))
            # Ajustar el ancho del frame interno al ancho del canvas
            controls_canvas.itemconfig(1, width=event.width)
        
        controls_canvas.bind("<Configure>", configure_canvas)
        
        # Permitir scroll con rueda del mouse
        def _on_mousewheel(event):
            controls_canvas.yview_scroll(int(-1*(event.delta/120)), "units")
        
        controls_canvas.bind("<MouseWheel>", _on_mousewheel)
        # Panel de preview
        preview_frame = ttk.LabelFrame(main_frame, text="Vista Previa", padding="8")
        preview_frame.grid(row=0, column=1, sticky=(tk.N, tk.S, tk.E, tk.W))
        preview_frame.columnconfigure(0, weight=1)
        preview_frame.rowconfigure(0, weight=1)  # Expansión para el canvas

        # Canvas
        self.preview_canvas = tk.Canvas(preview_frame, bg="#f0f0f0", relief="sunken", borderwidth=1)
        self.preview_canvas.grid(row=0, column=0, sticky=(tk.N, tk.S, tk.E, tk.W))

        # Scrollbars
        v_scroll = ttk.Scrollbar(preview_frame, orient="vertical", command=self.preview_canvas.yview)
        v_scroll.grid(row=0, column=1, sticky=(tk.N, tk.S))
        h_scroll = ttk.Scrollbar(preview_frame, orient="horizontal", command=self.preview_canvas.xview)
        h_scroll.grid(row=1, column=0, sticky=(tk.W, tk.E))
        self.preview_canvas.configure(yscrollcommand=v_scroll.set, xscrollcommand=h_scroll.set)

        # Info de zoom
        self.zoom_info = tk.StringVar(value="Vista previa")
        ttk.Label(preview_frame, textvariable=self.zoom_info, font=("Helvetica", 10)).grid(row=2, column=0, sticky=(tk.W, tk.E))

        # Bind de teclado para movimiento con flechas
        self.root.bind("<Left>", lambda e: self.nudge(-10, 0))
        self.root.bind("<Right>", lambda e: self.nudge(10, 0))
        self.root.bind("<Up>", lambda e: self.nudge(0, -10))
        self.root.bind("<Down>", lambda e: self.nudge(0, 10))
        self.root.bind("<Shift-Left>", lambda e: self.nudge(-1, 0))
        self.root.bind("<Shift-Right>", lambda e: self.nudge(1, 0))
        self.root.bind("<Shift-Up>", lambda e: self.nudge(0, -1))
        self.root.bind("<Shift-Down>", lambda e: self.nudge(0, 1))

        # Hacer focus en el canvas para que reciba los eventos de teclado
        self.preview_canvas.bind("<Button-1>", lambda e: self.preview_canvas.focus_set())
        
        # Bind para arrastre de raton
        self.preview_canvas.bind("<ButtonPress-1>", self.on_drag_start)
        self.preview_canvas.bind("<B1-Motion>", self.on_drag_motion)
        self.preview_canvas.bind("<ButtonRelease-1>", self.on_drag_release)

        # Barra de estado
        status_bar = ttk.Frame(main_frame)
        status_bar.grid(row=1, column=0, columnspan=2, sticky=(tk.W, tk.E), pady=(5, 0))
        ttk.Label(status_bar, textvariable=self.status_var, font=("Helvetica", 10)).pack(side=tk.LEFT)
        ttk.Label(status_bar, text="Lazypaper v1.0", font=("Helvetica", 10)).pack(side=tk.RIGHT)

    # ---------- METHOD arrastre con mouse ----------
    def on_drag_start(self, event):
        """Inicio del arrastre"""
        self.drag_data["x"] = event.x
        self.drag_data["y"] = event.y
        # Buscar si hay una imagen en la posicion del click pulsado
        items = self.preview_canvas.find_overlapping(event.x-1, event.y-1, event.x+1, event.y+1)
        if items:
            self.drag_data["item"] = items[0]

    def on_drag_motion(self, event):
        """Durante el arrastre"""
        if not self.drag_data["item"]:
            return     
        delta_x = event.x - self.drag_data["x"]
        delta_y = event.y - self.drag_data["y"]
        # Mover elemento
        self.preview_canvas.move(self.drag_data["item"], delta_x, delta_y)
        # Actualizar posiciones de referencia
        self.drag_data["x"] = event.x
        self.drag_data["y"] = event.y
        
    def on_drag_release(self, event):
        """Fin del arrastre"""
        self.drag_data["item"] = None

    # ---------- METHOD Utilidades ----------
    def get_target_resolution(self):
        """Obtener la resolución objetivo con validación"""
        res_name = self.resolution_var.get()
        
        # Validar que se haya seleccionado una resolución
        if not res_name:
            messagebox.showwarning("Advertencia", "Por favor, selecciona una resolución primero.")
            return (1920, 1080)
        
        if res_name == "Personalizado":
            try:
                width = int(self.custom_width.get())
                height = int(self.custom_height.get())
                # Validar dimensiones positivas
                if width <= 0 or height <= 0:
                    raise ValueError("Dimensiones deben ser positivas")
                return width, height
            except ValueError:
                messagebox.showwarning("Advertencia", f"Resolución '{res_name}' inválida. Usando 1920x1080.")
                return (1920, 1080)
        else:
            if res_name not in self.logic.resolutions:
                messagebox.showwarning("Advertencia", "Resolución seleccionada no es válida. Usando 1920x1080.")
                return 1920, 1080
            return self.logic.resolutions[res_name]
        
    def nudge(self, dx: int, dy: int):
        self.logic.offset_x_var.set(self.logic.offset_x_var.get() + dx)
        self.logic.offset_y_var.set(self.logic.offset_y_var.get() + dy)
        self.update_preview()
    
    # Actualizar opciones de rembg
    def update_options(self):
        """Habilita/deshabilita controles en función de rembg"""
        if self.remove_bg_var.get() and self.logic.REMBG_AVAILABLE:
            self.outline_check.config(state="normal")
        else:
            self.outline_check.config(state="disabled")
            
    def on_resolution_change(self, event=None):
        if self.resolution_var.get() == "Personalizado":
            self.custom_frame.grid()
        else:
            self.custom_frame.grid_remove()
            
    def choose_color(self):
        color = colorchooser.askcolor(title="Elegir color de fondo")
        if color and color[1]:
            self.custom_color = color[1]
            self.update_preview()
            
    def get_background_color(self):
        option = self.color_option.get()
        if option == "white":
            return (255, 255, 255)
        elif option == "black":
            return (0, 0, 0)
        elif option == "custom":
            hex_color = self.custom_color.lstrip('#')
            return tuple(int(hex_color[i:i+2], 16) for i in (0, 2, 4))
        else:
            if self.logic.original_image:
                return self.logic.get_dominant_color(self.logic.original_image)
            return (255, 255, 255)

    # ---------- METHOD Carga de imagen ----------
    def load_image(self):
        """Abre un file dialog y carga la imagen en hilo mostrando un progressbar modal."""
        self.status_var.set("Cargando imagen...")
        file_types = [
            ('Imágenes', '*.png *.jpg *.jpeg *.tiff *.tif'),
            ('PNG', '*.png'),
            ('JPEG', '*.jpg *.jpeg'),
            ('TIFF', '*.tiff *.tif')
        ]
        filename = filedialog.askopenfilename(title="Seleccionar imagen", filetypes=file_types)
        if not filename:
            self.status_var.set("Listo")
            return

        # Mostrar ventana modal con progressbar indeterminado
        progress_win = tk.Toplevel(self.root)
        progress_win.title("Cargando imagen...")
        progress_win.geometry("300x80")
        progress_win.transient(self.root)
        progress_win.grab_set()
        ttk.Label(progress_win, text=f"Cargando: {os.path.basename(filename)}").pack(pady=(8,4))
        pb = ttk.Progressbar(progress_win, mode='indeterminate')
        pb.pack(fill=tk.X, padx=12, pady=8)
        pb.start(10)

        def do_load():
            try:
                img = Image.open(filename)
                # Convertir si es necesario
                if img.mode not in ['RGB', 'RGBA']:
                    img = img.convert('RGB')
                # Pasar al hilo principal
                self.root.after(0, lambda: self._finish_load(img, filename))
            except Exception as e:
                self.root.after(0, lambda: messagebox.showerror("Error", f"No se pudo cargar la imagen: {str(e)}"))
            finally:
                # Cerrar ventana modal en hilo principal
                self.root.after(0, lambda: (pb.stop(), progress_win.destroy()))

        threading.Thread(target=do_load, daemon=True).start()
        
    def _finish_load(self, image, filename):
        # Guardar la imagen y resetear procesos previos para evitar previo antiguo persistente
        self.logic.original_image = image
        self.logic.current_image_path = filename
        self.logic.processed_image = None
        self.logic.offset_x_var.set(0)
        self.logic.offset_y_var.set(0)
        self.logic.analyze_image()
        self.image_info.set(self.logic.image_info.get())
        self.update_preview()
        self.status_var.set("Imagen cargada")

    # ---------- METHOD Generation ----------
    def generate_wallpaper(self):
        if not self.logic.original_image:
            messagebox.showwarning("Advertencia", "Por favor, carga una imagen primero.")
            return
        try:
            target_w, target_h = self.get_target_resolution()
            self.status_var.set("Generando wallpaper...")
            
            # Preparar opciones para pasar a la lógica
            options = {
                'remove_bg': self.remove_bg_var.get(),
                'add_outline': self.add_outline_var.get(),
                'blur_bg': self.blur_bg_var.get(),
                'position': self.logic.position_var.get(),
                'offset_x': self.logic.offset_x_var.get(),
                'offset_y': self.logic.offset_y_var.get(),
                'bg_color': self.get_background_color()
            }
            
            # Generar el wallpaper usando la lógica
            result = self.logic.generate_wallpaper((target_w, target_h), options)
            
            if result:
                self.logic.processed_image = result
                self.update_preview()
                self.status_var.set("Wallpaper generado")
                messagebox.showinfo("Éxito", "Wallpaper generado correctamente!")
            else:
                self.status_var.set("Error al generar")
                
        except Exception as e:
            self.status_var.set("Error al generar")
            messagebox.showerror("Error", f"Error al generar wallpaper: {str(e)}")

    # ---------- METHOD Preview ----------
    def update_preview(self):
        """Actualizar vista previa usando original o procesada, y respetando posicionamientos/offsets"""
        display_image = self.logic.processed_image if self.logic.processed_image else self.logic.original_image
        if not display_image:
            # Limpiar cache de canvas
            self.preview_canvas.delete("all")
            return

        # Escalar canvas manteniendo proporciones
        canvas_w = self.preview_canvas.winfo_width()
        canvas_h = self.preview_canvas.winfo_height()
        if canvas_w <= 1 or canvas_h <= 1:
            canvas_w, canvas_h = 600, 520

        img_ratio = display_image.width / display_image.height
        canvas_ratio = canvas_w / canvas_h
        if img_ratio > canvas_ratio:
            preview_w = canvas_w
            preview_h = int(canvas_w / img_ratio)
        else:
            preview_h = canvas_h
            preview_w = int(canvas_h * img_ratio)

        # Actualizar información de zoom
        zoom_percent = min(preview_w/display_image.width, preview_h/display_image.height) * 100
        self.zoom_info.set(f"Vista previa ({zoom_percent:.1f}%)")

        # Generar imagen reducida para mostrar (usar copia)
        preview_img = display_image.copy().resize((preview_w, preview_h), Image.LANCZOS)

        # Hacer preview mostrando ORIGINAL y posicionado dentro de fondo
        if self.logic.processed_image is None and self.logic.original_image:
            # fondo preview con color elegido
            bg_color = self.get_background_color()
            preview_bg = Image.new('RGB', (preview_w, preview_h), bg_color)
            # calcular pos en preview según position_var y offsets escalando
            pos = self.logic.position_var.get()
            # Convert preview_img a PhotoImage y colocarlo en canvas con coordenadas.
            self.preview_tk_image = ImageTk.PhotoImage(preview_img)
            self.preview_canvas.delete("all")

            # Calcular coordenadas en el canvas
            if self.logic.position_var.get() == 'left':
                x = 0 + int(self.logic.offset_x_var.get() * preview_w / max(1, display_image.width))
            elif self.logic.position_var.get() == 'right':
                x = preview_w - preview_img.width + int(self.logic.offset_x_var.get() * preview_w / max(1, display_image.width))
            else:
                x = (preview_w - preview_img.width)//2 + int(self.logic.offset_x_var.get() * preview_w / max(1, display_image.width))
            y = (preview_h - preview_img.height)//2 + int(self.logic.offset_y_var.get() * preview_h / max(1, display_image.height))

            # Centrar preview area dentro del canvas
            canvas_x = (canvas_w - preview_w)//2
            canvas_y = (canvas_h - preview_h)//2

            # Dibujar background (rect) y la imagen
            self.preview_canvas.create_rectangle(canvas_x, canvas_y, canvas_x+preview_w, canvas_y+preview_h, 
                                                fill='#%02x%02x%02x' % bg_color, outline='')
            self.preview_canvas.create_image(canvas_x + x, canvas_y + y, anchor=tk.NW, image=self.preview_tk_image)
        else:
            # Si self.processed_image existe, simplemente mostrar la imagen generada (es posible que sea grande)
            self.preview_tk_image = ImageTk.PhotoImage(preview_img)
            self.preview_canvas.delete("all")
            x = (canvas_w - preview_w)//2
            y = (canvas_h - preview_h)//2
            self.preview_canvas.create_image(x, y, anchor=tk.NW, image=self.preview_tk_image)

        self.preview_canvas.configure(scrollregion=self.preview_canvas.bbox("all"))

    # ---------- METHOD Guardado de imagen ----------
    def save_wallpaper(self):
        if not self.logic.processed_image:
            messagebox.showwarning("Advertencia", "Genera un wallpaper primero.")
            return
        file_types = [
            ('PNG', '*.png'),
            ('JPEG', '*.jpg'),
            ('TIFF', '*.tiff')
        ]
        filename = filedialog.asksaveasfilename(title="Guardar wallpaper", defaultextension=".png", filetypes=file_types)
        if not filename:
            return
        try:
            self.status_var.set("Guardando...")
            self.logic.save_wallpaper(filename)
            self.status_var.set("Wallpaper guardado")
            messagebox.showinfo("Éxito", f"Wallpaper guardado como: {filename}")
        except Exception as e:
            self.status_var.set("Error al guardar")
            messagebox.showerror("Error", f"No se pudo guardar: {str(e)}")