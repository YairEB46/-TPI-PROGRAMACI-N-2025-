import datetime
import tkinter as tk
from tkinter import messagebox

# Datos de los productos en un archivo simulado
# productos.txt tendrá el formato: "producto,precio"
productos_disponibles = {
    "zba bco": 12.5,
    "la huerta 530g": 15.0,
    "Speed 500ml": 10.0,
    "dur 200ml": 5.0,
    "R2": 20.0,
    "361 1L": 25.0
}

# Función para obtener el número de boleta (por ejemplo, Boleta1, Boleta2...)
def obtener_numero_boleta(cliente, fecha):
    # Convertimos la fecha a un formato adecuado para el nombre de archivo
    fecha_formateada = fecha.replace(":", ";").replace("/", "-").replace(" ", "_")
    nombre_archivo = f"{cliente}_{fecha_formateada}.txt"
    return nombre_archivo

# Función para registrar una boleta
def registrar_boleta(cliente, productos_cliente, total):
    fecha = datetime.datetime.now().strftime("%d/%m/%y %H:%M:%S")
    
    # Generar el nombre del archivo
    boleta_nombre = obtener_numero_boleta(cliente, fecha)

    # Abrir el archivo y escribir la boleta
    with open(boleta_nombre, "w") as boleta:
        boleta.write(f"Boleta para {cliente}\n")
        boleta.write(f"Fecha y Hora: {fecha}\n")
        boleta.write(f"\nDetalles de la Venta:\n")
        
        for cantidad, producto in productos_cliente:
            precio = productos_disponibles[producto]
            boleta.write(f"{cantidad} x {producto} a ${precio:.2f} c/u => Total: ${cantidad * precio:.2f}\n")
        
        boleta.write(f"\nTOTAL: ${total:.2f}\n")

    # Mostrar la boleta en una ventana separada usando Tkinter
    ventana_boleta = tk.Tk()
    ventana_boleta.title(f"Boleta de Venta - {cliente}")
    ventana_boleta.geometry("400x400")  # Definimos el tamaño de la ventana

    ventana_boleta.config(bg="#858585")  # Cambiar el color de fondo de la ventana

    # Crear un widget de texto en la ventana para mostrar la boleta
    texto_boleta = tk.Text(ventana_boleta, width=40, height=15, bg="lightyellow", fg="black", font=("Arial", 10))
    texto_boleta.pack(pady=10)
    
    # Mostrar la información de la boleta en el widget de texto
    boleta_info = f"Boleta para {cliente}\n"
    boleta_info += f"Fecha y Hora: {fecha}\n"
    boleta_info += "\nDetalles de la Venta:\n"
    
    for cantidad, producto in productos_cliente:
        precio = productos_disponibles[producto]
        boleta_info += f"{cantidad} x {producto} a ${precio:.2f} c/u => Total: ${cantidad * precio:.2f}\n"
    
    boleta_info += f"\nTOTAL: ${total:.2f}"

    texto_boleta.insert(tk.END, boleta_info)
    
    # Deshabilitar edición del texto
    texto_boleta.config(state=tk.DISABLED)
    
    # Mostrar el nombre del archivo generado al final
    label = tk.Label(ventana_boleta, text=f"Archivo generado: {boleta_nombre}")
    label.pack(pady=10)

    # Mostrar la ventana
    ventana_boleta.mainloop()

# Función principal para gestionar el flujo
def realizar_venta():
    while True:
        # Datos del cliente
        cliente = input("Ingrese el nombre del cliente: ")

        # Almacenaremos los productos y cantidades del cliente
        productos_cliente = []
        total = 0

        while True:
            # Pedimos la cantidad y nombre del producto
            entrada = input("Ingrese la cantidad y el producto (formato 'cantidad:producto') o 'fin' para terminar: ")
            if entrada.lower() == "fin":
                break  # Si el cliente dice 'fin', terminamos de ingresar productos
            
            try:
                cantidad, producto = entrada.split(":")
                cantidad = int(cantidad)
                producto = producto.strip()  # Limpiamos espacios extra

                # Verificamos si el producto existe
                if producto not in productos_disponibles:
                    print(f"❌ Producto '{producto}' no encontrado.")
                    continue

                # Agregamos el producto y cantidad
                productos_cliente.append((cantidad, producto))

                # Calculamos el total
                total += cantidad * productos_disponibles[producto]

            except ValueError:
                print("❌ Error en el formato. Debe ser 'cantidad:producto' (ejemplo: 12: zba bco)")
        
        # Guardamos la boleta
        registrar_boleta(cliente, productos_cliente, total)

        # Preguntamos si se quiere hacer otra boleta
        otra_boleta = input("¿Desea hacer otra boleta? (si/no): ").strip().lower()
        if otra_boleta != "si":
            break  # Si no, salimos del bucle

# Llamamos a la función principal
if __name__ == "__main__":
    realizar_venta()