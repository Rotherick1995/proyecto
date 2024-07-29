import pandas as pd
import tkinter as tk
from tkinter import filedialog, simpledialog, messagebox
import os
import re
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg

# Función para extraer año, mes y día del nombre del archivo
def extract_date_from_filename(filename):
    match = re.search(r'\.(\d{4})\.(\d{2})\.(\d{2})\.', filename)
    if match:
        return match.groups()
    return ("", "", "")

# Función para procesar archivos Excel
def process_files(folder_path, columns_range, start_row):
    dataset = pd.DataFrame()
    
    # Obtener lista de archivos Excel en la carpeta
    files = [f for f in os.listdir(folder_path) if f.endswith('.xlsx')]
    
    if not files:
        messagebox.showerror("Error", "No se encontraron archivos Excel en la carpeta.")
        return dataset
    
    # Iterar sobre cada archivo Excel
    for file in files:
        file_path = os.path.join(folder_path, file)
        
        try:
            # Leer solo la primera hoja con nombre "ITEM_O"
            df = pd.read_excel(file_path, sheet_name="ITEM_O", header=None, skiprows=start_row-1)
            
            # Seleccionar columnas especificadas
            columns = list(range(columns_range[0], columns_range[1] + 1))
            df = df.iloc[:, columns]
            
            # Extraer fecha del nombre del archivo
            year, month, day = extract_date_from_filename(file)
            df['ANIO'] = year
            df['MES'] = month
            df['DIA'] = day
            
            # Concatenar al dataset final
            dataset = pd.concat([dataset, df], ignore_index=True)
        
        except Exception as e:
            messagebox.showerror("Error", f"Error al procesar el archivo {file}: {e}")
    
    return dataset

# Función para guardar el dataset en un archivo Excel
def save_to_excel(dataset):
    try:
        dataset.to_excel('Out.xlsx', index=False)
        messagebox.showinfo("Éxito", "El dataset se ha guardado correctamente en 'Out.xlsx'.")
    except Exception as e:
        messagebox.showerror("Error", f"No se pudo guardar el archivo: {e}")

# Función para mostrar el dataset en una ventana emergente
def show_dataset(dataset):
    top = tk.Toplevel()
    top.title("Dataset Final")
    text = tk.Text(top)
    text.pack(expand=True, fill='both')
    text.insert(tk.END, dataset.to_string())
    scroll = tk.Scrollbar(top, command=text.yview)
    scroll.pack(side=tk.RIGHT, fill=tk.Y)
    text.config(yscrollcommand=scroll.set)

# Función para generar y mostrar gráficos estadísticos con barras de desplazamiento
def generate_and_show_charts(root, dataset):
    if dataset.empty:
        messagebox.showerror("Error", "El dataset está vacío.")
        return

    numeric_cols = dataset.select_dtypes(include=[float, int]).columns
    
    # Crear el Canvas
    canvas = tk.Canvas(root)
    canvas.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
    
    # Crear la barra de desplazamiento vertical
    v_scrollbar = tk.Scrollbar(root, orient=tk.VERTICAL, command=canvas.yview)
    v_scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
    
    # Crear la barra de desplazamiento horizontal
    h_scrollbar = tk.Scrollbar(root, orient=tk.HORIZONTAL, command=canvas.xview)
    h_scrollbar.pack(side=tk.BOTTOM, fill=tk.X)
    
    # Configurar el Canvas para usar las barras de desplazamiento
    canvas.configure(yscrollcommand=v_scrollbar.set, xscrollcommand=h_scrollbar.set)
    
    # Crear un Frame dentro del Canvas para contener los gráficos
    chart_frame = tk.Frame(canvas)
    
    # Añadir el Frame de gráficos al Canvas
    canvas.create_window((0, 0), window=chart_frame, anchor=tk.NW)
    
    # Función para actualizar el tamaño del área de visualización del Canvas
    def update_scrollregion(event=None):
        canvas.config(scrollregion=canvas.bbox(tk.ALL))
    
    chart_frame.bind("<Configure>", update_scrollregion)
    
    # Mostrar los gráficos en el Frame de gráficos
    for col in numeric_cols:
        fig, ax = plt.subplots(2, 1, figsize=(10, 10))  # Dos gráficos por columna

        # Histograma
        dataset[col].hist(bins=30, ax=ax[0])
        ax[0].set_title(f'Histograma de {col}')
        ax[0].set_xlabel(col)
        ax[0].set_ylabel('Frecuencia')

        # Boxplot
        dataset.boxplot(column=col, ax=ax[1])
        ax[1].set_title(f'Boxplot de {col}')
        
        # Ajustar el gráfico para que se ajuste al área disponible
        plt.tight_layout()

        # Crear un canvas para el gráfico y agregarlo al Frame de gráficos
        graph_canvas = FigureCanvasTkAgg(fig, master=chart_frame)
        graph_canvas.draw()
        graph_canvas.get_tk_widget().pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        # Actualizar el tamaño del área de visualización del Canvas
        chart_frame.update_idletasks()
        update_scrollregion()

# Función para calcular y mostrar los promedios en una torta
def calculate_and_plot_averages(dataset, chart_frame):
    # Ignorar columnas de fecha
    cols_to_ignore = ['ANIO', 'MES', 'DIA']
    numeric_cols = dataset.select_dtypes(include=[float, int]).columns
    numeric_cols = [col for col in numeric_cols if col not in cols_to_ignore]
    
    if not numeric_cols:
        messagebox.showerror("Error", "No hay columnas numéricas (excluyendo fechas) en el dataset.")
        return

    averages = dataset[numeric_cols].mean()
    
    # Crear y mostrar el gráfico de torta en el Frame de gráficos
    fig, ax = plt.subplots()
    ax.pie(averages, labels=averages.index, autopct='%1.1f%%', startangle=90)
    ax.axis('equal')  # Asegurar que el gráfico sea un círculo
    plt.title('Promedio de Columnas Numéricas (excluyendo fechas)')
    
    # Integrar el gráfico en el Frame de gráficos
    chart_canvas = FigureCanvasTkAgg(fig, master=chart_frame)
    chart_canvas.draw()
    chart_canvas.get_tk_widget().pack(fill=tk.BOTH, expand=True, padx=10, pady=10)

    # Cerrar el gráfico para liberar memoria
    plt.close(fig)

# Función principal de la interfaz gráfica
def main():
    def select_folder():
        folder_path = filedialog.askdirectory()
        if folder_path:
            folder_var.set(folder_path)
    
    def run_etl_process():
        try:
            folder_path = folder_var.get()
            columns_start = int(simpledialog.askstring("Entrada", "Ingrese la columna inicial (1-indexed):")) - 1
            columns_end = int(simpledialog.askstring("Entrada", "Ingrese la columna final (1-indexed):")) - 1
            start_row = int(simpledialog.askstring("Entrada", "Ingrese la fila inicial (1-indexed):"))
            
            if columns_start < 0 or columns_end < 0 or start_row < 1:
                raise ValueError("Los valores deben ser números positivos enteros.")
            
            dataset = process_files(folder_path, (columns_start, columns_end), start_row)
            
            if not dataset.empty:
                show_dataset(dataset)
                save_to_excel(dataset)
        except Exception as e:
            messagebox.showerror("Error", f"Ocurrió un error: {e}")
    
    def generate_charts():
        try:
            dataset = pd.read_excel('Out.xlsx')
            generate_and_show_charts(root, dataset)
        except Exception as e:
            messagebox.showerror("Error", f"Ocurrió un error al generar los gráficos: {e}")

    def plot_averages():
        try:
            dataset = pd.read_excel('Out.xlsx')
            calculate_and_plot_averages(dataset, chart_frame)
        except Exception as e:
            messagebox.showerror("Error", f"Ocurrió un error al graficar los promedios: {e}")

    root = tk.Tk()
    root.title("Proceso ETL")
    root.geometry("1200x800")  # Tamaño inicial de la ventana

    folder_var = tk.StringVar()

    # Crear el Frame para mostrar gráficos
    global chart_frame
    chart_frame = tk.Frame(root)
    chart_frame.pack(side=tk.RIGHT, fill=tk.BOTH, expand=True)

    tk.Button(root, text="Seleccionar Carpeta", command=select_folder).pack(pady=10)
    tk.Label(root, textvariable=folder_var).pack(pady=10)
    tk.Button(root, text="Iniciar Proceso ETL", command=run_etl_process).pack(pady=10)
    tk.Button(root, text="Generar Gráficos Estadísticos", command=generate_charts).pack(pady=10)
    tk.Button(root, text="Graficar Promedios", command=plot_averages).pack(pady=10)

    root.mainloop()

if __name__ == "__main__":
    main()
