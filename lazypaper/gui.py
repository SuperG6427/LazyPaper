# gui.py - Interfaz gráfica
import tkinter as tk
from tkinter import ttk, filedialog, messagebox, colorchooser
import tkinter.font as tkfont
from PIL import Image, ImageTk, ImageDraw
import os
import threading
import time

from logic import LazyPaperLogic

class LazyPaper:
    def __init__(self, root):
        self.root = root
        self.root.title("LazyPaper - Generador de Wallpapers")
        self.root.geometry("1500x800")
        self.root.minsize(1200, 700)
        
        # Inicializar la logica (logic.py)
        self.logic = LazyPaperLogic()
        
        # Variables y estado
        self.preview_tk_image = None
        self.status_var = tk.StringVar(value="Listo")
        self.drag_data = {"x": 0, "y": 0, "item": None}
        self.icon_photo = None
        self.resolution_var = tk.StringVar(value="Desktop FHD (1920x1080)")
        self.image_info_var = tk.StringVar(value="No hay imagen cargada")  # Cambiado para evitar conflicto
        self.zoom_info = tk.StringVar(value="Vista previa")
        self._preview_cache = None
        self._last_update_time = 0
        self._update_debounce_id = None
        # Configurar icono y fuente
        self.set_window_icon()
        self.set_default_font()
        # UI
        self.setup_ui()

    # -------------------- ICONO OPTIMIZADO --------------------
    def set_window_icon(self):
        """Carga optimizada del icono de la ventana"""
        icon_paths = [
            os.path.join(os.path.dirname(os.path.abspath(__file__)), "icon.png"),
            os.path.join(os.path.dirname(os.path.abspath(__file__)), "assets", "icon.png"),
            os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "icon.png"),
            os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "assets", "icon.png"),
        ]
        
        for icon_path in icon_paths:
            if os.path.exists(icon_path):
                try:
                    img = Image.open(icon_path).resize((64, 64), Image.LANCZOS)
                    photo = ImageTk.PhotoImage(img)
                    self.root.iconphoto(True, photo)
                    self.icon_photo = photo
                    print(f"Icono cargado desde: {icon_path}")
                    return
                except Exception as e:
                    print(f"Error al cargar icono: {e}")
        
        # Fallback: icono básico en memoria
        try:
            img = Image.new('RGB', (64, 64), color='#2c3e50')
            draw = ImageDraw.Draw(img)
            draw.rectangle([16, 16, 48, 48], fill='#3498db')
            photo = ImageTk.PhotoImage(img)
            self.root.iconphoto(True, photo)
            self.icon_photo = photo
        except Exception as e:
            print(f"No se pudo crear icono de fallback: {e}")

    # -------------------- FUENTE OPTIMIZADA --------------------
    def set_default_font(self):
        """Configuración optimizada de fuentes"""
        preferred_fonts = [
            "Segoe UI", "Helvetica", "Arial",
            "Liberation Sans", "DejaVu Sans", "Tahoma", "Verdana"
        ]
        
        available_font = "TkDefaultFont"
        try:
            # Probar fuentes disponibles
            test_font = tkfont.Font()
            for font in preferred_fonts:
                try:
                    test_font.config(family=font)
                    available_font = font
                    break
                except:
                    continue
        except:
            available_font = "TkDefaultFont"
        
        print(f"Usando fuente: {available_font}")
        # Configurar estilo global
        style = ttk.Style()
        style.configure(".", font=(available_font, 10))
        style.configure("TButton", font=(available_font, 10))
        style.configure("TLabel", font=(available_font, 10))
        style.configure("TEntry", font=(available_font, 10))
        style.configure("TCombobox", font=(available_font, 10))
        style.configure("TCheckbutton", font=(available_font, 10))
        style.configure("TRadiobutton", font=(available_font, 10))
        style.configure("TLabelFrame", font=(available_font, 10, "bold"))
        style.configure("Nudge.TButton", font=(available_font, 9, "bold"))

    # -------------------- UI OPTIMIZADA --------------------
    def setup_ui(self):
        """Configuración optimizada de la interfaz"""
        # Configuración principal
        self.root.columnconfigure(0, weight=1)
        self.root.rowconfigure(0, weight=1)
        main_frame = ttk.Frame(self.root, padding="10")
        main_frame.grid(row=0, column=0, sticky="nsew")
        main_frame.columnconfigure(1, weight=1)
        main_frame.rowconfigure(0, weight=1)

        # Panel de controles con scroll optimizado
        self.setup_controls_panel(main_frame)
        # Panel de vista previa
        self.setup_preview_panel(main_frame)
        # Barra de estado
        self.setup_status_bar(main_frame)

    def setup_controls_panel(self, parent):
        """Panel de controles optimizado"""
        # Contenedor principal
        controls_container = ttk.Frame(parent)
        controls_container.grid(row=0, column=0, sticky="nsew", padx=(0, 10))
        controls_container.columnconfigure(0, weight=1)
        controls_container.rowconfigure(0, weight=1)
        
        # Canvas y scrollbar
        controls_canvas = tk.Canvas(controls_container, highlightthickness=0, bg='#f0f0f0')
        controls_scrollbar = ttk.Scrollbar(controls_container, orient="vertical", command=controls_canvas.yview)
        controls_scrollable_frame = ttk.Frame(controls_canvas)
        
        # Configuración del scroll
        controls_scrollable_frame.bind("<Configure>", 
            lambda e: controls_canvas.configure(scrollregion=controls_canvas.bbox("all")))
        controls_canvas.create_window((0, 0), window=controls_scrollable_frame, anchor="nw")
        controls_canvas.configure(yscrollcommand=controls_scrollbar.set)
        controls_canvas.grid(row=0, column=0, sticky="nsew")
        controls_scrollbar.grid(row=0, column=1, sticky="ns")
        
        # Frame de controles
        controls_frame = ttk.LabelFrame(controls_scrollable_frame, text="Controles", padding="8")
        controls_frame.grid(row=0, column=0, sticky="nsew")
        controls_frame.columnconfigure(0, weight=1)
        
        # Secciones de controles
        self.setup_image_section(controls_frame)
        self.setup_processing_section(controls_frame)
        self.setup_resolution_section(controls_frame)
        self.setup_color_section(controls_frame)
        self.setup_position_section(controls_frame)
        
        # Eventos de scroll
        controls_canvas.bind("<Configure>", 
            lambda e: controls_canvas.itemconfig(1, width=e.width))
        def on_mousewheel(event):
            controls_canvas.yview_scroll(int(-1*(event.delta/120)), "units")
        controls_canvas.bind("<MouseWheel>", on_mousewheel)

    def setup_image_section(self, parent):
        """Sección de carga de imagen"""
        ttk.Button(parent, text="Cargar Imagen", command=self.load_image).grid(
            row=0, column=0, sticky="ew", pady=4)
        info_frame = ttk.Frame(parent)
        info_frame.grid(row=1, column=0, sticky="ew", pady=(0,8))
        ttk.Label(info_frame, text="Información:", font=("Helvetica", 10, "bold")).grid(
            row=0, column=0, sticky="w")
        ttk.Label(info_frame, textvariable=self.image_info_var, wraplength=220, 
        justify=tk.LEFT).grid(row=1, column=0, sticky="w")
        ttk.Separator(parent, orient="horizontal").grid(row=2, column=0, sticky="ew", pady=6)
        ttk.Button(parent, text="Generar Wallpaper", command=self.generate_wallpaper).grid(
            row=3, column=0, sticky="ew", pady=4)
        ttk.Button(parent, text="Guardar", command=self.save_wallpaper).grid(
            row=4, column=0, sticky="ew", pady=4)
        ttk.Separator(parent, orient="horizontal").grid(row=5, column=0, sticky="ew", pady=6)

    def setup_processing_section(self, parent):
        """Sección de procesamiento"""
        ttk.Label(parent, text="Opciones de procesamiento:").grid(
            row=6, column=0, sticky="w")
        self.remove_bg_var = tk.BooleanVar(value=False)
        remove_cb = ttk.Checkbutton(parent, text="Eliminar fondo (rembg)", 
        variable=self.remove_bg_var, command=self.update_options)
        remove_cb.grid(row=7, column=0, sticky="w", pady=2)
        if not self.logic.REMBG_AVAILABLE:
            remove_cb.config(state="disabled", 
        text="Eliminar fondo (rembg) — no disponible")
        self.add_outline_var = tk.BooleanVar()
        self.outline_check = ttk.Checkbutton(parent, text="Agregar contorno blanco", 
        variable=self.add_outline_var)
        self.outline_check.grid(row=8, column=0, sticky="w", pady=2)
        self.blur_bg_var = tk.BooleanVar()
        ttk.Checkbutton(parent, text="Fondo con blur", variable=self.blur_bg_var).grid(
            row=9, column=0, sticky="w", pady=2)
        ttk.Separator(parent, orient="horizontal").grid(row=10, column=0, sticky="ew", pady=6)

    def setup_resolution_section(self, parent):
        """Sección de resolución"""
        ttk.Label(parent, text="Resolución:").grid(row=11, column=0, sticky="w")
        
        resolution_combo = ttk.Combobox(parent, textvariable=self.resolution_var, 
        values=list(self.logic.resolutions.keys()), 
        state="readonly", width=20)
        resolution_combo.grid(row=12, column=0, sticky="ew", pady=2)
        resolution_combo.bind("<<ComboboxSelected>>", self.on_resolution_change)

        # Configuración personalizada
        self.custom_frame = ttk.Frame(parent)
        self.custom_frame.grid(row=13, column=0, sticky="ew", pady=2)
        self.custom_width = tk.StringVar(value="1920")
        self.custom_height = tk.StringVar(value="1080")
        ttk.Label(self.custom_frame, text="Ancho:").grid(row=0, column=0, sticky="w")
        ttk.Entry(self.custom_frame, textvariable=self.custom_width, width=8).grid(
        row=0, column=1, padx=2)
        ttk.Label(self.custom_frame, text="Alto:").grid(row=0, column=2, sticky="w", padx=(8,0))
        ttk.Entry(self.custom_frame, textvariable=self.custom_height, width=8).grid(
        row=0, column=3, padx=2)
        self.custom_frame.grid_remove()
        ttk.Separator(parent, orient="horizontal").grid(row=14, column=0, sticky="ew", pady=6)

    def setup_color_section(self, parent):
        """Sección de color de fondo"""
        ttk.Label(parent, text="Color de fondo:").grid(row=15, column=0, sticky="w")
        color_frame = ttk.Frame(parent)
        color_frame.grid(row=16, column=0, sticky="ew")
        self.color_option = tk.StringVar(value="auto")
        ttk.Radiobutton(color_frame, text="Automático", variable=self.color_option, 
        value="auto", command=self.debounced_update_preview).grid(
            row=0, column=0, sticky="w")
        ttk.Radiobutton(color_frame, text="Blanco", variable=self.color_option, 
        value="white", command=self.debounced_update_preview).grid(
            row=1, column=0, sticky="w")
        ttk.Radiobutton(color_frame, text="Negro", variable=self.color_option, 
        value="black", command=self.debounced_update_preview).grid(
            row=2, column=0, sticky="w")
        ttk.Radiobutton(color_frame, text="Personalizado", variable=self.color_option, 
        value="custom", command=self.debounced_update_preview).grid(
            row=3, column=0, sticky="w")
        
        self.custom_color = "#FFFFFF"
        ttk.Button(color_frame, text="Elegir color", command=self.choose_color).grid(
            row=4, column=0, sticky="w", pady=4)
        ttk.Separator(parent, orient="horizontal").grid(row=17, column=0, sticky="ew", pady=6)

    def setup_position_section(self, parent):
        """Sección de posicionamiento"""
        ttk.Label(parent, text="Posición de la imagen:").grid(row=18, column=0, sticky="w")
        pos_frame = ttk.Frame(parent)
        pos_frame.grid(row=19, column=0, sticky="ew", pady=2)
        ttk.Radiobutton(pos_frame, text="Izquierda", variable=self.logic.position_var, 
            value="left", command=self.debounced_update_preview).grid(
            row=0, column=0, sticky="w")
        ttk.Radiobutton(pos_frame, text="Centro", variable=self.logic.position_var, 
            value="center", command=self.debounced_update_preview).grid(
            row=0, column=1, sticky="w")
        ttk.Radiobutton(pos_frame, text="Derecha", variable=self.logic.position_var, 
            value="right", command=self.debounced_update_preview).grid(
            row=0, column=2, sticky="w")

        # Offsets
        offset_frame = ttk.Frame(parent)
        offset_frame.grid(row=20, column=0, sticky="ew", pady=4)
        ttk.Label(offset_frame, text="Offset X:").grid(row=0, column=0, sticky="w")
        ttk.Spinbox(offset_frame, from_=-5000, to=5000, textvariable=self.logic.offset_x_var, 
        width=7, command=self.debounced_update_preview).grid(row=0, column=1, padx=4)
        ttk.Label(offset_frame, text="Offset Y:").grid(row=0, column=2, sticky="w", padx=(8,0))
        ttk.Spinbox(offset_frame, from_=-5000, to=5000, textvariable=self.logic.offset_y_var, 
        width=7, command=self.debounced_update_preview).grid(row=0, column=3, padx=4)

        # Botones de ajuste
        self.setup_nudge_buttons(parent)

    def setup_nudge_buttons(self, parent):
        """Botones de ajuste fino"""
        nudges = ttk.Frame(parent)
        nudges.grid(row=21, column=0, sticky="ew", pady=(4,6))
        nudges.columnconfigure([0,1,2], weight=1)

        buttons = [
            ("↖", -10, -10), ("↑", 0, -10), ("↗", 10, -10),
            ("←", -10, 0), ("•", 0, 0), ("→", 10, 0),
            ("↙", -10, 10), ("↓", 0, 10), ("↘", 10, 10)
        ]
        for i, (text, dx, dy) in enumerate(buttons):
            row, col = i // 3, i % 3
            ttk.Button(nudges, text=text, width=3, style="Nudge.TButton",
                command=lambda dxx=dx, dyy=dy: self.nudge(dxx, dyy)).grid(
                row=row, column=col, padx=2, pady=2)

    def setup_preview_panel(self, parent):
        """Panel de vista previa optimizado"""
        preview_frame = ttk.LabelFrame(parent, text="Vista Previa", padding="8")
        preview_frame.grid(row=0, column=1, sticky="nsew")
        preview_frame.columnconfigure(0, weight=1)
        preview_frame.rowconfigure(0, weight=1)

        # Canvas con scrollbars
        self.preview_canvas = tk.Canvas(preview_frame, bg="#f0f0f0",
        relief="sunken", borderwidth=1)
        self.preview_canvas.grid(row=0, column=0, sticky="nsew")
        v_scroll = ttk.Scrollbar(preview_frame, orient="vertical",
        command=self.preview_canvas.yview)
        v_scroll.grid(row=0, column=1, sticky="ns")
        h_scroll = ttk.Scrollbar(preview_frame, orient="horizontal",
        command=self.preview_canvas.xview)
        h_scroll.grid(row=1, column=0, sticky="ew")
        self.preview_canvas.configure(yscrollcommand=v_scroll.set,
        xscrollcommand=h_scroll.set)

        # Info de zoom
        ttk.Label(preview_frame, textvariable=self.zoom_info,
        font=("Helvetica", 10)).grid(row=2, column=0, sticky="ew")

        # Bind de eventos
        self.setup_canvas_events()

    def setup_canvas_events(self):
        """Configuración de eventos del canvas"""
        # Teclado
        key_bindings = {
            "<Left>": (-10, 0), "<Right>": (10, 0),
            "<Up>": (0, -10), "<Down>": (0, 10),
            "<Shift-Left>": (-1, 0), "<Shift-Right>": (1, 0),
            "<Shift-Up>": (0, -1), "<Shift-Down>": (0, 1)
        }
        for key, (dx, dy) in key_bindings.items():
            self.root.bind(key, lambda e, dxx=dx, dyy=dy: self.nudge(dxx, dyy))
        
        # Manipulacion con el Raton
        self.preview_canvas.bind("<Button-1>", 
        lambda e: self.preview_canvas.focus_set())
        self.preview_canvas.bind("<ButtonPress-1>", self.on_drag_start)
        self.preview_canvas.bind("<B1-Motion>", self.on_drag_motion)
        self.preview_canvas.bind("<ButtonRelease-1>", self.on_drag_release)

    def setup_status_bar(self, parent):
        """Barra de estado"""
        status_bar = ttk.Frame(parent)
        status_bar.grid(row=1, column=0, columnspan=2, sticky="ew", pady=(5, 0))
        ttk.Label(status_bar, textvariable=self.status_var, 
        font=("Helvetica", 10)).pack(side=tk.LEFT)
        ttk.Label(status_bar, text="Lazypaper v1.0", 
        font=("Helvetica", 10)).pack(side=tk.RIGHT)

    # -------------------- MÉTODOS DE INTERACCIÓN --------------------
    def on_drag_start(self, event):
        """Inicio del arrastre optimizado"""
        self.drag_data.update({"x": event.x, "y": event.y, "item": None})
        items = self.preview_canvas.find_overlapping(event.x-1, event.y-1, event.x+1, event.y+1)
        if items:
            self.drag_data["item"] = items[0]

    def on_drag_motion(self, event):
        """Durante el arrastre optimizado"""
        if not self.drag_data["item"]:
            return
        dx = event.x - self.drag_data["x"]
        dy = event.y - self.drag_data["y"]
        self.preview_canvas.move(self.drag_data["item"], dx, dy)
        self.drag_data.update({"x": event.x, "y": event.y})

    def on_drag_release(self, event):
        """Fin del arrastre"""
        self.drag_data["item"] = None

    def debounced_update_preview(self, event=None):
        """Actualización con debounce para mejor rendimiento"""
        current_time = time.time()
        if current_time - self._last_update_time < 0.1:  # 100ms debounce
            if self._update_debounce_id:
                self.root.after_cancel(self._update_debounce_id)
            self._update_debounce_id = self.root.after(100, self.update_preview)
            return
        
        self._last_update_time = current_time
        self.update_preview()

    # -------------------- MÉTODOS UTILITARIOS --------------------
    def get_target_resolution(self):
        """Obtener resolución con validación optimizada"""
        res_name = self.resolution_var.get()
        if not res_name:
            messagebox.showwarning("Advertencia", "Selecciona una resolución primero.")
            return (1920, 1080)
        
        if res_name == "Personalizado":
            try:
                width = int(self.custom_width.get())
                height = int(self.custom_height.get())
                if width > 0 and height > 0:
                    return width, height
            except ValueError:
                pass
            messagebox.showwarning("Advertencia", "Resolución personalizada inválida.")
            return (1920, 1080)
        return self.logic.resolutions.get(res_name, (1920, 1080))
        
    def nudge(self, dx: int, dy: int):
        """Ajuste fino de posición"""
        self.logic.offset_x_var.set(self.logic.offset_x_var.get() + dx)
        self.logic.offset_y_var.set(self.logic.offset_y_var.get() + dy)
        self.debounced_update_preview()
    
    def update_options(self):
        """Actualizar opciones de procesamiento"""
        if self.remove_bg_var.get() and self.logic.REMBG_AVAILABLE:
            self.outline_check.config(state="normal")
        else:
            self.outline_check.config(state="disabled")
            
    def on_resolution_change(self, event=None):
        """Manejar cambio de resolución"""
        if self.resolution_var.get() == "Personalizado":
            self.custom_frame.grid()
        else:
            self.custom_frame.grid_remove()
            
    def choose_color(self):
        """Selector de color optimizado"""
        color = colorchooser.askcolor(title="Elegir color de fondo", 
        initialcolor=self.custom_color)
        if color and color[1]:
            self.custom_color = color[1]
            self.debounced_update_preview()
            
    def get_background_color(self):
        """Obtener color de fondo optimizado"""
        option = self.color_option.get()
        if option == "white":
            return (255, 255, 255)
        elif option == "black":
            return (0, 0, 0)
        elif option == "custom":
            try:
                hex_color = self.custom_color.lstrip('#')
                return tuple(int(hex_color[i:i+2], 16) for i in (0, 2, 4))
            except:
                return (255, 255, 255)
        else:
            if self.logic.original_image:
                return self.logic.get_dominant_color(self.logic.original_image)
            return (255, 255, 255)

    # -------------------- CARGA DE IMAGEN OPTIMIZADA --------------------
    def load_image(self):
        """Carga optimizada de imágenes con thread"""
        file_types = [
            ('Imágenes', '*.png *.jpg *.jpeg *.tiff *.tif'),
            ('PNG', '*.png'),
            ('JPEG', '*.jpg *.jpeg'),
            ('TIFF', '*.tiff *.tif')
        ]
        filename = filedialog.askopenfilename(title="Seleccionar imagen", filetypes=file_types)
        if not filename:
            return

        # Ventana de progreso
        progress_win = tk.Toplevel(self.root)
        progress_win.title("Cargando imagen...")
        progress_win.geometry("300x80")
        progress_win.transient(self.root)
        progress_win.grab_set()
        ttk.Label(progress_win, text=f"Cargando: {os.path.basename(filename)}").pack(pady=(8,4))
        pb = ttk.Progressbar(progress_win, mode='indeterminate')
        pb.pack(fill=tk.X, padx=12, pady=8)
        pb.start(10)

        self.status_var.set(f"Cargando {os.path.basename(filename)}...")

        def do_load():
            try:
                with Image.open(filename) as img:
                    if img.mode not in ['RGB', 'RGBA']:
                        img = img.convert('RGB')
                    # Crear thumbnail para análisis rápido
                    thumb = img.copy()
                    thumb.thumbnail((800, 800), Image.LANCZOS)
                    self.root.after(0, lambda: self._finish_load(img, thumb, filename, progress_win, pb))
            except Exception as e:
                self.root.after(0, lambda: (progress_win.destroy(), 
                    messagebox.showerror("Error", f"No se pudo cargar: {str(e)}")))

        threading.Thread(target=do_load, daemon=True).start()

    def _finish_load(self, image, thumbnail, filename, progress_win, pb):
        """Finalizar carga de imagen"""
        pb.stop()
        progress_win.destroy()
        self.logic.original_image = image
        self.logic.thumbnail = thumbnail
        self.logic.current_image_path = filename
        self.logic.processed_image = None
        self.logic.offset_x_var.set(0)
        self.logic.offset_y_var.set(0)
        self.update_preview()
        self.status_var.set("Imagen cargada")
        # Análisis en segundo plano
        threading.Thread(target=self._analyze_in_background, daemon=True).start()

    def _analyze_in_background(self):
        """Análisis en segundo plano"""
        if self.logic.original_image:
            self.logic.analyze_image()
            self.root.after(0, lambda: self.image_info_var.set(self.logic.image_info.get()))

    # -------------------- GENERACIÓN OPTIMIZADA --------------------
    def generate_wallpaper(self):
        """Generación optimizada de wallpaper"""
        if not self.logic.original_image:
            messagebox.showwarning("Advertencia", "Carga una imagen primero.")
            return
        try:
            target_size = self.get_target_resolution()
            self.status_var.set("Generando wallpaper...")
            options = {
                'remove_bg': self.remove_bg_var.get(),
                'add_outline': self.add_outline_var.get(),
                'blur_bg': self.blur_bg_var.get(),
                'position': self.logic.position_var.get(),
                'offset_x': self.logic.offset_x_var.get(),
                'offset_y': self.logic.offset_y_var.get(),
                'bg_color': self.get_background_color()
            }
            # Generar en thread separado para no bloquear la UI
            def generate_thread():
                result = self.logic.generate_wallpaper(target_size, options)
                self.root.after(0, lambda: self._finish_generate(result))
            threading.Thread(target=generate_thread, daemon=True).start()
        except Exception as e:
            self.status_var.set("Error al generar")
            messagebox.showerror("Error", f"Error al generar wallpaper: {str(e)}")

    def _finish_generate(self, result):
        """Finalizar generación"""
        if result:
            self.logic.processed_image = result
            self.update_preview()
            self.status_var.set("Wallpaper generado")
            messagebox.showinfo("Éxito", "Wallpaper generado correctamente!")
        else:
            self.status_var.set("Error al generar")
            messagebox.showerror("Error", "No se pudo generar el wallpaper")

    # -------------------- VISTA PREVIA OPTIMIZADA --------------------
    def update_preview(self):
        """Vista previa optimizada con cache"""
        display_image = self.logic.processed_image if self.logic.processed_image else self.logic.original_image
        if not display_image:
            self.preview_canvas.delete("all")
            return

        # Obtener dimensiones
        canvas_w = max(self.preview_canvas.winfo_width(), 1)
        canvas_h = max(self.preview_canvas.winfo_height(), 1)
        img_w, img_h = display_image.size
        img_ratio = img_w / img_h
        canvas_ratio = canvas_w / canvas_h

        # Calcular tamaño de preview
        if img_ratio > canvas_ratio:
            preview_w = canvas_w
            preview_h = int(canvas_w / img_ratio)
        else:
            preview_h = canvas_h
            preview_w = int(canvas_h * img_ratio)

        # Cache de imagen
        cache_key = (preview_w, preview_h, id(display_image))
        if self._preview_cache and self._preview_cache[0] == cache_key:
            preview_tk_image = self._preview_cache[1]
        else:
            preview_img = display_image.copy().resize((preview_w, preview_h), Image.LANCZOS)
            preview_tk_image = ImageTk.PhotoImage(preview_img)
            self._preview_cache = (cache_key, preview_tk_image)

        # Actualizar canvas
        self.preview_canvas.delete("all")
        # Calcular posición centrada
        x = (canvas_w - preview_w) // 2
        y = (canvas_h - preview_h) // 2

        # Dibujar fondo si es imagen original
        if self.logic.processed_image is None:
            bg_color = self.get_background_color()
            self.preview_canvas.create_rectangle(0, 0, canvas_w, canvas_h, 
            fill='#%02x%02x%02x' % bg_color, outline='')
        # Dibujar imagen
        self.preview_canvas.create_image(x, y, anchor=tk.NW, image=preview_tk_image)
        # Actualizar info de zoom
        zoom_percent = min(preview_w/img_w, preview_h/img_h) * 100
        self.zoom_info.set(f"Vista previa ({zoom_percent:.1f}%)")
        self.preview_canvas.configure(scrollregion=self.preview_canvas.bbox("all"))

    # -------------------- GUARDADO OPTIMIZADO --------------------
    def save_wallpaper(self):
        """Guardado optimizado"""
        if not self.logic.processed_image:
            messagebox.showwarning("Advertencia", "Genera un wallpaper primero.")
            return
        file_types = [
            ('PNG', '*.png'),
            ('JPEG', '*.jpg'),
            ('TIFF', '*.tiff')
        ]
        filename = filedialog.asksaveasfilename(
            title="Guardar wallpaper",
            defaultextension=".png",
            filetypes=file_types
        )
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