#!/usr/bin/env python3
# gestor_archivos_avanzado.py
"""
Gestor de archivos y carpetas (versión 'para 10')
- Menú en bucle
- Muestra ruta actual siempre
- Listado con tipo, color y tamaño legible
- Crear directorio
- Crear archivo .txt con contenido inicial
- Añadir texto (append) a archivos existentes
- Eliminar archivo o directorio (solo carpetas vacías) - Opción A elegida
- Mostrar información (tamaño, fecha modificación, tipo)
- Cambiar directorio (incluye subir a padre con ..)
- Renombrar archivos/directorios
- Historial de comandos en la sesión
- Manejo cuidadoso de errores y mensajes amigables
- Utiliza colorama para colorear salida
"""

import os
import sys
import shutil
from datetime import datetime
from pathlib import Path
from typing import List, Tuple

try:
    from colorama import init as colorama_init, Fore, Style
except Exception:
    print("Aviso: colorama no está instalado. Para colores instala 'colorama' (pip install colorama).")
    # Definir constantes vacías para evitar fallos si no existe colorama
    class Dummy:
        def __getattr__(self, name):
            return ''
    colorama_init = lambda: None
    Fore = Dummy()
    Style = Dummy()

colorama_init(autoreset=True)

# ---------- Configuración / Estado global ----------
HISTORIAL: List[str] = []   # historial de comandos de la sesión

# ---------- Utilidades ----------

def registrar_historial(entrada: str):
    """Guarda en el historial (solo comandos y acciones principales)."""
    HISTORIAL.append(f"{datetime.now().strftime('%Y-%m-%d %H:%M:%S')} - {entrada}")

def tamano_legible(bytes_size: int) -> str:
    """Convierte bytes a una representación legible (B, KB, MB, GB)."""
    try:
        if bytes_size < 0:
            return "0 B"
        unidades = ['B', 'KB', 'MB', 'GB', 'TB']
        i = 0
        size = float(bytes_size)
        while size >= 1024 and i < len(unidades) - 1:
            size /= 1024.0
            i += 1
        # Mostrar hasta 2 decimales si es necesario
        if i == 0:
            return f"{int(size)} {unidades[i]}"
        else:
            return f"{size:.2f} {unidades[i]}"
    except Exception:
        return f"{bytes_size} B"

def formatear_fecha(timestamp: float) -> str:
    """Devuelve fecha legible desde timestamp (segundos)."""
    try:
        return datetime.fromtimestamp(timestamp).strftime("%Y-%m-%d %H:%M:%S")
    except Exception:
        return "Desconocida"

def calcular_tamano_directorio(ruta_dir: str) -> int:
    """Suma tamaños de archivos en un directorio (no sigue enlaces simbólicos por seguridad)."""
    total = 0
    try:
        for root, dirs, files in os.walk(ruta_dir):
            for f in files:
                fp = os.path.join(root, f)
                try:
                    if os.path.islink(fp):
                        continue
                    total += os.path.getsize(fp)
                except OSError:
                    # Ignorar archivos inaccesibles
                    pass
        return total
    except Exception:
        return 0

def es_ruta_valida(nombre: str) -> bool:
    """Comprueba que el nombre no esté vacío ni tenga saltos de línea."""
    return bool(nombre and nombre.strip())

def imprimir_error(msg: str):
    print(f"{Fore.RED}[ERROR]{Style.RESET_ALL} {msg}")

def imprimir_exito(msg: str):
    print(f"{Fore.GREEN}[OK]{Style.RESET_ALL} {msg}")

def imprimir_info(msg: str):
    print(f"{Fore.CYAN}[INFO]{Style.RESET_ALL} {msg}")

# ---------- Funciones principales del gestor (según la estructura sugerida) ----------

def mostrar_menu():
    """Muestra el menú principal con la ruta actual."""
    cwd = os.getcwd()
    print("\n" + "=" * 80)
    print(f"{Fore.YELLOW}Gestor de Archivos - Ruta actual: {Fore.MAGENTA}{cwd}{Style.RESET_ALL}")
    print("=" * 80)
    print("1. Listar contenido del directorio actual")
    print("2. Crear un nuevo directorio")
    print("3. Crear un archivo de texto")
    print("4. Escribir texto en un archivo existente (añadir al final)")
    print("5. Eliminar un archivo o directorio (solo carpetas vacías)")
    print("6. Mostrar información del archivo/carpeta")
    print("7. Cambiar directorio")
    print("8. Renombrar archivo o carpeta")
    print("9. Mostrar historial de comandos")
    print("0. Salir")
    print("-" * 80)

def listar_contenido():
    """Lista archivos y carpetas del directorio actual, indicando tipo y tamaño legible."""
    try:
        ruta = os.getcwd()
        elementos = os.listdir(ruta)
        registrar_historial("Listar contenido")
        # Calcular tamaño total de archivos del directorio (no recursivo en la lista principal, pero mostramos total recursivo aparte)
        tam_total = 0
        for e in elementos:
            full = os.path.join(ruta, e)
            if os.path.isfile(full):
                try:
                    tam_total += os.path.getsize(full)
                except OSError:
                    pass
        # Mostrar
        if not elementos:
            imprimir_info("El directorio está vacío.")
            print(f"Tamaño total de archivos: {tamano_legible(tam_total)}")
            return
        print(f"\nContenido de: {Fore.MAGENTA}{ruta}{Style.RESET_ALL}")
        # Ordenar: directorios primero, luego archivos, ambos alfabéticamente
        dirs = sorted([e for e in elementos if os.path.isdir(os.path.join(ruta, e))])
        files = sorted([e for e in elementos if os.path.isfile(os.path.join(ruta, e))])
        others = sorted([e for e in elementos if e not in dirs and e not in files])
        # Mostrar directorios
        for d in dirs:
            full = os.path.join(ruta, d)
            tam = calcular_tamano_directorio(full)
            print(f"{Fore.BLUE}[DIR ]{Style.RESET_ALL} {d} — {tamano_legible(tam)}")
        # Mostrar archivos
        for f in files:
            full = os.path.join(ruta, f)
            try:
                tam = os.path.getsize(full)
            except OSError:
                tam = 0
            print(f"{Fore.WHITE}[FILE]{Style.RESET_ALL} {f} — {tamano_legible(tam)}")
        # Otros (enlaces simbólicos u otros tipos)
        for o in others:
            print(f"{Fore.YELLOW}[OTRO]{Style.RESET_ALL} {o}")
        print(f"\nTamaño total de archivos en este directorio: {tamano_legible(tam_total)}")
    except PermissionError:
        imprimir_error("Permiso denegado al listar el directorio.")
    except Exception as e:
        imprimir_error(f"Error inesperado al listar el directorio: {e}")

def crear_directorio():
    """Crea una nueva carpeta en el directorio actual."""
    nombre = input("Nombre del nuevo directorio: ").strip()
    if not es_ruta_valida(nombre):
        imprimir_error("Nombre no válido.")
        return
    ruta = os.path.join(os.getcwd(), nombre)
    if os.path.exists(ruta):
        imprimir_error("Ya existe un archivo o directorio con ese nombre.")
        return
    try:
        os.mkdir(ruta)
        registrar_historial(f"Crear directorio: {ruta}")
        imprimir_exito(f"Directorio '{nombre}' creado correctamente.")
    except PermissionError:
        imprimir_error("Permiso denegado para crear el directorio.")
    except OSError as e:
        imprimir_error(f"Error al crear el directorio: {e}")

def crear_archivo():
    """Crea un archivo de texto y permite escribir contenido inicial."""
    nombre = input("Nombre del archivo a crear (ej. nota.txt): ").strip()
    if not es_ruta_valida(nombre):
        imprimir_error("Nombre no válido.")
        return
    ruta = os.path.join(os.getcwd(), nombre)
    if os.path.exists(ruta):
        imprimir_error("Ya existe un archivo o directorio con ese nombre.")
        return
    print("Introduce el contenido inicial del archivo. Escribe una línea con solo '.' para terminar:")
    lineas = []
    while True:
        try:
            linea = input()
        except KeyboardInterrupt:
            print()  # salto de línea amable
            imprimir_info("Entrada interrumpida. El archivo no se creó.")
            return
        if linea.strip() == '.':
            break
        lineas.append(linea)
    try:
        with open(ruta, 'w', encoding='utf-8') as f:
            if lineas:
                f.write("\n".join(lineas) + "\n")
        registrar_historial(f"Crear archivo: {ruta}")
        imprimir_exito(f"Archivo '{nombre}' creado correctamente.")
    except PermissionError:
        imprimir_error("Permiso denegado al crear o escribir el archivo.")
    except OSError as e:
        imprimir_error(f"Error al crear el archivo: {e}")

def escribir_en_archivo():
    """Abre un archivo existente y añade texto al final (append)."""
    nombre = input("Nombre del archivo a abrir y añadir texto: ").strip()
    if not es_ruta_valida(nombre):
        imprimir_error("Nombre no válido.")
        return
    ruta = os.path.join(os.getcwd(), nombre)
    if not os.path.exists(ruta):
        imprimir_error("El archivo no existe.")
        return
    if os.path.isdir(ruta):
        imprimir_error("La ruta indicada es un directorio, no un archivo.")
        return
    print("Introduce el texto a añadir. Escribe una línea con solo '.' para terminar:")
    lineas = []
    while True:
        try:
            linea = input()
        except KeyboardInterrupt:
            print()
            imprimir_info("Entrada interrumpida. No se añadió contenido.")
            return
        if linea.strip() == '.':
            break
        lineas.append(linea)
    try:
        with open(ruta, 'a', encoding='utf-8') as f:
            if lineas:
                f.write("\n".join(lineas) + "\n")
        registrar_historial(f"Añadir a archivo: {ruta}")
        imprimir_exito(f"Contenido añadido a '{nombre}'.")
    except PermissionError:
        imprimir_error("Permiso denegado al abrir o escribir el archivo.")
    except OSError as e:
        imprimir_error(f"Error al escribir en el archivo: {e}")

def eliminar_elemento():
    """Elimina un archivo o directorio (solo carpetas vacías - os.rmdir)."""
    nombre = input("Nombre del archivo o directorio a eliminar: ").strip()
    if not es_ruta_valida(nombre):
        imprimir_error("Nombre no válido.")
        return
    ruta = os.path.join(os.getcwd(), nombre)
    if not os.path.exists(ruta):
        imprimir_error("El archivo o directorio no existe.")
        return
    confirmar = input(f"¿Seguro que quieres eliminar '{nombre}'? (s/N): ").strip().lower()
    if confirmar != 's':
        imprimir_info("Operación cancelada.")
        return
    try:
        if os.path.isfile(ruta):
            os.remove(ruta)
            registrar_historial(f"Eliminar archivo: {ruta}")
            imprimir_exito(f"Archivo '{nombre}' eliminado.")
        elif os.path.isdir(ruta):
            # Opción A: solo eliminar carpetas vacías
            try:
                os.rmdir(ruta)
                registrar_historial(f"Eliminar directorio vacío: {ruta}")
                imprimir_exito(f"Directorio '{nombre}' eliminado (estaba vacío).")
            except OSError:
                imprimir_error("La carpeta no está vacía o no se puede eliminar. (Solo se permiten carpetas vacías).")
        else:
            imprimir_error("No se reconoce el tipo de elemento a eliminar.")
    except PermissionError:
        imprimir_error("Permiso denegado al intentar eliminar.")
    except OSError as e:
        imprimir_error(f"Error al eliminar: {e}")

def mostrar_informacion():
    """Muestra tamaño, fecha de modificación y tipo de archivo/carpeta."""
    nombre = input("Nombre del archivo o directorio: ").strip()
    if not es_ruta_valida(nombre):
        imprimir_error("Nombre no válido.")
        return
    ruta = os.path.join(os.getcwd(), nombre)
    if not os.path.exists(ruta):
        imprimir_error("El archivo o directorio no existe.")
        return
    try:
        if os.path.isfile(ruta):
            tipo = "Archivo"
            tam = os.path.getsize(ruta)
        elif os.path.isdir(ruta):
            tipo = "Directorio"
            tam = calcular_tamano_directorio(ruta)
        else:
            tipo = "Otro"
            tam = 0
        mtime = os.path.getmtime(ruta)
        atime = os.path.getatime(ruta)
        ctime = os.path.getctime(ruta)
        print(f"\nInformación de: {Fore.MAGENTA}{ruta}{Style.RESET_ALL}")
        print(f"Tipo: {Fore.BLUE if tipo == 'Directorio' else Fore.WHITE}{tipo}{Style.RESET_ALL}")
        print(f"Tamaño: {tamano_legible(tam)} ({tam} bytes)")
        print(f"Última modificación: {formatear_fecha(mtime)}")
        print(f"Último acceso: {formatear_fecha(atime)}")
        print(f"Creación (o cambio de metadatos): {formatear_fecha(ctime)}")
        registrar_historial(f"Mostrar información: {ruta}")
    except PermissionError:
        imprimir_error("Permiso denegado al acceder a la información.")
    except OSError as e:
        imprimir_error(f"Error al obtener información: {e}")

def cambiar_directorio():
    """Cambia el directorio actual; permite usar rutas relativas (.. para padre)."""
    destino = input("Ruta a la que cambiar (usa .. para subir): ").strip()
    if not es_ruta_valida(destino):
        imprimir_error("Ruta no válida.")
        return
    try:
        os.chdir(destino)
        registrar_historial(f"Cambiar directorio a: {os.getcwd()}")
        imprimir_exito(f"Cambiado a: {os.getcwd()}")
    except FileNotFoundError:
        imprimir_error("Ruta no encontrada.")
    except NotADirectoryError:
        imprimir_error("La ruta indicada no es un directorio.")
    except PermissionError:
        imprimir_error("Permiso denegado para acceder a la ruta.")
    except OSError as e:
        imprimir_error(f"Error al cambiar de directorio: {e}")

def renombrar_elemento():
    """Renombra archivos o carpetas."""
    origen = input("Nombre actual del archivo o carpeta: ").strip()
    if not es_ruta_valida(origen):
        imprimir_error("Nombre no válido.")
        return
    ruta_origen = os.path.join(os.getcwd(), origen)
    if not os.path.exists(ruta_origen):
        imprimir_error("El elemento no existe.")
        return
    destino = input("Nuevo nombre: ").strip()
    if not es_ruta_valida(destino):
        imprimir_error("Nuevo nombre no válido.")
        return
    ruta_destino = os.path.join(os.getcwd(), destino)
    if os.path.exists(ruta_destino):
        imprimir_error("Ya existe un archivo o carpeta con el nuevo nombre.")
        return
    try:
        os.rename(ruta_origen, ruta_destino)
        registrar_historial(f"Renombrar: {ruta_origen} -> {ruta_destino}")
        imprimir_exito(f"Renombrado '{origen}' a '{destino}'.")
    except PermissionError:
        imprimir_error("Permiso denegado al renombrar.")
    except OSError as e:
        imprimir_error(f"Error al renombrar: {e}")

def mostrar_historial():
    """Muestra el historial de comandos registrados en la sesión."""
    if not HISTORIAL:
        imprimir_info("No hay historial de comandos en esta sesión.")
        return
    print(f"\n{Fore.CYAN}Historial de comandos (sesión actual):{Style.RESET_ALL}")
    for i, item in enumerate(HISTORIAL, start=1):
        print(f"{i:03d}. {item}")

# ---------- Bucle principal ----------

def main():
    try:
        while True:
            mostrar_menu()
            opcion = input("Selecciona una opción (número): ").strip()
            if not opcion:
                imprimir_error("Debes elegir una opción.")
                continue
            # Registrar la acción (solo opción, no datos sensibles)
            registrar_historial(f"Opción seleccionada: {opcion}")
            if opcion == '1':
                listar_contenido()
            elif opcion == '2':
                crear_directorio()
            elif opcion == '3':
                crear_archivo()
            elif opcion == '4':
                escribir_en_archivo()
            elif opcion == '5':
                eliminar_elemento()
            elif opcion == '6':
                mostrar_informacion()
            elif opcion == '7':
                cambiar_directorio()
            elif opcion == '8':
                renombrar_elemento()
            elif opcion == '9':
                mostrar_historial()
            elif opcion == '0':
                imprimir_info("Saliendo..... ¡Hasta luego!")
                break
            else:
                imprimir_error("Opción no válida. Elige un número del menú.")
    except KeyboardInterrupt:
        print()  # salto de línea limpio
        imprimir_info("Interrumpido por el usuario. Saliendo.....")
    except Exception as e:
        imprimir_error(f"Fallo inesperado en la aplicación: {e}")
    finally:
        # Mensaje final y posible guardado de historial opcional (no solicitado)
        imprimir_info("Sesión finalizada.")

if __name__ == "__main__":
    main()
