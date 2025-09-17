# logic.py - Lógica de la aplicación
import io
import os
from typing import Tuple, Optional
from collections import Counter
import tkinter as tk

from PIL import Image, ImageFilter, ImageDraw, ImageOps
import numpy as np

# Importar rembg opcionalmente
try:
    from rembg import remove as rembg_remove
    from rembg.session_factory import new_session
    REMBG_AVAILABLE = True
except Exception as e:
    print(f"rembg no disponible: {e}")
    REMBG_AVAILABLE = False

class LazyPaperLogic:
    def __init__(self):
        # Variables y estado
        self.original_image: Optional[Image.Image] = None
        self.processed_image: Optional[Image.Image] = None
        self.current_image_path: Optional[str] = None
        self._remove_bg_cache = None
        self._dominant_color_cache = None
        
        # Variables de estado para la interfaz
        self.image_info = tk.StringVar(value="No hay imagen cargada")
        self.position_var = tk.StringVar(value="center")  # left, center, right
        self.offset_x_var = tk.IntVar(value=0)
        self.offset_y_var = tk.IntVar(value=0)
        
        # Resoluciones comunes
        self.resolutions = {
            "Desktop HD (1280x720)": (1280, 720),
            "Desktop FHD (1920x1080)": (1920, 1080),
            "Desktop QHD (2560x1440)": (2560, 1440),
            "Desktop 4K (3840x2160)": (3840, 2160),
            "Mobile HD (1080x2150)": (1080, 2160),
            "Mobile QHD (1170x2532)": (1440, 2960),
            "Apple iPad (2048x1536)": (2048, 1536),
            "Apple iPad Pro (2048x2732)": (2048, 2732),
            "Tablet Android HD (1920x1200)": (1920, 1200),
            "Tablet Android Full HD (2048x2732)": (2560, 1600),
            "Personalizado": None
        }
        
        # Disponibilidad de rembg
        self.REMBG_AVAILABLE = REMBG_AVAILABLE

    # ---------- METHOD Analizar imagen----------
    def analyze_image(self):
        if not self.original_image:
            self.image_info.set("No hay imagen cargada")
            return
        w, h = self.original_image.size
        mode = self.original_image.mode
        has_transparency = mode in ['RGBA', 'LA'] or 'transparency' in self.original_image.info
        has_uniform_bg = self.detect_uniform_background()
        info_text = f"Dimensiones: {w}x{h}\nModo: {mode}\nTransparencia: {'Sí' if has_transparency else 'No'}\nFondo uniforme: {'Probable' if has_uniform_bg else 'No detectado'}"
        self.image_info.set(info_text)

    def detect_uniform_background(self) -> bool:
        if not self.original_image:
            return False
        img_rgb = self.original_image.convert('RGB')
        arr = np.array(img_rgb)
        h, w = arr.shape[:2]
        border_pixels = []
        border_pixels.extend(arr[0, :].reshape(-1, 3))
        border_pixels.extend(arr[-1, :].reshape(-1, 3))
        border_pixels.extend(arr[:, 0].reshape(-1, 3))
        border_pixels.extend(arr[:, -1].reshape(-1, 3))
        border_colors = [tuple(p) for p in border_pixels]
        if not border_colors:
            return False
        counts = Counter(border_colors)
        most_common_count = counts.most_common(1)[0][1]
        return (most_common_count / len(border_colors)) > 0.8

    # ---------- METHOD Background removal ----------
        
    def remove_background(self, image: Image.Image) -> Optional[Image.Image]:
        if not self.REMBG_AVAILABLE:
            return None
        
        # Verificar cache
        image_hash = hash(image.tobytes())
        if self._remove_bg_cache and self._remove_bg_cache[0] == image_hash:
            return self._remove_bg_cache[1].copy()
            
        try:
            # Optimizar: reducir tamaño para rembg si la imagen es muy grande
            if image.width * image.height > 2000 * 2000:
                # Crear una versión más pequeña para procesamiento
                temp_img = image.copy()
                temp_img.thumbnail((1500, 1500), Image.LANCZOS)
                
                # Convertir a bytes
                buf = io.BytesIO()
                temp_img.save(buf, format='PNG')
                data = buf.getvalue()
                
                # Procesar
                res = rembg_remove(data)
                result = Image.open(io.BytesIO(res)).convert('RGBA')
                
                # Escalar de vuelta al tamaño original
                result = result.resize(image.size, Image.LANCZOS)
            else:
                # Procesar imagen normal
                buf = io.BytesIO()
                image.save(buf, format='PNG')
                data = buf.getvalue()
                res = rembg_remove(data)
                result = Image.open(io.BytesIO(res)).convert('RGBA')
            
            # Actualizar cache
            self._remove_bg_cache = (image_hash, result.copy())
            return result
            
        except Exception as e:
            print(f"No se pudo eliminar el fondo: {str(e)}")
            return None

    # ---------- METHOD Outline ----------
    def add_outline_to_image(self, image: Image.Image, outline_width: int = 6) -> Image.Image:
        """Crear contorno blanco a partir del canal alfa de la imagen (si la imagen tiene alfa)"""
        # Asegurar RGBA
        if image.mode != 'RGBA':
            image = image.convert('RGBA')
        alpha = image.split()[-1]

        # blur + threshold
        dilated = alpha.filter(ImageFilter.GaussianBlur(radius=outline_width/2))
        # Threshold
        bw = dilated.point(lambda p: 255 if p > 10 else 0)
        # Contorno blanco
        outline_img = Image.new('RGBA', (image.width, image.height), (255, 255, 255, 0))
        # Rellenar de blanco donde bw es blanco
        outline_img.paste(Image.new('RGBA', (image.width, image.height), (255,255,255,255)), mask=bw)
        # Pegar la imagen original encima
        outline_img.paste(image, (0,0), image)
        return outline_img

    # ---------- METHOD Blur background ----------
    def create_blur_background(self, image: Image.Image, target_size: Tuple[int, int]) -> Image.Image:
        target_w, target_h = target_size
        img_ratio = image.width / image.height
        target_ratio = target_w / target_h
        if img_ratio > target_ratio:
            new_height = target_h
            new_width = int(img_ratio * new_height)
        else:
            new_width = target_w
            new_height = int(new_width / img_ratio)
        bg = image.resize((new_width, new_height), Image.LANCZOS)
        bg = bg.filter(ImageFilter.GaussianBlur(radius=20))
        result = Image.new('RGB', (target_w, target_h), (0,0,0))
        x = (target_w - new_width)//2
        y = (target_h - new_height)//2
        result.paste(bg, (x,y))
        return result
            
    def get_dominant_color(self, image: Image.Image) -> Tuple[int, int, int]:
        """Método mejorado para obtener color dominante"""
        # Verificar cache
        image_hash = hash(image.tobytes())
        if self._dominant_color_cache and self._dominant_color_cache[0] == image_hash:
            return self._dominant_color_cache[1]
        
        try:
            # Reducir tamaño para análisis
            img = image.copy()
            img.thumbnail((100, 100), Image.LANCZOS)
            
            # Convertir a numpy array
            arr = np.array(img)
            
            # Si la imagen tiene transparencia, usar solo píxeles no transparentes
            if arr.shape[2] == 4:
                # Crear máscara para píxeles no transparentes
                alpha = arr[:,:,3] > 10  # Umbral para considerar no transparente
                if np.any(alpha):
                    pixels = arr[alpha][:,:3]
                else:
                    # Si toda la imagen es transparente, usar blanco
                    return (255, 255, 255)
            else:
                # Para imágenes sin transparencia, usar todos los píxeles
                pixels = arr.reshape(-1, 3)
            
            if len(pixels) == 0:
                return (255, 255, 255)
            
            try:
                # Obtener colores de los bordes
                border_pixels = []
                border_pixels.extend(arr[0, :, :3])  # Borde superior
                border_pixels.extend(arr[-1, :, :3])  # Borde inferior
                border_pixels.extend(arr[:, 0, :3])  # Borde izquierdo
                border_pixels.extend(arr[:, -1, :3])  # Borde derecho
                
                if len(border_pixels) > 0:
                    border_pixels = np.array(border_pixels)
                    # Usar el color más común en los bordes
                    border_colors = [tuple(color) for color in border_pixels]
                    color_counts = Counter(border_colors)
                    if color_counts:
                        most_common_border = color_counts.most_common(1)[0][0]
                        # Verificar si este color es predominante en los bordes
                        if color_counts.most_common(1)[0][1] > len(border_pixels) * 0.3:
                            result = tuple(int(c) for c in most_common_border)
                            self._dominant_color_cache = (image_hash, result)
                            return result
            except:
                pass
            
            # Si el método de bordes falla, usar el color promedio
            avg_color = np.mean(pixels, axis=0).astype(int)
            result = tuple(avg_color)
            
            # Actualizar cache
            self._dominant_color_cache = (image_hash, result)
            return result
            
        except Exception as e:
            print(f"Error en get_dominant_color: {e}")
            return (255, 255, 255)  # Blanco por defecto en caso de error

    # ---------- METHOD Generation ----------
    def generate_wallpaper(self, target_size, options):
        if not self.original_image:
            return None
            
        try:
            target_w, target_h = target_size
            work_image = self.original_image.copy()

            # Eliminar fondo
            if options['remove_bg']:
                removed = self.remove_background(work_image)
                if removed:
                    work_image = removed

                    if options['add_outline']:
                        work_image = self.add_outline_to_image(work_image)
                else:
                    # Si rembg falla, devolver None para indicar error
                    return None

            # Crear fondo
            if options['blur_bg'] and not options['remove_bg']:
                result = self.create_blur_background(self.original_image, (target_w, target_h))
            else:
                bg_color = options['bg_color']
                result = Image.new('RGB', (target_w, target_h), bg_color)

            # Calculo de tamaño manteniendo proporciones
            img_ratio = work_image.width / work_image.height
            target_ratio = target_w / target_h
            if img_ratio > target_ratio:
                new_w = min(target_w, work_image.width)
                new_h = int(new_w / img_ratio)
            else:
                new_h = min(target_h, work_image.height)
                new_w = int(new_h * img_ratio)

            if work_image.size != (new_w, new_h):
                work_image = work_image.resize((new_w, new_h), Image.LANCZOS)

            # Position horizontal
            pos = options['position']
            offset_x = options['offset_x']
            offset_y = options['offset_y']

            if pos == 'left':
                x = 0 + offset_x
            elif pos == 'right':
                x = target_w - new_w + offset_x
            else:  # center
                x = (target_w - new_w)//2 + offset_x
            y = (target_h - new_h)//2 + offset_y

            # Pegar respetando alfa si existe
            if work_image.mode == 'RGBA':
                base = result.convert('RGBA')
                temp = Image.new('RGBA', (target_w, target_h), (0,0,0,0))
                temp.paste(work_image, (x, y), work_image)
                base = Image.alpha_composite(base, temp)
                result = base.convert('RGB')
            else:
                result.paste(work_image, (x, y))

            return result
            
        except Exception as e:
            print(f"Error al generar wallpaper: {str(e)}")
            return None

    # ---------- METHOD Guardado de imagen ----------
    def save_wallpaper(self, filename):
        if not self.processed_image:
            return
            
        if filename.lower().endswith(('.jpg', '.jpeg')):
            save_image = self.processed_image.convert('RGB')
            save_image.save(filename, 'JPEG', quality=95)
        elif filename.lower().endswith('.tiff'):
            self.processed_image.save(filename, 'TIFF')
        else:
            self.processed_image.save(filename, 'PNG')