import tkinter as tk
from tkinter import ttk, messagebox, font
from collections import deque, OrderedDict

class PageReplacementSimulator:
    def __init__(self, root):
        self.root = root
        self.root.title("Simulador de Algoritmos de Reemplazo de Páginas")
        self.root.geometry("1000x700")
        
        # Configurar fuentes
        self.big_font = font.Font(size=10)
        self.bold_font = font.Font(size=10, weight='bold')
        
        # Variables de control
        self.algorithm = tk.StringVar(value="FIFO")
        self.frame_count = tk.IntVar(value=3)
        self.reference_string = tk.StringVar(value="1 2 3 4 1 2 5 1 2 3 4 5")
        self.results = []
        
        # Configurar interfaz
        self.setup_ui()
    
    def setup_ui(self):
        # Frame principal
        main_frame = ttk.Frame(self.root, padding="20")
        main_frame.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        
        # Configurar expansión
        self.root.columnconfigure(0, weight=1)
        self.root.rowconfigure(0, weight=1)
        
        # Panel de configuración
        config_frame = ttk.LabelFrame(main_frame, text="Configuración", padding=(15, 10))
        config_frame.grid(row=0, column=0, sticky=(tk.W, tk.E), pady=10)
        
        # Controles de configuración
        ttk.Label(config_frame, text="Algoritmo:", font=self.bold_font).grid(row=0, column=0, sticky=tk.W, pady=5)
        algo_combo = ttk.Combobox(config_frame, textvariable=self.algorithm, 
                                values=["FIFO", "LRU", "Óptimo","FIFO+"], state="readonly", font=self.big_font)
        algo_combo.grid(row=0, column=1, sticky=tk.W, padx=15, pady=5)
        
        ttk.Label(config_frame, text="Número de marcos:", font=self.bold_font).grid(row=1, column=0, sticky=tk.W, pady=5)
        frame_spin = ttk.Spinbox(config_frame, from_=1, to=10, textvariable=self.frame_count, font=self.big_font)
        frame_spin.grid(row=1, column=1, sticky=tk.W, padx=15, pady=5)

# Botón "Actualizar"
        ttk.Button(config_frame, text="Actualizar", command=self.update_simulation, padding=5).grid(row=1, column=2, sticky=tk.W, padx=10)
        ttk.Label(config_frame, text="Cadena de referencia (números separados por espacios):", 
                font=self.bold_font).grid(row=2, column=0, sticky=tk.W, pady=5)
        ref_entry = ttk.Entry(config_frame, textvariable=self.reference_string, width=40, font=self.big_font)
        ref_entry.grid(row=2, column=1, sticky=tk.W, padx=15, pady=5)
        ttk.Button(config_frame, text="Modificar", command=self.modify_references, padding=5).grid(row=2, column=2, sticky=tk.W, padx=10)
        # Botones (hemos eliminado el de "Agregar Proceso" ya que no era necesario)
        button_frame = ttk.Frame(main_frame)
        button_frame.grid(row=1, column=0, sticky=tk.W, pady=15)
        
        ttk.Button(button_frame, text="Agregar Proceso/s", command=self.keep_running_simulation, padding=5).grid(row=0, column=0, padx=10)
        ttk.Button(button_frame, text="Limpiar", command=self.clear_simulation, padding=5).grid(row=0, column=2, padx=10)
        
        # Panel de resultados
        results_frame = ttk.LabelFrame(main_frame, text="Resultados", padding=(15, 10))
        results_frame.grid(row=2, column=0, sticky=(tk.W, tk.E, tk.N, tk.S), pady=10)
        
        # Configurar expansión
        main_frame.rowconfigure(2, weight=1)
        main_frame.columnconfigure(0, weight=1)
        results_frame.columnconfigure(0, weight=1)
        results_frame.rowconfigure(0, weight=1)
        
        # Treeview con las columnas solicitadas
        columns = ('step', 'page', 'action', 'frames', 'replaced', 'hit_miss')
        self.tree = ttk.Treeview(results_frame, columns=columns, show='headings', height=15)
        
        # Configurar columnas
        self.tree.heading('step', text='Paso')
        self.tree.heading('page', text='Página')
        self.tree.heading('action', text='Entra')
        self.tree.heading('frames', text='Marcos')
        self.tree.heading('replaced', text='Sale')
        self.tree.heading('hit_miss', text='Resultado')
        
        self.tree.column('step', width=60, anchor='center')
        self.tree.column('page', width=80, anchor='center')
        self.tree.column('action', width=60, anchor='center')
        self.tree.column('frames', width=300, anchor='center')
        self.tree.column('replaced', width=60, anchor='center')
        self.tree.column('hit_miss', width=100, anchor='center')
        
        # Scrollbar
        scrollbar = ttk.Scrollbar(results_frame, orient=tk.VERTICAL, command=self.tree.yview)
        self.tree.configure(yscroll=scrollbar.set)
        
        self.tree.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        scrollbar.grid(row=0, column=1, sticky=(tk.N, tk.S))
        
        # Panel de estadísticas
        stats_frame = ttk.LabelFrame(main_frame, text="Estadísticas", padding=(15, 10))
        stats_frame.grid(row=3, column=0, sticky=(tk.W, tk.E), pady=10)
        
        self.stats_label = ttk.Label(stats_frame, 
                                   text="Fallos de página: 0\nAciertos: 0", 
                                   font=self.big_font)
        self.stats_label.grid(row=0, column=0, sticky=tk.W)
    
    def clear_simulation(self, tipo= "A"):
        """Limpiar los resultados anteriores"""
        self.tree.delete(*self.tree.get_children())
        self.stats_label.config(text="Fallos de página: 0\nAciertos: 0")
        self.results = []
        if tipo == "A":
            self.accumulated_references = []
    def modify_references(self):
        """Colocar las entradas acumuladas en el campo de texto para modificarlas"""
        if not hasattr(self, 'accumulated_references') or not self.accumulated_references:
            messagebox.showerror("Error", "No hay entradas acumuladas para modificar")
            return

    # Convertir las referencias acumuladas a una cadena separada por espacios
        self.reference_string.set(" ".join(map(str, self.accumulated_references)))
    def update_simulation(self):
        """Actualizar la simulación con el nuevo número de marcos y detectar anomalías"""
        if not hasattr(self, 'accumulated_references') or not self.accumulated_references:
            messagebox.showerror("Error", "No hay entradas acumuladas para actualizar la simulación")
            return

        algorithm = self.algorithm.get()
        frame_count = self.frame_count.get()
        if frame_count > 1:
        # Ejecutar el algoritmo seleccionado con las entradas acumuladas
            if algorithm == "FIFO":
                previous_results, previous_faults, _ = self.fifo_algorithm(self.accumulated_references, frame_count - 1)
                results, faults, hits = self.fifo_algorithm(self.accumulated_references, frame_count)
            elif algorithm == "LRU":
                previous_results, previous_faults, _ = self.lru_algorithm(self.accumulated_references, frame_count - 1)
                results, faults, hits = self.lru_algorithm(self.accumulated_references, frame_count)
            elif algorithm == "Óptimo":
                previous_results, previous_faults, _ = self.optimal_algorithm(self.accumulated_references, frame_count - 1 )
                results, faults, hits = self.optimal_algorithm(self.accumulated_references, frame_count)
            elif algorithm == "FIFO+":
                previous_results, previous_faults, _ = self.fifoPlus_algorithm(self.accumulated_references, frame_count - 1)
                results, faults, hits = self.fifoPlus_algorithm(self.accumulated_references, frame_count)
        else:
            if algorithm == "FIFO":
                previous_results, previous_faults, _ = self.fifo_algorithm(self.accumulated_references, frame_count )
                results, faults, hits = self.fifo_algorithm(self.accumulated_references, frame_count)
            elif algorithm == "LRU":
                previous_results, previous_faults, _ = self.lru_algorithm(self.accumulated_references, frame_count )
                results, faults, hits = self.lru_algorithm(self.accumulated_references, frame_count)
            elif algorithm == "Óptimo":
                previous_results, previous_faults, _ = self.optimal_algorithm(self.accumulated_references, frame_count )
                results, faults, hits = self.optimal_algorithm(self.accumulated_references, frame_count)
            elif algorithm == "FIFO+":
                previous_results, previous_faults, _ = self.fifoPlus_algorithm(self.accumulated_references, frame_count )
                results, faults, hits = self.fifoPlus_algorithm(self.accumulated_references, frame_count)

        # Detectar anomalía
        if frame_count > 1 and faults > previous_faults:
            messagebox.showwarning("Anomalía de Belady detectada", "Se detectó una anomalía: los fallos aumentaron al incrementar los marcos.")

        # Limpiar los resultados anteriores
        self.tree.delete(*self.tree.get_children())

        # Mostrar resultados en el formato solicitado
        for i, result in enumerate(results, 1):
            frames_str = "   ".join(f"{f}" if f is not None else "-" for f in result['frames'])
            
            self.tree.insert('', 'end', values=(
                i,
                result['page'],
                "->" if not result['hit'] else "",
                frames_str,
                result.get('replaced', "*") if not result['hit'] else "",
                "Acierto" if result['hit'] else "Fallo (*)"
            ))

        # Mostrar estadísticas
        self.stats_label.config(text=f"Fallos de página: {faults}\nAciertos: {hits}")    
    def run_simulation(self):
        """Ejecutar la simulación con los parámetros actuales"""
        self.clear_simulation()
        
        new_reference_string = self.reference_string.get()
        algorithm = self.algorithm.get()
        frame_count = self.frame_count.get()
        
        if not new_reference_string:
            messagebox.showerror("Error", "Ingrese una cadena de referencia")
            return
        
        try:
            new_references = list(map(int, new_reference_string.split()))
        except ValueError:
            messagebox.showerror("Error", "La cadena debe contener solo números separados por espacios")
            return
        
        if hasattr(self, 'accumulated_references'):
            self.accumulated_references += new_references
        else:
            self.accumulated_references = new_references
    

        # Ejecutar el algoritmo seleccionado
        if algorithm == "FIFO":
            results, faults, hits = self.fifo_algorithm(self.accumulated_references, frame_count)
        elif algorithm == "LRU":
            results, faults, hits = self.lru_algorithm(self.accumulated_references, frame_count)
        elif algorithm == "Óptimo":
            results, faults, hits = self.optimal_algorithm(self.accumulated_references, frame_count)
        elif algorithm == "FIFO+":
            results, faults, hits = self.fifoPlus_algorithm(self.accumulated_references, frame_count)
            # Mostrar resultados en el formato solicitado
        for i, result in enumerate(results, 1):
            frames_str = "   ".join(f"{f}" if f is not None else "-" for f in result['frames'])
            
            self.tree.insert('', 'end', values=(
                i,
                result['page'],
                "->" if not result['hit'] else "",
                frames_str,
                result.get('replaced', "*") if not result['hit'] else "",
                "Acierto" if result['hit'] else "Fallo (*)"
            ))
        
        # Mostrar estadísticas
        self.stats_label.config(text=f"Fallos de página: {faults}\nAciertos: {hits}")
    
    def keep_running_simulation(self):
        """Ejecutar la simulación con los parámetros actuales"""
        self.clear_simulation("B")
        
        new_reference_string = self.reference_string.get()
        algorithm = self.algorithm.get()
        frame_count = self.frame_count.get()
        
        if not new_reference_string and not hasattr(self, 'accumulated_references'):
            messagebox.showerror("Error", "Ingrese una cadena de referencia")
            return
        try:
            new_references = list(map(int, new_reference_string.split()))
        except ValueError:
            messagebox.showerror("Error", "La cadena debe contener solo números separados por espacios")
            return
        
        if hasattr(self, 'accumulated_references'):
            self.accumulated_references += new_references
        else:
            self.accumulated_references = new_references
    

        # Ejecutar el algoritmo seleccionado
        if algorithm == "FIFO":
            results, faults, hits = self.fifo_algorithm(self.accumulated_references, frame_count)
        elif algorithm == "LRU":
            results, faults, hits = self.lru_algorithm(self.accumulated_references, frame_count)
        elif algorithm == "Óptimo":
            results, faults, hits = self.optimal_algorithm(self.accumulated_references, frame_count)
        elif algorithm == "FIFO+":
            results, faults, hits = self.fifoPlus_algorithm(self.accumulated_references, frame_count)
            # Mostrar resultados en el formato solicitado
        for i, result in enumerate(results, 1):
            frames_str = "   ".join(f"{f}" if f is not None else "-" for f in result['frames'])
            
            self.tree.insert('', 'end', values=(
                i,
                result['page'],
                "->" if not result['hit'] else "",
                frames_str,
                result.get('replaced', "*") if not result['hit'] else "",
                "Acierto" if result['hit'] else "Fallo (*)"
            ))
        
        # Mostrar estadísticas
        self.stats_label.config(text=f"Fallos de página: {faults}\nAciertos: {hits}")
    

    def fifo_algorithm(self, references, frame_count):
        """Implementación del algoritmo FIFO"""
        frames = [None] * frame_count
        queue = deque()
        faults = 0
        hits = 0
        results = []
        
        for page in references:
            hit = False
            replaced = None
            
            if page in frames:
                hits += 1
                hit = True
            else:
                faults += 1
                if None in frames:
                    index = frames.index(None)
                    frames[index] = page
                    queue.append(index)
                else:
                    index = queue.popleft()
                    replaced = frames[index]
                    frames[index] = page
                    queue.append(index)
            
            results.append({
                'page': page,
                'frames': frames.copy(),
                'hit': hit,
                'replaced': replaced
            })
        
        return results, faults, hits
    
    def lru_algorithm(self, references, frame_count):
        """Implementación del algoritmo LRU"""
        cache = OrderedDict()
        faults = 0
        hits = 0
        results = []
        
        for page in references:
            hit = False
            replaced = None
            
            if page in cache:
                cache.move_to_end(page)
                hits += 1
                hit = True
            else:
                faults += 1
                if len(cache) == frame_count:
                    replaced, _ = cache.popitem(last=False)
                cache[page] = True
            
            current_frames = list(cache.keys())
            frames = current_frames + [None] * (frame_count - len(current_frames))
            results.append({
                'page': page,
                'frames': frames,
                'hit': hit,
                'replaced': replaced
            })
        
        return results, faults, hits
    
    def optimal_algorithm(self, references, frame_count):
        """Implementación del algoritmo Óptimo"""
        frames = [None] * frame_count
        faults = 0
        hits = 0
        results = []
        
        for i, page in enumerate(references):
            hit = False
            replaced = None
            
            if page in frames:
                hits += 1
                hit = True
            else:
                faults += 1
                if None in frames:
                    index = frames.index(None)
                    frames[index] = page
                else:
                    farthest = -1
                    replace_index = 0
                    
                    for j, frame in enumerate(frames):
                        try:
                            next_use = references.index(frame, i+1)
                            if next_use > farthest:
                                farthest = next_use
                                replace_index = j
                        except ValueError:
                            replace_index = j
                            break
                    replaced = frames[replace_index]
                    frames[replace_index] = page
            
            results.append({
                'page': page,
                'frames': frames.copy(),
                'hit': hit,
                'replaced': replaced
            })
        
        return results, faults, hits

    def fifoPlus_algorithm(self, references, frame_count):
        """Implementación del algoritmo FIFO+ con segundas oportunidades"""
        frames = [None] * frame_count
        queue = deque()
        faults = 0
        hits = 0
        results = []
        segundasOportunidades = []
        reposicion = deque()

        for page in references:
            hit = False
            replaced = None
            reposicion = deque()
            # Eliminar el asterisco si está presente en la página
            if "*" in str(page):
                page = int(str(page).replace("*", ""))

            if page in frames or str(page) + "*" in frames:
                hits += 1
                hit = True
                if page not in segundasOportunidades:
                    for i, frame in enumerate(frames):
                        if "*" in str(frame):
                            frames[i] = int(str(frame).replace("*", ""))
                    segundasOportunidades= []
                    segundasOportunidades.append(page)
                    
            else:
                faults += 1
                if None in frames:
                    # Si hay espacio disponible, agregar la página sin quitar oportunidades
                    index = frames.index(None)
                    frames[index] = page
                    queue.append(index)
                else:
                    # Si no hay espacio disponible, aplicar el reemplazo con segundas oportunidades
                    while True:
                        index = queue.popleft()
                        if "*" in str(frames[index]):
                            frames[index] = int(str(frames[index]).replace("*", ""))  # Eliminar el asterisco
                        if frames[index] in segundasOportunidades  :
                            # Eliminar la oportunidad y el asterisco
                            segundasOportunidades.remove(frames[index])
                            frames[index] = int(str(frames[index]).replace("*", ""))  # Eliminar el asterisco
                            reposicion.appendleft(index)  # Reposicionar el índice para la próxima iteración
                            
                        else:
                            replaced = frames[index]
                            frames[index] = page
                            queue.append(index)
                            break
            
            for index in reposicion:
                queue.appendleft(index)
            # Actualizar los frames con asteriscos para las segundas oportunidades
            for i, frame in enumerate(frames):
                if frame in segundasOportunidades:
                    frames[i] = str(frame) + "*"
                

            # Registrar el resultado
            results.append({
                'page': page,
                'frames': frames.copy(),
                'hit': hit,
                'replaced': replaced
            })

        return results, faults, hits
if __name__ == "__main__":
    root = tk.Tk()
    # Configurar estilo
    style = ttk.Style()
    style.configure('TLabel', font=('Arial', 10))
    style.configure('TButton', font=('Arial', 10), padding=5)
    style.configure('Treeview', font=('Arial', 10), rowheight=25)
    style.configure('Treeview.Heading', font=('Arial', 10, 'bold'))
    
    app = PageReplacementSimulator(root)
    root.mainloop()