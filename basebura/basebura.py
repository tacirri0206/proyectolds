import tkinter as tk
from tkinter import messagebox, ttk
import sqlite3
import webbrowser
import os
import re

class BaseburaApp:
    def __init__(self, root): 
        self.root = root
        self.root.title("Basebura - Sistema de Recolección")
        self.root.geometry("600x400")
        

        # Conexión a base de datos
        self.conn = sqlite3.connect('basebura.db')
        self.crear_tablas()

        # Variable para almacenar el correo del usuario que inició sesión
        self.usuario_correo = None

        # Frame principal
        self.frame_principal = tk.Frame(root)
        self.frame_principal.pack(expand=True, fill='both')

        # Título de la aplicación
        self.titulo = tk.Label(self.frame_principal, text="Basebura", font=("Arial", 24))
        self.titulo.pack(pady=20)

        # Descripción
        self.descripcion = tk.Label(
            self.frame_principal, 
            text="Recolección de basura en tianguis de manera eficiente y práctica", 
            font=("Arial", 12), 
            wraplength=500
        )
        self.descripcion.pack(pady=10)

        # Botón para comenzar
        self.btn_comenzar = tk.Button(
            self.frame_principal, 
            text="Comenzar", 
            command=self.abrir_login
        )
        self.btn_comenzar.pack(pady=20)

    def crear_tablas(self):
        cursor = self.conn.cursor()
        # Tabla de usuarios
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS usuarios (
                id INTEGER PRIMARY KEY,
                correo TEXT UNIQUE,
                contrasena TEXT,
                tipo_cuenta TEXT
            )
        ''')
        # Tabla de recolecciones
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS recolecciones (
                id INTEGER PRIMARY KEY,
                correo TEXT,
                tianguis TEXT,
                cantidad_basura REAL,
                tiempo_recoleccion REAL,
                Fecha Text

            )
        ''')
        cursor.execute('''
        CREATE TABLE IF NOT EXISTS solicitudes_servicio (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            correo TEXT NOT NULL,
            tianguis TEXT NOT NULL,
            FOREIGN KEY (correo) REFERENCES usuarios (correo)
        )
    ''')
        self.conn.commit()

    def abrir_login(self):
        # Ocultar frame principal
        self.frame_principal.pack_forget()

        # Crear frame de login
        self.frame_login = tk.Frame(self.root)
        self.frame_login.pack(expand=True, fill='both')

        # Título de login
        tk.Label(self.frame_login, text="Iniciar Sesión", font=("Arial", 18)).pack(pady=20)

        # Email
        tk.Label(self.frame_login, text="Correo electrónico:").pack()
        self.email_entry = tk.Entry(self.frame_login, width=30)
        self.email_entry.pack(pady=5)

        # Contraseña
        tk.Label(self.frame_login, text="Contraseña:").pack()
        self.pass_entry = tk.Entry(self.frame_login, show="*", width=30)
        self.pass_entry.pack(pady=5)

        # Botones de login
        frame_botones = tk.Frame(self.frame_login)
        frame_botones.pack(pady=10)

        btn_admin = tk.Button(frame_botones, text="Administrador", command=lambda: self.iniciar_sesion('admin'))
        btn_admin.pack(side=tk.LEFT, padx=5)

        btn_representante = tk.Button(frame_botones, text="Representante", command=lambda: self.iniciar_sesion('representante'))
        btn_representante.pack(side=tk.LEFT, padx=5)

        btn_trabajador = tk.Button(frame_botones, text="Trabajador", command=lambda: self.iniciar_sesion('trabajador'))
        btn_trabajador.pack(side=tk.LEFT, padx=5)

        # Botón de cancelar
        btn_cancelar = tk.Button(self.frame_login, text="Cancelar", command=self.volver_inicio)
        btn_cancelar.pack(pady=10)

    def iniciar_sesion(self, tipo_cuenta):
        correo = self.email_entry.get()
        contrasena = self.pass_entry.get()

        cursor = self.conn.cursor()
        cursor.execute(
            "SELECT * FROM usuarios WHERE correo=? AND contrasena=? AND tipo_cuenta=?", 
            (correo, contrasena, tipo_cuenta)
        )
        usuario = cursor.fetchone()

        if usuario:
            # Guardar el correo del usuario que inició sesión
            self.usuario_correo = correo

            # Limpiar frames anteriores
            for widget in self.root.winfo_children():
                widget.destroy()

            # Abrir menú según tipo de cuenta
            if tipo_cuenta == 'admin':
                self.menu_admin()
            elif tipo_cuenta == 'representante':
                self.menu_representante()
            elif tipo_cuenta == 'trabajador':
                self.menu_trabajador()
        else:
            messagebox.showerror("Error", "Credenciales incorrectas")

    def volver_inicio(self):
        # Limpiar frames anteriores
        for widget in self.root.winfo_children():
            widget.destroy()
        
        # Recrear frame principal
        self.__init__(self.root)

    def menu_admin(self):
        # Menú de administrador
        frame_admin = tk.Frame(self.root)
        frame_admin.pack(expand=True, fill='both')

        tk.Label(frame_admin, text="Menú de Administrador", font=("Arial", 18)).pack(pady=20)

        opciones = [
            ("Crear Cuentas", self.crear_cuentas),
            ("Editar Cuentas", self.editar_cuentas),
            ("Eliminar Cuentas", self.eliminar_cuentas),
            ("Consultar Servicios", self.consultar_solicitudes),
            ("Contactar Administradores", self.contactar_administradores),
            ("Cerrar Sesión", self.volver_inicio)
        ]

        for texto, comando in opciones:
            btn = tk.Button(frame_admin, text=texto, command=comando, width=30)
            btn.pack(pady=5)

    def crear_cuentas(self):
        # Crear cuentas de administrador
        def guardar_usuario():
            correo = correo_entry.get()
            contrasena = contrasena_entry.get()
            tipo_cuenta = tipo_cuenta_var.get()

            # Verificar si el correo ya existe en la base de datos
            cursor = self.conn.cursor()
            cursor.execute("SELECT * FROM usuarios WHERE correo=?", (correo,))
            usuario_existente = cursor.fetchone()

            if usuario_existente:
                messagebox.showerror("Error", "El correo ya está registrado.")
            else:
                try:
                    cursor.execute("INSERT INTO usuarios (correo, contrasena, tipo_cuenta) VALUES (?, ?, ?)",
                                   (correo, contrasena, tipo_cuenta))
                    self.conn.commit()
                    messagebox.showinfo("Éxito", "Cuenta creada correctamente")
                    ventana_crear.destroy()
                except sqlite3.IntegrityError:
                    messagebox.showerror("Error", "Error al crear la cuenta.")

        # Ventana para crear cuenta
        ventana_crear = tk.Toplevel(self.root)
        ventana_crear.title("Crear Cuenta")
        ventana_crear.geometry("400x300")

        tk.Label(ventana_crear, text="Correo electrónico:").pack(pady=5)
        correo_entry = tk.Entry(ventana_crear, width=30)
        correo_entry.pack(pady=5)

        tk.Label(ventana_crear, text="Contraseña:").pack(pady=5)
        contrasena_entry = tk.Entry(ventana_crear, show="*", width=30)
        contrasena_entry.pack(pady=5)

        tk.Label(ventana_crear, text="Tipo de cuenta:").pack(pady=5)
        tipo_cuenta_var = tk.StringVar(value="admin")
        tipo_cuenta_menu = tk.OptionMenu(ventana_crear, tipo_cuenta_var, "admin", "representante", "trabajador")
        tipo_cuenta_menu.pack(pady=5)

        btn_guardar = tk.Button(ventana_crear, text="Guardar", command=guardar_usuario)
        btn_guardar.pack(pady=20)

    def editar_cuentas(self):
        # Mostrar tabla con cuentas
        cursor = self.conn.cursor()
        cursor.execute("SELECT * FROM usuarios")
        cuentas = cursor.fetchall()

        def editar_seleccionada():
            seleccion = tabla.curselection()
            if seleccion:
                usuario = cuentas[seleccion[0]]
                correo = usuario[1]
                contrasena = usuario[2]
                tipo_cuenta = usuario[3]

                def guardar_ediciones():
                    nuevo_correo = correo_entry.get()
                    nueva_contrasena = contrasena_entry.get()
                    nuevo_tipo = tipo_cuenta_var.get()

                    cursor.execute("UPDATE usuarios SET correo=?, contrasena=?, tipo_cuenta=? WHERE correo=?",
                                   (nuevo_correo, nueva_contrasena, nuevo_tipo, correo))
                    self.conn.commit()
                    messagebox.showinfo("Éxito", "Cuenta editada exitosamente")
                    ventana_editar.destroy()

                ventana_editar = tk.Toplevel(self.root)
                ventana_editar.title("Editar Cuenta")
                ventana_editar.geometry("400x300")

                tk.Label(ventana_editar, text="Nuevo correo:").pack(pady=5)
                correo_entry = tk.Entry(ventana_editar, width=30)
                correo_entry.insert(0, correo)
                correo_entry.pack(pady=5)

                tk.Label(ventana_editar, text="Nueva contraseña:").pack(pady=5)
                contrasena_entry = tk.Entry(ventana_editar, show="*", width=30)
                contrasena_entry.insert(0, contrasena)
                contrasena_entry.pack(pady=5)

                tk.Label(ventana_editar, text="Nuevo tipo de cuenta:").pack(pady=5)
                tipo_cuenta_var = tk.StringVar(value=tipo_cuenta)
                tipo_cuenta_menu = tk.OptionMenu(ventana_editar, tipo_cuenta_var, "admin", "representante", "trabajador")
                tipo_cuenta_menu.pack(pady=5)

                btn_guardar = tk.Button(ventana_editar, text="Guardar cambios", command=guardar_ediciones)
                btn_guardar.pack(pady=20)

        # Ventana para editar cuentas
        ventana_editar_cuentas = tk.Toplevel(self.root)
        ventana_editar_cuentas.title("Editar Cuentas")
        ventana_editar_cuentas.geometry("500x400")

        tk.Label(ventana_editar_cuentas, text="Selecciona la cuenta a editar:").pack(pady=10)

        # Tabla de cuentas
        tabla = tk.Listbox(ventana_editar_cuentas, height=10, width=50)
        for cuenta in cuentas:
            tabla.insert(tk.END, f"{cuenta[1]} - {cuenta[3]}")  # Mostrar correo y tipo de cuenta
        tabla.pack(pady=10)

        btn_editar = tk.Button(ventana_editar_cuentas, text="Editar", command=editar_seleccionada)
        btn_editar.pack(pady=10)

    def eliminar_cuentas(self):
        # Mostrar tabla con cuentas
        cursor = self.conn.cursor()
        cursor.execute("SELECT * FROM usuarios")
        cuentas = cursor.fetchall()

        def eliminar_seleccionada():
            seleccion = tabla.curselection()
            if seleccion:
                usuario = cuentas[seleccion[0]]
                correo = usuario[1]

                confirmacion = messagebox.askyesno("Confirmación", f"¿Seguro que deseas eliminar la cuenta {correo}?")
                if confirmacion:
                    cursor.execute("DELETE FROM usuarios WHERE correo=?", (correo,))
                    self.conn.commit()
                    messagebox.showinfo("Éxito", "Cuenta eliminada exitosamente")
                    ventana_eliminar.destroy()

        # Ventana para eliminar cuentas
        ventana_eliminar = tk.Toplevel(self.root)
        ventana_eliminar.title("Eliminar Cuenta")
        ventana_eliminar.geometry("500x400")

        tk.Label(ventana_eliminar, text="Selecciona la cuenta a eliminar:").pack(pady=10)

        # Tabla de cuentas
        tabla = tk.Listbox(ventana_eliminar, height=10, width=50)
        for cuenta in cuentas:
            tabla.insert(tk.END, f"{cuenta[1]} - {cuenta[3]}")  # Mostrar correo y tipo de cuenta
        tabla.pack(pady=10)

        btn_eliminar = tk.Button(ventana_eliminar, text="Eliminar", command=eliminar_seleccionada)
        btn_eliminar.pack(pady=10)

    def contactar_administradores(self):
        # Crear una nueva ventana Toplevel para mostrar la información de contacto
        ventana_contacto = tk.Toplevel(self.root)
        ventana_contacto.title("Contactar Administradores")
        ventana_contacto.geometry("400x300")

        # Información de los administradores
        info_contacto = (
            "Alvaro A. Rangel\n"
            "arangela2300@Alumno.ipn.mx\n"
            "\n"
            "Cervantes Arriaga Daniel Arturo\n"
            "cervantesarriagadanielarturo@Alumno.ipn.mx\n"
            "\n"
            "Briana Galicia\n"
            "brianasg@Alumno.ipn.mx\n"
            "\n"
            "Sebastian Martinez Chavez\n"
            "smartinezc2305@Alumno.ipn.mx\n"
            "\n"
            "Carlos Lain Maldonafo Avellaneda\n"
            "cmaldonadoa2300@Alumno.ipn.mx\n"
            "\n"
            "Sebastián Sánchez Bravo\n"
            "sebastiansanchezbravi@Alumno.ipn.mx"
        )

        # Etiqueta para mostrar la información
        tk.Label(ventana_contacto, text=info_contacto, font=("Arial", 12), justify="left").pack(pady=10, padx=10)



    def menu_representante(self):
        # Menú de representante
        frame_representante = tk.Frame(self.root)
        frame_representante.pack(expand=True, fill='both')

        tk.Label(frame_representante, text="Menú de Representante", font=("Arial", 18)).pack(pady=20)

        opciones = [
            ("Solicitar Servicio", self.solicitar_servicio),
            ("Consultar Reporte", self.consultar_reporte),
            ("Comunicarse con los Administradores", self.contactar_administradores),
            ("Cerrar Sesión", self.volver_inicio)
        ]

        for texto, comando in opciones:
            btn = tk.Button(frame_representante, text=texto, command=comando, width=30)
            btn.pack(pady=5)

    def solicitar_servicio(self):
        def enviar_solicitud():
            correo = correo_entry.get()

            # Validar si el correo coincide con el del usuario que inició sesión
            if correo != self.usuario_correo:
                messagebox.showerror("Error", "El correo no coincide con el usuario actual.")
                return

            tianguis = tianguis_var.get()

            # Insertar la solicitud de servicio en la base de datos
            cursor = self.conn.cursor()
            cursor.execute(
                "INSERT INTO solicitudes_servicio (correo, tianguis) VALUES (?, ?)",
                (correo, tianguis)
            )
            self.conn.commit()
            
            messagebox.showinfo("Éxito", f"Solicitud enviada para el Tianguis: {tianguis}")
            ventana_solicitud.destroy()

        # Ventana para solicitar servicio
        ventana_solicitud = tk.Toplevel(self.root)
        ventana_solicitud.title("Solicitar Servicio")
        ventana_solicitud.geometry("400x300")

        tk.Label(ventana_solicitud, text="Correo electrónico:").pack(pady=5)
        correo_entry = tk.Entry(ventana_solicitud, width=30)
        correo_entry.pack(pady=5)

        tk.Label(ventana_solicitud, text="Seleccionar Tianguis:").pack(pady=5)
        tianguis_var = tk.StringVar(value="Tianguis 1 Herreros 64, El Rosario, Azcapotzalco, 02100 Ciudad de México, CDMX")
        tianguis_menu = ttk.Combobox(ventana_solicitud, textvariable=tianguis_var)
        tianguis_menu['values'] = ['Tianguis 1 :"Herreros 64, El Rosario, Azcapotzalco, 02100 Ciudad de México, CDMX"',
                                'Tianguis 2 "Herreros 142-156, El Rosario, Azcapotzalco, 02100 Ciudad de México, CDMX"',
                                'Tianguis 3 "BELLE ÂME, Astronomía #1 U.H, El Rosario, 02100 Ciudad de México"',
                                'Tianguis 4 "El Rosario, Azcapotzalco, 02100 Ciudad de México, CDMX"',
                                'Tianguis 5 "Calle Helio 37-17, El Rosario, Azcapotzalco, 02100 Ciudad de México, CDMX"',
                                'Tianguis 6 "Argon 2, El Rosario, Azcapotzalco, 02100 Ciudad de México, CDMX"',
                                'Tianguis 7 "Del Pescadito 10, El Rosario, Azcapotzalco, 02100 Ciudad de México, CDMX"']
        tianguis_menu.pack(pady=5)

        btn_enviar = tk.Button(ventana_solicitud, text="Enviar Solicitud", command=enviar_solicitud)
        btn_enviar.pack(pady=20)


    def consultar_reporte(self):
        # Ventana para consultar reportes
        ventana_consulta = tk.Toplevel(self.root)
        ventana_consulta.title("Consultar Reportes")
        ventana_consulta.geometry("600x400")

        tk.Label(ventana_consulta, text="Reportes de Recolección", font=("Arial", 16)).pack(pady=10)

        # Crear tabla para mostrar reportes
        columnas = ("tianguis", "cantidad_basura", "tiempo_recoleccion", "Fecha")
        tabla = ttk.Treeview(ventana_consulta, columns=columnas, show="headings")
        tabla.pack(expand=True, fill="both", pady=10)

        # Configurar encabezados
        tabla.heading("tianguis", text="Número de Tianguis")
        tabla.heading("cantidad_basura", text="Basura Generada (kg)")
        tabla.heading("tiempo_recoleccion", text="Tiempo de Recolección (min)")
        tabla.heading("Fecha", text="Fecha Del Servicio")


        # Consultar reportes de la base de datos
        cursor = self.conn.cursor()
        cursor.execute("SELECT tianguis, cantidad_basura, tiempo_recoleccion, Fecha FROM recolecciones")
        reportes = cursor.fetchall()

        # Insertar datos en la tabla
        for reporte in reportes:
            tabla.insert("", tk.END, values=reporte)

        btn_cerrar = tk.Button(ventana_consulta, text="Cerrar", command=ventana_consulta.destroy)
        btn_cerrar.pack(pady=10)

    
    def menu_trabajador(self):
        # Menú del trabajador
        frame_trabajador = tk.Frame(self.root)
        frame_trabajador.pack(expand=True, fill='both')

        tk.Label(frame_trabajador, text="Menú de Trabajador", font=("Arial", 18)).pack(pady=20)

        opciones = [
            ("Mapa de los Tianguis", self.mapa_tianguis),
            ("Registrar Datos de Recolección", self.registrar_recoleccion),
            ("Consultar Servicios", self.consultar_solicitudes),
            ("Comunicarse con los Administradores", self.contactar_administradores),
            ("Cerrar Sesión", self.volver_inicio)
        ]

        for texto, comando in opciones:
            btn = tk.Button(frame_trabajador, text=texto, command=comando, width=30)
            btn.pack(pady=5)

    def consultar_solicitudes(self):
        # Ventana para consultar solicitudes de servicio
        ventana_consulta = tk.Toplevel(self.root)
        ventana_consulta.title("Consultar Solicitudes de Servicio")
        ventana_consulta.geometry("600x400")

        tk.Label(ventana_consulta, text="Solicitudes de Servicio", font=("Arial", 16)).pack(pady=10)

        # Crear tabla para mostrar solicitudes
        columnas = ("correo", "tianguis")
        tabla = ttk.Treeview(ventana_consulta, columns=columnas, show="headings")
        tabla.pack(expand=True, fill="both", pady=10)

        # Configurar encabezados
        tabla.heading("correo", text="Correo del Representante")
        tabla.heading("tianguis", text="Tianguis Solicitado")

        # Consultar solicitudes de la base de datos
        cursor = self.conn.cursor()
        cursor.execute("SELECT correo, tianguis FROM solicitudes_servicio")
        solicitudes = cursor.fetchall()

        # Insertar datos en la tabla
        for solicitud in solicitudes:
            tabla.insert("", tk.END, values=solicitud)

        btn_cerrar = tk.Button(ventana_consulta, text="Cerrar", command=ventana_consulta.destroy)
        btn_cerrar.pack(pady=10)


    def mapa_tianguis(self):
        # Función para abrir el mapa de tianguis en el navegador
        file_path = os.path.abspath("mapa_tianguis.html")
        webbrowser.open(f"file:///{file_path}", new=2)

        
    def registrar_recoleccion(self):
        # Ventana para registrar recolección
        ventana_registro = tk.Toplevel(self.root)
        ventana_registro.title("Registrar Datos de Recolección")
        ventana_registro.geometry("400x300")

        # Campos para ingresar los datos
        tk.Label(ventana_registro, text="Número de Tianguis:").pack(pady=5)
        tianguis_entry = tk.Entry(ventana_registro, width=30)
        tianguis_entry.pack(pady=5)

        tk.Label(ventana_registro, text="Cantidad de basura generada (kg):").pack(pady=5)
        basura_entry = tk.Entry(ventana_registro, width=30)
        basura_entry.pack(pady=5)

        tk.Label(ventana_registro, text="Tiempo de recolección (min):").pack(pady=5)
        tiempo_entry = tk.Entry(ventana_registro, width=30)
        tiempo_entry.pack(pady=5)

        tk.Label(ventana_registro, text="Fecha del Servicio (dd/mm/aaaa):").pack(pady=5)
        fecha_entry = tk.Entry(ventana_registro, width=30)
        fecha_entry.pack(pady=5)

        def guardar_recoleccion():
            # Obtener datos ingresados
            tianguis = tianguis_entry.get()
            cantidad_basura = basura_entry.get()
            tiempo_recoleccion = tiempo_entry.get()
            fecha = fecha_entry.get()

            # Validar entradas
            if not (tianguis and cantidad_basura and tiempo_recoleccion and fecha):
                messagebox.showerror("Error", "Todos los campos son obligatorios.")
                return

            # Validar formato de la fecha
            if not re.match(r"\d{2}/\d{2}/\d{4}", fecha):
                messagebox.showerror("Error", "La fecha debe estar en formato dd/mm/aaaa.")
                return

            try:
                # Validar valores numéricos
                tianguis = int(tianguis)
                cantidad_basura = float(cantidad_basura)
                tiempo_recoleccion = float(tiempo_recoleccion)

                if cantidad_basura < 0 or tiempo_recoleccion < 0:
                    messagebox.showerror("Error", "No se permiten valores negativos.")
                    return

                # Guardar en la base de datos
                cursor = self.conn.cursor()
                cursor.execute(
                    "INSERT INTO recolecciones (tianguis, cantidad_basura, tiempo_recoleccion, Fecha) VALUES (?, ?, ?, ?)",
                    (tianguis, cantidad_basura, tiempo_recoleccion, fecha)
                )
                self.conn.commit()
                messagebox.showinfo("Éxito", "Datos de recolección registrados correctamente.")
                ventana_registro.destroy()
            except ValueError:
                messagebox.showerror("Error", "Por favor ingresa valores numéricos válidos.")

        # Botón para guardar
        btn_guardar = tk.Button(ventana_registro, text="Guardar", command=guardar_recoleccion)
        btn_guardar.pack(pady=20)

    

# Inicializar la aplicación
root = tk.Tk()
app = BaseburaApp(root)
root.mainloop()