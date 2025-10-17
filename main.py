# main.py
from kivy.app import App
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.popup import Popup
from kivy.uix.label import Label
from kivy.uix.button import Button
from kivy.uix.textinput import TextInput
from kivy.uix.scrollview import ScrollView
from kivy.uix.gridlayout import GridLayout
from kivy.uix.dropdown import DropDown
from kivy.properties import ObjectProperty, StringProperty, NumericProperty
from kivy.clock import Clock
from kivy.metrics import dp
from kivy.uix.screenmanager import Screen
from kivy import platform
from datetime import datetime
import requests
import json
import logging
import threading
from functools import partial

# Configurar logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# URL del servidor
SERVER_URL = "http://34.67.103.132:5000"
# SERVER_URL = "http://127.0.0.1:5000"

# Solicitar permisos en Android
if platform == "android":
    try:
        from android.permissions import request_permissions, Permission
        request_permissions([Permission.INTERNET])
    except ImportError:
        pass

class MaterialItem(BoxLayout):
    """Widget para mostrar un material en la lista de requerimientos."""
    producto = StringProperty("")
    unidad = StringProperty("")
    cantidad = NumericProperty(0.0)

    def __init__(self, producto="", unidad="", cantidad=0.0, **kwargs):
        super(MaterialItem, self).__init__(**kwargs)
        self.producto = producto
        self.unidad = unidad
        self.cantidad = cantidad

class FormularioScreen(Screen):
    """Pantalla principal del formulario de requerimientos."""
    fecha_input = ObjectProperty(None)
    solicitante_input = ObjectProperty(None)
    orden_trabajo_input = ObjectProperty(None)
    cliente_input = ObjectProperty(None)
    materiales_container = ObjectProperty(None)

    def __init__(self, **kwargs):
        super(FormularioScreen, self).__init__(**kwargs)
        self.materiales = []
        self.clientes = []
        self.materiales_lista = []
        # Variables para optimizar sugerencias
        self.sugerencias_evento = None  # Para materiales (ScrollView)
        # Variables para optimizar sugerencias de clientes (DropDown)
        self.sugerencias_clientes_evento = None
        self.dropdown_clientes = None
        Clock.schedule_once(self.on_start)

    def on_start(self, *args):
        """Inicializa la pantalla con la fecha actual."""
        # Establecer fecha actual (formato YYYY-MM-DD para mejor ordenamiento)
        fecha_actual = datetime.now().strftime("%Y-%m-%d")
        self.fecha_input.text = fecha_actual

        # Configurar eventos para conversión a mayúsculas
        self.solicitante_input.bind(on_text_validate=self.convertir_solicitante_capitalizado)
        self.solicitante_input.bind(focus=self.on_solicitante_focus)
        self.orden_trabajo_input.bind(on_text_validate=self.convertir_ot_mayusculas)
        self.orden_trabajo_input.bind(focus=self.on_ot_focus)
        self.cliente_input.bind(on_text_validate=self.convertir_cliente_mayusculas)
        self.cliente_input.bind(focus=self.on_cliente_focus)
        
        # Configurar eventos para sugerencias de clientes con debounce
        self.cliente_input.bind(text=self.on_cliente_text_change_debounce)
        self.cliente_input.bind(focus=self.on_cliente_focus_optimizado)
        self.cliente_input.bind(on_touch_down=self.on_cliente_touch_down)

        # Cargar lista de materiales y clientes
        self.cargar_materiales()
        self.cargar_clientes()

    def convertir_solicitante_capitalizado(self, instance):
        """Convierte el texto de Solicitante a formato capitalizado cuando se presiona Enter."""
        if instance.text:
            instance.text = instance.text.title()

    def on_solicitante_focus(self, instance, value):
        """Convierte el texto de Solicitante a formato capitalizado cuando pierde el foco."""
        if not value and instance.text:  # value es False cuando pierde el foco
            instance.text = instance.text.title()

    def convertir_ot_mayusculas(self, instance):
        """Convierte el texto de Orden de Trabajo a mayúsculas cuando se presiona Enter."""
        if instance.text:
            instance.text = instance.text.upper()

    def on_ot_focus(self, instance, value):
        """Convierte el texto de Orden de Trabajo a mayúsculas cuando pierde el foco."""
        if not value and instance.text:  # value es False cuando pierde el foco
            instance.text = instance.text.upper()

    def convertir_cliente_mayusculas(self, instance):
        """Convierte el texto de Cliente a mayúsculas cuando se presiona Enter."""
        if instance.text:
            instance.text = instance.text.upper()

    def on_cliente_focus(self, instance, value):
        """Convierte el texto de Cliente a mayúsculas cuando pierde el foco."""
        if not value and instance.text:  # value es False cuando pierde el foco
            instance.text = instance.text.upper()

    def on_cliente_focus_optimizado(self, instance, value):
        """Maneja el foco optimizado del campo cliente."""
        if value:
            # Cuando obtiene el foco, mostrar todos los clientes
            self.mostrar_todos_los_clientes()
        elif self.dropdown_clientes:
            # Cerrar dropdown cuando pierde el foco
            self.dropdown_clientes.dismiss()

    def on_cliente_touch_down(self, instance, touch):
        """Maneja el toque en el campo cliente para mostrar lista inmediatamente."""
        if instance.collide_point(*touch.pos):
            # Mostrar todos los clientes cuando se hace clic en el campo
            Clock.schedule_once(lambda dt: self.mostrar_todos_los_clientes(), 0.1)
        return False  # Permitir que el evento continúe

    def mostrar_todos_los_clientes(self):
        """Muestra todos los clientes disponibles en el dropdown."""
        # Cerrar dropdown anterior si existe
        if self.dropdown_clientes:
            self.dropdown_clientes.dismiss()
            self.dropdown_clientes = None
        
        if not self.clientes:
            return
        
        # Crear nuevo dropdown
        self.dropdown_clientes = DropDown(
            max_height=dp(180),  # Altura optimizada para clientes
            bar_width=dp(2),
            scroll_type=['bars']
        )
        
        # Agregar todos los clientes (máximo 6)
        for cliente in self.clientes[:6]:
            btn = Button(
                text=cliente,
                size_hint_y=None,
                height=dp(42),
                text_size=(None, None),
                halign='left',
                valign='middle',
                background_color=(0.9, 0.95, 1.0, 1),  # Color azul claro para diferenciar
                color=(0, 0, 0, 1)
            )
            btn.cliente_data = cliente
            btn.bind(on_release=lambda btn: self.seleccionar_cliente_optimizado(btn.cliente_data))
            self.dropdown_clientes.add_widget(btn)

        # Abrir dropdown
        try:
            self.dropdown_clientes.open(self.cliente_input)
        except Exception as e:
            logger.warning(f"Error al abrir dropdown de todos los clientes: {e}")

    def on_cliente_text_change_debounce(self, instance, value):
        """Maneja el cambio de texto en el campo cliente con debounce."""
        # Solo mostrar sugerencias filtradas si hay texto escrito
        if value and len(value.strip()) > 0:
            # Cancelar evento anterior si existe
            if self.sugerencias_clientes_evento:
                self.sugerencias_clientes_evento.cancel()
            
            # Programar nueva actualización con delay
            self.sugerencias_clientes_evento = Clock.schedule_once(
                lambda dt: self.mostrar_sugerencias_cliente_optimizado(value), 
                0.2  # 200ms de delay para clientes (más rápido que materiales)
            )
        elif not value or len(value.strip()) == 0:
            # Si el campo está vacío, mostrar todos los clientes
            self.mostrar_todos_los_clientes()

    def mostrar_sugerencias_cliente_optimizado(self, texto):
        """Muestra sugerencias de clientes usando DropDown optimizado."""
        # Cerrar dropdown anterior si existe
        if self.dropdown_clientes:
            self.dropdown_clientes.dismiss()
            self.dropdown_clientes = None

        if not texto or len(texto) < 1:
            return
        
        texto_upper = texto.upper()
        sugerencias = [c for c in self.clientes if texto_upper in c.upper()]
        
        if not sugerencias:
            return

        # Crear nuevo dropdown
        self.dropdown_clientes = DropDown(
            max_height=dp(180),  # Altura optimizada para clientes
            bar_width=dp(2),
            scroll_type=['bars']
        )
        
        # Agregar sugerencias de clientes
        for cliente in sugerencias[:6]:  # Máximo 6 sugerencias
            btn = Button(
                text=cliente,
                size_hint_y=None,
                height=dp(42),
                text_size=(None, None),
                halign='left',
                valign='middle',
                background_color=(0.9, 0.95, 1.0, 1),  # Color azul claro para diferenciar
                color=(0, 0, 0, 1)
            )
            btn.cliente_data = cliente
            btn.bind(on_release=lambda btn: self.seleccionar_cliente_optimizado(btn.cliente_data))
            self.dropdown_clientes.add_widget(btn)

        # Abrir dropdown
        try:
            self.dropdown_clientes.open(self.cliente_input)
        except Exception as e:
            logger.warning(f"Error al abrir dropdown de clientes: {e}")

    def seleccionar_cliente_optimizado(self, cliente):
        """Selecciona un cliente de la lista de sugerencias optimizada."""
        self.cliente_input.text = cliente.upper()
        if self.dropdown_clientes:
            self.dropdown_clientes.dismiss()
            self.dropdown_clientes = None

    def cargar_materiales(self):
        """Carga la lista de materiales desde el servidor."""
        threading.Thread(target=self._cargar_materiales_thread).start()

    def _cargar_materiales_thread(self):
        """Función para cargar materiales en un hilo separado."""
        try:
            response = requests.get(f"{SERVER_URL}/api/logistica/materiales", timeout=10)
            response.raise_for_status()
            self.materiales = response.json()
            logger.info(f"Materiales cargados: {len(self.materiales)}")
        except requests.exceptions.RequestException as e:
            logger.error(f"Error al cargar materiales: {e}")
            Clock.schedule_once(lambda dt: self.mostrar_error(
                "Error de conexión",
                "No se pudo conectar al servidor para cargar la lista de materiales. "
                "Puede continuar trabajando, pero la función de autocompletado no estará disponible."
            ))

    def cargar_clientes(self):
        """Carga la lista de clientes desde el servidor."""
        threading.Thread(target=self._cargar_clientes_thread).start()

    def _cargar_clientes_thread(self):
        """Función para cargar clientes en un hilo separado."""
        try:
            response = requests.get(f"{SERVER_URL}/api/logistica/clientes", timeout=10)
            response.raise_for_status()
            self.clientes = response.json()
            logger.info(f"Clientes cargados: {len(self.clientes)}")
        except requests.exceptions.RequestException as e:
            logger.error(f"Error al cargar clientes: {e}")
            Clock.schedule_once(lambda dt: self.mostrar_error(
                "Error de conexión",
                "No se pudo conectar al servidor para cargar la lista de clientes. "
                "Puede continuar trabajando, pero las sugerencias de clientes no estarán disponibles."
            ))

    def mostrar_popup_agregar_material(self):
        """Muestra el popup para agregar un nuevo material."""
        content = BoxLayout(orientation='vertical', spacing=10, padding=20)

        # Título
        title_label = Label(
            text="Agregar Material",
            font_size=dp(24),
            size_hint_y=None,
            height=dp(40)
        )
        content.add_widget(title_label)

        # Campos del formulario
        form_layout = GridLayout(cols=2, spacing=10, size_hint_y=None, height=dp(180))

        # Producto
        form_layout.add_widget(Label(text="Producto:", font_size=dp(18)))
        producto_input = TextInput(
            multiline=False,
            font_size=dp(18),
            hint_text="Comience a tipear..."
        )
        form_layout.add_widget(producto_input)

        # Unidad
        form_layout.add_widget(Label(text="Unidad:", font_size=dp(18)))
        unidad_input = TextInput(
            multiline=False,
            font_size=dp(18),
            hint_text="Unidad"
        )
        form_layout.add_widget(unidad_input)

        # Cantidad
        form_layout.add_widget(Label(text="Cantidad:", font_size=dp(18)))
        cantidad_input = TextInput(
            multiline=False,
            font_size=dp(18),
            input_filter='float',
            hint_text="Ingrese número"
        )
        form_layout.add_widget(cantidad_input)

        content.add_widget(form_layout)

        # Sugerencias de productos (ScrollView optimizado para móviles)
        sugerencias_scroll = ScrollView(
            size_hint=(1, None), 
            height=dp(150),  # Altura reducida para móviles
            do_scroll_x=False,
            bar_width=dp(4),
            scroll_type=['bars', 'content']
        )
        self.sugerencias_layout = GridLayout(
            cols=1, 
            spacing=dp(2), 
            size_hint_y=None,
            padding=[dp(5), 0]
        )
        self.sugerencias_layout.bind(minimum_height=self.sugerencias_layout.setter('height'))
        sugerencias_scroll.add_widget(self.sugerencias_layout)
        content.add_widget(sugerencias_scroll)

        # Botones
        buttons_layout = BoxLayout(size_hint_y=None, height=dp(50), spacing=10)

        cancelar_btn = Button(
            text="Cancelar",
            size_hint_x=0.5
        )

        agregar_btn = Button(
            text="Agregar",
            size_hint_x=0.5,
            background_color=(0, 0.7, 0, 1)
        )

        buttons_layout.add_widget(cancelar_btn)
        buttons_layout.add_widget(agregar_btn)
        content.add_widget(buttons_layout)

        # Crear y mostrar el popup (tamaño optimizado para ScrollView)
        popup = Popup(
            title="Agregar Material",
            content=content,
            size_hint=(0.9, 0.75),  # Tamaño optimizado para incluir sugerencias
            pos_hint={'center_x': 0.5, 'center_y': 0.6},  # Posición más alta para evitar teclado
            auto_dismiss=False
        )

        # Configurar eventos
        cancelar_btn.bind(on_release=popup.dismiss)
        agregar_btn.bind(on_release=lambda x: self.agregar_material(
            producto_input.text,
            unidad_input.text,
            cantidad_input.text,
            popup
        ))

        # Configurar autocompletado con ScrollView optimizado
        producto_input.bind(text=lambda instance, value: self.actualizar_sugerencias_scrollview_debounce(value, self.sugerencias_layout, producto_input, unidad_input))

        popup.open()

    def actualizar_sugerencias_scrollview_debounce(self, texto, sugerencias_layout, producto_input, unidad_input):
        """Actualiza sugerencias ScrollView con debounce para evitar lag."""
        # Cancelar evento anterior si existe
        if self.sugerencias_evento:
            self.sugerencias_evento.cancel()
        
        # Programar nueva actualización con delay
        self.sugerencias_evento = Clock.schedule_once(
            lambda dt: self.actualizar_sugerencias_scrollview(texto, sugerencias_layout, producto_input, unidad_input), 
            0.25  # 250ms de delay optimizado
        )

    def actualizar_sugerencias_scrollview(self, texto, sugerencias_layout, producto_input, unidad_input):
        """Actualiza la lista de sugerencias en ScrollView (versión optimizada)."""
        # Limpiar sugerencias anteriores
        sugerencias_layout.clear_widgets()

        if not texto or len(texto) < 2:
            return

        texto = texto.upper()
        sugerencias = [m for m in self.materiales if texto in m['material'].upper()]

        # Limitar a 6 sugerencias para mejor rendimiento en móvil
        for material in sugerencias[:6]:
            btn = Button(
                text=material['material'],
                size_hint_y=None,
                height=dp(44),  # Altura optimizada para móvil
                text_size=(None, None),
                halign='left',
                valign='middle',
                background_color=(0.95, 0.95, 0.95, 1),
                color=(0, 0, 0, 1),
                border=(1, 1, 1, 1)
            )
            # Agregar referencia directa para evitar closure issues
            btn.material_data = material
            btn.bind(on_release=lambda btn: self.seleccionar_material_scrollview(
                btn.material_data, producto_input, unidad_input, sugerencias_layout
            ))
            sugerencias_layout.add_widget(btn)

    def seleccionar_material_scrollview(self, material, producto_input, unidad_input, sugerencias_layout):
        """Selecciona un material desde ScrollView y limpia las sugerencias."""
        producto_input.text = material['material']
        unidad_input.text = material['unidad']
        # Limpiar sugerencias después de seleccionar
        sugerencias_layout.clear_widgets()


    def seleccionar_material(self, material, producto_input, unidad_input):
        """Selecciona un material de la lista de sugerencias."""
        producto_input.text = material['material']
        unidad_input.text = material['unidad']

    def agregar_material(self, producto, unidad, cantidad, popup):
        """Agrega un material a la lista de requerimientos."""
        if not producto:
            self.mostrar_error("Error", "Debe ingresar un producto")
            return

        if not unidad:
            self.mostrar_error("Error", "Debe ingresar una unidad")
            return

        try:
            cantidad_float = float(cantidad) if cantidad else 0.0
            if cantidad_float <= 0:
                self.mostrar_error("Error", "La cantidad debe ser mayor a cero")
                return

            # Formatear cantidad a 2 decimales
            cantidad_formateada = "{:.2f}".format(cantidad_float)

            # Agregar a la lista
            self.materiales_lista.append({
                'producto': producto,
                'unidad': unidad,
                'cantidad': cantidad_formateada
            })

            # Actualizar la UI
            self.actualizar_lista_materiales()

            # Cerrar popup
            popup.dismiss()

        except ValueError:
            self.mostrar_error("Error", "La cantidad debe ser un número válido")

    def actualizar_lista_materiales(self):
        """Actualiza la lista de materiales en la UI."""
        if self.materiales_container:
            self.materiales_container.clear_widgets()

            for i, material in enumerate(self.materiales_lista):
                item = MaterialItem(
                    producto=material['producto'],
                    unidad=material['unidad'],
                    cantidad=float(material['cantidad'])
                )

                # Agregar botones de editar y eliminar
                editar_btn = Button(
                    text="Editar",
                    size_hint=(None, None),
                    size=(dp(80), dp(40))
                )
                editar_btn.bind(on_release=partial(self.editar_material, i))

                eliminar_btn = Button(
                    text="Eliminar",
                    size_hint=(None, None),
                    size=(dp(80), dp(40)),
                    background_color=(0.8, 0, 0, 1)
                )
                eliminar_btn.bind(on_release=partial(self.eliminar_material, i))

                item.add_widget(editar_btn)
                item.add_widget(eliminar_btn)

                self.materiales_container.add_widget(item)

    def editar_material(self, indice, *args):
        """Muestra el popup para editar un material existente."""
        material = self.materiales_lista[indice]

        content = BoxLayout(orientation='vertical', spacing=10, padding=20)

        # Título
        title_label = Label(
            text="Editar Material",
            font_size=dp(24),
            size_hint_y=None,
            height=dp(40)
        )
        content.add_widget(title_label)

        # Campos del formulario
        form_layout = GridLayout(cols=2, spacing=10, size_hint_y=None, height=dp(180))

        # Producto
        form_layout.add_widget(Label(text="Producto:", font_size=dp(18)))
        producto_input = TextInput(
            multiline=False,
            font_size=dp(18),
            text=material['producto']
        )
        form_layout.add_widget(producto_input)

        # Unidad
        form_layout.add_widget(Label(text="Unidad:", font_size=dp(18)))
        unidad_input = TextInput(
            multiline=False,
            font_size=dp(18),
            text=material['unidad']
        )
        form_layout.add_widget(unidad_input)

        # Cantidad
        form_layout.add_widget(Label(text="Cantidad:", font_size=dp(18)))
        cantidad_input = TextInput(
            multiline=False,
            font_size=dp(18),
            input_filter='float',
            text=material['cantidad']
        )
        form_layout.add_widget(cantidad_input)

        content.add_widget(form_layout)

        # Botones
        buttons_layout = BoxLayout(size_hint_y=None, height=dp(50), spacing=10)

        cancelar_btn = Button(
            text="Cancelar",
            size_hint_x=0.5
        )

        guardar_btn = Button(
            text="Guardar",
            size_hint_x=0.5,
            background_color=(0, 0.7, 0, 1)
        )

        buttons_layout.add_widget(cancelar_btn)
        buttons_layout.add_widget(guardar_btn)
        content.add_widget(buttons_layout)

        # Crear y mostrar el popup
        popup = Popup(
            title="Editar Material",
            content=content,
            size_hint=(0.9, 0.8),
            auto_dismiss=False
        )

        # Configurar eventos
        cancelar_btn.bind(on_release=popup.dismiss)
        guardar_btn.bind(on_release=lambda x: self.guardar_edicion_material(
            indice,
            producto_input.text,
            unidad_input.text,
            cantidad_input.text,
            popup
        ))

        popup.open()

    def guardar_edicion_material(self, indice, producto, unidad, cantidad, popup):
        """Guarda los cambios de un material editado."""
        if not producto:
            self.mostrar_error("Error", "Debe ingresar un producto")
            return

        if not unidad:
            self.mostrar_error("Error", "Debe ingresar una unidad")
            return

        try:
            cantidad_float = float(cantidad) if cantidad else 0.0
            if cantidad_float <= 0:
                self.mostrar_error("Error", "La cantidad debe ser mayor a cero")
                return

            # Formatear cantidad a 2 decimales
            cantidad_formateada = "{:.2f}".format(cantidad_float)

            # Actualizar en la lista
            self.materiales_lista[indice] = {
                'producto': producto,
                'unidad': unidad,
                'cantidad': cantidad_formateada
            }

            # Actualizar la UI
            self.actualizar_lista_materiales()

            # Cerrar popup
            popup.dismiss()

        except ValueError:
            self.mostrar_error("Error", "La cantidad debe ser un número válido")

    def eliminar_material(self, indice, *args):
        """Elimina un material de la lista."""
        content = BoxLayout(orientation='vertical', spacing=10, padding=20)

        # Mensaje
        msg_label = Label(
            text="¿Está seguro que desea eliminar este material?",
            font_size=dp(18)
        )
        content.add_widget(msg_label)

        # Botones
        buttons_layout = BoxLayout(size_hint_y=None, height=dp(50), spacing=10)

        cancelar_btn = Button(
            text="Cancelar",
            size_hint_x=0.5
        )

        confirmar_btn = Button(
            text="Eliminar",
            size_hint_x=0.5,
            background_color=(0.8, 0, 0, 1)
        )

        buttons_layout.add_widget(cancelar_btn)
        buttons_layout.add_widget(confirmar_btn)
        content.add_widget(buttons_layout)

        # Crear y mostrar el popup
        popup = Popup(
            title="Confirmar eliminación",
            content=content,
            size_hint=(0.8, 0.4),
            auto_dismiss=False
        )

        # Configurar eventos
        cancelar_btn.bind(on_release=popup.dismiss)
        confirmar_btn.bind(on_release=lambda x: self.confirmar_eliminar_material(indice, popup))

        popup.open()

    def confirmar_eliminar_material(self, indice, popup):
        """Confirma la eliminación de un material."""
        # Eliminar de la lista
        del self.materiales_lista[indice]

        # Actualizar la UI
        self.actualizar_lista_materiales()

        # Cerrar popup
        popup.dismiss()

    def enviar_requerimientos(self):
        """Envía los requerimientos al servidor."""
        # Validar campos obligatorios
        if not self.fecha_input.text:
            self.mostrar_error("Error", "Debe ingresar la fecha")
            return

        if not self.solicitante_input.text:
            self.mostrar_error("Error", "Debe ingresar el nombre del solicitante")
            return

        if not self.orden_trabajo_input.text:
            self.mostrar_error("Error", "Debe ingresar la orden de trabajo")
            return

        if not self.cliente_input.text:
            self.mostrar_error("Error", "Debe ingresar el nombre del cliente")
            return

        if not self.materiales_lista:
            self.mostrar_error("Error", "Debe agregar al menos un material")
            return

        # Preparar datos
        datos = {
            'fecha': self.fecha_input.text,
            'solicitante': self.solicitante_input.text,
            'orden_trabajo': self.orden_trabajo_input.text,
            'cliente': self.cliente_input.text,
            'productos': self.materiales_lista
        }

        # Mostrar popup de carga
        content = BoxLayout(orientation='vertical', spacing=10, padding=20)
        msg_label = Label(
            text="Enviando requerimientos al servidor...",
            font_size=dp(18)
        )
        content.add_widget(msg_label)

        popup = Popup(
            title="Enviando datos",
            content=content,
            size_hint=(0.8, 0.4),
            auto_dismiss=False
        )
        popup.open()

        # Enviar datos en un hilo separado
        threading.Thread(target=self._enviar_requerimientos_thread, args=(datos, popup)).start()

    def _enviar_requerimientos_thread(self, datos, popup):
        """Función para enviar requerimientos en un hilo separado."""
        try:
            response = requests.post(
                f"{SERVER_URL}/api/logistica/enviar-requerimientos",
                json=datos,
                timeout=30
            )
            response.raise_for_status()

            # Cerrar popup de carga
            Clock.schedule_once(lambda dt: popup.dismiss())

            # Mostrar mensaje de éxito
            Clock.schedule_once(lambda dt: self.mostrar_exito(
                "Requerimientos enviados",
                "Envío exitoso."
            ))

            # Limpiar formulario
            Clock.schedule_once(lambda dt: self.limpiar_formulario())

        except requests.exceptions.RequestException as e:
            logger.error(f"Error al enviar requerimientos: {e}")

            # Cerrar popup de carga
            Clock.schedule_once(lambda dt: popup.dismiss())

            # Mostrar mensaje de error
            Clock.schedule_once(lambda dt: self.mostrar_error(
                "Error de conexión",
                "No se pudo conectar al servidor para enviar los requerimientos. "
                "Por favor, verifique su conexión a internet e intente nuevamente."
            ))

    def limpiar_formulario(self):
        """Limpia el formulario después de enviar los requerimientos."""
        # Cerrar dropdowns abiertos
        self.cerrar_dropdowns()
        
        # Mantener solo la fecha actual (formato YYYY-MM-DD para mejor ordenamiento)
        fecha_actual = datetime.now().strftime("%Y-%m-%d")
        self.fecha_input.text = fecha_actual

        # Limpiar otros campos
        self.solicitante_input.text = ""
        self.orden_trabajo_input.text = ""
        self.cliente_input.text = ""

        # Limpiar lista de materiales
        self.materiales_lista = []
        self.actualizar_lista_materiales()

    def cerrar_dropdowns(self):
        """Cierra todos los dropdowns abiertos para liberar memoria."""
        # Solo dropdown de clientes (materiales usa ScrollView)
        if self.dropdown_clientes:
            self.dropdown_clientes.dismiss()
            self.dropdown_clientes = None
        # Cancelar eventos pendientes
        if self.sugerencias_evento:
            self.sugerencias_evento.cancel()
            self.sugerencias_evento = None
        if self.sugerencias_clientes_evento:
            self.sugerencias_clientes_evento.cancel()
            self.sugerencias_clientes_evento = None

    def mostrar_error(self, titulo, mensaje):
        """Muestra un popup de error."""
        content = BoxLayout(orientation='vertical', spacing=10, padding=20)

        msg_label = Label(
            text=mensaje,
            font_size=dp(18)
        )
        content.add_widget(msg_label)

        btn = Button(
            text="Aceptar",
            size_hint=(None, None),
            size=(dp(150), dp(50)),
            pos_hint={'center_x': 0.5}
        )
        content.add_widget(btn)

        popup = Popup(
            title=titulo,
            content=content,
            size_hint=(0.8, 0.4),
            auto_dismiss=False
        )

        btn.bind(on_release=popup.dismiss)
        popup.open()

    def mostrar_exito(self, titulo, mensaje):
        """Muestra un popup de éxito."""
        content = BoxLayout(orientation='vertical', spacing=10, padding=20)

        msg_label = Label(
            text=mensaje,
            font_size=dp(18)
        )
        content.add_widget(msg_label)

        btn = Button(
            text="Aceptar",
            size_hint=(None, None),
            size=(dp(150), dp(50)),
            pos_hint={'center_x': 0.5},
            background_color=(0, 0.7, 0, 1)
        )
        content.add_widget(btn)

        popup = Popup(
            title=titulo,
            content=content,
            size_hint=(0.8, 0.4),
            auto_dismiss=False
        )

        btn.bind(on_release=popup.dismiss)
        popup.open()

class FormularioApp(App):
    def build(self):
        return FormularioScreen()

if __name__ == '__main__':
    FormularioApp().run()
