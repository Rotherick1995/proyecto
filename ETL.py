import pandas as pd
import tkinter as tk
from tkinter import filedialog, simpledialog, messagebox
import os
import re

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
    
    root = tk.Tk()
    root.title("Proceso ETL")

    folder_var = tk.StringVar()

    tk.Button(root, text="Seleccionar Carpeta", command=select_folder).pack(pady=10)
    tk.Label(root, textvariable=folder_var).pack(pady=10)
    tk.Button(root, text="Iniciar Proceso ETL", command=run_etl_process).pack(pady=10)

    root.mainloop()

if __name__ == "__main__":
    main()
