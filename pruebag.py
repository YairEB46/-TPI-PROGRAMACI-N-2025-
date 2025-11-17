import datetime
import tkinter as tk
from tkinter import messagebox
import qrcode
from PIL import Image, ImageTk
import os

# ============================================
#   ARCHIVO DE PRODUCTOS
# ============================================

ARCHIVO_PRODUCTOS = "C:\\Users\\FRVM\\Desktop\\TPI PROGRAMACION 2025\\-TPI-PROGRAMACI-N-2025-\\lista_de_productos.txt"

def leer_productos():
    productos = {}
    try:
        with open(ARCHIVO_PRODUCTOS, "r", encoding="utf-8") as f:
            for linea in f:
                linea = linea.strip()
                if not linea or linea.startswith("-"):
                    continue
                if ":" in linea:
                    nombre, precio = linea.split(":", 1)
                    nombre = nombre.strip().strip('"')
                    precio = precio.strip().strip(",")
                    try:
                        productos[nombre] = float(precio)
                    except:
                        continue
    except FileNotFoundError:
        messagebox.showerror("Error", f"No se encontró el archivo '{ARCHIVO_PRODUCTOS}'")
    return productos

def listar_productos_con_codigo():
    """
    Devuelve una lista de strings tipo '1: Producto - $precio'
    """
    productos_dict = leer_productos()
    lista = []
    for i, (nombre, precio) in enumerate(productos_dict.items(), start=1):
        lista.append(f"{i}: {nombre} - ${precio}")
    return lista

def producto_por_codigo(codigo):
    productos_dict = leer_productos()
    productos_lista = list(productos_dict.keys())
    if 1 <= codigo <= len(productos_lista):
        return productos_lista[codigo-1]
    return None

# ============================================
#   GENERAR BOLETA Y QR
# ============================================

BOLETAS_DIR = "boletas"
os.makedirs(BOLETAS_DIR, exist_ok=True)

def generar_contenido_boleta(cliente, productos, productos_dict, total, fecha):
    lineas = [
        f"Boleta para: {cliente}",
        f"Fecha: {fecha}",
        "\nProductos comprados:\n"
    ]
    for cantidad, producto in productos:
        precio = productos_dict.get(producto, 0)
        subtotal = cantidad * precio
        lineas.append(f"{cantidad} x {producto} = ${subtotal:.2f}")
    lineas.append(f"\nTOTAL: ${total:.2f}")
    return "\n".join(lineas)

def obtener_nombre_boleta(cliente, fecha):
    fecha_formateada = fecha.replace(":", ";").replace("/", "-").replace(" ", "_")
    return f"{cliente}_{fecha_formateada}.txt"

def registrar_boleta(cliente, productos_agregados):
    productos_dict = leer_productos()
    fecha = datetime.datetime.now().strftime("%d-%m-%y %H-%M-%S")
    total = sum(cantidad * productos_dict.get(prod, 0) for cantidad, prod in productos_agregados)
    contenido = generar_contenido_boleta(cliente, productos_agregados, productos_dict, total, fecha)

    archivo = obtener_nombre_boleta(cliente, fecha)
    ruta_txt = os.path.join(BOLETAS_DIR, archivo)
    with open(ruta_txt, "w", encoding="utf-8") as f:
        f.write(contenido)

    # Generar QR
    qr = qrcode.make(contenido)
    qr_path = os.path.join(BOLETAS_DIR, f"QR_{archivo.replace('.txt','')}.png")
    qr.save(qr_path)

    mostrar_ticket(contenido, ruta_txt, qr_path)

# ============================================
#   MOSTRAR TICKET Y QR
# ============================================

def mostrar_ticket(contenido, archivo, ruta_qr):
    v = tk.Toplevel()
    v.title("Ticket generado")
    v.geometry("550x600")

    tk.Label(v, text=f"Archivo generado: {archivo.split('/')[-1]}", font=("Arial", 12, "bold")).pack(pady=5)

    caja = tk.Text(v, width=60, height=20, font=("Arial", 10))
    caja.pack(pady=10)
    caja.insert(tk.END, contenido)
    caja.config(state=tk.DISABLED)

    img = Image.open(ruta_qr).resize((220, 220))
    qr_img = ImageTk.PhotoImage(img)

    etiqueta_qr = tk.Label(v, image=qr_img)
    etiqueta_qr.image = qr_img
    etiqueta_qr.pack(pady=10)

    tk.Button(v, text="Cerrar", command=v.destroy, bg="#4CAF50", fg="white").pack(pady=10)

# ============================================
#   INTERFAZ PRINCIPAL
# ============================================

productos_agregados = []

def agregar_producto():
    cantidad = entry_cantidad.get().strip()
    codigo = entry_producto.get().strip()

    if not cantidad.isdigit() or int(cantidad) <= 0:
        messagebox.showerror("Error", "Cantidad inválida")
        return

    if not codigo.isdigit() or int(codigo) <= 0:
        messagebox.showerror("Error", "Código inválido")
        return

    codigo = int(codigo)
    producto = producto_por_codigo(codigo)
    if not producto:
        messagebox.showerror("Error", f"No existe un producto con el código {codigo}")
        return

    productos_agregados.append((int(cantidad), producto))
    log.insert(tk.END, f"{cantidad} x {producto}\n")

    entry_cantidad.delete(0, tk.END)
    entry_producto.delete(0, tk.END)

def eliminar_producto():
    """
    Permite eliminar un producto agregado por índice de la lista de agregados
    """
    indice = entry_eliminar.get().strip()
    if not indice.isdigit() or int(indice) <= 0:
        messagebox.showerror("Error", "Índice inválido")
        return
    indice = int(indice)
    if 1 <= indice <= len(productos_agregados):
        eliminado = productos_agregados.pop(indice-1)
        messagebox.showinfo("Eliminado", f"Se eliminó {eliminado[1]}")
        actualizar_log()
        entry_eliminar.delete(0, tk.END)
    else:
        messagebox.showerror("Error", "Índice fuera de rango")

def actualizar_log():
    log.delete(1.0, tk.END)
    log.insert(tk.END, "Productos agregados:\n")
    for i, (cant, prod) in enumerate(productos_agregados, start=1):
        log.insert(tk.END, f"{i}: {cant} x {prod}\n")

def finalizar_venta():
    cliente = entry_cliente.get().strip()

    if not cliente:
        messagebox.showerror("Error", "Debe ingresar el nombre del cliente.")
        return

    if not productos_agregados:
        messagebox.showerror("Error", "No se agregaron productos.")
        return

    registrar_boleta(cliente, productos_agregados)

    productos_agregados.clear()
    actualizar_log()

def ver_lista_productos():
    v = tk.Toplevel()
    v.title("Lista de productos")

    tk.Label(v, text="Productos disponibles (ingrese el código):", font=("Arial", 12)).pack()

    caja = tk.Text(v, width=50, height=20, font=("Arial", 10))
    caja.pack()

    lista = listar_productos_con_codigo()
    if lista:
        for prod in lista:
            caja.insert(tk.END, prod + "\n")
    else:
        caja.insert(tk.END, "El archivo está vacío o no se encontró.")

leer_productos()

# ============================================
#   CREACIÓN DE VENTANA PRINCIPAL
# ============================================

root = tk.Tk()
root.title("Sistema de Ventas")
root.geometry("500x600")

tk.Label(root, text="Nombre del Cliente:", font=("Arial", 12)).pack(pady=5)
entry_cliente = tk.Entry(root, font=("Arial", 12))
entry_cliente.pack(pady=5)

tk.Label(root, text="Cantidad:", font=("Arial", 12)).pack(pady=5)
entry_cantidad = tk.Entry(root, font=("Arial", 12))
entry_cantidad.pack(pady=5)

tk.Label(root, text="Código del Producto:", font=("Arial", 12)).pack(pady=5)
entry_producto = tk.Entry(root, font=("Arial", 12))
entry_producto.pack(pady=5)

tk.Button(root, text="Agregar Producto", command=agregar_producto,
          bg="#0A84FF", fg="white", font=("Arial", 12)).pack(pady=10)

# Eliminar productos
tk.Label(root, text="Índice para eliminar producto:", font=("Arial", 12)).pack(pady=5)
entry_eliminar = tk.Entry(root, font=("Arial", 12))
entry_eliminar.pack(pady=5)
tk.Button(root, text="Eliminar Producto", command=eliminar_producto,
          bg="#FF3B30", fg="white", font=("Arial", 12)).pack(pady=10)

tk.Button(root, text="Finalizar Venta", command=finalizar_venta,
          bg="#4CAF50", fg="white", font=("Arial", 12)).pack(pady=10)

tk.Button(root, text="Ver Lista de Productos", command=ver_lista_productos,
          bg="#6C6C6C", fg="white", font=("Arial", 12)).pack(pady=10)

log = tk.Text(root, width=60, height=10, font=("Arial", 10))
log.pack(pady=10)
log.insert(tk.END, "Productos agregados:\n")

root.mainloop()
