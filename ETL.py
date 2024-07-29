import pandas as pd
import streamlit as st
import io
import matplotlib.pyplot as plt
import numpy as np
import re

def extract_date_from_filename(filename):
    match = re.search(r'\d{4}\.\d{2}\.\d{2}', filename)
    if match:
        year, month, day = match.group(0).split('.')
        return int(year), int(month), int(day)
    return None, None, None

def process_files(files, columns_range, start_row):
    all_data = []
    for file in files:
        try:
            df = pd.read_excel(file, sheet_name="ITEM_O", skiprows=start_row-1, usecols=columns_range)
            filename = file.name
            year, month, day = extract_date_from_filename(filename)
            if year is not None:
                df['ANIO'] = year
                df['MES'] = month
                df['DIA'] = day
                all_data.append(df)
            else:
                st.warning(f"Filename {filename} does not match the expected date format.")
        except Exception as e:
            st.error(f"Error processing file {file.name}: {e}")

    if all_data:
        combined_df = pd.concat(all_data, ignore_index=True)
        st.write(f"Processed {len(all_data)} files.")
        return combined_df
    else:
        st.warning("No data was processed from the provided files.")
        return pd.DataFrame()  # Return an empty DataFrame if no data is processed

def save_with_report_and_graphs(df):
    try:
        # Create a summary report
        summary = df.describe(include='all')

        # Identify the numeric columns
        numeric_columns = df.select_dtypes(include=[np.number]).columns.tolist()
        if not numeric_columns:
            raise ValueError("No numeric columns found in the dataframe")

        # Use the first numeric column for the graph
        value_column = numeric_columns[0]
        year_column = 'ANIO' if 'ANIO' in df.columns else 'AÑO'

        # Create the histogram with customized style
        plt.style.use('dark_background')
        plt.figure(figsize=(12, 8))
        for year in df[year_column].unique():
            year_data = df[df[year_column] == year]
            plt.hist(year_data[value_column], bins=20, alpha=0.5, label=str(year), color='green')
        
        plt.title(f"Histograma de {value_column} por Año", color='white')
        plt.xlabel(value_column, color='white')
        plt.ylabel("Frecuencia", color='white')
        plt.legend(title="Año")
        plt.grid(True, color='white')
        
        # Save plot to BytesIO object
        img_stream = io.BytesIO()
        plt.savefig(img_stream, format='png')
        plt.close()
        img_stream.seek(0)

        return summary, img_stream
    except Exception as e:
        st.error(f"Error generating report: {e}")
        return None, None

def main():
    st.title("Procesos ETL Rotherick")

    # File uploader
    uploaded_files = st.file_uploader("Carga Archivos Excel", type="xlsx", accept_multiple_files=True)

    columns_range = st.text_input("Rango de Columnas (e.g., A:I):")
    start_row = st.number_input("Fila de Inicio:", min_value=1, value=1)

    if st.button("Ejecutar ETL"):
        if uploaded_files and columns_range:
            with st.spinner('Procesando Archivos...'):
                df_final = process_files(uploaded_files, columns_range, start_row)
                if not df_final.empty:
                    st.write("Data Preview:")
                    st.dataframe(df_final)
                    st.session_state.df_final = df_final  # Save the dataframe to session state
                    st.success("Datos Procesados Satisfactoriamente!")
                else:
                    st.warning("Datos No Encontrados. Revisa el contenido del archivo.")
        else:
            st.warning("Por favor cargar los archivos y especifica el rango de columnas y la fila inicial.")

    if st.button("Generar Reporte Gráfico"):
        if 'df_final' in st.session_state and not st.session_state.df_final.empty:
            summary, img_stream = save_with_report_and_graphs(st.session_state.df_final)
            if summary is not None:
                st.write("Resumen de Reporte:")
                st.write(summary)
                st.image(img_stream)
        else:
            st.warning("No datos disponibles para generar reporte. Primeramente ejecute el proceso ETL.")

if __name__ == "__main__":
    main()
