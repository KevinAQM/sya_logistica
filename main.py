# main.py
from kivy.app import App
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.popup import Popup
from kivy.uix.label import Label
from kivy.uix.button import Button
from kivy.uix.textinput import TextInput
from kivy.uix.scrollview import ScrollView
from kivy.uix.gridlayout import GridLayout
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
        self.materiales_lista = []
        Clock.schedule_once(self.on_start)

    def on_start(self, *args):
        """Inicializa la pantalla con la fecha actual."""
        # Establecer fecha actual
        fecha_actual = datetime.now().strftime("%Y/%m/%d")
        self.fecha_input.text = fecha_actual

        # Cargar lista de materiales
        self.cargar_materiales()

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

        # Sugerencias de productos
        sugerencias_scroll = ScrollView(size_hint=(1, None), height=dp(200))
        self.sugerencias_layout = GridLayout(cols=1, spacing=2, size_hint_y=None)
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

        # Crear y mostrar el popup
        popup = Popup(
            title="Agregar Material",
            content=content,
            size_hint=(0.9, 0.8),
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

        # Configurar autocompletado
        producto_input.bind(text=lambda instance, value: self.actualizar_sugerencias(value, self.sugerencias_layout, producto_input, unidad_input))

        popup.open()

    def actualizar_sugerencias(self, texto, sugerencias_layout, producto_input, unidad_input):
        """Actualiza la lista de sugerencias basadas en el texto ingresado."""
        sugerencias_layout.clear_widgets()

        if not texto or len(texto) < 2:
            return

        texto = texto.upper()
        sugerencias = [m for m in self.materiales if texto in m['material'].upper()]

        for material in sugerencias[:10]:  # Limitar a 10 sugerencias
            btn = Button(
                text=material['material'],
                size_hint_y=None,
                height=dp(40),
                halign='left',
                valign='middle'
            )
            btn.bind(on_release=lambda btn, m=material: self.seleccionar_material(
                m, producto_input, unidad_input
            ))
            sugerencias_layout.add_widget(btn)

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
        # Mantener solo la fecha actual
        fecha_actual = datetime.now().strftime("%Y/%m/%d")
        self.fecha_input.text = fecha_actual

        # Limpiar otros campos
        self.solicitante_input.text = ""
        self.orden_trabajo_input.text = ""
        self.cliente_input.text = ""

        # Limpiar lista de materiales
        self.materiales_lista = []
        self.actualizar_lista_materiales()

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
