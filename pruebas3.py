import datetime
import tkinter as tk
import qrcode
from tkinter import messagebox
from pathlib import Path
from productos_data import PRODUCTOS_DISPONIBLES
from PIL import Image, ImageTk


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
    """Registra y muestra la boleta."""
    fecha = datetime.datetime.now().strftime("%d/%m/%y %H:%M:%S")
    boleta_nombre = obtener_nombre_boleta(cliente, fecha)
    contenido = generar_contenido_boleta(cliente, productos_cliente, total, fecha)

    # Guardar boleta en archivo
    ruta_boleta = BOLETAS_DIR / boleta_nombre
    try:
        with open(ruta_boleta, "w", encoding="utf-8") as boleta:
            boleta.write(contenido)
    except IOError as e:
        messagebox.showerror("Error", f"No se pudo guardar la boleta: {e}")
        return

    # === Generar código QR único por boleta ===
    qr_img = qrcode.make(contenido)
    qr_path = BOLETAS_DIR / f"QR_{boleta_nombre.replace('.txt', '')}.png"
    qr_img.save(qr_path)

    # Mostrar boleta y QR en ventana
    mostrar_boleta_ventana(cliente, contenido, boleta_nombre, qr_path)


def mostrar_boleta_ventana(cliente, contenido, boleta_nombre, qr_path):
    """Muestra la boleta en una ventana Tkinter."""
    ventana_boleta = tk.Tk()
    ventana_boleta.title(f"Boleta de Venta - {cliente}")
    ventana_boleta.geometry("520x560")
    ventana_boleta.config(bg="#858585")

    # Texto de la boleta
    texto_boleta = tk.Text(
        ventana_boleta,
        width=50,
        height=20,
        bg="lightyellow",
        fg="black",
        font=("Arial", 10)
    )
    texto_boleta.pack(pady=10, padx=10, fill=tk.BOTH, expand=True)
    texto_boleta.insert(tk.END, contenido)
    texto_boleta.config(state=tk.DISABLED)

    # Información del archivo
    frame_info = tk.Frame(ventana_boleta, bg="#858585")
    frame_info.pack(pady=5)

    label = tk.Label(
        frame_info,
        text=f"Archivo: {boleta_nombre}",
        bg="#858585",
        fg="white",
        font=("Arial", 9)
    )
    label.pack()

    # === Mostrar QR ===
    qr_img = Image.open(qr_path)
    qr_img = qr_img.resize((180, 180))
    qr_tk = ImageTk.PhotoImage(qr_img)

    label_qr = tk.Label(ventana_boleta, image=qr_tk, bg="#858585")
    label_qr.image = qr_tk  # evitar que Python lo limpie
    label_qr.pack(pady=10)

    # Botón cerrar
    btn_cerrar = tk.Button(
        ventana_boleta,
        text="Cerrar",
        command=ventana_boleta.quit,
        bg="#4CAF50",
        fg="white",
        font=("Arial", 10)
    )
    btn_cerrar.pack(pady=10)

    ventana_boleta.mainloop()


def validar_entrada_producto(entrada):
    """Valida y procesa la entrada del producto."""
    try:
        partes = entrada.split(":")
        if len(partes) != 2:
            raise ValueError("Formato incorrecto")

        cantidad_str, producto = partes
        cantidad = int(cantidad_str.strip())
        producto = producto.strip()

        if cantidad <= 0:
            raise ValueError("La cantidad debe ser mayor a 0")

        if producto not in PRODUCTOS_DISPONIBLES:
            raise ValueError(f"Producto '{producto}' no encontrado")

        return cantidad, producto

    except ValueError as e:
        return None, str(e)


def realizar_venta():
    """Gestiona el flujo de ventas."""
    while True:
        cliente = input("\nIngrese el nombre del cliente (o 'salir' para terminar): ").strip()

        if cliente.lower() == "salir":
            print("¡Hasta luego!")
            break

        if not cliente:
            print("❌ El nombre del cliente no puede estar vacío.")
            continue

        productos_cliente = []
        total = 0

        print("\nIngrese productos (formato: 'cantidad:producto' o 'fin' para terminar)")
        print("Productos disponibles:")
        for producto in PRODUCTOS_DISPONIBLES.keys():
            print(f"  - {producto}")

        while True:
            entrada = input("\nCantidad:Producto (o 'fin'): ").strip()

            if entrada.lower() == "fin":
                break

            if not entrada:
                print("❌ Entrada vacía. Intente de nuevo.")
                continue

            cantidad, producto = validar_entrada_producto(entrada)

            if cantidad is None:
                print(f"❌ Error: {producto}")
                continue

            productos_cliente.append((cantidad, producto))
            subtotal = cantidad * PRODUCTOS_DISPONIBLES[producto]
            total += subtotal
            print(f"✓ Agregado: {cantidad}x {producto} = ${subtotal:.2f}")

        if not productos_cliente:
            print("❌ No se agregaron productos. Intente nuevamente.")
            continue

        print(f"\n💰 Total de la venta: ${total:.2f}")
        registrar_boleta(cliente, productos_cliente, total)

        otra_boleta = input("\n¿Desea hacer otra boleta? (si/no): ").strip().lower()
        if otra_boleta not in ["si", "s"]:
            break


if __name__ == "__main__":
    realizar_venta()