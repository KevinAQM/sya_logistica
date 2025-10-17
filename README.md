# S&A - Sistema de Logística

Software de gestión logística desarrollado para Smont y Aragon. Sistema completo para la gestión de requerimientos de materiales con aplicaciones móvil (Android) y de escritorio (Windows), integradas con servidor backend.

## 📋 Tabla de Contenidos

- [Descripción General](#descripción-general)
- [Características Principales](#características-principales)
- [Arquitectura del Sistema](#arquitectura-del-sistema)
- [Tecnologías Utilizadas](#tecnologías-utilizadas)
- [Instalación](#instalación)
- [Uso](#uso)
- [Componentes del Sistema](#componentes-del-sistema)
- [API Endpoints](#api-endpoints)
- [Estructura de Archivos](#estructura-de-archivos)
- [Configuración](#configuración)
- [Seguridad](#seguridad)

## 📖 Descripción General

Sistema integral de gestión logística que permite a los usuarios:
- Crear y gestionar requerimientos de materiales
- Administrar bases de datos de materiales y clientes
- Sincronizar información entre aplicaciones móvil y de escritorio
- Generar reportes en formato Excel

## ✨ Características Principales

### Aplicación Móvil (Android - Kivy)

- **Formulario de Requerimientos Intuitivo**:
  - Campo de fecha con fecha actual pre-cargada
  - Autoconversión de texto a mayúsculas/capitalizado
  - Autocompletado optimizado para materiales y clientes
  - Sistema de sugerencias con debounce (evita lag)
  
- **Gestión de Materiales**:
  - Agregar múltiples materiales por requerimiento
  - Editar materiales existentes
  - Eliminar materiales con confirmación
  - ScrollView optimizado para visualización móvil
  
- **Autocompletado Inteligente**:
  - Sugerencias de materiales desde base de datos CSV
  - Dropdown de clientes con búsqueda rápida
  - Límite de 6 sugerencias para mejor rendimiento
  - Carga asíncrona de datos del servidor

- **Validaciones**:
  - Validación de campos obligatorios
  - Formato de cantidad (números con 2 decimales)
  - Verificación de conexión al servidor

### Aplicación de Escritorio (Windows - Tkinter)

- **Gestión de Archivos Excel**:
  - Descarga de requerimientos desde servidor
  - Ordenamiento automático por fecha (descendente)
  - Autoajuste de columnas para mejor visualización
  - Apertura directa de archivos descargados

- **Administración de Bases de Datos**:
  - Descarga/subida de base de datos de materiales (CSV)
  - Descarga/subida de base de datos de clientes (CSV)
  - Sistema de validación por contraseña para operaciones críticas
  - Gestión de carpeta de descargas local

- **Interfaz Gráfica Moderna**:
  - Estilos personalizados con ttk
  - Botones codificados por color según función
  - Barra de estado con retroalimentación en tiempo real
  - Logo corporativo integrado (con fallback)

### Servidor Backend (Flask)

- **API RESTful Completa**:
  - Endpoints para materiales, clientes y requerimientos
  - Sistema de gestión de archivos Excel y CSV
  - Manejo automático de codificación de archivos
  - CORS habilitado para comunicación con apps

- **Gestión de Datos**:
  - Almacenamiento de requerimientos con timestamp
  - Ordenamiento automático por fecha
  - Inicialización automática de archivos al inicio
  - Detección inteligente de codificación de archivos

- **Operaciones Soportadas**:
  - Recepción de requerimientos desde app móvil
  - Generación y descarga de reportes Excel
  - Actualización de bases de datos CSV
  - Gestión de múltiples tipos de archivos

## 🏗️ Arquitectura del Sistema

```
┌─────────────────────┐         ┌──────────────────────┐
│   App Android       │         │   App Escritorio     │
│   (Kivy/Python)     │◄───────►│   (Tkinter/Python)   │
└──────────┬──────────┘         └──────────┬───────────┘
           │                               │
           │         HTTP/REST             │
           │                               │
           └───────────┬───────────────────┘
                       │
                       ▼
           ┌───────────────────────┐
           │   Servidor Flask      │
           │   (Python/Flask)      │
           └───────────┬───────────┘
                       │
                       ▼
           ┌───────────────────────┐
           │   Archivos de Datos   │
           │   - Excel (.xlsx)     │
           │   - CSV (.csv)        │
           └───────────────────────┘
```

## 💻 Tecnologías Utilizadas

### Backend
- **Flask 3.1.0**: Framework web para API RESTful
- **Flask-CORS 5.0.1**: Manejo de CORS para comunicación cross-origin
- **pandas 2.2.3**: Procesamiento y análisis de datos
- **openpyxl 3.1.5**: Manipulación de archivos Excel
- **requests 2.32.3**: Cliente HTTP para comunicación con servidor

### Frontend Móvil
- **Kivy 2.3.1**: Framework para aplicaciones móviles multiplataforma
- **kivy-deps**: Dependencias nativas para Windows (angle, glew, sdl2)

### Frontend Escritorio
- **Tkinter**: Interfaz gráfica estándar de Python
- **Pillow (PIL)**: Procesamiento de imágenes para logo
- **openpyxl**: Manipulación de Excel en cliente

### Utilidades
- **chardet**: Detección automática de codificación de archivos
- **python-dateutil**: Manejo avanzado de fechas
- **numpy**: Soporte para operaciones numéricas

## 🚀 Instalación

### Requisitos Previos
- Python 3.8 o superior
- pip (gestor de paquetes de Python)
- Conexión a Internet (para comunicación con servidor)

### Pasos de Instalación

1. **Clonar o descargar el repositorio**:
```bash
cd /ruta/al/proyecto
```

2. **Crear entorno virtual (recomendado)**:
```bash
python -m venv venv

# Windows
venv\Scripts\activate

# Linux/Mac
source venv/bin/activate
```

3. **Instalar dependencias**:
```bash
pip install -r requirements.txt
```

4. **Configurar archivos de datos**:
   - Crear carpeta `data/` si no existe
   - Colocar archivos CSV:
     - `logistica_materiales.csv` (material, unidad)
     - `logistica_clientes.csv` (cliente)

5. **Configurar servidor** (si se ejecuta localmente):
```bash
# En sya_operaciones_server.py, cambiar:
# SERVER_URL = "http://127.0.0.1:5000"  # Local
# SERVER_URL = "http://34.67.103.132:5000"  # Producción
```

## 📱 Uso

### Ejecutar Servidor

```bash
python sya_operaciones_server.py
```

El servidor se iniciará en `http://0.0.0.0:5000`

### Ejecutar Aplicación Móvil

```bash
python main.py
```

**Flujo de trabajo móvil**:
1. Verificar fecha actual pre-cargada
2. Ingresar nombre del solicitante
3. Ingresar orden de trabajo
4. Seleccionar/ingresar cliente (con autocompletado)
5. Agregar materiales usando botón "AGREGAR":
   - Escribir nombre (aparecen sugerencias)
   - Seleccionar o ingresar manualmente
   - Ingresar cantidad
6. Revisar lista de materiales
7. Editar/eliminar si es necesario
8. Presionar "ENVIAR REQUERIMIENTOS"

### Ejecutar Aplicación de Escritorio

```bash
python sya_logistica_desktop.py
```

**Funciones disponibles**:

- **Descargar Requerimientos**: Obtiene el Excel con todos los requerimientos
- **Abrir Excel Requerimientos**: Abre el último archivo descargado
- **Descargar BB.DD. Materiales**: Descarga archivo CSV de materiales
- **Abrir BB.DD. Materiales**: Abre el CSV de materiales
- **Subir BB.DD. Materiales**: Actualiza la base de datos en servidor (requiere contraseña)
- **Descargar Clientes**: Descarga archivo CSV de clientes
- **Abrir Clientes**: Abre el CSV de clientes
- **Subir Clientes**: Actualiza la base de datos de clientes (requiere contraseña)
- **Abrir Carpeta Descargas**: Abre la carpeta local de descargas

## 🔧 Componentes del Sistema

### 1. main.py (Aplicación Móvil)

**Clases principales**:

- `MaterialItem`: Widget para mostrar materiales en lista
- `FormularioScreen`: Pantalla principal con lógica del formulario

**Funciones clave**:
- `on_start()`: Inicializa fecha y eventos
- `cargar_materiales()` / `cargar_clientes()`: Carga datos desde servidor
- `mostrar_popup_agregar_material()`: Popup para agregar materiales
- `actualizar_sugerencias_scrollview_debounce()`: Autocompletado optimizado
- `mostrar_sugerencias_cliente_optimizado()`: Sugerencias de clientes
- `enviar_requerimientos()`: Envío de datos al servidor
- `limpiar_formulario()`: Limpieza post-envío

**Optimizaciones**:
- Debounce de 250ms para materiales, 200ms para clientes
- Límite de 6 sugerencias por consulta
- Carga asíncrona con threading
- Gestión de memoria con cierre de dropdowns

### 2. sya_logistica_desktop.py (Aplicación de Escritorio)

**Clases principales**:

- `FileUtils`: Utilidades para manejo de archivos
- `APIClient`: Cliente para comunicación con servidor
- `ExcelUtils`: Operaciones con archivos Excel
- `SyaLogisticaApp`: Aplicación principal

**Funciones destacadas**:
- `ordenar_excel_por_fecha()`: Ordenamiento descendente por fecha
- `ajustar_columnas()`: Autoajuste de anchos de columna
- `validar_contraseña_admin()`: Popup de validación de seguridad
- `descargar_archivo()` / `subir_archivo()`: Comunicación HTTP

**Características**:
- Configuración DPI para Windows (alta resolución)
- Estilos personalizados por tipo de operación
- Barra de estado con retroalimentación
- Contraseña de administrador: `syasya25`

### 3. sya_operaciones_server.py (Servidor Backend)

**Funciones principales**:

- `inicializar_excel()`: Crea archivos Excel con estructura inicial
- `procesar_logistica_requerimientos()`: Procesa y almacena requerimientos
- `read_csv_with_encoding_detection()`: Detección automática de codificación

**API Endpoints Logística**:

| Endpoint | Método | Descripción |
|----------|--------|-------------|
| `/api/logistica/materiales` | GET | Lista de materiales |
| `/api/logistica/clientes` | GET | Lista de clientes |
| `/api/logistica/enviar-requerimientos` | POST | Enviar nuevo requerimiento |
| `/api/logistica/descargar-requerimientos` | GET | Descargar Excel de requerimientos |
| `/api/logistica/descargar-bdd` | GET | Descargar CSV de materiales |
| `/api/logistica/subir-bdd` | POST | Actualizar CSV de materiales |
| `/api/logistica/descargar-clientes` | GET | Descargar CSV de clientes |
| `/api/logistica/subir-clientes` | POST | Actualizar CSV de clientes |

## 📂 Estructura de Archivos

```
logistica_code/
│
├── main.py                          # App móvil Android (Kivy)
├── formulario.kv                    # Diseño UI de Kivy
├── sya_logistica_desktop.py         # App de escritorio Windows
├── sya_operaciones_server.py        # Servidor Flask
├── requirements.txt                 # Dependencias Python
├── README.md                        # Documentación
│
├── data/                            # Bases de datos
│   ├── logistica_materiales.csv     # Base de datos de materiales
│   └── logistica_clientes.csv       # Base de datos de clientes
│
├── descargas/                       # Archivos descargados (local)
│   └── sya_logistica_requerimientos.xlsx
│
├── images/                          # Recursos gráficos
│   ├── smontyaragon.ico            # Icono de aplicación
│   └── smontyaragon.png            # Logo corporativo
│
└── sya_logistica_requerimientos.xlsx  # Excel de requerimientos (servidor)
```

## ⚙️ Configuración

### Configuración del Servidor

En `main.py` y `sya_logistica_desktop.py`:

```python
# Producción
SERVER_URL = "http://34.67.103.132:5000"

# Desarrollo local
SERVER_URL = "http://127.0.0.1:5000"
```

### Estructura CSV Materiales

```csv
material,unidad
"ALAMBRE TELEFÓNICO 2P Nº14",ml
"CABLE THW 14 AWG",ml
"CEMENTO PORTLAND TIPO I",BL
```

### Estructura CSV Clientes

```csv
cliente
"EMPRESA EJEMPLO S.A.C."
"MUNICIPALIDAD DISTRITAL"
"CONSORCIO ABC"
```

### Estructura Excel Requerimientos

| Fecha | Solicitante | Orden de Trabajo | Cliente | Cantidad | Unidad | Producto | Stock | Timestamp |
|-------|-------------|------------------|---------|----------|--------|----------|-------|-----------|
| 17/10/2025 | Juan Pérez | OT90-25 | EMPRESA X | 100.00 | ml | CABLE | | 2025-10-17 14:30:00 |

## 🔐 Seguridad

### Contraseña de Administrador

Las operaciones críticas (subir bases de datos) requieren autenticación:

- **Contraseña por defecto**: `syasya25`
- **Ubicación**: Variable `ADMIN_PASSWORD` en `sya_logistica_desktop.py`

**Para cambiar la contraseña**:

```python
# En sya_logistica_desktop.py
ADMIN_PASSWORD = "tu_nueva_contraseña"
```

### Validación de Entrada

- Cantidad: Solo números decimales positivos
- Fecha: Formato YYYY-MM-DD validado
- Campos obligatorios: Verificación antes de envío

### Comunicación

- CORS habilitado para endpoints específicos
- Timeout de 30s en descargas, 60s en subidas
- Manejo de excepciones HTTP

## 📊 Formato de Datos

### Request POST Requerimientos

```json
{
  "fecha": "2025-10-17",
  "solicitante": "Juan Pérez",
  "orden_trabajo": "OT90-25",
  "cliente": "EMPRESA EJEMPLO S.A.C.",
  "productos": [
    {
      "producto": "CABLE THW 14 AWG",
      "unidad": "ml",
      "cantidad": "100.00"
    },
    {
      "producto": "CEMENTO PORTLAND TIPO I",
      "unidad": "BL",
      "cantidad": "50.00"
    }
  ]
}
```

### Response GET Materiales

```json
[
  {
    "material": "CABLE THW 14 AWG",
    "unidad": "ml"
  },
  {
    "material": "CEMENTO PORTLAND TIPO I",
    "unidad": "BL"
  }
]
```

### Response GET Clientes

```json
[
  "EMPRESA EJEMPLO S.A.C.",
  "MUNICIPALIDAD DISTRITAL",
  "CONSORCIO ABC"
]
```

## 🐛 Solución de Problemas

### Error de Conexión al Servidor

**Síntoma**: "No se pudo conectar al servidor"

**Soluciones**:
1. Verificar que el servidor esté ejecutándose
2. Comprobar la URL del servidor en el código
3. Verificar conexión a Internet
4. Revisar firewall/antivirus

### Archivos CSV no se Cargan

**Síntoma**: Base de datos vacía o errores de codificación

**Soluciones**:
1. Verificar formato UTF-8 de archivos CSV
2. Asegurar que las columnas sean `material,unidad` o `cliente`
3. Usar el sistema de detección automática de codificación del servidor

### Aplicación Móvil con Lag

**Síntoma**: Aplicación lenta al escribir

**Soluciones**:
1. Sistema de debounce ya implementado (250ms materiales, 200ms clientes)
2. Limitar sugerencias a 6 elementos
3. Cerrar dropdowns después de selección

### Error al Abrir Excel

**Síntoma**: "No se puede abrir el archivo"

**Soluciones**:
1. Instalar Microsoft Excel o compatible (LibreOffice)
2. Verificar que el archivo se haya descargado completamente
3. Comprobar permisos de la carpeta de descargas

## 📝 Notas de Desarrollo

- **Versión**: 2.0
- **Fecha**: Octubre 2025
- **Compatibilidad**: Python 3.8+, Windows 10+, Android 8.0+
- **Licencia**: Uso interno Smont y Aragon

## 🔄 Próximas Mejoras

- [ ] Exportación a PDF de requerimientos
- [ ] Sistema de notificaciones push
- [ ] Modo offline con sincronización posterior
- [ ] Dashboard web de visualización
- [ ] Historial de cambios en bases de datos
- [ ] Sistema de usuarios con roles

## 👥 Contacto

**Desarrollador**: Sistema interno S&A  
**Empresa**: Smont y Aragon  
**Soporte**: Área de TI

---

**© 2025 Smont y Aragon - Todos los derechos reservados**
