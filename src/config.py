"""
config.py
Configuración central del proyecto
"""

import os
from dotenv import load_dotenv

# Cargar variables de entorno
load_dotenv()

# API Key
API_KEY = os.getenv('ANTHROPIC_API_KEY')

# Archivos y directorios
DICCIONARIO_FILE = 'diccionario_normalizaciones.json'
INPUT_FILE = 'datos/hubspot_export.csv'
OUTPUT_FILE = 'datos/datos_limpios.csv'
LOG_FILE = 'logs/ejecucion.log'
BACKUP_DIR = 'backups'

# Universidades guatemaltecas conocidas
UNIVERSIDADES_GT = {
    'usac': 'Universidad de San Carlos de Guatemala (USAC)',
    'san carlos': 'Universidad de San Carlos de Guatemala (USAC)',
    'universidad de san carlos': 'Universidad de San Carlos de Guatemala (USAC)',
    'url': 'Universidad Rafael Landívar',
    'landivar': 'Universidad Rafael Landívar',
    'rafael landivar': 'Universidad Rafael Landívar',
    'landívar': 'Universidad Rafael Landívar',
    'umg': 'Universidad Mariano Gálvez',
    'mariano galvez': 'Universidad Mariano Gálvez',
    'mariano gálvez': 'Universidad Mariano Gálvez',
    'galileo': 'Universidad Galileo',
    'ufm': 'Universidad Francisco Marroquín',
    'francisco marroquin': 'Universidad Francisco Marroquín',
    'francisco marroquín': 'Universidad Francisco Marroquín',
    'uvg': 'Universidad del Valle de Guatemala',
    'valle': 'Universidad del Valle de Guatemala',
    'da vinci': 'Universidad Da Vinci',
    'davinci': 'Universidad Da Vinci',
    'mesoamericana': 'Universidad Mesoamericana',
    'umes': 'Universidad Mesoamericana',
    'panamericana': 'Universidad Panamericana',
    'upana': 'Universidad Panamericana',
    'rural': 'Universidad Rural',
    'del istmo': 'Universidad del Istmo',
    'istmo': 'Universidad del Istmo',
}

# Colegios que NO son universidades
COLEGIOS_NO_UNIVERSITARIOS = {
    'valle colonial',
    'valle colonial colegio',
    'colegio valle colonial'
}

# Respuestas inválidas
RESPUESTAS_INVALIDAS = [
    'no', 'ninguno', 'ninguna', 'no estudio', 'no estoy estudiando',
    'no aplica', 'n/a', 'na', 'no tengo', 'ya me gradué', 'graduado',
    'terminado', 'solo necesito información', 'hola', 'saludos',
    'diseño grafico', 'diseño gráfico', 'ingenieria', 'ingeniería',
    'certificado en', 'perito en', 'maestria', 'maestría', 'licenciatura'
]

# Siglas ambiguas
SIGLAS_AMBIGUAS = [
    'igs', 'mo', 'itce', 'insar', 'altiplano', 'ecc', 'xd',
    'fase', 'usar', 'aub no', 'graduated from', 'ex alumna', 'educate'
]

# Instituciones que NO son colegios
NO_SON_COLEGIOS = [
    'instituto nacional de seguros',
    'instituto guatemalteco de seguridad social',
    'asociación grupo ceiba',
    'cooperativa',
    'aden business school'
]

# Mapeo de formularios a carreras
MAPEO_FORMULARIOS = {
    'form lic administracion': 'Administración de Empresas',
    'form lic marketing': 'International Marketing and Business Analytics',
    'form ing administracion': 'Ciencia de la Administración',
    'conoce la licenciatura en administracion': 'Administración de Empresas',
    'conoce la licenciatura en administración': 'Administración de Empresas',
}

# Patrones de URLs
URL_PATTERNS = {
    'Administración de Empresas': [
        'administracion-empresas',
        'licenciatura-administracion',
        'lic-administracion',
        'webinar-conoce-licenciatura-en-administracion',
        'conoce-la-licenciatura-en-administracion',
        'lic%2badministracion',
        'form-lic-administracion',
        'promoting-form-lic-administracion'
    ],
    'Ciencia de la Administración': [
        'ingenieria-ciencia-administracion',
        'ingenieria-administracion',
        'ciencia-administracion',
        'ing-administracion',
        'ing%2badministracion',
        'form-ing-administracion',
        'promoting-form-ing-administracion'
    ],
    'International Marketing and Business Analytics': [
        'marketing-analytics',
        'licenciatura-marketing',
        'international-marketing',
        'lic-marketing',
        'lic%2bmarketing',
        'form-lic-marketing',
        'promoting-form-lic-marketing'
    ],
    'Comunicación Estratégica': [
        'comunicacion-estrategica',
        'licenciatura-comunicacion',
        'comunicacion/',
        'lic-comunicacion'
    ],
    'Maestrías': [
        'maestria',
        'master-',
        '/master',
        'maestrias'
    ]
}

# Casos especiales de URLs que son "Otro"
URL_CASOS_OTRO = [
    'facebook.com',
    'fb.com',
    'instagram.com',
    'gracias-ok',
    'thank-you',
    'thank_you',
    'lead_ads_forms',
    'publishing_tools',
    'form_uvg_bridge'
]


def crear_carpetas():
    """Crea las carpetas necesarias si no existen"""
    import os
    os.makedirs('datos', exist_ok=True)
    os.makedirs('logs', exist_ok=True)
    os.makedirs(BACKUP_DIR, exist_ok=True)