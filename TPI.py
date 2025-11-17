import datetime
import tkinter as tk
from tkinter import messagebox
import qrcode
from PIL import Image, ImageTk
import os

# ============================================
#   CARGAR PRODUCTOS DESDE EL TXT
# ============================================

def cargar_productos():
    """Lee los productos desde lista_de_productos.txt y devuelve un diccionario {nombre: precio}"""
    productos = {}
    try:
        with open("lista_de_productos.txt", "r", encoding="utf-8") as f:
            for linea in f:
                linea = linea.strip()
                if not linea or linea.startswith("-"):  # Ignora categorías y líneas vacías
                    continue
                if ":" in linea:
                    try:
                        nombre, precio = linea.split(":", 1)
                        nombre = nombre.strip().strip('"')
                        precio = float(precio.strip().rstrip(","))
                        productos[nombre] = precio
                    except:
                        continue
    except FileNotFoundError:
        print("❌ El archivo lista_de_productos.txt no existe.")
    return productos

PRODUCTOS = cargar_productos()

# ============================================
#   FUNCIONES DE BOLETA Y QR
# ============================================

BOLETAS_DIR = "boletas"
if not os.path.exists(BOLETAS_DIR):
    os.makedirs(BOLETAS_DIR)

def generar_contenido_boleta(cliente, productos, total, fecha):
    lineas = [
        f"Boleta para: {cliente}",
        f"Fecha: {fecha}",
        "\nProductos comprados:\n"
    ]
    for cantidad, producto in productos:
        precio = PRODUCTOS.get(producto, 0)
        subtotal = cantidad * precio
        lineas.append(f"{cantidad} x {producto} = ${subtotal:.2f}")
    lineas.append(f"\nTOTAL: ${total:.2f}")
    return "\n".join(lineas)

def obtener_nombre_boleta(cliente, fecha):
    fecha_formateada = fecha.replace(":", ";").replace("/", "-").replace(" ", "_")
    return f"{cliente}_{fecha_formateada}.txt"

def registrar_boleta(cliente, productos):
    fecha = datetime.datetime.now().strftime("%d/%m/%y %H:%M:%S")
    total = sum(cantidad * PRODUCTOS[prod] for cantidad, prod in productos)
    contenido = generar_contenido_boleta(cliente, productos, total, fecha)

    archivo = obtener_nombre_boleta(cliente, fecha)
    ruta_txt = os.path.join(BOLETAS_DIR, archivo)
    with open(ruta_txt, "w", encoding="utf-8") as f:
        f.write(contenido)

    # Generar QR
    qr = qrcode.make(contenido)
    qr_path = os.path.join(BOLETAS_DIR, f"QR_{archivo.replace('.txt', '')}.png")
    qr.save(qr_path)

    mostrar_ticket(contenido, ruta_txt, qr_path)

# ============================================
#   MOSTRAR TICKET Y QR
# ============================================

def mostrar_ticket(contenido, archivo, ruta_qr):
    v = tk.Toplevel()
    v.title("Ticket generado")
    v.geometry("550x600")

    tk.Label(v, text=f"Archivo generado: {os.path.basename(archivo)}", font=("Arial", 12, "bold")).pack(pady=5)

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
    producto = entry_producto.get().strip()

    if not cantidad.isdigit() or int(cantidad) <= 0:
        messagebox.showerror("Error", "Cantidad inválida")
        return

    if producto not in PRODUCTOS:
        messagebox.showerror("Error", f"El producto '{producto}' no existe en la lista.")
        return

    productos_agregados.append((int(cantidad), producto))
    log.insert(tk.END, f"{cantidad} x {producto}\n")

    entry_cantidad.delete(0, tk.END)
    entry_producto.delete(0, tk.END)

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
    log.delete(1.0, tk.END)
    log.insert(tk.END, "Productos agregados:\n")

def ver_lista_productos():
    v = tk.Toplevel()
    v.title("Lista de productos")
    tk.Label(v, text="Productos disponibles:", font=("Arial", 12)).pack()
    caja = tk.Text(v, width=50, height=20, font=("Arial", 10))
    caja.pack()
    if PRODUCTOS:
        for nombre, precio in PRODUCTOS.items():
            caja.insert(tk.END, f"{nombre}: ${precio}\n")
    else:
        caja.insert(tk.END, "El archivo está vacío o no se pudo leer.")

# ============================================
#   VENTANA PRINCIPAL
# ============================================

root = tk.Tk()
root.title("Sistema de Ventas")
root.geometry("450x550")

tk.Label(root, text="Nombre del Cliente:", font=("Arial", 12)).pack(pady=5)
entry_cliente = tk.Entry(root, font=("Arial", 12))
entry_cliente.pack(pady=5)

tk.Label(root, text="Cantidad:", font=("Arial", 12)).pack(pady=5)
entry_cantidad = tk.Entry(root, font=("Arial", 12))
entry_cantidad.pack(pady=5)

tk.Label(root, text="Producto:", font=("Arial", 12)).pack(pady=5)
entry_producto = tk.Entry(root, font=("Arial", 12))
entry_producto.pack(pady=5)

tk.Button(root, text="Agregar Producto", command=agregar_producto,
          bg="#0A84FF", fg="white", font=("Arial", 12)).pack(pady=10)

tk.Button(root, text="Finalizar Venta", command=finalizar_venta,
          bg="#4CAF50", fg="white", font=("Arial", 12)).pack(pady=10)

tk.Button(root, text="Ver Lista de Productos", command=ver_lista_productos,
          bg="#6C6C6C", fg="white", font=("Arial", 12)).pack(pady=10)

log = tk.Text(root, width=50, height=10, font=("Arial", 10))
log.pack(pady=10)
log.insert(tk.END, "Productos agregados:\n")

root.mainloop()
