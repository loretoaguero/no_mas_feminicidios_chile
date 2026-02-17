# No Más Feminicidios Chile

Este proyecto consolida, limpia y visualiza datos de feminicidios en Chile a partir de fuentes públicas (Google Sheets) y los presenta de forma interactiva usando Streamlit.

## Estructura del proyecto

- `main.py`: Descarga, limpia y consolida los datos desde Google Sheets.
- `data_utils.py`: Funciones utilitarias para limpieza y normalización de datos.
- `consolidated_data.pkl`: Archivo pickle con los datos consolidados y listos para análisis.
- `streamlit_app.py`: Aplicación Streamlit para análisis interactivo y visualización de los datos.
- `assets/`: Imágenes y recursos gráficos para la app.
- `requirements.txt`: Dependencias necesarias para reproducir el entorno.

## Instalación

1. Clona el repositorio y entra a la carpeta del proyecto.
2. (Opcional) Crea y activa un entorno virtual:
   ```sh
   python3 -m venv venv
   source venv/bin/activate
   ```
3. Instala las dependencias:
   ```sh
   pip install -r requirements.txt
   ```

## Uso

### 1. Consolidar y limpiar datos

Ejecuta el script principal para descargar y limpiar los datos:
```sh
python main.py
```
Esto generará/actualizará el archivo `consolidated_data.pkl`.

### 2. Ejecutar la app interactiva

Lanza la aplicación Streamlit:
```sh
streamlit run streamlit_app.py
```

La app permite:
- Filtrar por región, categoría, tipificación penal, relación víctima-femicida y año.
- Visualizar métricas, gráficos de barras y heatmaps de nombres.
- Explorar los datos filtrados en tabla.

## Personalización
- Puedes modificar los filtros y visualizaciones en `streamlit_app.py`.
- Para agregar nuevas fuentes de datos, edita el diccionario `google_sheets` en `main.py`.

## Créditos y fuentes
- Datos originales: Red Chilena contra la Violencia hacia las Mujeres, SernamEG, Poder Judicial, entre otros.
- Visualización: Streamlit, Plotly.

## Licencia
Uso académico y sin fines de lucro. Cita la fuente si reutilizas el código o los datos.
