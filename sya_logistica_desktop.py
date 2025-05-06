# sya_logistica_desktop.py
import os
import sys
import requests
import tkinter as tk
from tkinter import messagebox, ttk
import subprocess
from datetime import datetime

class LogisticaDesktopApp:
    def __init__(self, root):
        self.root = root
        self.root.title("S&A Logística - Aplicación de Escritorio")
        self.root.geometry("800x600")
        self.root.resizable(True, True)
        
        # Configurar estilo
        self.configurar_estilo()
        
        # Crear carpeta de descargas si no existe
        self.ruta_descargas = self.crear_carpeta_descargas()
        
        # Crear interfaz
        self.crear_interfaz()
    
    def configurar_estilo(self):
        """Configura el estilo de la aplicación."""
        style = ttk.Style()
        style.configure("TFrame", background="#f0f0f0")
        style.configure("TButton", 
                        font=("Arial", 12, "bold"), 
                        padding=10, 
                        background="#0066cc", 
                        foreground="white")
        style.configure("TLabel", 
                        font=("Arial", 12), 
                        background="#f0f0f0", 
                        foreground="#333333")
        style.configure("Header.TLabel", 
                        font=("Arial", 16, "bold"), 
                        background="#f0f0f0", 
                        foreground="#0066cc")
        style.configure("Status.TLabel", 
                        font=("Arial", 10), 
                        background="#f0f0f0", 
                        foreground="#666666")
    
    def crear_carpeta_descargas(self):
        """Crea la carpeta de descargas si no existe."""
        ruta_app = os.path.dirname(os.path.abspath(__file__))
        ruta_descargas = os.path.join(ruta_app, "descargas")
        if not os.path.exists(ruta_descargas):
            try:
                os.makedirs(ruta_descargas)
            except Exception as e:
                messagebox.showerror("Error", f"No se pudo crear la carpeta 'descargas':\n{e}")
        return ruta_descargas
    
    def crear_interfaz(self):
        """Crea la interfaz de usuario."""
        # Frame principal
        main_frame = ttk.Frame(self.root, padding="20")
        main_frame.pack(fill=tk.BOTH, expand=True)
        
        # Título
        header_label = ttk.Label(main_frame, 
                                text="Sistema de Logística S&A", 
                                style="Header.TLabel")
        header_label.pack(pady=(0, 20))
        
        # Descripción
        desc_label = ttk.Label(main_frame, 
                              text="Esta aplicación permite descargar y gestionar los requerimientos de materiales enviados desde la aplicación móvil.", 
                              wraplength=700)
        desc_label.pack(pady=(0, 30))
        
        # Frame para botones
        button_frame = ttk.Frame(main_frame)
        button_frame.pack(pady=20)
        
        # Botón para descargar requerimientos
        download_button = ttk.Button(button_frame, 
                                    text="Descargar Requerimientos", 
                                    command=self.descargar_requerimientos)
        download_button.pack(pady=10, padx=20, fill=tk.X)
        
        # Botón para abrir archivo Excel
        open_button = ttk.Button(button_frame, 
                                text="Abrir Archivo Excel", 
                                command=self.abrir_excel)
        open_button.pack(pady=10, padx=20, fill=tk.X)
        
        # Etiqueta de estado
        self.status_label = ttk.Label(main_frame, 
                                     text="Listo", 
                                     style="Status.TLabel")
        self.status_label.pack(side=tk.BOTTOM, pady=10)
    
    def descargar_requerimientos(self):
        """Descarga el archivo Excel de requerimientos desde el servidor."""
        self.status_label.config(text="Descargando requerimientos...")
        self.root.update()
        
        try:
            # URL del servidor (ajustar según la configuración real)
            url_servidor = "http://34.67.103.132:5000/api/descargar-requerimientos"
            
            # Nombre del archivo a guardar
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            nombre_archivo = f"sya_logistica_requerimientos_{timestamp}.xlsx"
            ruta_archivo = os.path.join(self.ruta_descargas, nombre_archivo)
            
            # Realizar la descarga
            response = requests.get(url_servidor, stream=True, timeout=30)
            response.raise_for_status()
            
            # Guardar el archivo
            with open(ruta_archivo, 'wb') as f:
                for chunk in response.iter_content(chunk_size=8192):
                    f.write(chunk)
            
            # Actualizar estado y mostrar mensaje
            self.status_label.config(text=f"Archivo descargado: {nombre_archivo}")
            messagebox.showinfo("Descarga Completada", 
                               f"El archivo de requerimientos ha sido descargado correctamente.\n\nRuta: {ruta_archivo}")
            
            # Guardar la ruta del último archivo descargado
            self.ultimo_archivo = ruta_archivo
            
        except requests.exceptions.RequestException as e:
            self.status_label.config(text="Error al descargar el archivo")
            messagebox.showerror("Error de Conexión", 
                                f"No se pudo conectar al servidor:\n{e}")
        except Exception as e:
            self.status_label.config(text="Error al descargar el archivo")
            messagebox.showerror("Error", 
                                f"Ocurrió un error al descargar el archivo:\n{e}")
    
    def abrir_excel(self):
        """Abre el último archivo Excel descargado."""
        try:
            if hasattr(self, 'ultimo_archivo') and os.path.exists(self.ultimo_archivo):
                # Abrir el archivo con la aplicación predeterminada
                if sys.platform == 'win32':
                    os.startfile(self.ultimo_archivo)
                elif sys.platform == 'darwin':  # macOS
                    subprocess.call(['open', self.ultimo_archivo])
                else:  # Linux
                    subprocess.call(['xdg-open', self.ultimo_archivo])
                
                self.status_label.config(text=f"Archivo abierto: {os.path.basename(self.ultimo_archivo)}")
            else:
                # Si no hay archivo descargado, mostrar mensaje
                messagebox.showinfo("Información", 
                                   "No hay archivo para abrir. Por favor, descargue primero los requerimientos.")
                self.status_label.config(text="No hay archivo para abrir")
        except Exception as e:
            self.status_label.config(text="Error al abrir el archivo")
            messagebox.showerror("Error", 
                                f"Ocurrió un error al abrir el archivo:\n{e}")

if __name__ == "__main__":
    root = tk.Tk()
    app = LogisticaDesktopApp(root)
    root.mainloop()
