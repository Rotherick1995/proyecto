import os
import pandas as pd
import tkinter as tk
from tkinter import filedialog, ttk, messagebox

class ETLApp:
    def __init__(self, master):
        self.master = master
        self.master.title("ETL Process")
        self.master.geometry("600x450")

        # Variables
        self.folder_path = tk.StringVar()
        self.start_col = tk.StringVar()
        self.end_col = tk.StringVar()
        self.start_row = tk.IntVar(value=2)  # Valor predeterminado: 2

        # Crear y configurar widgets
        tk.Label(master, text="Carpeta de archivos Excel:").grid(row=0, column=0, sticky="w", padx=5, pady=5)
        self.folder_entry = tk.Entry(master, textvariable=self.folder_path, width=50, state='readonly')
        self.folder_entry.grid(row=0, column=1, padx=5, pady=5)
        tk.Button(master, text="Seleccionar Carpeta", command=self.browse_folder).grid(row=0, column=2, padx=5, pady=5)

        tk.Label(master, text="Columna inicial:").grid(row=1, column=0, sticky="w", padx=5, pady=5)
        tk.Entry(master, textvariable=self.start_col, width=5).grid(row=1, column=1, sticky="w", padx=5, pady=5)

        tk.Label(master, text="Columna final:").grid(row=2, column=0, sticky="w", padx=5, pady=5)
        tk.Entry(master, textvariable=self.end_col, width=5).grid(row=2, column=1, sticky="w", padx=5, pady=5)

        tk.Label(master, text="Fila inicial:").grid(row=3, column=0, sticky="w", padx=5, pady=5)
        tk.Entry(master, textvariable=self.start_row, width=5).grid(row=3, column=1, sticky="w", padx=5, pady=5)

        tk.Button(master, text="Procesar", command=self.process_files).grid(row=4, column=1, pady=20)

        self.progress = ttk.Progressbar(master, orient="horizontal", length=300, mode="determinate")
        self.progress.grid(row=5, column=0, columnspan=3, padx=5, pady=5)

        self.result_text = tk.Text(master, height=10, width=70)
        self.result_text.grid(row=6, column=0, columnspan=3, padx=5, pady=5)

    def browse_folder(self):
        folder_selected = filedialog.askdirectory()
        if folder_selected:
            self.folder_path.set(folder_selected)
            self.folder_entry.config(state='normal')
            self.folder_entry.delete(0, tk.END)
            self.folder_entry.insert(0, folder_selected)
            self.folder_entry.config(state='readonly')

    def process_files(self):
        if not self.folder_path.get():
            messagebox.showerror("Error", "Por favor, seleccione una carpeta.")
            return

        try:
            folder_path = self.folder_path.get()
            start_col = self.start_col.get().upper()
            end_col = self.end_col.get().upper()
            start_row = self.start_row.get()

            excel_files = [f for f in os.listdir(folder_path) if f.endswith('.xlsx') and f.startswith('AvanceVentasINTI')]

            if not excel_files:
                messagebox.showwarning("Advertencia", "No se encontraron archivos Excel válidos en la carpeta seleccionada.")
                return

            all_data = []
            total_files = len(excel_files)

            for i, file in enumerate(excel_files):
                file_path = os.path.join(folder_path, file)
                
                # Extraer año, mes y día del nombre del archivo
                date_parts = file.split('.')
                if len(date_parts) >= 4:
                    year, month, day = date_parts[1:4]
                else:
                    # Si el nombre del archivo no tiene el formato esperado, usar valores predeterminados
                    year, month, day = "N/A", "N/A", "N/A"

                # Leer solo la hoja "ITEM_O"
                df = pd.read_excel(file_path, sheet_name="ITEM_O", usecols=f"{start_col}:{end_col}", skiprows=start_row-1)
                
                # Añadir columnas de año, mes y día
                df['ANIO'] = year
                df['MES'] = month
                df['DIA'] = day

                all_data.append(df)

                # Actualizar la barra de progreso
                self.progress['value'] = (i + 1) / total_files * 100
                self.master.update_idletasks()

            # Concatenar todos los DataFrames
            final_df = pd.concat(all_data, ignore_index=True)

            # Asegurar que todas las columnas estén presentes y en el orden correcto
            expected_columns = ['OFICINA', 'CODIGO', 'NOMBRE', 'LINEA', 'GRUPO', 'PNG', 'U', 'VALOR', 'U2', 'VALOR2', 'LV1', 'VALORC', 'LV2', 'ANIO', 'MES', 'DIA']
            final_df = final_df.reindex(columns=expected_columns)

            # Exportar a Excel
            output_path = os.path.join(folder_path, 'Out.xlsx')
            final_df.to_excel(output_path, index=False)

            # Mostrar las primeras filas del DataFrame en el widget de texto
            self.result_text.delete('1.0', tk.END)
            self.result_text.insert(tk.END, final_df.head().to_string())

            messagebox.showinfo("Proceso completado", f"El archivo Out.xlsx ha sido creado en {output_path}")

        except Exception as e:
            messagebox.showerror("Error", str(e))

if __name__ == "__main__":
    root = tk.Tk()
    app = ETLApp(root)
    root.mainloop()