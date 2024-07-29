import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import os
from sklearn.linear_model import LogisticRegression, LinearRegression 
from sklearn.metrics import r2_score, mean_squared_error
from sklearn.preprocessing import PolynomialFeatures
from sklearn.tree import DecisionTreeClassifier
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import StandardScaler
from sklearn.pipeline import make_pipeline
import numpy as np

# Function to load the CSV file
@st.cache_data
def load_data(file):
    data = pd.read_csv(file)
    return data

# Function to display and save descriptive statistics
def display_descriptive_stats(data, biomarker):
    st.write(f"## Estadísticas Descriptivas para {biomarker}")
    stats = data[biomarker].describe()
    st.write(stats)
    
    # Save descriptive statistics to Excel file
    stats_df = pd.DataFrame(stats).reset_index()
    stats_df.columns = ['Estadística', 'Valor']
    stats_filename = os.path.join(os.getcwd(), f"{biomarker}_descriptive_stats.xlsx")
    stats_df.to_excel(stats_filename, index=False)
    st.write(f"Estadísticas descriptivas guardadas en {stats_filename}")
    
    st.write("### Descripción y Explicación del Gráfico")
    st.write(f"Las estadísticas descriptivas para el biomarcador **{biomarker}** incluyen las siguientes medidas:")
    st.write("- **Recuento (count):** El número total de observaciones.")
    st.write("- **Media (mean):** El valor promedio del biomarcador.")
    st.write("- **Desviación estándar (std):** Una medida de la dispersión de los datos respecto a la media.")
    st.write("- **Mínimo (min):** El valor más bajo del biomarcador.")
    st.write("- **25% (Q1):** El primer cuartil, es decir, el valor debajo del cual se encuentra el 25% de las observaciones.")
    st.write("- **50% (mediana):** El valor medio del biomarcador, donde el 50% de las observaciones están por debajo y el 50% están por encima.")
    st.write("- **75% (Q3):** El tercer cuartil, donde el 75% de las observaciones están por debajo.")
    st.write("- **Máximo (max):** El valor más alto del biomarcador.")
    st.write("Estas medidas nos proporcionan una visión general de la distribución y variabilidad del biomarcador en la muestra de datos.")

# Function to display and save a histogram
def display_histogram(data, biomarker):
    st.write(f"## Histograma para {biomarker}")
    fig, ax = plt.subplots()
    sns.histplot(data[biomarker], kde=True, ax=ax)
    st.pyplot(fig)
    
    # Save histogram to PNG file
    hist_filename = os.path.join(os.getcwd(), f"{biomarker}_histogram.png")
    fig.savefig(hist_filename)
    st.write(f"Histograma guardado en {hist_filename}")
    
    st.write("### Descripción y Explicación del Gráfico")
    st.write(f"El histograma para el biomarcador **{biomarker}** muestra la distribución de sus valores en diferentes intervalos. La línea suave (KDE) superpuesta proporciona una estimación de la densidad de la distribución. Este gráfico es útil para visualizar cómo se distribuyen los valores del biomarcador y para identificar patrones como la simetría, la asimetría y la presencia de valores atípicos.")

# Function to display and save a box plot
def display_box_plot(data, biomarker):
    st.write(f"## Diagrama de Caja para {biomarker}")
    fig, ax = plt.subplots()
    sns.boxplot(x=data[biomarker], ax=ax)
    st.pyplot(fig)
    
    # Save box plot to PNG file
    box_filename = os.path.join(os.getcwd(), f"{biomarker}_box_plot.png")
    fig.savefig(box_filename)
    st.write(f"Diagrama de caja guardado en {box_filename}")
    
    st.write("### Descripción y Explicación del Gráfico")
    st.write(f"El diagrama de caja para el biomarcador **{biomarker}** visualiza la distribución de los datos a través de sus cuartiles. Los elementos clave del diagrama de caja incluyen:")
    st.write("- **Caja:** Representa el rango intercuartil (IQR), que contiene el 50% medio de los datos.")
    st.write("- **Línea dentro de la caja:** Indica la mediana de los datos.")
    st.write("- **Bigotes:** Se extienden hasta los valores mínimos y máximos que no son considerados atípicos.")
    st.write("- **Puntos fuera de los bigotes:** Representan valores atípicos.")
    st.write("Este gráfico es útil para identificar la simetría de la distribución, detectar valores atípicos y comparar la dispersión entre diferentes grupos de datos.")

# Function to display and save scatter plots
def display_scatter_and_age_plot(data, biomarker):
    st.write(f"## Diagrama de Dispersión (Edad vs {biomarker})")

    # Scatter plot with Age on X-axis and Biomarker on Y-axis
    fig, ax = plt.subplots(figsize=(12, 6))
    sns.scatterplot(x='Age', y=biomarker, data=data, ax=ax, color='green')
    sns.regplot(x='Age', y=biomarker, data=data, ax=ax, scatter=False, color='red', line_kws={"linewidth":2})
    ax.set_xlabel('Edad')
    ax.set_ylabel(biomarker)
    st.pyplot(fig)
    
    # Save scatter plot to PNG file
    scatter_filename = os.path.join(os.getcwd(), f"{biomarker}_scatter_plot.png")
    fig.savefig(scatter_filename)
    st.write(f"Diagrama de dispersión con Edad vs {biomarker} guardado en {scatter_filename}")
    
    st.write("### Descripción y Explicación del Gráfico")
    st.write(f"El diagrama de dispersión muestra la relación entre la **Edad** y el biomarcador **{biomarker}**. Cada punto azul representa un individuo en el conjunto de datos. La línea roja es una línea de regresión que indica la tendencia general de la relación entre la edad y el biomarcador. Este gráfico es útil para identificar patrones y relaciones lineales entre dos variables numéricas.")

# Function to perform and display polynomial regression results
def display_polynomial_regression(data, predictor, target, degree):
    st.write(f"## Análisis de Regresión Polinómica (Grado {degree}) ({predictor} vs {target})")
    
    # Prepare the data
    X = data[[predictor]]
    y = data[target]
    
    # Eliminate rows with NaN values
    valid_data = data[[predictor, target]].dropna()
    X = valid_data[[predictor]]
    y = valid_data[target]
    
    # Transform features to polynomial features
    poly = PolynomialFeatures(degree=degree)
    X_poly = poly.fit_transform(X)
    
    # Fit the polynomial regression model
    model = LinearRegression()
    model.fit(X_poly, y)
    
    # Make predictions
    y_pred = model.predict(X_poly)
    
    # Calculate R-squared and MSE
    r2 = r2_score(y, y_pred)
    mse = mean_squared_error(y, y_pred)
    sqrt_r2 = np.sqrt(r2)
    
    # Display R-squared, sqrt(R-squared), and MSE
    st.write(f"R-cuadrado: {r2}")
    st.write(f"Raíz cuadrada de R-cuadrado: {sqrt_r2}")
    st.write(f"Error Cuadrático Medio: {mse}")
    
    # Plot the polynomial regression line
    fig, ax = plt.subplots(figsize=(12, 6))
    sns.scatterplot(x=predictor, y=target, data=valid_data, ax=ax, color='orange')
    
    # Sort values for plotting
    sorted_data = valid_data.sort_values(predictor)
    X_sorted = sorted_data[[predictor]]
    X_sorted_poly = poly.transform(X_sorted)
    y_sorted_pred = model.predict(X_sorted_poly)
    
    sns.lineplot(x=sorted_data[predictor], y=y_sorted_pred, ax=ax, color='red', linewidth=2)
    ax.set_xlabel(predictor)
    ax.set_ylabel(target)
    ax.set_title(f"Regresión Polinómica (Grado {degree}): {predictor} vs {target}")
    st.pyplot(fig)
    
    # Save regression plot to PNG file
    regression_filename = os.path.join(os.getcwd(), f"{target}_polynomial_regression_plot.png")
    fig.savefig(regression_filename)
    st.write(f"Gráfico de regresión polinómica guardado en {regression_filename}")
    
    st.write("### Descripción y Explicación del Análisis")
    st.write(f"En este análisis de regresión polinómica, se muestra la relación entre **{predictor}** y **{target}** utilizando un modelo polinómico de grado **{degree}**. La línea roja representa la predicción del modelo polinómico. Este análisis es útil para capturar relaciones no lineales entre las variables.")
    st.write("Las métricas de evaluación incluidas son:")
    st.write("- **R-cuadrado:** Indica la proporción de la variabilidad en la variable objetivo que es explicada por el modelo.")
    st.write("- **Raíz cuadrada de R-cuadrado:** Proporciona una medida más interpretable de la relación explicada.")
    st.write("- **Error Cuadrático Medio:** Mide la precisión de las predicciones realizadas por el modelo.")

# Function to calculate and display average of all biomarkers
def display_average_biomarkers(data):
    st.write("## Promedio de Todos los Biomarcadores")
    
    # Exclude columns 'Category', 'Unnamed: 0', and 'Sexo'
    exclude_columns = ['Category', 'Unnamed: 0', 'Sex']
    biomarker_data = data.drop(columns=exclude_columns, errors='ignore')
    
    # Select only numeric columns
    numeric_biomarkers = biomarker_data.select_dtypes(include=[np.number])
    
    # Calculate average of each biomarker
    biomarker_averages = numeric_biomarkers.mean()
    st.write(biomarker_averages)
    
    # Plot the averages
    fig, ax = plt.subplots(figsize=(12, 6))
    sns.barplot(x=biomarker_averages.index, y=biomarker_averages.values, ax=ax)
    ax.set_xlabel('Biomarcadores')
    ax.set_ylabel('Promedio')
    ax.set_title('Promedio de Todos los Biomarcadores')
    plt.xticks(rotation=90)
    st.pyplot(fig)
    
    # Save averages plot to PNG file
    averages_filename = os.path.join(os.getcwd(), "average_biomarkers_plot.png")
    fig.savefig(averages_filename)
    st.write(f"Gráfico de promedio de todos los biomarcadores guardado en {averages_filename}")
    
    st.write("### Descripción y Explicación del Gráfico")
    st.write("En este gráfico se muestra el promedio de cada biomarcador en el conjunto de datos. Cada barra representa el valor promedio de un biomarcador específico. Este análisis es útil para obtener una visión general de los niveles promedio de cada biomarcador y para identificar aquellos que pueden tener valores significativamente diferentes.")

# Function to display a heat map of selected biomarkers
def display_heatmap(data):
    st.write("## Heat Map de Biomarcadores Seleccionados")
    
    # Select only the desired biomarkers
    biomarkers = ['ALB', 'ALP', 'ALT', 'AST', 'BIL', 'CHE', 'CHOL', 'CREA', 'GGT', 'PROT']
    heatmap_data = data[biomarkers]
    
    # Compute the correlation matrix
    corr = heatmap_data.corr()
    
    # Plot the heatmap
    fig, ax = plt.subplots(figsize=(12, 6))
    sns.heatmap(corr, annot=True, cmap='coolwarm', ax=ax)
    st.pyplot(fig)
    
    # Save heatmap to PNG file
    heatmap_filename = os.path.join(os.getcwd(), "biomarkers_heatmap.png")
    fig.savefig(heatmap_filename)
    st.write(f"Heatmap guardado en {heatmap_filename}")
    
    st.write("### Descripción y Explicación del Heat Map")
    st.write("Este heat map muestra las correlaciones entre diferentes biomarcadores seleccionados. Las correlaciones pueden variar entre -1 y 1, donde los valores cercanos a 1 indican una fuerte correlación positiva, los valores cercanos a -1 indican una fuerte correlación negativa, y los valores cercanos a 0 indican una correlación débil o nula. Este gráfico es útil para identificar relaciones y patrones entre múltiples biomarcadores.")

# Function to train and predict using a machine learning model
def train_and_predict_model(data):
    st.write("## Predicción de Estado Basado en Biomarcadores")

    # Prepare data
    exclude_columns = ['Category', 'Unnamed: 0', 'Sex']
    feature_columns = [col for col in data.columns if col not in exclude_columns]
    X = data[feature_columns]
    y = data['Category']

    # Handle missing values by dropping rows with NaN values
    data = data.dropna(subset=feature_columns + ['Category'])
    X = data[feature_columns]
    y = data['Category']

    # Split data into train and test sets
    X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)

    # Train a Logistic Regression Classifier
    model = make_pipeline(StandardScaler(), LogisticRegression(random_state=42))
    model.fit(X_train, y_train)

    # Display model accuracy
    accuracy = model.score(X_test, y_test)
    st.write(f"Precisión del modelo: {accuracy:.2f}")

    # User input for biomarker values
    st.write("### Ingrese los valores de los biomarcadores para la predicción")
    user_input = {col: st.number_input(f"{col}", value=0.0) for col in feature_columns}

    # Convert user input to DataFrame
    user_input_df = pd.DataFrame([user_input])

    # Predict using the trained model
    prediction_prob = model.predict_proba(user_input_df)
    prediction = model.predict(user_input_df)
    
    # Display prediction probability
    probability_hepatitis_c = prediction_prob[0][1] * 100  # Convert to percentage
    st.write(f"Probabilidad de Hepatitis C: **{probability_hepatitis_c:.2f}%**")
    
    # Display heatmap of selected biomarkers
    display_heatmap(data)
    
    # Display average biomarkers
    display_average_biomarkers(data)

# Function to display comparison by category
def display_comparison_by_category(data, biomarker, category_column):
    st.write(f"## Comparación de {biomarker} por {category_column}")

    # Create a box plot for the comparison
    fig, ax = plt.subplots(figsize=(12, 6))
    sns.boxplot(x=category_column, y=biomarker, data=data, ax=ax)
    ax.set_xlabel(category_column)
    ax.set_ylabel(biomarker)
    ax.set_title(f"Comparación de {biomarker} por {category_column}")
    st.pyplot(fig)
    
    # Save the comparison plot to PNG file
    comparison_filename = os.path.join(os.getcwd(), f"{biomarker}_comparison_by_{category_column}.png")
    fig.savefig(comparison_filename)
    st.write(f"Gráfico de comparación guardado en {comparison_filename}")
    
    st.write("### Descripción y Explicación del Gráfico")
    st.write(f"El diagrama de caja compara el biomarcador **{biomarker}** entre las diferentes categorías de **{category_column}**. Cada caja representa la distribución del biomarcador en cada categoría, permitiendo observar diferencias y patrones entre categorías.")

# Streamlit UI
st.title("Análisis de Biomarcadores en Pacientes con Hepatitis C")

# Check if 'analysis_mode' exists in session_state, if not initialize it
if 'analysis_mode' not in st.session_state:
    st.session_state.analysis_mode = False

if 'diagnosis_mode' not in st.session_state:
    st.session_state.diagnosis_mode = False

# Handle file upload
uploaded_file = st.file_uploader("Elija un archivo CSV", type="csv")

if uploaded_file is not None:
    data = load_data(uploaded_file)
    
    col1, col2 = st.columns([1, 1])
    with col1:
        if st.button("Modelo de Análisis"):
            st.session_state.analysis_mode = True
            st.session_state.diagnosis_mode = False
    with col2:
        if st.button("Diagnosticar"):
            st.session_state.analysis_mode = False
            st.session_state.diagnosis_mode = True

# Display data preview and analysis if analysis_mode is True
if st.session_state.analysis_mode:
    st.write("### Vista Previa de los Datos")
    st.dataframe(data)

    # Filter out 'Unnamed: 0' columns
    columns = [col for col in data.columns if col != 'Unnamed: 0']

    # Selectors for columns
    desc_column = st.selectbox("Seleccione una columna para las estadísticas descriptivas", columns)
    predictor = st.selectbox("Seleccione la columna predictora", columns)
    target = st.selectbox("Seleccione la columna objetivo", columns)
    
    # Ensure predictor and target are not the same
    if predictor == target:
        st.error("La columna predictora y la columna objetivo no pueden ser el mismo biomarcador.")
    else:
        # Display descriptive statistics and plots
        display_descriptive_stats(data, desc_column)
        display_histogram(data, desc_column)
        display_box_plot(data, desc_column)
        display_scatter_and_age_plot(data, desc_column)
        
        # Polynomial regression
        degree = st.slider("Seleccione el Grado de la Regresión Polinómica", 1, 150, 2)
        display_polynomial_regression(data, predictor, target, degree)
        
        # Comparison by category
        mode = st.selectbox("Seleccionar modo de análisis", ["Comparación por Categoría", "Árbol de Decisión"])
        if mode == "Comparación por Categoría":
            category_column = st.selectbox("Seleccione la columna de Categoría", [col for col in data.columns if col != 'Category'])
            biomarker_for_comparison = st.selectbox("Seleccione el biomarcador para comparar", columns)
            display_comparison_by_category(data, biomarker_for_comparison, category_column)

# Display average biomarkers if diagnosis_mode is True
if st.session_state.diagnosis_mode:
    st.write("### Vista Previa de los Datos")
    st.dataframe(data)
    
    # Display average biomarkers and heatmap
    


    # Run the prediction model
    train_and_predict_model(data)