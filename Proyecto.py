import requests
import tkinter as tk
from tkinter import messagebox, scrolledtext
import pandas as pd
import matplotlib.pyplot as plt
from sqlalchemy import create_engine
import folium
import webbrowser
import matplotlib
from datetime import datetime, timedelta

matplotlib.use('TkAgg')  # Asegura el uso del backend TkAgg

class WeatherApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Análisis Climático")

        # Ajustar tamaño de la ventana principal al 45% de la pantalla y centrar
        self.resize_and_center_window(self.root, 0.45)

        self.api_key = 'TU_CLAVE_API_DE_WEATHERBIT'  # Tu clave API de Weatherbit
        self.df = pd.DataFrame()  # Inicializa un DataFrame vacío

        # Cuadro de texto para ingresar la ciudad
        self.city_entry_label = tk.Label(root, text="Ingrese la ciudad:")
        self.city_entry_label.pack(pady=5)
        self.city_entry = tk.Entry(root)
        self.city_entry.pack(pady=5)

        # Botón para cargar datos desde API
        self.api_button = tk.Button(root, text="Cargar datos desde API", command=self.load_data_from_api)
        self.api_button.pack(pady=10)

        # Botón para mostrar análisis
        self.analyze_button = tk.Button(root, text="Mostrar Análisis", command=self.show_analysis)
        self.analyze_button.pack(pady=10)

        # Botón para mostrar mapa
        self.map_button = tk.Button(root, text="Mostrar Mapa", command=self.show_map)
        self.map_button.pack(pady=10)

    def resize_and_center_window(self, window, percent):
        screen_width = window.winfo_screenwidth()
        screen_height = window.winfo_screenheight()
        width = int(screen_width * percent)
        height = int(screen_height * percent)
        x = (screen_width - width) // 2
        y = (screen_height - height) // 2
        window.geometry(f"{width}x{height}+{x}+{y}")

    def load_data_from_api(self):
        city = self.city_entry.get()  # Obtener la ciudad desde el cuadro de texto
        if not city:
            messagebox.showwarning("Warning", "Por favor ingrese una ciudad.")
            return

        try:
            # Obtener latitud y longitud de la ciudad
            location_url = f'http://api.openweathermap.org/data/2.5/weather?q={city}&appid=ef18dc6e5bb7111d78e0046d9dfefd57'
            location_response = requests.get(location_url)
            location_data = location_response.json()
            lat = location_data['coord']['lat']
            lon = location_data['coord']['lon']

            # Obtener datos históricos de los últimos 30 días
            end_date = datetime.now()
            start_date = end_date - timedelta(days=30)
            weather_url = f'https://api.weatherbit.io/v2.0/history/daily?lat={lat}&lon={lon}&start_date={start_date.strftime("%Y-%m-%d")}&end_date={end_date.strftime("%Y-%m-%d")}&key={self.api_key}'
            response = requests.get(weather_url)
            response.raise_for_status()  # Lanza una excepción para códigos de estado HTTP erróneos
            data = response.json()
            new_data = self.transform_weather_data_from_api(data)
            self.df = pd.concat([self.df, new_data], ignore_index=True)  # Acumula los datos en el DataFrame
            db_url = 'mysql+mysqlconnector://root:Rfcm8329330@localhost/proyecto'  # URL de la base de datos
            self.load_weather_data(self.df, db_url)
            messagebox.showinfo("Info", f"Datos cargados y transformados desde API para {city}")
        except requests.RequestException as e:
            messagebox.showerror("Error", f"No se pudo cargar los datos desde la API: {e}")

    def show_analysis(self):
        if not self.df.empty:
            AnalysisWindow(tk.Toplevel(self.root), self.df)
        else:
            messagebox.showwarning("Warning", "No hay datos cargados.")

    def show_map(self):
        if not self.df.empty:
            try:
                lat = -16.5000000  # Latitud de La Paz, Bolivia
                lon = -68.1500000  # Longitud de La Paz, Bolivia

                weather_map = folium.Map(location=[lat, lon], zoom_start=12)
                folium.Marker(
                    location=[lat, lon],
                    popup=f"Temperatura: {self.df['temp'].iloc[-1]}°C\nHumedad: {self.df['rh'].iloc[-1]}%",
                    icon=folium.Icon(color='blue')
                ).add_to(weather_map)

                # Guardar mapa en archivo HTML y abrir en el navegador
                map_path = "weather_map.html"
                weather_map.save(map_path)
                webbrowser.open(map_path)
            except Exception as e:
                messagebox.showerror("Error", f"No se pudo mostrar el mapa: {e}")
        else:
            messagebox.showwarning("Warning", "No hay datos cargados.")

    def transform_weather_data_from_api(self, data):
        # Transformar los datos de la API en un DataFrame
        records = data['data']
        df = pd.DataFrame(records)
        df['datetime'] = pd.to_datetime(df['datetime'])
        return df

    def load_weather_data(self, df, db_url):
        try:
            engine = create_engine(db_url)
            df.to_sql('weather_data', engine, if_exists='replace', index=False)
        except Exception as e:
            messagebox.showerror("Error", f"No se pudo guardar los datos en la base de datos: {e}")

class AnalysisWindow:
    def __init__(self, root, df):
        self.df = df
        self.root = root
        self.root.title("Análisis Climático")
        
        # Ajustar tamaño de la ventana secundaria al 20% de la pantalla y centrar
        self.resize_and_center_window(self.root, 0.20)

        # Botón para mostrar gráfico de temperatura
        self.plot_button = tk.Button(root, text="Mostrar Gráfico de Temperatura", command=self.plot_temperature)
        self.plot_button.pack(pady=10)

        # Botón para mostrar resumen de datos
        self.summary_button = tk.Button(root, text="Mostrar Resumen de Datos", command=self.show_summary)
        self.summary_button.pack(pady=10)

    def resize_and_center_window(self, window, percent):
        screen_width = window.winfo_screenwidth()
        screen_height = window.winfo_screenheight()
        width = int(screen_width * percent)
        height = int(screen_height * percent)
        x = (screen_width - width) // 2
        y = (screen_height - height) // 2
        window.geometry(f"{width}x{height}+{x}+{y}")

    def plot_temperature(self):
        try:
            if 'datetime' in self.df.columns and 'temp' in self.df.columns:
                # Asegúrate de que las fechas están en el formato correcto
                self.df['datetime'] = pd.to_datetime(self.df['datetime'])
                if self.df.empty:
                    messagebox.showwarning("Warning", "El DataFrame está vacío.")
                    return
                if not {'temp', 'max_temp', 'min_temp'}.issubset(self.df.columns):
                    messagebox.showwarning("Warning", "Faltan columnas en los datos.")
                    return
                # Crear gráfico y guardarlo en un archivo
                ax = self.df.set_index('datetime')[['temp', 'max_temp', 'min_temp']].plot()
                plt.title('Tendencias de Temperatura')
                plt.xlabel('Fecha')
                plt.ylabel('Temperatura (°C)')
                plt.savefig('temperature_plot.png')  # Guarda el gráfico en un archivo
                plt.close()  # Cierra la figura para liberar memoria
                messagebox.showinfo("Info", "Gráfico guardado como 'temperature_plot.png'")
                # Opcional: abre el archivo para verificar
                webbrowser.open('temperature_plot.png')
            else:
                messagebox.showwarning("Warning", "Datos de temperatura no encontrados.")
        except Exception as e:
            messagebox.showerror("Error", f"Se produjo un error al mostrar el gráfico: {e}")

    def show_summary(self):
        try:
            summary = self.df.describe().transpose()
            summary_window = tk.Toplevel(self.root)
            summary_window.title("Resumen de Datos")
            summary_text = scrolledtext.ScrolledText(summary_window, width=80, height=20)
            summary_text.pack(pady=10, padx=10)
            summary_text.insert(tk.END, summary.to_string())
            summary_text.config(state=tk.DISABLED)
        except Exception as e:
            messagebox.showerror("Error", f"Se produjo un error al mostrar el resumen de datos: {e}")

if __name__ == "__main__":
    root = tk.Tk()
    app = WeatherApp(root)
    root.mainloop()
