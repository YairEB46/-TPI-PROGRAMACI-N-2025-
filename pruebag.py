import datetime
import tkinter as tk
from tkinter import messagebox, ttk
from pathlib import Path
from productos_data import PRODUCTOS_DISPONIBLES

# Directorio para guardar boletas
BOLETAS_DIR = Path("boletas")
BOLETAS_DIR.mkdir(exist_ok=True)


def generar_contenido_boleta(cliente, productos_cliente, total, fecha):
    """Genera el contenido de la boleta para reutilizar en archivo y GUI."""
    lineas = [
        f"Boleta para {cliente}",
        f"Fecha y Hora: {fecha}",
        "\nDetalles de la Venta:\n"
    ]

    for cantidad, producto in productos_cliente:
        precio = PRODUCTOS_DISPONIBLES[producto]
        subtotal = cantidad * precio
        lineas.append(f"{cantidad} x {producto} a ${precio:.2f} c/u => Total: ${subtotal:.2f}")

    lineas.append(f"\nTOTAL: ${total:.2f}")
    return "\n".join(lineas)


def obtener_nombre_boleta(cliente, fecha):
    """Genera el nombre del archivo de boleta."""
    fecha_formateada = fecha.replace(":", ";").replace("/", "-").replace(" ", "_")
    return f"{cliente}_{fecha_formateada}.txt"


def registrar_boleta(cliente, productos_cliente, total):
    """Guarda la boleta en disco y devuelve el nombre y contenido."""
    fecha = datetime.datetime.now().strftime("%d/%m/%y %H:%M:%S")
    boleta_nombre = obtener_nombre_boleta(cliente, fecha)
    contenido = generar_contenido_boleta(cliente, productos_cliente, total, fecha)

    ruta_boleta = BOLETAS_DIR / boleta_nombre
    try:
        with open(ruta_boleta, "w", encoding="utf-8") as boleta:
            boleta.write(contenido)
    except IOError as e:
        raise

    return boleta_nombre, contenido


class VentaApp:
    def __init__(self, root):
        self.root = root
        root.title("Sistema de Boletas - Ventana Única")
        root.geometry("700x500")

        self.cart = []  # lista de (cantidad, producto)

        # --- Cliente ---
        frame_cliente = tk.Frame(root)
        frame_cliente.pack(fill=tk.X, padx=10, pady=6)

        tk.Label(frame_cliente, text="Nombre del cliente:").pack(side=tk.LEFT)
        self.cliente_entry = tk.Entry(frame_cliente)
        self.cliente_entry.pack(side=tk.LEFT, padx=6, fill=tk.X, expand=True)

        # --- Selección de producto ---
        frame_producto = tk.Frame(root)
        frame_producto.pack(fill=tk.X, padx=10, pady=6)

        tk.Label(frame_producto, text="Producto:").pack(side=tk.LEFT)
        productos = list(PRODUCTOS_DISPONIBLES.keys())
        self.producto_cb = ttk.Combobox(frame_producto, values=productos, state="readonly")
        if productos:
            self.producto_cb.set(productos[0])
        self.producto_cb.pack(side=tk.LEFT, padx=6)

        tk.Label(frame_producto, text="Cantidad:").pack(side=tk.LEFT, padx=(10, 0))
        self.cantidad_entry = tk.Entry(frame_producto, width=6)
        self.cantidad_entry.insert(0, "1")
        self.cantidad_entry.pack(side=tk.LEFT, padx=6)

        self.btn_agregar = tk.Button(frame_producto, text="Agregar", command=self.agregar_producto)
        self.btn_agregar.pack(side=tk.LEFT, padx=6)

        # --- Area de carrito / boleta ---
        frame_principal = tk.Frame(root)
        frame_principal.pack(fill=tk.BOTH, expand=True, padx=10, pady=6)

        self.text_boleta = tk.Text(frame_principal, bg="lightyellow", font=("Arial", 11))
        self.text_boleta.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        self.text_boleta.config(state=tk.DISABLED)

        # Panel derecho con total y acciones
        frame_derecha = tk.Frame(frame_principal)
        frame_derecha.pack(side=tk.LEFT, fill=tk.Y, padx=8)

        tk.Label(frame_derecha, text="Resumen").pack(pady=(0, 8))
        self.label_total = tk.Label(frame_derecha, text="TOTAL: $0.00", font=("Arial", 12, "bold"))
        self.label_total.pack(pady=4)

        self.btn_guardar = tk.Button(frame_derecha, text="Guardar boleta", bg="#4CAF50", fg="white", command=self.guardar_boleta)
        self.btn_guardar.pack(pady=8, fill=tk.X)

        self.btn_limpiar = tk.Button(frame_derecha, text="Limpiar carrito", command=self.limpiar_carrito)
        self.btn_limpiar.pack(pady=4, fill=tk.X)

        # Inicializar visual
        self.actualizar_vista()

    def agregar_producto(self):
        producto = self.producto_cb.get()
        try:
            cantidad = int(self.cantidad_entry.get())
        except ValueError:
            messagebox.showerror("Error", "La cantidad debe ser un número entero.")
            return

        if cantidad <= 0:
            messagebox.showerror("Error", "La cantidad debe ser mayor que 0.")
            return

        if producto not in PRODUCTOS_DISPONIBLES:
            messagebox.showerror("Error", f"Producto '{producto}' no está disponible.")
            return

        self.cart.append((cantidad, producto))
        self.cantidad_entry.delete(0, tk.END)
        self.cantidad_entry.insert(0, "1")
        self.actualizar_vista()

    def actualizar_vista(self):
        total = 0
        contenido = []
        for cantidad, producto in self.cart:
            precio = PRODUCTOS_DISPONIBLES[producto]
            subtotal = cantidad * precio
            contenido.append(f"{cantidad} x {producto} a ${precio:.2f} = ${subtotal:.2f}")
            total += subtotal

        self.text_boleta.config(state=tk.NORMAL)
        self.text_boleta.delete("1.0", tk.END)
        if contenido:
            self.text_boleta.insert(tk.END, "\n".join(contenido) + "\n")
        else:
            self.text_boleta.insert(tk.END, "(Carrito vacío)\n")
        self.text_boleta.config(state=tk.DISABLED)

        self.label_total.config(text=f"TOTAL: ${total:.2f}")

    def guardar_boleta(self):
        cliente = self.cliente_entry.get().strip()
        if not cliente:
            messagebox.showerror("Error", "Ingrese el nombre del cliente.")
            return

        if not self.cart:
            messagebox.showerror("Error", "No hay productos en el carrito.")
            return

        # calcular total
        total = sum(cantidad * PRODUCTOS_DISPONIBLES[producto] for cantidad, producto in self.cart)
        try:
            boleta_nombre, contenido = registrar_boleta(cliente, self.cart, total)
        except Exception as e:
            messagebox.showerror("Error", f"No se pudo guardar la boleta: {e}")
            return

        messagebox.showinfo("Boleta guardada", f"Boleta guardada como: {boleta_nombre}")
        self.limpiar_carrito()

    def limpiar_carrito(self):
        self.cart = []
        self.actualizar_vista()


if __name__ == "__main__":
    root = tk.Tk()
    app = VentaApp(root)
    root.mainloop()
