import datetime
import tkinter as tk
from tkinter import messagebox, ttk
from pathlib import Path
try:
    import qrcode
except Exception:
    qrcode = None
try:
    from PIL import Image, ImageTk
except Exception:
    Image = None
    ImageTk = None
import os   #Trabajar con archivos y directorios
import sys  #Rutas del intérprete
import subprocess   # Ejecuta programas externos desde python

def cargar_productos():
    """Carga los productos desde lista_de_productos.txt"""
    productos = {}
    try:
        with open("lista_de_productos.txt", "r", encoding="utf-8") as f:
            for linea in f:
                linea = linea.strip()
                # Saltar líneas vacías y categorías (que comienzan y terminan con -)
                if not linea or (linea.startswith("-") and linea.endswith("-")):
                    continue
                
                # Pasar línea formato: "Producto": precio,
                if "\"" in linea and ": " in linea:
                    try:
                        # Extraer el nombre del producto entre comillas
                        inicio = linea.index("\"")
                        fin = linea.index("\"", inicio + 1)
                        producto = linea[inicio + 1:fin]
                        
                        # Extraer el precio (después de ": " y antes de la coma)
                        precio_str = linea[fin + 2:].strip()
                        if precio_str.endswith(","):
                            precio_str = precio_str[:-1]
                        precio = float(precio_str.strip())
                        
                        productos[producto] = precio
                    except (ValueError, IndexError):
                        pass
    except FileNotFoundError:
        print("Error: No se encontró lista_de_productos.txt")
    return productos

PRODUCTOS_DISPONIBLES = cargar_productos()

# Directorio para guardar boletas
BOLETAS_DIR = Path("boletas")
BOLETAS_DIR.mkdir(exist_ok=True)

# Variable para almacenar la última boleta generada
ULTIMA_BOLETA = None


def abrir_archivo(ruta: Path):
    """Abrir un archivo con la aplicación por defecto del sistema."""
    try:
        if sys.platform.startswith('win'):
            os.startfile(str(ruta))
        elif sys.platform == 'darwin':
            subprocess.run(['open', str(ruta)])
        else:
            subprocess.run(['xdg-open', str(ruta)])
    except Exception as e:
        print(f"No se pudo abrir el archivo {ruta}: {e}")


def cargar_historial_clientes():
    #Carga la lista de clientes desde clientes.txt.
    clientes = []
    try:
        with open("clientes.txt", "r", encoding="utf-8") as f: # Se abre el archivo modo lectura y se leen bien los tildes y caracteres especiales.
            clientes = [linea.strip() for linea in f if linea.strip()] #Crea una lista de clientes sin listas vacías, se eliminan los espacios en los extremos.
    except FileNotFoundError:
        pass
    return clientes


def guardar_cliente(cliente: str):
    #Guarda un cliente nuevo en el historial (sin duplicados).
    if not cliente or not cliente.strip():
        return
    cliente = cliente.strip()
    clientes = cargar_historial_clientes()
    if cliente not in clientes:
        clientes.insert(0, cliente)  # Insertar al principio (más reciente)
        # Mantener solo últimos 20 clientes
        clientes = clientes[:20]
        try:
            with open("clientes.txt", "w", encoding="utf-8") as f:
                for c in clientes:
                    f.write(c + "\n")
        except Exception as e:
            print(f"No se pudo guardar cliente: {e}")


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

    # Guardar directamente en la carpeta boletas/
    ruta_boleta = BOLETAS_DIR / boleta_nombre
    try:
        with open(ruta_boleta, "w", encoding="utf-8") as boleta:
            boleta.write(contenido)
    except IOError as e:
        raise

    # Intentar generar un código QR con el contenido de la boleta
    try:
        # si la importación falló antes, intentar importar localmente (por si se instaló luego)
        qr_lib = qrcode
        if qr_lib is None:
            try:
                import qrcode as _qrcode
                qr_lib = _qrcode
            except Exception:
                qr_lib = None

        if qr_lib is not None:
            img = qr_lib.make(contenido)
            ruta_qr = ruta_boleta.with_suffix('.png')
            try:
                img.save(ruta_qr)
            except Exception as save_err:
                print(f"No se pudo guardar el QR: {save_err}")
    except Exception as e:
        print(f"No se generó el QR: {e}")

    # guardar última boleta para poder abrirla desde la UI (SIN abrir automáticamente)
    try:
        global ULTIMA_BOLETA
        ULTIMA_BOLETA = ruta_boleta
    except Exception:
        ULTIMA_BOLETA = None

    return boleta_nombre, contenido


class VentaApp:     
    def __init__(self, root):   
        self.root = root    #Guarda la ventana principal
        # Fuente global más grande para mejor legibilidad
        # Ajustado a tamaño mayor para visibilidad: 18pt
        root.option_add("*Font", "Arial 18")
        root.title("Sistema de Boletas - Ventana Única")
        root.geometry("1000x600")

        # Estilos para Treeview (encabezados y celdas)
        style = ttk.Style(root)
        # Tema más personalizable
        try:
            style.theme_use('clam')
        except Exception:
            pass

        # Treeview
        style.configure("Treeview.Heading", font=("Arial", 16, "bold"), foreground="#222")
        style.configure("Treeview", font=("Arial", 15), rowheight=30)

        # Botones y entradas
        style.configure('TButton', font=("Arial", 14), padding=6)
        style.configure('Primary.TButton', background='#4CAF50', foreground='white')
        style.map('Primary.TButton', background=[('active', '#45A049')])
        style.configure('Danger.TButton', background='#D9534F', foreground='white')
        style.map('Danger.TButton', background=[('active', '#C9302C')])

        style.configure('TEntry', font=("Arial", 16))
        # Estado de direcciones de ordenamiento por columna (True = asc, False = desc)
        self.sort_directions = {}

        self.cart = []  # lista de (cantidad, producto)

        # --- Cliente ---
        frame_cliente = tk.Frame(root)
        frame_cliente.pack(fill=tk.X, padx=10, pady=6)

        tk.Label(frame_cliente, text="Nombre del cliente:").pack(side=tk.LEFT)
        self.cliente_entry = ttk.Entry(frame_cliente)
        self.cliente_entry.pack(side=tk.LEFT, padx=6, fill=tk.X, expand=True)
        
        # Evento para actualizar QR cuando cambie el cliente
        self.cliente_entry.bind('<KeyRelease>', lambda e: self.actualizar_vista_qr())
        
        # Cargar historial de clientes para autocomplete
        self.historial_clientes = cargar_historial_clientes()

        # --- Selección de producto ---
        frame_producto = tk.Frame(root)
        frame_producto.pack(fill=tk.X, padx=10, pady=6)

        tk.Label(frame_producto, text="Producto:").pack(side=tk.LEFT)
        productos = list(PRODUCTOS_DISPONIBLES.keys())
        self.producto_cb = ttk.Combobox(frame_producto, values=productos, state="readonly")
        if productos:
            self.producto_cb.set(productos[0])
        self.producto_cb.pack(side=tk.LEFT, padx=6)

        # Mostrar precio unitario del producto seleccionado antes de agregar
        self.precio_var = tk.StringVar(value="P. Unitario: -")
        self.label_precio = tk.Label(frame_producto, textvariable=self.precio_var)
        self.label_precio.pack(side=tk.LEFT, padx=(10, 0))

        # Actualizar precio al cambiar selección
        self.producto_cb.bind('<<ComboboxSelected>>', self.mostrar_precio_seleccionado)
        # inicializar precio si hay productos
        if productos:
            precio_inicial = PRODUCTOS_DISPONIBLES.get(productos[0], 0)
            self.precio_var.set(f"P. Unitario: ${precio_inicial:.2f}")

        tk.Label(frame_producto, text="Cantidad:").pack(side=tk.LEFT, padx=(10, 0))
        self.cantidad_entry = ttk.Entry(frame_producto, width=6)
        self.cantidad_entry.insert(0, "1")
        self.cantidad_entry.pack(side=tk.LEFT, padx=6)

        self.btn_agregar = ttk.Button(frame_producto, text="Agregar", command=self.agregar_producto)
        self.btn_agregar.pack(side=tk.LEFT, padx=6)

        # --- Area de carrito / boleta (Treeview con columnas) ---
        frame_principal = tk.Frame(root)
        frame_principal.pack(fill=tk.BOTH, expand=True, padx=10, pady=6)

        cols = ("producto", "cantidad", "precio", "subtotal")
        self.tree = ttk.Treeview(frame_principal, columns=cols, show="headings", selectmode="browse")
        # Encabezados clicables: permiten ordenar el carrito usando ordenamiento por selección
        self.tree.heading("producto", text="Producto", command=lambda: self.on_header_click("producto"))
        self.tree.heading("cantidad", text="Cantidad", command=lambda: self.on_header_click("cantidad"))
        self.tree.heading("precio", text="P. Unitario", command=lambda: self.on_header_click("precio"))
        self.tree.heading("subtotal", text="Subtotal", command=lambda: self.on_header_click("subtotal"))
        self.tree.column("producto", width=300)
        self.tree.column("cantidad", width=80, anchor=tk.CENTER)
        self.tree.column("precio", width=100, anchor=tk.E)
        self.tree.column("subtotal", width=100, anchor=tk.E)

        vsb = ttk.Scrollbar(frame_principal, orient=tk.VERTICAL, command=self.tree.yview)
        self.tree.configure(yscroll=vsb.set)
        self.tree.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        vsb.pack(side=tk.LEFT, fill=tk.Y)

        # Panel derecho con total, QR y acciones
        frame_derecha = tk.Frame(frame_principal)
        frame_derecha.pack(side=tk.LEFT, fill=tk.Y, padx=8)

        tk.Label(frame_derecha, text="Resumen").pack(pady=(0, 8))
        # Total con fuente aún más visible
        self.label_total = tk.Label(frame_derecha, text="TOTAL: $0.00", font=("Arial", 24, "bold"))
        self.label_total.pack(pady=4)

        # Panel para mostrar código QR
        tk.Label(frame_derecha, text="Vista previa QR", font=("Arial", 9, "bold")).pack(pady=(10, 5))
        
        self.frame_qr = tk.Frame(frame_derecha, bg="white", width=200, height=200, relief=tk.SUNKEN, bd=2)
        self.frame_qr.pack(pady=5, fill=tk.BOTH, expand=False)
        self.frame_qr.pack_propagate(False)
        
        self.label_qr = tk.Label(self.frame_qr, bg="white", text="El QR aparecerá\naquí cuando\nguardes", 
                                 font=("Arial", 9), fg="#999")
        self.label_qr.pack(expand=True)
        
        # Referencia para mantener imagen en memoria
        self.qr_photo = None

        # Botones con estilos ttk
        self.btn_guardar = ttk.Button(frame_derecha, text="Guardar boleta", style='Primary.TButton', command=self.guardar_boleta)
        self.btn_guardar.pack(pady=8, fill=tk.X)

        # Botón de mostrar boleta (abrir .txt y .png) y deshacer eliminación
        self.btn_mostrar = ttk.Button(frame_derecha, text="Mostrar boleta", command=self.mostrar_boleta)
        self.btn_mostrar.pack(pady=4, fill=tk.X)

        # Botón para abrir carpeta de boletas del día actual
        self.btn_abrir_carpeta = ttk.Button(frame_derecha, text="Abrir carpeta", command=self.abrir_carpeta_boletas)
        self.btn_abrir_carpeta.pack(pady=4, fill=tk.X)

        self.btn_deshacer = ttk.Button(frame_derecha, text="Deshacer eliminación", command=self.deshacer_eliminacion)
        self.btn_deshacer.pack(pady=4, fill=tk.X)

        # Botón de eliminar con estilo Danger
        self.btn_eliminar = ttk.Button(frame_derecha, text="Eliminar seleccionado", style='Danger.TButton', command=self.eliminar_seleccionado)
        self.btn_eliminar.pack(pady=4, fill=tk.X)

        self.btn_limpiar = ttk.Button(frame_derecha, text="Limpiar carrito", command=self.limpiar_carrito)
        self.btn_limpiar.pack(pady=4, fill=tk.X)


        # Estado para deshacer
        self.ultimo_borrado = []

        # Atajos de teclado
        root.bind('<Control-s>', lambda e: self.guardar_boleta())
        root.bind('<Delete>', lambda e: self.eliminar_seleccionado())
        root.bind('<Control-n>', lambda e: self.limpiar_carrito())

        # Inicializar visual
        self.actualizar_vista()

    def agregar_producto(self):
        producto = self.producto_cb.get()
        try:
            cantidad = int(self.cantidad_entry.get())   #Convierte lo que el usuario ingresa a entero
        except ValueError:
            messagebox.showerror("Error", "La cantidad debe ser un número entero.")
            return

        if cantidad <= 0:
            messagebox.showerror("Error", "La cantidad debe ser mayor que 0.")
            return

        if producto not in PRODUCTOS_DISPONIBLES:
            messagebox.showerror("Error", f"Producto '{producto}' no está disponible.")
            return

        precio = PRODUCTOS_DISPONIBLES[producto]

        # Buscar si el producto ya existe en el carrito
        producto_encontrado = False
        for i, (item_id, cant, prod) in enumerate(self.cart):
            if prod == producto:
                # Sumar la cantidad al producto existente
                nueva_cantidad = cant + cantidad
                subtotal = nueva_cantidad * precio
                
                # Actualizar el treeview
                self.tree.item(item_id, values=(producto, nueva_cantidad, f"${precio:.2f}", f"${subtotal:.2f}"))
                
                # Actualizar el carrito
                self.cart[i] = (item_id, nueva_cantidad, prod)
                producto_encontrado = True
                break
        
        if not producto_encontrado:
            # Si no existe, agregarlo como nuevo
            subtotal = cantidad * precio
            item_id = self.tree.insert("", "end", values=(producto, cantidad, f"${precio:.2f}", f"${subtotal:.2f}"))
            self.cart.append((item_id, cantidad, producto))
        
        self.cantidad_entry.delete(0, tk.END)
        self.cantidad_entry.insert(0, "1")
        self.actualizar_vista()

    def mostrar_precio_seleccionado(self, event=None):
        producto = self.producto_cb.get()
        precio = PRODUCTOS_DISPONIBLES.get(producto)
        if precio is None:
            self.precio_var.set("P. Unitario: -")
        else:
            self.precio_var.set(f"P. Unitario: ${precio:.2f}")

    def actualizar_vista(self):
        # recalcular total desde los elementos del treeview (o desde self.cart)
        total = 0
        for _id, cantidad, producto in self.cart:
            precio = PRODUCTOS_DISPONIBLES.get(producto, 0)
            total += cantidad * precio

        self.label_total.config(text=f"TOTAL: ${total:.2f}")
        
        # Actualizar vista previa del QR con el contenido actual
        self.actualizar_vista_qr()

    def actualizar_vista_qr(self):
        """Actualiza la vista previa del QR en la interfaz principal."""
        cliente = self.cliente_entry.get().strip()
        
        # Si no hay cliente o no hay productos, mostrar mensaje
        if not cliente or not self.cart:
            self.label_qr.config(image='', text="El QR aparecerá\naquí cuando\nguardes", fg="#999")
            self.qr_photo = None
            return
        
        # Generar contenido de boleta actual
        try:
            productos_para_qr = [(cantidad, producto) for _id, cantidad, prod in self.cart for producto in [prod]]
            total = sum(cantidad * PRODUCTOS_DISPONIBLES[producto] for cantidad, producto in productos_para_qr)
            fecha = datetime.datetime.now().strftime("%d/%m/%y %H:%M:%S")
            contenido = generar_contenido_boleta(cliente, productos_para_qr, total, fecha)
            
            # Generar código QR
            if qrcode is not None:
                qr = qrcode.make(contenido)
                # Redimensionar a 190x190 para que quepa en el frame
                qr_img = qr.resize((190, 190))
                
                # Convertir a PhotoImage
                if Image and ImageTk:
                    qr_photo = ImageTk.PhotoImage(qr_img)
                    self.label_qr.config(image=qr_photo, text="")
                    self.qr_photo = qr_photo  # Mantener referencia
        except Exception as e:
            self.label_qr.config(image='', text="Error al\ngenerar QR", fg="#999")
            self.qr_photo = None

    def on_header_click(self, col):
        """Ordena el carrito por la columna seleccionada usando ordenamiento por selección.
        Alterna la dirección en cada click (ascendente/descendente).
        """
        # obtener dirección actual (True = ascendente)
        asc = self.sort_directions.get(col, True)

        # construir lista de entradas (cantidad, producto)
        entradas = [(cantidad, product) for _id, cantidad, product in self.cart]

        def key_func(entr):    #Se usa la función como clave de ordenamiento
            cantidad, producto = entr
            if col == "producto":
                return str(producto).lower()
            elif col == "cantidad":
                try:
                    return int(cantidad)
                except Exception:
                    try:
                        return int(float(cantidad))
                    except Exception:
                        return 0
            elif col == "precio":
                return PRODUCTOS_DISPONIBLES.get(producto, 0)
            elif col == "subtotal":
                return cantidad * PRODUCTOS_DISPONIBLES.get(producto, 0)
            return 0

        # selection sort sobre la lista 
        n = len(entradas)
        for i in range(n):
            sel = i
            for j in range(i + 1, n):
                a = key_func(entradas[j])
                b = key_func(entradas[sel])
                if asc:
                    if a < b:
                        sel = j
                else:
                    if a > b:
                        sel = j
            if sel != i:
                entradas[i], entradas[sel] = entradas[sel], entradas[i]

        # alternar dirección para el próximo click
        self.sort_directions[col] = not asc

        # reconstruir el Treeview y self.cart en el nuevo orden
        for it in self.tree.get_children():
            self.tree.delete(it)
        self.cart = []
        for cantidad, producto in entradas:
            precio = PRODUCTOS_DISPONIBLES.get(producto, 0)
            subtotal = cantidad * precio
            item_id = self.tree.insert("", "end", values=(producto, cantidad, f"${precio:.2f}", f"${subtotal:.2f}"))
            self.cart.append((item_id, cantidad, producto))
        self.actualizar_vista()

    def guardar_boleta(self):
        cliente = self.cliente_entry.get().strip()
        if not cliente:
            messagebox.showerror("Error", "Ingrese el nombre del cliente.")
            return
        
        # Validar que el nombre contenga solo letras y espacios
        if not all(c.isalpha() or c.isspace() for c in cliente):
            messagebox.showerror("Error", "El nombre del cliente debe contener solo letras y espacios.")
            return

        if not self.cart:
            messagebox.showerror("Error", "No hay productos en el carrito.")
            return

        # calcular total desde self.cart y preparar lista de productos (cantidad, producto)
        productos_para_guardar = [(cantidad, producto) for _id, cantidad, product in self.cart for producto in [product]]
        total = sum(cantidad * PRODUCTOS_DISPONIBLES[producto] for cantidad, producto in productos_para_guardar)
        try:
            boleta_nombre, contenido = registrar_boleta(cliente, productos_para_guardar, total)
        except Exception as e:
            messagebox.showerror("Error", f"No se pudo guardar la boleta: {e}")
            return

        # Guardar cliente en historial
        guardar_cliente(cliente)

        # mostrar ruta completa en el mensaje
        ruta_relativa = ""
        if ULTIMA_BOLETA:
            try:
                ruta_relativa = str(ULTIMA_BOLETA.relative_to(Path.cwd()))
            except Exception:
                ruta_relativa = str(ULTIMA_BOLETA)
        
        msg = f"Boleta guardada como:\n{boleta_nombre}\n\nRuta: {ruta_relativa}"
        messagebox.showinfo("Boleta guardada", msg)
        
        # Limpiar carrito
        self.limpiar_carrito()

    def limpiar_carrito(self):
        # limpiar nombre del cliente
        self.cliente_entry.delete(0, tk.END)
        
        # limpiar treeview y carrito
        for item in self.tree.get_children():
            self.tree.delete(item)
        self.cart = []
        self.actualizar_vista()

    def eliminar_seleccionado(self):
        sel = self.tree.selection()
        if not sel:
            messagebox.showerror("Error", "No hay ningún item seleccionado.")
            return

        # confirmación
        if not messagebox.askyesno("Confirmar", "¿Eliminar los items seleccionados?"):
            return

        borrado = []
        for item_id in sel:
            try:
                vals = self.tree.item(item_id, 'values')
                # guardar valores para deshacer: (values)
                borrado.append((vals, item_id))
                self.tree.delete(item_id)
            except Exception:
                pass
            # borrar del carrito por item id
            self.cart = [entry for entry in self.cart if entry[0] != item_id]

        # almacenar para posible deshacer (solo los valores)
        if borrado:
            # almacenar solo la lista de valores
            self.ultimo_borrado.append([v for v, _id in borrado])

        self.actualizar_vista()

    def deshacer_eliminacion(self):
        if not self.ultimo_borrado:
            messagebox.showinfo("Deshacer", "No hay acciones para deshacer.")
            return
        items = self.ultimo_borrado.pop()
        # items es una lista de tuplas val
        for vals in items:
            #  (producto, cantidad, precio_str, subtotal_str)
            producto, cantidad, precio_str, subtotal_str = vals
            try:
                cantidad_int = int(cantidad)
            except Exception:
                try:
                    cantidad_int = int(float(cantidad))
                except Exception:
                    cantidad_int = 1
            item_id = self.tree.insert("", "end", values=(producto, cantidad_int, precio_str, subtotal_str))
            self.cart.append((item_id, cantidad_int, producto))
        self.actualizar_vista()

    def mostrar_boleta(self):
        # Mostrar la boleta y el código QR en una ventana
        global ULTIMA_BOLETA
        if ULTIMA_BOLETA and ULTIMA_BOLETA.exists():
            # Crear ventana emergente
            ventana_boleta = tk.Toplevel(self.root)
            ventana_boleta.title("Boleta y Código QR")
            ventana_boleta.geometry("800x700")
            
            try:
                ruta_rel = str(ULTIMA_BOLETA.relative_to(Path.cwd()))
            except Exception:
                ruta_rel = str(ULTIMA_BOLETA)
            
            # Título con la ruta de la boleta
            tk.Label(ventana_boleta, text=f"Boleta: {ULTIMA_BOLETA.name}", 
                    font=("Arial", 12, "bold")).pack(pady=5)
            
            # Frame principal para dividir en dos partes
            frame_principal = tk.Frame(ventana_boleta)
            frame_principal.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
            
            # Frame izquierda: contenido de la boleta
            frame_izq = tk.Frame(frame_principal)
            frame_izq.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=(0, 5))
            
            tk.Label(frame_izq, text="Contenido de la Boleta", font=("Arial", 10, "bold")).pack()
            
            caja_boleta = tk.Text(frame_izq, width=40, height=30, font=("Courier", 9))
            caja_boleta.pack(fill=tk.BOTH, expand=True, pady=5)
            
            # Cargar contenido de la boleta
            try:
                with open(ULTIMA_BOLETA, "r", encoding="utf-8") as f:
                    contenido = f.read()
                    caja_boleta.insert(tk.END, contenido)
            except Exception as e:
                caja_boleta.insert(tk.END, f"Error al leer boleta: {e}")
            
            caja_boleta.config(state=tk.DISABLED)
            
            # Frame derecha: código QR
            frame_der = tk.Frame(frame_principal)
            frame_der.pack(side=tk.RIGHT, fill=tk.BOTH, expand=True, padx=(5, 0))
            
            tk.Label(frame_der, text="Código QR", font=("Arial", 10, "bold")).pack()
            
            # Intenta mostrar el código QR
            ruta_qr = ULTIMA_BOLETA.with_suffix('.png')
            if ruta_qr.exists() and Image and ImageTk:
                try:
                    img = Image.open(ruta_qr).resize((350, 350))
                    qr_img = ImageTk.PhotoImage(img)
                    
                    etiqueta_qr = tk.Label(frame_der, image=qr_img)
                    etiqueta_qr.image = qr_img  # Mantener referencia
                    etiqueta_qr.pack(pady=10)
                except Exception as e:
                    tk.Label(frame_der, text=f"No se pudo cargar QR: {e}").pack(pady=10)
            else:
                tk.Label(frame_der, text="Código QR no disponible").pack(pady=10)
            
            # Botones
            frame_botones = tk.Frame(ventana_boleta)
            frame_botones.pack(fill=tk.X, padx=10, pady=5)
            
            tk.Button(frame_botones, text="Abrir archivo", 
                     command=lambda: abrir_archivo(ULTIMA_BOLETA),
                     bg="#4CAF50", fg="white").pack(side=tk.LEFT, padx=5)
            
            tk.Button(frame_botones, text="Cerrar", 
                     command=ventana_boleta.destroy,
                     bg="#808080", fg="white").pack(side=tk.LEFT, padx=5)
        else:
            messagebox.showinfo("Mostrar boleta", "No hay boleta reciente para mostrar.")

    def abrir_carpeta_boletas(self):
        """Abre la carpeta de boletas en el Explorador."""
        if BOLETAS_DIR.exists():
            try:
                abrir_archivo(BOLETAS_DIR)
            except Exception as e:
                messagebox.showerror("Error", f"No se pudo abrir la carpeta: {e}")
        else:
            messagebox.showinfo("Carpeta de boletas", 
                              f"La carpeta no existe aún.\nSe creará cuando guardes la primera boleta en:\n{BOLETAS_DIR}")

if __name__ == "__main__":
    root = tk.Tk()
    app = VentaApp(root)
    root.mainloop()
