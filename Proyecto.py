import requests
import tkinter as tk
from tkinter import filedialog, messagebox
import pandas as pd
import matplotlib.pyplot as plt
from sqlalchemy import create_engine
import folium
from io import BytesIO
import webbrowser

class WeatherApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Análisis Climático")

        self.api_key = 'ef18dc6e5bb7111d78e0046d9dfefd57'  # Tu clave API de OpenWeatherMap

        # Botón para cargar datos desde API
        self.api_button = tk.Button(root, text="Cargar datos desde API", command=self.load_data_from_api)
        self.api_button.pack(pady=10)

        # Botón para cargar datos desde Excel
        self.excel_button = tk.Button(root, text="Cargar datos desde Excel", command=self.load_data_from_excel)
        self.excel_button.pack(pady=10)

        # Botón para mostrar análisis
        self.analyze_button = tk.Button(root, text="Mostrar Análisis", command=self.show_analysis)
        self.analyze_button.pack(pady=10)

        # Botón para mostrar mapa
        self.map_button = tk.Button(root, text="Mostrar Mapa", command=self.show_map)
        self.map_button.pack(pady=10)

    def load_data_from_api(self):
        city = 'La Paz, BO'  # Ciudad deseada en Bolivia
        url = f'http://api.openweathermap.org/data/2.5/weather?q={city}&appid={self.api_key}&units=metric'
        response = requests.get(url)
        if response.status_code == 200:
            data = response.json()
            self.df = self.transform_weather_data_from_api(data)
            db_url = 'sqlite:///weather_data.db'  # URL de la base de datos
            self.load_weather_data(self.df, db_url)
            messagebox.showinfo("Info", f"Datos cargados y transformados desde API para {city}")
        else:
            messagebox.showerror("Error", "No se pudo cargar los datos desde la API")

    def load_data_from_excel(self):
        file_path = filedialog.askopenfilename(filetypes=[("Excel files", "*.xlsx")])
        if file_path:
            self.df = self.extract_data_from_excel(file_path)
            self.df = self.transform_weather_data(self.df)
            db_url = 'sqlite:///weather_data.db'  # URL de la base de datos
            self.load_weather_data(self.df, db_url)
            messagebox.showinfo("Info", f"Datos cargados y transformados desde {file_path}")

    def show_analysis(self):
        if hasattr(self, 'df'):
            AnalysisWindow(tk.Toplevel(self.root), self.df)
        else:
            messagebox.showwarning("Warning", "No hay datos cargados.")

    def show_map(self):
        if hasattr(self, 'df'):
            lat = -16.5000000  # Latitud de La Paz, Bolivia
            lon = -68.1500000  # Longitud de La Paz, Bolivia

            weather_map = folium.Map(location=[lat, lon], zoom_start=12)
            folium.Marker(
                location=[lat, lon],
                popup=f"Temperatura: {self.df['temperatura'].iloc[0]}°C\nHumedad: {self.df['humedad'].iloc[0]}%",
                icon=folium.Icon(color='blue')
            ).add_to(weather_map)

            # Guardar mapa en archivo HTML y abrir en el navegador
            map_path = "weather_map.html"
            weather_map.save(map_path)
            webbrowser.open(map_path)
        else:
            messagebox.showwarning("Warning", "No hay datos cargados.")

    def extract_data_from_excel(self, file_path):
        return pd.read_excel(file_path)

    def transform_weather_data(self, df):
        df['fecha'] = pd.to_datetime(df[['gestion', 'mes', 'dia']])
        return df

    def transform_weather_data_from_api(self, data):
        # Transformar los datos de la API en un DataFrame
        df = pd.DataFrame({
            'fecha': [pd.to_datetime('now')],
            'temperatura': [data['main']['temp']],
            'temperatura_max': [data['main']['temp_max']],
            'temperatura_min': [data['main']['temp_min']],
            'humedad': [data['main']['humidity']],
            'presion': [data['main']['pressure']],
            'viento_velocidad': [data['wind']['speed']],
            'viento_direccion': [data['wind']['deg']],
            'descripcion': [data['weather'][0]['description']]
        })
        return df

    def load_weather_data(self, df, db_url):
        engine = create_engine(db_url)
        df.to_sql('weather_data', engine, if_exists='replace', index=False)

class AnalysisWindow:
    def __init__(self, root, df):
        self.df = df
        self.root = root
        self.root.title("Análisis Climático")

        # Botón para mostrar gráfico de temperatura
        self.plot_button = tk.Button(root, text="Mostrar Gráfico de Temperatura", command=self.plot_temperature)
        self.plot_button.pack(pady=10)

        # Botón para mostrar resumen de datos
        self.summary_button = tk.Button(root, text="Mostrar Resumen de Datos", command=self.show_summary)
        self.summary_button.pack(pady=10)

    def plot_temperature(self):
        self.df.set_index('fecha')[['temperatura', 'temperatura_max', 'temperatura_min']].plot()
        plt.title('Tendencias de Temperatura')
        plt.xlabel('Fecha')
        plt.ylabel('Temperatura (°C)')
        plt.show()

    def show_summary(self):
        summary = self.df.describe()
        messagebox.showinfo("Resumen de Datos", str(summary))

if __name__ == "__main__":
    root = tk.Tk()
    app = WeatherApp(root)
    root.mainloop()