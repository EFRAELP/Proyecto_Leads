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
    'urural': 'Universidad Rural',
    'del istmo': 'Universidad del Istmo',
    'istmo': 'Universidad del Istmo',
    # ⭐ NUEVO: Universidad Regional
    'regional': 'Universidad Regional',
    'universidad regional': 'Universidad Regional',
}

# ⭐ Colegios conocidos con nombres exactos
COLEGIOS_CONOCIDOS = {
    'iga': 'Instituto Guatemalteco Americano (IGA)',
    'instituto guatemalteco americano': 'Instituto Guatemalteco Americano (IGA)',
    'ipga': 'Instituto Privado Guatemala Americano (IPGA)',
    'instituto privado guatemala americano': 'Instituto Privado Guatemala Americano (IPGA)',
    'kinal': 'Centro Educativo Técnico Laboral Kinal',
    'centro educativo tecnico laboral kinal': 'Centro Educativo Técnico Laboral Kinal',
    'imence': 'Instituto Mixto de Enseñanza IMENCE',
    'linsa': 'Liceo Integral del Norte LINSA',
    # ⭐ NUEVOS: Casos específicos que identificaste
    'insar': 'Otro',
    'usar': 'Otro',
    'ecc': 'Otro',
    'itv': 'Otro',
    'ccb': 'Otro',
    'valle colonial': 'Otro',
    'campo alto': 'Campo Alto',
    'educate': 'Otro',
    'edúcate': 'Otro',
    'aden': 'Otro',
}

# ⭐ Colegios específicos que tienen nombres similares a universidades
# Estos deben verificarse ANTES de clasificar como universidad
COLEGIOS_ESPECIFICOS = {
    'instituto rafael landivar': 'Instituto Rafael Landívar',
    'instituto rafael landívar': 'Instituto Rafael Landívar',
    'instituto rafael landival': 'Instituto Rafael Landívar',
    'instituto rafael landibal': 'Instituto Rafael Landívar',
    'colegio rafael landivar': 'Instituto Rafael Landívar',
    'colegio rafael landívar': 'Instituto Rafael Landívar',
    'colegio rafael landival': 'Instituto Rafael Landívar',
}

# Colegios que NO son universidades
COLEGIOS_NO_UNIVERSITARIOS = {
    'valle colonial',
    'valle colonial colegio',
    'colegio valle colonial'
}

# ⭐ Respuestas inválidas (EXPANDIDO)
RESPUESTAS_INVALIDAS = [
    # Originales
    'no', 'ninguno', 'ninguna', 'no estudio', 'no estoy estudiando',
    'no aplica', 'n/a', 'na', 'no tengo', 'ya me gradué', 'graduado',
    'terminado', 'solo necesito información', 'hola', 'saludos',
    'diseño grafico', 'diseño gráfico', 'ingenieria', 'ingeniería',
    'certificado en', 'perito en', 'maestria', 'maestría', 'licenciatura',
    # ⭐ NUEVOS - Casos identificados
    'xd', 'aub no', 'hola hay', 'hay maestria', 'hay maestría',
    'ahorita no tengo', 'no tengo oportunidad',
    'universidad completa', 'ya tengo universidad',
    'ya tengo maestria', 'ya tengo maestría',
    'graduada', 'graduado',
    'perito', 'tecnico', 'técnico',
    'colegio publico', 'colegio público',
    'no estudio ya me gradue', 'no estudio ya me gradué',
    'este año no estoy estudiando', 'aun no estudio', 'aún no estudio',
    'trabajo en', 'no estoy estudiando por motivos',
]

# ⭐ Siglas ambiguas (MANTENIDO)
SIGLAS_AMBIGUAS = [
    'igs', 'mo', 'itce', 'insar', 'altiplano', 'ecc', 'xd',
    'fase', 'usar', 'aub no', 'graduated from', 'ex alumna', 'educate'
]

# ⭐ NUEVO: Siglas que se deben expandir (para usar con web_search)
SIGLAS_EXPANDIBLES = [
    'iga', 'ipga', 'imence', 'linsa', 'imb-pc', 'igs', 
    'iemcoop', 'isea', 'ced-ieca', 'ineb', 'ined'
]

# Instituciones que NO son colegios
NO_SON_COLEGIOS = [
    'instituto nacional de seguros',
    'instituto guatemalteco de seguridad social',
    'asociación grupo ceiba',
    'cooperativa',
    'aden business school'
]

# Patrones de nombres de colegios
PATRONES_COLEGIO = [
    'liceo', 'instituto', 'colegio', 'escuela', 'centro educativo'
]

# Mapeo de formularios a carreras
MAPEO_FORMULARIOS = {
    'form lic administracion': 'Administración de Empresas',
    'form lic marketing': 'International Marketing and Business Analytics',
    'form ing administracion': 'Ciencia de la Administración',
    'conoce la licenciatura en administracion': 'Administración de Empresas',
    'conoce la licenciatura en administración': 'Administración de Empresas',
}

# ⭐ Mapeo de carreras del CSV (con underscores)
MAPEO_CARRERAS_CSV = {
    'ingeniería_en_administración_de_empresas': 'Ciencia de la Administración',
    'ingenieria_en_administracion_de_empresas': 'Ciencia de la Administración',
    'ciencia_de_la_administración': 'Ciencia de la Administración',
    'ciencia_de_la_administracion': 'Ciencia de la Administración',
    'licenciatura_en_international_marketing': 'International Marketing and Business Analytics',
    'international_marketing': 'International Marketing and Business Analytics',
    'marketing': 'International Marketing and Business Analytics',
    'administración_de_empresas': 'Administración de Empresas',
    'administracion_de_empresas': 'Administración de Empresas',
    'licenciatura_en_administración_de_empresas': 'Administración de Empresas',
    'licenciatura_en_administracion_de_empresas': 'Administración de Empresas',
    'comunicación_estratégica': 'Comunicación Estratégica',
    'comunicacion_estrategica': 'Comunicación Estratégica',
    'maestrías': 'Maestrías',
    'maestrias': 'Maestrías',
}

# Patrones de URLs
URL_PATTERNS = {
    'Administración de Empresas': [
        'administracion-empresas',
        'licenciatura-administracion',
        'lic-administracion',
        'lic+administracion',
        'lic%2badministracion',
        'form-lic-administracion',
        'promoting-form-lic-administracion',
        'webinar-conoce-licenciatura-en-administracion',
        'conoce-la-licenciatura-en-administracion',
    ],
    'Ciencia de la Administración': [
        'ingenieria-ciencia-administracion',
        'ingenieria-administracion',
        'ciencia-administracion',
        'ing-administracion',
        'ing%2badministracion',
        'form-ing-administracion',
        'promoting-form-ing-administracion',
    ],
    'International Marketing and Business Analytics': [
        'marketing-analytics',
        'licenciatura-marketing',
        'international-marketing',
        'lic-marketing',
        'lic%2bmarketing',
        'form-lic-marketing',
        'promoting-form-lic-marketing',
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

# Casos especiales que siempre son "Otro"
CASOS_OTRO_URL = [
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
    os.makedirs('datos', exist_ok=True)
    os.makedirs('logs', exist_ok=True)
    os.makedirs(BACKUP_DIR, exist_ok=True)