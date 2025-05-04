import heapq
import tkinter as tk
from tkinter import ttk, messagebox
import networkx as nx
import matplotlib.pyplot as plt
import matplotlib.patches as mpatches

class Grafo:
    def __init__(self):
        self.vertices = {}
        self.categorias = {}  # NUEVO

    def agregar_vertice(self, nombre, categoria=None):
        if nombre not in self.vertices:
            self.vertices[nombre] = {}
        if categoria:
            self.categorias[nombre] = categoria

    def agregar_arista(self, origen, destino, distancia):
        self.vertices[origen][destino] = distancia
        self.vertices[destino][origen] = distancia

    def obtener_vertices(self):
        return list(self.vertices.keys())

    def dijkstra(self, inicio, fin):
        distancias = {vertice: float('inf') for vertice in self.vertices} # Inicializa todas las distancias a infinito
        distancias[inicio] = 0
        prioridad = [(0, inicio)]
        camino = {} #Diccionario para reconstruir el camino más corto

        while prioridad:# Mientras haya nodos por visitar
            distancia_actual, vertice_actual = heapq.heappop(prioridad) # Saca el nodo con la menor distancia actual
           
            if distancia_actual > distancias[vertice_actual]: # Si la distancia es mayor que la ya registrada, se ignora
                continue

            for vecino, peso in self.vertices[vertice_actual].items():# Recorre todos los vecinos del nodo actual
                distancia = distancia_actual + peso #cal nueva distancia origen
                if distancia < distancias[vecino]:# Si la nueva distancia es menor, se actualiza
                    distancias[vecino] = distancia# Actualiza la mejor distancia
                    camino[vecino] = vertice_actual # Guarda el camino anterior
                    heapq.heappush(prioridad, (distancia, vecino)) # Añade a la cola


        # Reconstruye la ruta más corta desde el destino hacia el inicio
        ruta = []
        actual = fin
        while actual != inicio:
            ruta.append(actual)
            actual = camino.get(actual)
            if actual is None:
                return None, float('inf')
        ruta.append(inicio)# Nodo inicio y revierte la lista para mostrar de inicio a fin
        ruta.reverse()
        return ruta, distancias[fin]

def dibujar_grafo(grafo, ruta=None, origen=None, destino=None):
    G = nx.Graph()

    # Crear los nodos y aristas a partir del diccionario de vértices
    for orig in grafo.vertices:
        for dest, distancia in grafo.vertices[orig].items():
            G.add_edge(orig, dest, weight=distancia)

    # Posiciones fijas para reproducibilidad
    pos = nx.spring_layout(G, seed=42)

    # Colores por categoría (se mantienen internamente pero no en la leyenda)
    categoria_colores = {
        "Escolar": "#EE8E27",               # Naranja
        "Escolar/Recreativo": "#30E0D5",    # Azul claro
        "Recreativo": "#42A5F5",            # Azul
        "Estacionamiento": "#BDBDBD",       # Gris
        "Servicio": "#F44932"               # Rojo
    }

    colores_nodos = []
    for nodo in G.nodes():
        if nodo == origen:
            colores_nodos.append('#00FF00')  # origen: verde brillante
        elif nodo == destino:
            colores_nodos.append('#FF0000')  # destino: rojo brillante
        else:
            categoria = grafo.categorias.get(nodo, "Servicio")
            colores_nodos.append(categoria_colores.get(categoria, "#90CAF9"))

    # Crear figura y ejes
    fig, ax = plt.subplots(figsize=(10, 7))
    ax.set_title("Sistema de Rutas UDLAP", fontsize=16, weight='bold')
    plt.axis('off')

    # Dibujar nodos y aristas
    nx.draw_networkx_nodes(G, pos, node_color=colores_nodos, node_size=700, ax=ax)
    nx.draw_networkx_edges(G, pos, width=2, ax=ax, edge_color='#888888')

    # Dibujar ruta si se especifica
    if ruta:
        ruta_edges = list(zip(ruta, ruta[1:]))
        
        # Dibujar borde blanco para hacer la ruta más visible
        nx.draw_networkx_edges(G, pos, edgelist=ruta_edges, width=8, 
                             edge_color='white', ax=ax, alpha=0.7)
        # Dibujar ruta principal
        nx.draw_networkx_edges(G, pos, edgelist=ruta_edges, width=6, 
                             edge_color='#FF5722', ax=ax)

    # Etiquetas abreviadas (iniciales)
    etiquetas = {}
    for nodo in G.nodes():
        if nodo == "Santander/Lumen":
            etiquetas[nodo] = "S/L"  # Abreviación especial para Santander/Lumen
        else:
            etiquetas[nodo] = ''.join(p[0] for p in nodo.split())
    
    nx.draw_networkx_labels(G, pos, labels=etiquetas, font_size=11, 
                          font_family="sans-serif", ax=ax, font_color='white')

    # Etiquetas de aristas
    etiquetas_aristas = nx.get_edge_attributes(G, 'weight')
    nx.draw_networkx_edge_labels(G, pos, edge_labels=etiquetas_aristas, 
                               font_size=9, ax=ax)

    # Crear tooltip oculto inicialmente
    tooltip = ax.text(0, 0, "", fontsize=10, weight='bold', color='black',
                     bbox=dict(boxstyle="round,pad=0.5", fc="#FFF9C4", ec="#FBC02D", lw=1.5),
                     ha='center', va='bottom', visible=False)

    # Función para detectar si el cursor está sobre un nodo
    def on_motion(event):
        if not event.inaxes:
            tooltip.set_visible(False)
            fig.canvas.draw_idle()
            return

        for nodo, (x, y) in pos.items():
            xt, yt = ax.transData.transform((x, y))
            if abs(xt - event.x) < 15 and abs(yt - event.y) < 15:
                categoria = grafo.categorias.get(nodo, "Servicio")
                tipo = ""
                if nodo == origen:
                    tipo = " (ORIGEN)"
                elif nodo == destino:
                    tipo = " (DESTINO)"
                
                tooltip.set_position((x, y + 0.05))
                tooltip.set_text(f"{nodo}{tipo}\nTipo: {categoria}")
                tooltip.set_visible(True)
                fig.canvas.draw_idle()
                return

        tooltip.set_visible(False)
        fig.canvas.draw_idle()

    # Conectar el evento de movimiento
    fig.canvas.mpl_connect('motion_notify_event', on_motion)

    # Leyenda simplificada (solo origen y destino)
    leyenda = [
        mpatches.Patch(color='#00FF00', label='Origen'),
        mpatches.Patch(color='#FF0000', label='Destino')
    ]
    ax.legend(handles=leyenda, loc='upper left')

    plt.tight_layout()
    plt.show()

# Crear el grafo y agregar lugares con categorías
grafo = Grafo()

lugares_con_categoria = [
    ("Biblioteca UDLAP", "Escolar/Recreativo"),
    ("Centro Estudiantil", "Recreativo"),
    ("Auditorio UDLAP", "Escolar"),
    ("Escuela de Ingenierías", "Escolar"),
    ("Estacionamiento de Ingenierías", "Estacionamiento"),
    ("Estacionamiento Centro Estudiantil", "Estacionamiento"),
    ("Templo del Dolor", "Recreativo"),
    ("Santander/Lumen", "Servicio")
]

for nombre, categoria in lugares_con_categoria:
    grafo.agregar_vertice(nombre, categoria)

for nombre, categoria in lugares_con_categoria:
    grafo.agregar_vertice(nombre, categoria)

grafo.agregar_arista("Biblioteca UDLAP", "Centro Estudiantil", 2)
grafo.agregar_arista("Centro Estudiantil", "Auditorio UDLAP", 3)
grafo.agregar_arista("Auditorio UDLAP", "Escuela de Ingenierías", 2)
grafo.agregar_arista("Escuela de Ingenierías", "Estacionamiento de Ingenierías", 4)
grafo.agregar_arista("Centro Estudiantil", "Estacionamiento Centro Estudiantil", 3)
grafo.agregar_arista("Estacionamiento Centro Estudiantil", "Templo del Dolor", 4)
grafo.agregar_arista("Auditorio UDLAP", "Santander/Lumen", 3)
grafo.agregar_arista("Santander/Lumen", "Estacionamiento de Ingenierías", 5)

class Aplicacion(tk.Tk):
    def __init__(self, grafo):
        super().__init__()
        self.grafo = grafo
        self.title("Sistema de Rutas UDLAP")
        self.geometry("500x450")
        self.configure(bg='#f5f5f5')
        
        # Frame principal con borde redondeado
        main_frame = tk.Frame(self, bg='white', bd=2, relief='groove')
        main_frame.place(relx=0.5, rely=0.5, anchor='center', width=450, height=380)
        
        # Título con fondo decorativo
        title_frame = tk.Frame(main_frame, bg='#FF5722', height=60)
        title_frame.pack(fill='x', pady=(0, 20))
        
        title_label = tk.Label(
            title_frame, 
            text="Sistema de Navegación UDLAP",
            font=('Helvetica', 16, 'bold'),
            bg='#FF5722',
            fg='white',
            pady=15
        )
        title_label.pack()
        
        # Frame de controles con alineación uniforme
        control_frame = tk.Frame(main_frame, bg='white')
        control_frame.pack(padx=30, pady=10, fill='both', expand=True)
        
        # Configuración de estilo para los combobox
        style = ttk.Style()
        style.configure('TCombobox', padding=8, relief='flat', bordercolor='#e0e0e0')
        style.map('TCombobox', fieldbackground=[('readonly', 'white')])
        
        # Campo de origen - alineado
        origin_frame = tk.Frame(control_frame, bg='white')
        origin_frame.grid(row=0, column=0, sticky='ew', pady=5)
        
        self.label_origen = tk.Label(
            origin_frame,
            text="Lugar de origen:",
            font=('Helvetica', 11),
            bg='white',
            fg='#333333',
            width=15,
            anchor='w'
        )
        self.label_origen.pack(side='left')
        
        self.origen = ttk.Combobox(
            origin_frame,
            values=grafo.obtener_vertices(),
            state="readonly",
            font=('Helvetica', 11),
            width=25
        )
        self.origen.pack(side='left', padx=(10, 0))
        
        # Campo de destino - alineado exactamente igual
        dest_frame = tk.Frame(control_frame, bg='white')
        dest_frame.grid(row=1, column=0, sticky='ew', pady=5)
        
        self.label_destino = tk.Label(
            dest_frame,
            text="Lugar de destino:",
            font=('Helvetica', 11),
            bg='white',
            fg='#333333',
            width=15,
            anchor='w'
        )
        self.label_destino.pack(side='left')
        
        self.destino = ttk.Combobox(
            dest_frame,
            values=grafo.obtener_vertices(),
            state="readonly",
            font=('Helvetica', 11),
            width=25
        )
        self.destino.pack(side='left', padx=(10, 0))
        
        # Botón de búsqueda centrado
        btn_frame = tk.Frame(control_frame, bg='white')
        btn_frame.grid(row=2, column=0, pady=(20, 0))
        
        self.boton_buscar = tk.Button(
            btn_frame,
            text="BUSCAR RUTA ÓPTIMA",
            command=self.buscar_ruta,
            font=('Helvetica', 12, 'bold'),
            bg='#FF5722',
            fg='white',
            activebackground='#E64A19',
            activeforeground='white',
            relief='flat',
            padx=30,
            pady=8,
            bd=0,
            cursor='hand2'
        )
        self.boton_buscar.pack()
        

    def buscar_ruta(self):
        origen = self.origen.get()
        destino = self.destino.get()
        if origen and destino:
            ruta, distancia = self.grafo.dijkstra(origen, destino)
            if ruta:
                messagebox.showinfo(
                    "Ruta encontrada", 
                    f"Ruta más corta:\n{' → '.join(ruta)}\n\nDistancia total: {distancia} unidades",
                    icon='info'
                )
                dibujar_grafo(self.grafo, ruta, origen, destino)
            else:
                messagebox.showerror(
                    "Error", 
                    "No se encontró una ruta entre los lugares seleccionados",
                    icon='error'
                )
        else:
            messagebox.showwarning(
                "Campos incompletos", 
                "Por favor selecciona tanto el lugar de origen como el destino",
                icon='warning'
            )

def evaluador(grafo):
    pruebas = [
        ("Biblioteca UDLAP", "Estacionamiento de Ingenierías", ["Biblioteca UDLAP", "Centro Estudiantil", "Auditorio UDLAP", "Escuela de Ingenierías", "Estacionamiento de Ingenierías"]),
        ("Templo del Dolor", "Escuela de Ingenierías", ["Templo del Dolor", "Estacionamiento Centro Estudiantil", "Centro Estudiantil", "Auditorio UDLAP", "Escuela de Ingenierías"]),
    ]
    resultados = []

    for origen, destino, ruta_esperada in pruebas:
        ruta, _ = grafo.dijkstra(origen, destino)
        resultados.append((ruta == ruta_esperada, origen, destino, ruta, ruta_esperada))

    return resultados

if __name__ == "__main__":
    app = Aplicacion(grafo)
    app.mainloop()