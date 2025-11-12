import os
from datetime import datetime

# Intentamos usar colores, si no, se usa texto simple
try:
    from colorama import init, Fore, Style
    init(autoreset=True)
except ImportError:
    print("Colorama no disponible, se usarán textos simples")
    Fore = Style = type('', (), {'RESET_ALL':'','RED':'','GREEN':'','CYAN':'','YELLOW':'','MAGENTA':'','WHITE':''})()

# Historial de la sesión
HISTORIAL = []

# ---------- Funciones auxiliares ----------

def registrar_historial(texto):
    """Guardar acción en historial"""
    fecha = datetime.now().strftime('%d/%m %H:%M')
    HISTORIAL.append(f"{fecha} - {texto}")

def tamano_legible(size):
    """Convierte bytes a KB/MB etc"""
    unidades = ['B', 'KB', 'MB', 'GB']
    i = 0
    while size >= 1024 and i < len(unidades)-1:
        size /= 1024
        i += 1
    if i == 0:
        return f"{int(size)} {unidades[i]}"
    return f"{size:.2f} {unidades[i]}"

def formatear_fecha(ts):
    return datetime.fromtimestamp(ts).strftime('%d/%m/%Y %H:%M')

def es_valido(nombre):
    return bool(nombre and nombre.strip())

def imprimir_error(msg):
    print(f"{Fore.RED}[ERROR]{Style.RESET_ALL} {msg}")

def imprimir_ok(msg):
    print(f"{Fore.GREEN}[OK]{Style.RESET_ALL} {msg}")

def imprimir_info(msg):
    print(f"{Fore.CYAN}[INFO]{Style.RESET_ALL} {msg}")

# ---------- Funciones principales ----------

def listar_contenido():
    try:
        items = os.listdir()
        if not items:
            imprimir_info("El directorio está vacío")
            return
        print("Contenido:")
        tam_total = 0
        for i in sorted(items):
            full = os.path.join(os.getcwd(), i)
            if os.path.isfile(full):
                tipo = "Archivo"
                tam = os.path.getsize(full)
                tam_total += tam
            elif os.path.isdir(full):
                tipo = "Directorio"
                tam = sum(os.path.getsize(os.path.join(full,f)) for f in os.listdir(full) if os.path.isfile(os.path.join(full,f)))
            else:
                tipo = "Otro"
                tam = 0
            print(f"{i} - {tipo} - {tamano_legible(tam)}")
        print(f"Tamaño total de archivos en este directorio: {tamano_legible(tam_total)}")
        registrar_historial("Listar contenido")
    except PermissionError:
        imprimir_error("Permiso denegado")
    except Exception as e:
        imprimir_error(f"Error al listar: {e}")

def crear_directorio():
    nombre = input("Nombre del directorio: ").strip()
    if not es_valido(nombre):
        imprimir_error("Nombre no válido")
        return
    if os.path.exists(nombre):
        imprimir_error("Ya existe ese nombre")
        return
    try:
        os.mkdir(nombre)
        imprimir_ok(f"Directorio '{nombre}' creado")
        registrar_historial(f"Crear directorio {nombre}")
    except PermissionError:
        imprimir_error("Permiso denegado")
    except Exception as e:
        imprimir_error(f"Error: {e}")

def crear_archivo():
    nombre = input("Nombre del archivo (ej. nota.txt): ").strip()
    if not es_valido(nombre):
        imprimir_error("Nombre no válido")
        return
    if os.path.exists(nombre):
        imprimir_error("Ya existe")
        return
    print("Escribe contenido inicial. Línea con solo '.' para terminar:")
    lineas = []
    while True:
        try:
            linea = input()
        except KeyboardInterrupt:
            print("\nInterrumpido")
            return
        if linea.strip() == '.':
            break
        lineas.append(linea)
    try:
        with open(nombre, 'w', encoding='utf-8') as f:
            if lineas:
                f.write("\n".join(lineas)+"\n")
        imprimir_ok(f"Archivo '{nombre}' creado")
        registrar_historial(f"Crear archivo {nombre}")
    except PermissionError:
        imprimir_error("Permiso denegado")
    except Exception as e:
        imprimir_error(f"Error: {e}")

def escribir_en_archivo():
    nombre = input("Archivo a añadir texto: ").strip()
    if not es_valido(nombre):
        imprimir_error("Nombre no válido")
        return
    if not os.path.exists(nombre) or os.path.isdir(nombre):
        imprimir_error("No existe o es un directorio")
        return
    print("Escribe texto. Línea con solo '.' para terminar:")
    lineas = []
    while True:
        try:
            linea = input()
        except KeyboardInterrupt:
            print("\nInterrumpido")
            return
        if linea.strip() == '.':
            break
        lineas.append(linea)
    try:
        with open(nombre,'a',encoding='utf-8') as f:
            if lineas:
                f.write("\n".join(lineas)+"\n")
        imprimir_ok(f"Contenido añadido a '{nombre}'")
        registrar_historial(f"Añadir a archivo {nombre}")
    except PermissionError:
        imprimir_error("Permiso denegado")
    except Exception as e:
        imprimir_error(f"Error: {e}")

def eliminar_elemento():
    nombre = input("Archivo o directorio a eliminar: ").strip()
    if not es_valido(nombre):
        imprimir_error("Nombre no válido")
        return
    if not os.path.exists(nombre):
        imprimir_error("No existe")
        return
    confirmar = input(f"¿Seguro que quieres eliminar '{nombre}'? (s/N): ").strip().lower()
    if confirmar != 's':
        imprimir_info("Operación cancelada")
        return
    try:
        if os.path.isfile(nombre):
            os.remove(nombre)
            imprimir_ok(f"Archivo '{nombre}' eliminado")
        elif os.path.isdir(nombre):
            try:
                os.rmdir(nombre)
                imprimir_ok(f"Directorio '{nombre}' eliminado (vacío)")
            except OSError:
                imprimir_error("Carpeta no vacía")
        registrar_historial(f"Eliminar {nombre}")
    except PermissionError:
        imprimir_error("Permiso denegado")
    except Exception as e:
        imprimir_error(f"Error: {e}")

def mostrar_informacion():
    nombre = input("Archivo o directorio: ").strip()
    if not es_valido(nombre):
        imprimir_error("Nombre no válido")
        return
    if not os.path.exists(nombre):
        imprimir_error("No existe")
        return
    try:
        if os.path.isfile(nombre):
            tipo = "Archivo"
            tam = os.path.getsize(nombre)
        elif os.path.isdir(nombre):
            tipo = "Directorio"
            tam = sum(os.path.getsize(os.path.join(nombre,f)) for f in os.listdir(nombre) if os.path.isfile(os.path.join(nombre,f)))
        else:
            tipo = "Otro"
            tam = 0
        mtime = os.path.getmtime(nombre)
        print(f"Tipo: {tipo}")
        print(f"Tamaño: {tamano_legible(tam)}")
        print(f"Última modificación: {formatear_fecha(mtime)}")
        registrar_historial(f"Mostrar info {nombre}")
    except PermissionError:
        imprimir_error("Permiso denegado")
    except Exception as e:
        imprimir_error(f"Error: {e}")

def cambiar_directorio():
    ruta = input("Ruta a la que cambiar (.. para padre): ").strip()
    if not es_valido(ruta):
        imprimir_error("Ruta no válida")
        return
    try:
        os.chdir(ruta)
        imprimir_ok(f"Cambiado a: {os.getcwd()}")
        registrar_historial(f"Cambiar directorio {ruta}")
    except FileNotFoundError:
        imprimir_error("No encontrado")
    except NotADirectoryError:
        imprimir_error("No es un directorio")
    except PermissionError:
        imprimir_error("Permiso denegado")

def renombrar_elemento():
    origen = input("Nombre actual: ").strip()
    if not es_valido(origen) or not os.path.exists(origen):
        imprimir_error("No válido o no existe")
        return
    destino = input("Nuevo nombre: ").strip()
    if not es_valido(destino) or os.path.exists(destino):
        imprimir_error("Nombre no válido o ya existe")
        return
    try:
        os.rename(origen,destino)
        imprimir_ok(f"Renombrado '{origen}' a '{destino}'")
        registrar_historial(f"Renombrar {origen} -> {destino}")
    except PermissionError:
        imprimir_error("Permiso denegado")
    except Exception as e:
        imprimir_error(f"Error: {e}")

def mostrar_historial():
    if not HISTORIAL:
        imprimir_info("Sin historial")
        return
    print("Historial de acciones:")
    for i, h in enumerate(HISTORIAL,1):
        print(f"{i}. {h}")

# ---------- Menú principal ----------

def mostrar_menu():
    print("\n" + "="*50)
    print(f"Gestor de Archivos - {os.getcwd()}")
    print("="*50)
    print("1. Listar contenido")
    print("2. Crear directorio")
    print("3. Crear archivo")
    print("4. Añadir texto a archivo")
    print("5. Eliminar archivo/carpeta vacía")
    print("6. Mostrar info")
    print("7. Cambiar directorio")
    print("8. Renombrar archivo/carpeta")
    print("9. Historial")
    print("0. Salir")
    print("="*50)

def main():
    while True:
        mostrar_menu()
        opcion = input("Elige opción: ").strip()
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
            imprimir_info("Saliendo...")
            break
        else:
            imprimir_error("Opción no válida")

if __name__ == "__main__":
    main()
