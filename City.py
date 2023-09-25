import sqlite3
import hashlib
import os

# Función para generar un hash de contraseña con sal
def generar_hash_contraseña(contraseña, sal=None):
    if sal is None:
        sal = os.urandom(32)
    key = hashlib.pbkdf2_hmac('sha256', contraseña.encode('utf-8'), sal, 100000)
    return sal, key

# Función para verificar una contraseña
def verificar_contraseña(contraseña, sal, hash_guardado):
    key = hashlib.pbkdf2_hmac('sha256', contraseña.encode('utf-8'), sal, 100000)
    return key == hash_guardado

# Conexión a la base de datos o creación si no existe
conn = sqlite3.connect("city_watch.db")
cursor = conn.cursor()

# Creación de la tabla para Incidentes Reportados
cursor.execute('''
    CREATE TABLE IF NOT EXISTS incidentes_reportados (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        fecha_hora TEXT,
        ubicacion TEXT,
        descripcion TEXT,
        categoria TEXT,
        estado TEXT,
        reportante_nombre TEXT,
        reportante_contacto TEXT
    )
''')

# Creación de la tabla para Usuarios Registrados
cursor.execute('''
    CREATE TABLE IF NOT EXISTS usuarios_registrados (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        nombre_usuario TEXT UNIQUE,
        contraseña_salt BLOB,
        contraseña_hash BLOB,
        informacion_contacto TEXT
    )
''')

# Creación de la tabla para Datos de Autoridades
cursor.execute('''
    CREATE TABLE IF NOT EXISTS datos_autoridades (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        nombre_autoridad TEXT,
        nivel_acceso TEXT,
        permisos TEXT
    )
''')

# Creación de la tabla para Comentarios y Actualizaciones
cursor.execute('''
    CREATE TABLE IF NOT EXISTS comentarios_actualizaciones (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        incidente_id INTEGER,
        usuario_id INTEGER,
        comentario_actualizacion TEXT,
        fecha_hora TEXT,
        FOREIGN KEY (incidente_id) REFERENCES incidentes_reportados (id),
        FOREIGN KEY (usuario_id) REFERENCES usuarios_registrados (id)
    )
''')

# Guardar los cambios en la base de datos
conn.commit()

# Función para insertar un nuevo usuario
def insertar_usuario(nombre_usuario, contraseña):
    sal, hash_contraseña = generar_hash_contraseña(contraseña)
    cursor.execute("INSERT INTO usuarios_registrados (nombre_usuario, contraseña_salt, contraseña_hash) VALUES (?, ?, ?)", (nombre_usuario, sal, hash_contraseña))
    conn.commit()

# Función para verificar las credenciales de un usuario
def verificar_credenciales(nombre_usuario, contraseña):
    cursor.execute("SELECT nombre_usuario, contraseña_salt, contraseña_hash FROM usuarios_registrados WHERE nombre_usuario=?", (nombre_usuario,))
    usuario = cursor.fetchone()
    if usuario:
        nombre_usuario, sal, hash_guardado = usuario
        if verificar_contraseña(contraseña, sal, hash_guardado):
            return True
    return False

# Función para insertar un nuevo incidente reportado
def insertar_incidente(fecha_hora, ubicacion, descripcion, categoria, estado, reportante_nombre, reportante_contacto):
    cursor.execute("INSERT INTO incidentes_reportados (fecha_hora, ubicacion, descripcion, categoria, estado, reportante_nombre, reportante_contacto) VALUES (?, ?, ?, ?, ?, ?, ?)", (fecha_hora, ubicacion, descripcion, categoria, estado, reportante_nombre, reportante_contacto))
    conn.commit()

# Función para insertar un nuevo comentario o actualización
def insertar_comentario_actualizacion(incidente_id, usuario_id, comentario_actualizacion, fecha_hora):
    cursor.execute("INSERT INTO comentarios_actualizaciones (incidente_id, usuario_id, comentario_actualizacion, fecha_hora) VALUES (?, ?, ?, ?)", (incidente_id, usuario_id, comentario_actualizacion, fecha_hora))
    conn.commit()

# Ejemplo de uso: Insertar un usuario
insertar_usuario("usuario1", "contraseña123")

# Ejemplo de uso: Verificar las credenciales de un usuario
if verificar_credenciales("usuario1", "contraseña123"):
    print("Credenciales válidas")
else:
    print("Credenciales inválidas")

# Ejemplo de uso: Insertar un incidente reportado
insertar_incidente("2023-09-20 10:30:00", "Latitud, Longitud", "Descripción del incidente", "Tráfico", "Abierto", "Nombre del reportante", "contacto@correo.com")

# Ejemplo de uso: Insertar un comentario o actualización
insertar_comentario_actualizacion(1, 1, "Se está investigando el incidente.", "2023-09-20 11:00:00")

# Cierra la conexión a la base de datos
conn.close()
