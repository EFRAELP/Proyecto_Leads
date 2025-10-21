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

    # ⭐ NUEVAS VARIANTES AGREGADAS
    'itec uvg': 'Universidad del Valle de Guatemala',
    'itec altiplano': 'Universidad del Valle de Guatemala',
    'itec uvg altiplano': 'Universidad del Valle de Guatemala',
    'itec uvg campus altiplano': 'Universidad del Valle de Guatemala',
    'uvg altiplano': 'Universidad del Valle de Guatemala',
    'uvg sur': 'Universidad del Valle de Guatemala',
    'san pablo': 'Universidad de San Pablo de Guatemala',
    'san pablo de guatemala': 'Universidad de San Pablo de Guatemala',

}

# ⭐ Colegios conocidos con nombres exactos (se mantiene todo lo existente)
COLEGIOS_CONOCIDOS = {
    # Colegios importantes que NO deben ser marcados como "Otro"
    'iga': 'Instituto Guatemalteco Americano (IGA)',
    'instituto guatemalteco americano': 'Instituto Guatemalteco Americano (IGA)',
    'ined': 'Instituto Nacional de Educación Diversificada (INED)',
    'instituto nacional de educación diversificada': 'Instituto Nacional de Educación Diversificada (INED)',
    'ineb': 'Instituto Nacional de Educación Básica (INEB)',
    'instituto nacional de educación básica': 'Instituto Nacional de Educación Básica (INEB)',
    'don bosco': 'Colegio Don Bosco',
    'colegio don bosco': 'Colegio Don Bosco',
    'liceo javier': 'Liceo Javier',
    'javier': 'Liceo Javier',
    'american school': 'Colegio Americano',
    'colegio americano': 'Colegio Americano',
    'maya': 'Colegio Maya',
    'colegio maya': 'Colegio Maya',
    'liceo guatemala': 'Liceo Guatemala',
    'monte maría': 'Colegio Monte María',
    'colegio monte maría': 'Colegio Monte María',
    'kinal': 'Centro Educativo Técnico Laboral Kinal',
    'centro educativo tecnico laboral kinal': 'Centro Educativo Técnico Laboral Kinal',
    'imence': 'Instituto Mixto de Enseñanza IMENCE',
    'linsa': 'Liceo Integral del Norte LINSA',
    # ⭐ NUEVOS: Casos específicos que identificaste
    'insar': 'Otro',
    'usar': 'Otro',
    'ecc': 'Otro',
    'itv': 'Otro',
    'ccb': 'Colegio Colonial Bilingüe',
    'valle colonial': 'Otro',
    'campo alto': 'Campo Alto',
    'educate': 'Otro',
    'edúcate': 'Otro',
    'aden': 'ADEN International Business School',
}

# ⭐ COLEGIOS DE INTERÉS PRIORITARIO (Agregar después de las líneas existentes)
COLEGIOS_PRIORITARIOS = {
    # KINAL
    'kinal': 'Centro Educativo Técnico Laboral Kinal',
    'colegio kinal': 'Centro Educativo Técnico Laboral Kinal',
    'cetl kinal': 'Centro Educativo Técnico Laboral Kinal',
    'centro kinal': 'Centro Educativo Técnico Laboral Kinal',
    'centro educativo kinal': 'Centro Educativo Técnico Laboral Kinal',
    'tecnico laboral kinal': 'Centro Educativo Técnico Laboral Kinal',
    
    # INSTITUTO BELGA GUATEMALTECO
    'belga': 'Instituto Belga Guatemalteco',
    'instituto belga': 'Instituto Belga Guatemalteco',
    'belga guatemalteco': 'Instituto Belga Guatemalteco',
    
    # HEBRÓN
    'hebron': 'Colegio Hebrón',
    'hebrón': 'Colegio Hebrón',
    
    # EL VALLE
    'el valle': 'Centro Educativo El Valle',
    'centro valle': 'Centro Educativo El Valle',
    'centro educativo el valle': 'Centro Educativo El Valle',
    
    # DISCOVERY SCHOOL
    'discovery': 'Colegio Discovery School',
    'discovery school': 'Colegio Discovery School',
    
    # BETHANIA
    'bethania': 'Instituto Bethania',
    'instituto bethania': 'Instituto Bethania',
    
    # EDUCATE
    'educate': 'Colegio Bilingüe Educate',
    'bilingue educate': 'Colegio Bilingüe Educate',
    
    # SANTA TERESITA
    'santa teresita': 'Colegio Santa Teresita',
    
    # INTERNACIONES
    'internaciones': 'Colegio Internaciones',
    
    # CAPOUILLIEZ
    'capouilliez': 'Colegio Mixto Capouilliez',
    'mixto capouilliez': 'Colegio Mixto Capouilliez',
    'capouiliez': 'Colegio Mixto Capouilliez',
    
    # ALFREDO CARRILLO RAMÍREZ
    'alfredo carrillo': 'Escuela Normal de Maestras para Párvulos Alfredo Carrillo Ramírez',
    'alfredo carrillo ramirez': 'Escuela Normal de Maestras para Párvulos Alfredo Carrillo Ramírez',
    'normal parvulos': 'Escuela Normal de Maestras para Párvulos Alfredo Carrillo Ramírez',
    'normal de maestras': 'Escuela Normal de Maestras para Párvulos Alfredo Carrillo Ramírez',
    
    # LICEO GUATEMALA
    'liceo guatemala': 'Instituto Privado de Educación Diversificada Liceo Guatemala',
    
    # SAGRADO CORAZÓN
    'sagrado corazon': 'Colegio El Sagrado Corazón de Jesús',
    'sagrado corazon de jesus': 'Colegio El Sagrado Corazón de Jesús',
    'el sagrado corazon': 'Colegio El Sagrado Corazón de Jesús',
    
    # IGA (ya existe, pero agregar más variaciones)
    'guatemalteco americano': 'Instituto Guatemalteco Americano (IGA)',
    
    # MANOS A LA OBRA
    'manos a la obra': 'Colegio Bilingüe Manos a la Obra',
    'manos obra': 'Colegio Bilingüe Manos a la Obra',
    'caes': 'Colegio Bilingüe Manos a la Obra CAES',
    'manos a la obra caes': 'Colegio Bilingüe Manos a la Obra CAES',
    'manos a la obra roosevelt': 'Colegio Bilingüe Manos a la Obra Roosevelt',
    'manos obra roosevelt': 'Colegio Bilingüe Manos a la Obra Roosevelt',
    
    # EL SHADDAI (normalizar sin zona)
    'shaddai': 'Colegio Cristiano Bilingüe El Shaddai',
    'el shaddai': 'Colegio Cristiano Bilingüe El Shaddai',
    'cristiano el shaddai': 'Colegio Cristiano Bilingüe El Shaddai',
    
    # MONTANO CORTIJO
    'montano cortijo': 'Colegio Montano Cortijo',
    
    # ALEMÁN
    'aleman': 'Colegio Alemán de Guatemala',
    'colegio aleman': 'Colegio Alemán de Guatemala',
    
    # VIENA
    'viena': 'Colegio Viena Guatemalteco',
    'viena guatemalteco': 'Colegio Viena Guatemalteco',
    
    # CAMPO VERDE
    'campo verde': 'Colegio Bilingüe Campo Verde',
    
    # VERBO
    'verbo': 'Colegio Cristiano Verbo',
    'cristiano verbo': 'Colegio Cristiano Verbo',
    'experimental verbo': 'Colegio Cristiano Verbo',
    
    # AGUSTINIANO
    'agustiniano': 'Colegio Agustiniano',
    
    # AMERITEC
    'ameritec': 'Colegio Tecnológico Americano Ameritec',
    'tecnologico americano': 'Colegio Tecnológico Americano Ameritec',
    
    # MONTANO PORTAL
    'montano portal': 'Colegio Montano Portal Los Álamos',
    'portal los alamos': 'Colegio Montano Portal Los Álamos',
    
    # AMERICANO DEL SUR
    'americano del sur': 'Colegio Americano del Sur',
    'americano sur': 'Colegio Americano del Sur',
    
    # LEHNSEN
    'lehnsen': 'Colegio Lehnsen',
    
    # RICARDO BRESSANI
    'bressani': 'Liceo Dr. Ricardo Bressani',
    'ricardo bressani': 'Liceo Dr. Ricardo Bressani',
    'dr bressani': 'Liceo Dr. Ricardo Bressani',
    
    # VALLE DE OCCIDENTE
    'valle occidente': 'Colegio El Valle de Occidente',
    'valle de occidente': 'Colegio El Valle de Occidente',
    
    # LA ASUNCIÓN
    'la asuncion': 'Colegio La Asunción',
    'asuncion': 'Colegio La Asunción',
    
    # ROCA DE AYUDA
    'roca de ayuda': 'Liceo Cristiano Roca de Ayuda',
    'roca ayuda': 'Liceo Cristiano Roca de Ayuda',
    
    # EL PRADO
    'el prado': 'Colegio Bilingüe El Prado',
    'bilingue el prado': 'Colegio Bilingüe El Prado',
    
    # LA SALLE
    'la salle': 'Liceo La Salle',
    'liceo la salle': 'Liceo La Salle',
    'lasalle': 'Liceo La Salle',
    
    # FRATER
    'frater': 'Liceo Cristiano Frater',
    'cristiano frater': 'Liceo Cristiano Frater',
    
    # ESQUIPULTECO
    'esquipulteco': 'Liceo Esquipulteco Bilingüe',
    'liceo esquipulteco': 'Liceo Esquipulteco Bilingüe',
    
    # SAGRADO CORAZÓN EL NARANJO
    'sagrado corazon naranjo': 'Colegio de Señoritas El Sagrado Corazón El Naranjo',
    'el naranjo': 'Colegio de Señoritas El Sagrado Corazón El Naranjo',
    'señoritas el naranjo': 'Colegio de Señoritas El Sagrado Corazón El Naranjo',
    
    # INTELLEGO
    'intellego': 'Colegio Centro de Aprendizaje Intelecto Intellego',
    'intelecto': 'Colegio Centro de Aprendizaje Intelecto Intellego',
    'centro intelecto': 'Colegio Centro de Aprendizaje Intelecto Intellego',
    
    # BOSTON
    'boston': 'Colegio Boston',
    
    # TECNOLÓGICO BILINGÜE
    'tecnologico bilingue': 'Instituto Tecnológico Bilingüe',
    
    # COLONIAL BILINGÜE
    'colonial': 'Colegio Colonial Bilingüe',
    'colegio colonial': 'Colegio Colonial Bilingüe',
    'colonial bilingue': 'Colegio Colonial Bilingüe',
    
    # MAPLE BEAR
    'maple bear': 'Maple Bear',
    'maple': 'Maple Bear',
    
    # SAN FRANCISCO JAVIER
    'san francisco javier': 'Colegio San Francisco Javier',
    'francisco javier': 'Colegio San Francisco Javier',
    
    # SAN JOSÉ DE LOS INFANTES
    'san jose infantes': 'Colegio San José de los Infantes',
    'san jose de los infantes': 'Colegio San José de los Infantes',
    'infantes': 'Colegio San José de los Infantes',
    
    # MACDERMONT
    'macdermont': 'Colegio Mixto Bilingüe Macdermont',
    'bilingue macdermont': 'Colegio Mixto Bilingüe Macdermont',
    
    # IMB-PC
    'imb-pc': 'Colegio de Informática IMB-PC',
    'imb pc': 'Colegio de Informática IMB-PC',
    'imbpc': 'Colegio de Informática IMB-PC',
    'imb': 'Colegio de Informática IMB-PC',
    
    # GIBBS
    'gibbs': 'Colegio Gibbs',
    
    # CHRISTIAN AMERICAN SCHOOL
    'christian american': 'Colegio Christian American School of Guatemala',
    'cas guatemala': 'Colegio Christian American School of Guatemala',
    'cas': 'Colegio Christian American School of Guatemala',
    
    # CONTINENTAL AMERICANO
    'continental americano': 'Colegio Continental Americano',
    'continental': 'Colegio Continental Americano',
    
    # CED
    'ced': 'Centro de Estudios Diversificados CED',
    'centro estudios diversificados': 'Centro de Estudios Diversificados CED',
    
    # SAN MATEO
    'san mateo': 'Liceo Mixto San Mateo',
    'liceo san mateo': 'Liceo Mixto San Mateo',
    
    # EPIC
    'epic': 'Colegio Epic Guatemala',
    'epic guatemala': 'Colegio Epic Guatemala',
    
    # MARÍA AUXILIADORA
    'maria auxiliadora': 'Instituto María Auxiliadora',
    'auxiliadora': 'Instituto María Auxiliadora',
    
    # SUIZO
    'suizo': 'Colegio Privado Mixto Suizo Quetzaltenango',
    'colegio suizo': 'Colegio Privado Mixto Suizo Quetzaltenango',
    
    # JESÚS REY DE GLORIA
    'rey de gloria': 'Colegio Jesús Rey de Gloria',
    'jesus rey': 'Colegio Jesús Rey de Gloria',
    'jesus rey de gloria': 'Colegio Jesús Rey de Gloria',
    
    # CENTRO DE APRENDIZAJE BILINGÜE
    'cab': 'Centro de Aprendizaje Bilingüe',
    'centro aprendizaje bilingue': 'Centro de Aprendizaje Bilingüe',
    
    # AMERICANO SAN JUAN
    'americano san juan': 'Colegio Americano San Juan',
    
    # IEA
    'iea': 'Instituto de Estudios Avanzados (IEA)',
    'estudios avanzados': 'Instituto de Estudios Avanzados (IEA)',
    
    # VON HUMBOLDT
    'von humboldt': 'Colegio Von Humboldt',
    'humboldt': 'Colegio Von Humboldt',
    
    # SAGRADA FAMILIA
    'sagrada familia': 'Colegio Sagrada Familia',
    
    # NALEB
    'naleb': 'Colegio Naleb',
    
    # ASA - AFTER SCHOOL ACADEMY
    'asa': 'Centro Educativo ASA (After School Academy)',
    'after school academy': 'Centro Educativo ASA (After School Academy)',
    'after school': 'Centro Educativo ASA (After School Academy)',
    
    # INTECAP
    'intecap': 'INTECAP',
    
    # CAMPO ALTO
    'campo alto': 'Colegio Bilingüe Campo Alto',
    'bilingue campo alto': 'Colegio Bilingüe Campo Alto',
    'campo alto sur': 'Colegio Bilingüe Campo Alto Sur',
    
    # LA VID
    'la vid': 'Centro Educativo La Vid',
    'centro la vid': 'Centro Educativo La Vid',
    
    # CAMPO REAL
    'campo real': 'Colegio Bilingüe Campo Real',
    'bilingue campo real': 'Colegio Bilingüe Campo Real',
    
    # HOWARD GARDNER
    'howard gardner': 'Colegio Americano Howard Gardner',
    'colegio howard gardner': 'Colegio Americano Howard Gardner',
    'gardner': 'Colegio Americano Howard Gardner',
}

# ⭐ Agregar colegios prioritarios a COLEGIOS_CONOCIDOS
COLEGIOS_CONOCIDOS.update(COLEGIOS_PRIORITARIOS)
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


# Respuestas inválidas (EXPANDIDO)
RESPUESTAS_INVALIDAS = [
    # Originales
    'no', 'ninguno', 'ninguna', 'no estudio', 'no estoy estudiando',
    'no aplica', 'n/a', 'na', 'no tengo', 'ya me gradué', 'graduado',
    'terminado', 'solo necesito información', 'hola', 'saludos',
    'diseño grafico', 'diseño gráfico', 'ingenieria', 'ingeniería',
    'certificado en', 'perito en', 'maestria', 'maestría', 'licenciatura',
    # Casos adicionales
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

# Siglas ambiguas
SIGLAS_AMBIGUAS = [
    'igs', 'mo', 'itce', 'insar', 'altiplano', 'ecc', 'xd',
    'fase', 'usar', 'aub no', 'graduated from', 'ex alumna', 'educate'
]

# Siglas que se deben expandir
SIGLAS_EXPANDIBLES = [
    'iga', 'iemcoop', 'isea', 'ced-ieca', 'ineb', 'ined'
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

# Mapeo de carreras del CSV (con underscores)
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
    os.makedirs('datos', exist_ok=True)
    os.makedirs('logs', exist_ok=True)
    os.makedirs(BACKUP_DIR, exist_ok=True)


# ============================================================
# ⭐ NUEVAS CONSTANTES PARA NORMALIZACIÓN DE GRADOS ACADÉMICOS
# ============================================================

# Mapeo de números escritos en texto a dígitos
NUMEROS_TEXTO = {
    'primero': '1',
    'primer': '1',
    'primera': '1',
    'segundo': '2',
    'segunda': '2',
    'tercero': '3',
    'tercer': '3',
    'tercera': '3',
    'cuarto': '4',
    'cuarta': '4',
    'quinto': '5',
    'quinta': '5',
    'sexto': '6',
    'sexta': '6',
    'septimo': '7',  # Sin tilde porque se normalizan
    'septima': '7',
}

# Keywords para detectar estudiantes universitarios
KEYWORDS_UNIVERSITARIO = [
    'universidad',
    'universitario',
    'universitaria',
    'carrera',
    'facultad',
    'licenciatura',
    'ingenieria',  # Sin tilde
    'tecnico superior',
    'semestre',
    'ano',  # Sin tilde (año)
    'trimestre',
    'cuatrimestre',
    'bachelor',
    'pem',
    'profesor',
    'profesora',
    'maestria',  # Sin tilde
    'postgrado',
    'posgrado',
]

# Keywords para detectar graduación
KEYWORDS_GRADUADO = [
    'graduado',
    'graduada',
    'egresado',
    'egresada',
    'finalizado',
    'finalizada',
    'terminado',
    'terminada',
    'finalice',
    'termine',
    'gradue',  # Sin tilde
    'egrese',
]

# Keywords para detectar diversificado/bachillerato
KEYWORDS_DIVERSIFICADO = [
    'diversificado',
    'bachiller',
    'bachillerato',
    'bachi',
    'perito',
    'perita',
    'secretari',
    'magisterio',
]

# Keywords para detectar básico
KEYWORDS_BASICO = [
    'basico',  # Sin tilde
    'ciclo basico',
    'educacion basica',  # Sin tilde
]

# Patrones que indican valores de prueba/basura
PATRONES_BASURA = [
    'test',
    'prueba',
    'demo',
    'ejemplo',
    'aaa',
    'xxx',
    'asdf',
    'qwerty',
    'n/a',
    '---',
    '...',
]

# Opciones disponibles para validación manual de grados
GRADOS_OPCIONES = [
    "1ro. Básico",
    "2do. Básico",
    "3ro. Básico",
    "4to. Diversificado",
    "5to. Diversificado",
    "6to. Diversificado",
    "7mo. Diversificado",
    "Estudiante Universitario",
    "Graduado Diversificado",
    "Graduado Universitario",
    "Sin especificar",
]