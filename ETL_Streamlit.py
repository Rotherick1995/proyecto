import pandas as pd
import streamlit as st
import os
import re
import matplotlib.pyplot as plt

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
        st.error("No se encontraron archivos Excel en la carpeta.")
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
            st.error(f"Error al procesar el archivo {file}: {e}")
    
    return dataset

# Función para guardar el dataset en un archivo Excel
def save_to_excel(dataset):
    try:
        dataset.to_excel('Out.xlsx', index=False)
        st.success("El dataset se ha guardado correctamente en 'Out.xlsx'.")
    except Exception as e:
        st.error(f"No se pudo guardar el archivo: {e}")

# Función para mostrar el dataset en Streamlit
def show_dataset(dataset):
    st.write(dataset)

# Función para generar y mostrar gráficos estadísticos con Streamlit
def generate_and_show_charts(dataset):
    if dataset.empty:
        st.error("El dataset está vacío.")
        return

    numeric_cols = dataset.select_dtypes(include=[float, int]).columns
    
    for col in numeric_cols:
        st.subheader(f'Histograma y Boxplot de {col}')
        
        # Histograma
        fig, ax = plt.subplots(2, 1, figsize=(10, 10))  # Dos gráficos por columna
        dataset[col].hist(bins=30, ax=ax[0])
        ax[0].set_title(f'Histograma de {col}')
        ax[0].set_xlabel(col)
        ax[0].set_ylabel('Frecuencia')

        # Boxplot
        dataset.boxplot(column=col, ax=ax[1])
        ax[1].set_title(f'Boxplot de {col}')
        
        # Ajustar el gráfico
        plt.tight_layout()
        st.pyplot(fig)

# Función para calcular y mostrar los promedios en una torta
def calculate_and_plot_averages(dataset):
    # Ignorar columnas de fecha
    cols_to_ignore = ['ANIO', 'MES', 'DIA']
    numeric_cols = dataset.select_dtypes(include=[float, int]).columns
    numeric_cols = [col for col in numeric_cols if col not in cols_to_ignore]
    
    if not numeric_cols:
        st.error("No hay columnas numéricas (excluyendo fechas) en el dataset.")
        return

    averages = dataset[numeric_cols].mean()
    
    # Crear y mostrar el gráfico de torta
    fig, ax = plt.subplots()
    ax.pie(averages, labels=averages.index, autopct='%1.1f%%', startangle=90)
    ax.axis('equal')  # Asegurar que el gráfico sea un círculo
    plt.title('Promedio de Columnas Numéricas (excluyendo fechas)')
    
    st.pyplot(fig)

# Función principal de la interfaz de Streamlit
def main():
    st.title("Proceso ETL")
    
    folder_path = st.text_input("Ingrese la ruta de la carpeta con archivos Excel:")
    
    columns_start = st.number_input("Ingrese la columna inicial (1-indexed):", min_value=1) - 1
    columns_end = st.number_input("Ingrese la columna final (1-indexed):", min_value=1) - 1
    start_row = st.number_input("Ingrese la fila inicial (1-indexed):", min_value=1)
    
    if st.button("Iniciar Proceso ETL"):
        dataset = process_files(folder_path, (columns_start, columns_end), start_row)
        
        if not dataset.empty:
            show_dataset(dataset)
            save_to_excel(dataset)
    
    if st.button("Generar Gráficos Estadísticos"):
        try:
            dataset = pd.read_excel('Out.xlsx')
            generate_and_show_charts(dataset)
        except Exception as e:
            st.error(f"Ocurrió un error al generar los gráficos: {e}")
    
    if st.button("Graficar Promedios"):
        try:
            dataset = pd.read_excel('Out.xlsx')
            calculate_and_plot_averages(dataset)
        except Exception as e:
            st.error(f"Ocurrió un error al graficar los promedios: {e}")

if __name__ == "__main__":
    main()
