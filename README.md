# SolemneUSS — Análisis y presentación de datos utilizando APIs en Python

Proyecto de análisis de datos del mercado laboral en Chile, desarrollado como parte de la asignatura **FITO9017** de la **Universidad San Sebastián**.

## Descripción

La aplicación obtiene datos de la **Encuesta Nacional de Empleo (ENE)** publicados en el portal de datos abiertos del gobierno de Chile ([datos.gob.cl](https://datos.gob.cl/dataset/encuesta-nacional-de-empleo-ene)) mediante una consulta GET a la API CKAN y los presenta de forma interactiva a través de una aplicación web desarrollada con Streamlit.

### Funcionalidades

- Consulta en tiempo real a la API REST pública de `datos.gob.cl`.
- Análisis de las tasas de desocupación, ocupación y participación laboral.
- Filtros interactivos por **año**, **región** y **sexo**.
- Visualizaciones con **matplotlib**:
  - Evolución temporal de la tasa de desocupación.
  - Comparación regional.
  - Brecha de género en desocupación.
- Tabla de datos filtrada con opción de descarga CSV.
- Panel JSON con la metadata del dataset obtenida desde la API.

## Librerías utilizadas

| Librería | Uso |
|-----------|-----|
| `requests` | Consultas GET a la API REST de datos.gob.cl |
| `json` | Parseo y formateo de respuestas JSON de la API |
| `pandas` | Análisis y procesamiento de los datos |
| `matplotlib` | Generación de gráficos y visualizaciones |
| `streamlit` | Desarrollo de la aplicación web interactiva |

## Fuente de datos

- **Portal**: [datos.gob.cl](https://datos.gob.cl/group) — Datos abiertos del gobierno de Chile.
- **Dataset**: [Encuesta Nacional de Empleo (ENE) — INE](https://datos.gob.cl/dataset/encuesta-nacional-de-empleo-ene).
- **Acceso**: API CKAN — endpoint `GET /api/3/action/package_show`.

## Instalación y ejecución local

### Prerequisitos

- Python 3.9 o superior.

### Pasos

1. Clona el repositorio:
   ```bash
   git clone https://github.com/fvrandecic/SolemneUSS.git
   cd SolemneUSS
   ```

2. Crea un entorno virtual e instala las dependencias:
   ```bash
   python -m venv venv
   source venv/bin/activate   # En Windows: venv\Scripts\activate
   pip install -r requirements.txt
   ```

3. Ejecuta la aplicación:
   ```bash
   streamlit run app.py
   ```

4. Abre el navegador en `http://localhost:8501`.

> **Nota**: si la API de datos.gob.cl no se encuentra disponible, la aplicación mostrará un aviso y desplegará datos de demostración estadísticamente representativos de la metodología ENE.
