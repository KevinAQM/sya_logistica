import os
import sys
import requests
import tkinter as tk
from tkinter import messagebox, ttk
import subprocess
from datetime import datetime

# Intentar importar PIL para manejo de imágenes
try:
    from PIL import Image, ImageTk
    PIL_AVAILABLE = True
except ImportError:
    PIL_AVAILABLE = False

def resource_path(relative_path):
    try:
        base_path = sys._MEIPASS
    except Exception:
        base_path = os.path.abspath(".")
    return os.path.join(base_path, relative_path)

def obtener_ruta_aplicacion():
    if getattr(sys, 'frozen', False):
        return os.path.dirname(sys.executable)
    else:
        return os.path.dirname(os.path.abspath(__file__))

def crear_carpeta_descargas():
    ruta_app = obtener_ruta_aplicacion()
    ruta_descargas = os.path.join(ruta_app, "descargas")
    if not os.path.exists(ruta_descargas):
        try:
            os.makedirs(ruta_descargas)
        except Exception as e:
            messagebox.showerror("Error", f"No se pudo crear la carpeta 'descargas':\n{e}")
    return ruta_descargas

def descargar_requerimientos():
    """Descarga el archivo Excel de requerimientos desde el servidor."""
    status_label.config(text="Descargando requerimientos...")
    root.update()

    try:
        # URL del servidor
        url_servidor = "http://34.67.103.132:5000/api/logistica/descargar-requerimientos"

        # Nombre del archivo a guardar
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        nombre_archivo = f"sya_logistica_requerimientos.xlsx"
        ruta_descargas = crear_carpeta_descargas()
        ruta_archivo = os.path.join(ruta_descargas, nombre_archivo)

        # Realizar la descarga
        response = requests.get(url_servidor, stream=True, timeout=30)
        response.raise_for_status()

        # Guardar el archivo
        with open(ruta_archivo, 'wb') as f:
            for chunk in response.iter_content(chunk_size=8192):
                f.write(chunk)

        # Actualizar estado y mostrar mensaje
        status_label.config(text=f"Archivo descargado: {nombre_archivo}")
        messagebox.showinfo("Descarga Completada",
                           f"El archivo de requerimientos ha sido descargado correctamente.")

        # Guardar la ruta del último archivo descargado
        global ultimo_archivo
        ultimo_archivo = ruta_archivo
        return ruta_archivo

    except requests.exceptions.RequestException as e:
        status_label.config(text="Error al descargar el archivo")
        messagebox.showerror("Error de Conexión",
                            f"No se pudo conectar al servidor:\n{e}")
        return None
    except Exception as e:
        status_label.config(text="Error al descargar el archivo")
        messagebox.showerror("Error",
                            f"Ocurrió un error al descargar el archivo:\n{e}")
        return None

def abrir_archivo(ruta_archivo):
    """Abre un archivo con la aplicación predeterminada del sistema."""
    try:
        if sys.platform == 'win32':
            os.startfile(ruta_archivo)
        else:
            # Para macOS y Linux usamos subprocess
            if sys.platform == 'darwin':  # macOS
                cmd = ['open', ruta_archivo]
            else:  # Linux
                cmd = ['xdg-open', ruta_archivo]
            subprocess.call(cmd)
        return True
    except Exception as e:
        messagebox.showerror("Error", f"Error al abrir el archivo: {e}")
        return False

def abrir_excel():
    """Abre el último archivo Excel descargado."""
    global ultimo_archivo

    try:
        if 'ultimo_archivo' in globals() and os.path.exists(ultimo_archivo):
            # Abrir el archivo con la aplicación predeterminada
            if abrir_archivo(ultimo_archivo):
                status_label.config(text=f"Archivo abierto: {os.path.basename(ultimo_archivo)}")
        else:
            # Buscar el archivo más reciente en la carpeta de descargas
            ruta_descargas = crear_carpeta_descargas()
            archivos_excel = [f for f in os.listdir(ruta_descargas) if f.startswith("sya_logistica_requerimientos") and f.endswith(".xlsx")]

            if archivos_excel:
                # Ordenar por fecha de modificación (más reciente primero)
                archivos_excel.sort(key=lambda x: os.path.getmtime(os.path.join(ruta_descargas, x)), reverse=True)
                ultimo_archivo = os.path.join(ruta_descargas, archivos_excel[0])

                # Abrir el archivo
                if abrir_archivo(ultimo_archivo):
                    status_label.config(text=f"Archivo abierto: {os.path.basename(ultimo_archivo)}")
            else:
                # Si no hay archivo descargado, mostrar mensaje
                messagebox.showinfo("Información",
                                   "No hay archivo para abrir. Por favor, descargue primero los requerimientos.")
                status_label.config(text="No hay archivo para abrir")
    except Exception as e:
        status_label.config(text="Error al abrir el archivo")
        messagebox.showerror("Error",
                            f"Ocurrió un error al abrir el archivo:\n{e}")

def abrir_carpeta_descargas():
    """Abre la carpeta de descargas."""
    ruta_descargas = crear_carpeta_descargas()
    try:
        if abrir_archivo(ruta_descargas):
            status_label.config(text="Carpeta de descargas abierta")
    except Exception as e:
        status_label.config(text="Error al abrir la carpeta")
        messagebox.showerror("Error", f"Ocurrió un error al abrir la carpeta de descargas:\n{e}")

# Crear la ventana principal
root = tk.Tk()
root.title("S&A - Sistema de Logística")
root.geometry("450x520")
root.resizable(True, True)
root.configure(bg='#f0f0f0')

# Variable global para almacenar la ruta del último archivo descargado
ultimo_archivo = None

# Intentar cargar el icono
try:
    root.iconbitmap(resource_path("images/smontyaragon.ico"))
except Exception:
    pass

# Configurar estilos
style = ttk.Style(root)
style.theme_use('clam')

style.configure("Title.TLabel", font=("Helvetica", 16, "bold"), foreground="#333", background='#f0f0f0')

style.configure("Base.TButton", font=("Helvetica", 14), padding=(15, 12), relief="flat", background="#e0e0e0", foreground="#333")
style.map("Base.TButton",
          background=[("active", "#f0f0f0")],
          relief=[("active", "raised")]
          )

style.configure("Descargar.TButton", parent="Base.TButton", background="#cce0ff", foreground="#003366")
style.map("Descargar.TButton",
          background=[("active", "#b3d1ff")],
          foreground=[("active", "#003366")]
          )

style.configure("Abrir.TButton", parent="Base.TButton", background="#90EE90", foreground="#006400") # Verde claro
style.map("Abrir.TButton",
          background=[("active", "#7FFFD4")], # Acuamarine
          foreground=[("active", "#006400")]
          )

# Título
titulo = ttk.Label(root, text="S&A - Sistema de Logística", style="Title.TLabel")
titulo.pack(pady=20)

# Intentar cargar la imagen
if PIL_AVAILABLE:
    try:
        image = Image.open(resource_path("images/smontyaragon.png"))
        photo = ImageTk.PhotoImage(image)
        label_imagen = ttk.Label(root, image=photo)
        label_imagen.image = photo
        label_imagen.pack(pady=15)
    except Exception:
        # Si no se puede cargar la imagen, mostrar un texto alternativo
        label_texto = ttk.Label(root, text="S&A Logística", font=("Helvetica", 20, "bold"), foreground="#0066cc")
        label_texto.pack(pady=15)
else:
    # Si PIL no está disponible, mostrar un texto alternativo
    label_texto = ttk.Label(root, text="S&A Logística", font=("Helvetica", 20, "bold"), foreground="#0066cc")
    label_texto.pack(pady=15)

# Crear carpeta de descargas
crear_carpeta_descargas()

# Frame para botones
frame_botones = ttk.Frame(root)
frame_botones.pack(pady=20)

# Botones para requerimientos
frame_requerimientos_botones = ttk.Frame(frame_botones)
frame_requerimientos_botones.pack(pady=5)

btn_descargar_requerimientos = ttk.Button(frame_requerimientos_botones, text="Descargar Requerimientos", command=descargar_requerimientos, style="Descargar.TButton")
btn_descargar_requerimientos.pack(side='left', padx=10)

btn_abrir_excel = ttk.Button(frame_requerimientos_botones, text="Abrir Excel", command=abrir_excel, style="Abrir.TButton")
btn_abrir_excel.pack(side='left', padx=10)

# Botón para abrir carpeta de descargas
frame_carpeta_botones = ttk.Frame(frame_botones)
frame_carpeta_botones.pack(pady=5)

btn_abrir_carpeta = ttk.Button(frame_carpeta_botones, text="Abrir Carpeta Descargas", command=abrir_carpeta_descargas, style="Abrir.TButton")
btn_abrir_carpeta.pack(padx=10)

# Etiqueta de estado
status_label = ttk.Label(root, text="Listo", font=("Helvetica", 10), background="#f0f0f0")
status_label.pack(side=tk.BOTTOM, pady=10)

# Iniciar la aplicación
root.mainloop()
