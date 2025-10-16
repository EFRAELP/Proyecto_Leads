"""
NORMALIZADOR DE LEADS - HubSpot 
VERSIÓN MEJORADA CON CLASIFICACIÓN DE URLs ROBUSTA
Automatiza la limpieza y normalización de datos de leads
"""

import pandas as pd
import json
import os
import shutil
import re
from datetime import datetime
from anthropic import Anthropic
from rapidfuzz import fuzz
from dotenv import load_dotenv

# Cargar variables de entorno (API key)
load_dotenv()

# Configuración
API_KEY = os.getenv('ANTHROPIC_API_KEY')
DICCIONARIO_FILE = 'diccionario_normalizaciones.json'
INPUT_FILE = 'datos/hubspot_export.csv'
OUTPUT_FILE = 'datos/datos_limpios.csv'
LOG_FILE = 'logs/ejecucion.log'
BACKUP_DIR = 'backups'

# Crear carpetas si no existen
os.makedirs('datos', exist_ok=True)
os.makedirs('logs', exist_ok=True)
os.makedirs(BACKUP_DIR, exist_ok=True)

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

# ⭐ NUEVO: Colegios que NO son universidades (se clasifican como "Otro")
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

class NormalizadorLeads:
    def __init__(self):
        self.client = Anthropic(api_key=API_KEY) if API_KEY else None
        self.diccionario = self.cargar_diccionario()
        self.tokens_usados = 0
        self.normalizaciones_nuevas = []
        self.urls_nuevas = []
        self.formularios_nuevos = []
    
    def log(self, mensaje):
        """Registra mensajes en consola y archivo"""
        timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        log_msg = f"[{timestamp}] {mensaje}"
        print(mensaje)
        
        try:
            with open(LOG_FILE, 'a', encoding='utf-8') as f:
                f.write(log_msg + '\n')
        except Exception as e:
            print(f"⚠️ Error al escribir log: {e}")
    
    def cargar_diccionario(self):
        """Carga el diccionario de normalizaciones previas"""
        if os.path.exists(DICCIONARIO_FILE):
            try:
                with open(DICCIONARIO_FILE, 'r', encoding='utf-8') as f:
                    diccionario = json.load(f)
                    if 'urls' not in diccionario:
                        diccionario['urls'] = {}
                    if 'formularios' not in diccionario:
                        diccionario['formularios'] = {}
                    return diccionario
            except:
                pass
        
        return {
            'colegios': {},
            'grados': {},
            'urls': {},
            'formularios': {}
        }
    
    def guardar_diccionario(self):
        """Guarda el diccionario actualizado con backup"""
        if os.path.exists(DICCIONARIO_FILE):
            timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
            backup_name = f'diccionario_backup_{timestamp}.json'
            backup_path = os.path.join(BACKUP_DIR, backup_name)
            
            try:
                shutil.copy2(DICCIONARIO_FILE, backup_path)
                self.log(f"💾 Backup creado: {backup_name}")
            except Exception as e:
                self.log(f"⚠️ No se pudo crear backup: {e}")
            
            self.limpiar_backups_antiguos()
        
        with open(DICCIONARIO_FILE, 'w', encoding='utf-8') as f:
            json.dump(self.diccionario, indent=2, ensure_ascii=False, fp=f)
        
        total_colegios = len(self.diccionario.get('colegios', {}))
        total_urls = len(self.diccionario.get('urls', {}))
        total_forms = len(self.diccionario.get('formularios', {}))
        
        self.log(f"✅ Diccionario guardado:")
        self.log(f"   • {total_colegios} colegios")
        self.log(f"   • {total_urls} URLs")
        self.log(f"   • {total_forms} formularios")
    
    def limpiar_backups_antiguos(self, max_backups=10):
        """Mantiene solo los últimos N backups"""
        try:
            backups = [f for f in os.listdir(BACKUP_DIR) if f.startswith('diccionario_backup_')]
            backups.sort(reverse=True)
            
            for backup in backups[max_backups:]:
                backup_path = os.path.join(BACKUP_DIR, backup)
                os.remove(backup_path)
                self.log(f"🗑️ Backup antiguo eliminado: {backup}")
        except Exception as e:
            self.log(f"⚠️ Error al limpiar backups: {e}")
    
    def es_sigla_ambigua(self, texto):
        """Detecta siglas ambiguas"""
        if not texto or pd.isna(texto):
            return False
        
        texto_limpio = str(texto).strip().lower()
        
        if len(texto_limpio) <= 3 and texto_limpio not in ['usac', 'url', 'umg', 'ufm', 'uvg']:
            return True
        
        return texto_limpio in SIGLAS_AMBIGUAS
    
    def fuzzy_match(self, texto, categoria):
        """Fuzzy matching en diccionario"""
        if not texto or pd.isna(texto):
            return None
            
        texto_limpio = str(texto).strip().lower()
        diccionario_cat = self.diccionario.get(categoria, {})
        
        mejor_match = None
        mejor_score = 0
        
        for key in diccionario_cat.keys():
            score = fuzz.ratio(texto_limpio, key.lower())
            if score > mejor_score:
                mejor_score = score
                mejor_match = key
        
        if mejor_score > 85:
            return diccionario_cat[mejor_match]
        
        return None
    
    def detectar_respuesta_invalida(self, texto):
        """Detecta respuestas inválidas"""
        if not texto or pd.isna(texto):
            return True
        
        texto_limpio = str(texto).strip().lower()
        
        if len(texto_limpio) < 2:
            return True
        
        if texto_limpio in RESPUESTAS_INVALIDAS:
            return True
        
        frases_invalidas = [
            'no estudio', 'no estoy', 'ninguno', 'ya me gradué',
            'solo necesito', 'trabajo en', 'certificado en'
        ]
        if any(frase in texto_limpio for frase in frases_invalidas):
            return True
        
        return False
    
    def buscar_universidad_conocida(self, texto):
        """Busca universidades guatemaltecas"""
        if not texto or pd.isna(texto):
            return None
        
        texto_limpio = str(texto).strip().lower()
        
        # ⭐ NUEVA VERIFICACIÓN: Verificar si es un colegio que NO es universidad
        if texto_limpio in COLEGIOS_NO_UNIVERSITARIOS:
            self.log(f"⚠️ No es universidad: '{texto}' → 'Otro'")
            return None
        
        if texto_limpio in UNIVERSIDADES_GT:
            return UNIVERSIDADES_GT[texto_limpio]
        
        for key, universidad in UNIVERSIDADES_GT.items():
            if key in texto_limpio or texto_limpio in key:
                return universidad
        
        mejor_match = None
        mejor_score = 0
        
        for key, universidad in UNIVERSIDADES_GT.items():
            score = fuzz.ratio(texto_limpio, key)
            if score > mejor_score and score > 75:
                mejor_score = score
                mejor_match = universidad
        
        return mejor_match
    
    def normalizar_con_claude(self, texto, tipo):
        """Usa Claude API para normalizar"""
        if not self.client:
            self.log("⚠️ No hay API key")
            return texto
        
        prompts = {
            'colegio': f"""Nombre de institución: "{texto}"

REGLAS:
1. Si NO estudia → "Otro"
2. Si es UNIVERSIDAD → Nombre oficial
3. Si es COLEGIO → Nombre limpio
4. Si es ambiguo → nombre original

SOLO el nombre normalizado, sin explicaciones.""",
            'grado': f"""Grado académico: "{texto}"

REGLAS:
- 3ro Básico, 2do Básico, etc.
- 4to Diversificado, 5to Diversificado, 6to Diversificado
- Estudiante Universitario
- Graduado Diversificado

SOLO el grado normalizado."""
        }
        
        try:
            self.log(f"🤖 Consultando Claude: '{texto}'")
            
            response = self.client.messages.create(
                model="claude-sonnet-4-20250514",
                max_tokens=150,
                messages=[{
                    "role": "user",
                    "content": prompts.get(tipo, texto)
                }]
            )
            
            self.tokens_usados += response.usage.input_tokens + response.usage.output_tokens
            
            normalizado = response.content[0].text.strip()
            normalizado = self.validar_respuesta_claude(texto, normalizado)
            
            return normalizado
            
        except Exception as e:
            self.log(f"❌ Error Claude: {e}")
            return texto
    
    def validar_normalizacion(self, original, propuesta, tipo):
        """Valida normalización con usuario"""
        print(f"\n{'='*60}")
        print(f"📝 {tipo.upper()}")
        print(f"Original: {original}")
        print(f"Propuesta: {propuesta}")
        print(f"{'='*60}")
        print("\n1. Aceptar propuesta")
        print("2. Ingresar manualmente")
        print("3. Marcar como 'Otro'")
        
        while True:
            respuesta = input("\nSelecciona (1-3): ").strip()
            
            if respuesta == '1':
                return propuesta
            elif respuesta == '2':
                manual = input("Ingresa el nombre correcto: ").strip()
                return manual if manual else propuesta
            elif respuesta == '3':
                return "Otro"
            else:
                print("⚠️ Opción inválida")
    
    def detectar_no_es_colegio(self, texto):
        """Detecta si NO es un colegio"""
        if not texto or pd.isna(texto):
            return False
        
        texto_limpio = str(texto).strip().lower()
        
        for institucion in NO_SON_COLEGIOS:
            if institucion in texto_limpio:
                return True
        
        return False
    
    def normalizar_colegio(self, colegio, modo_validacion=True):
        """Normaliza nombre de colegio"""
        if not colegio or pd.isna(colegio):
            return "Otro"
        
        colegio_str = str(colegio).strip()
        if not colegio_str:
            return "Otro"
        
        if self.detectar_respuesta_invalida(colegio_str):
            self.log(f"⚠️ Respuesta inválida: '{colegio_str}' → 'Otro'")
            self.diccionario['colegios'][colegio_str] = 'Otro'
            return "Otro"
        
        if self.detectar_no_es_colegio(colegio_str):
            self.log(f"⚠️ No es colegio: '{colegio_str}' → 'Otro'")
            self.diccionario['colegios'][colegio_str] = 'Otro'
            return "Otro"
        
        if colegio_str in self.diccionario['colegios']:
            return self.diccionario['colegios'][colegio_str]
        
        universidad = self.buscar_universidad_conocida(colegio_str)
        if universidad:
            self.log(f"🎓 Universidad: '{colegio_str}' → '{universidad}'")
            self.diccionario['colegios'][colegio_str] = universidad
            self.normalizaciones_nuevas.append(f"Colegio: {colegio_str} → {universidad}")
            return universidad
        
        match = self.fuzzy_match(colegio_str, 'colegios')
        if match:
            self.log(f"✓ Fuzzy match: '{colegio_str}' → '{match}'")
            return match
        
        if self.es_sigla_ambigua(colegio_str):
            self.log(f"🔍 Sigla ambigua: '{colegio_str}'")
            if modo_validacion:
                normalizado = self.validar_normalizacion(
                    colegio_str,
                    colegio_str,
                    'colegio (SIGLA AMBIGUA)'
                )
                self.diccionario['colegios'][colegio_str] = normalizado
                self.normalizaciones_nuevas.append(f"Colegio (sigla): {colegio_str} → {normalizado}")
                return normalizado
            else:
                return colegio_str
        
        normalizado = self.normalizar_con_claude(colegio_str, 'colegio')
        
        if modo_validacion:
            normalizado = self.validar_normalizacion(colegio_str, normalizado, 'colegio')
        
        self.diccionario['colegios'][colegio_str] = normalizado
        self.normalizaciones_nuevas.append(f"Colegio: {colegio_str} → {normalizado}")
        
        return normalizado
    
    def normalizar_grado(self, grado):
        """Normaliza grado académico"""
        if not grado or pd.isna(grado):
            return "Sin especificar"
        
        grado_str = str(grado).strip()
        if not grado_str:
            return "Sin especificar"
        
        grado_lower = grado_str.lower()
        
        if 'universitario' in grado_lower or 'universidad' in grado_lower:
            return "Estudiante Universitario"
        
        match = re.search(r'(\d+)', grado_lower)
        if match:
            numero = match.group(1)
            
            if any(palabra in grado_lower for palabra in ['bachillerato', 'perito', 'diversificado']):
                if numero == '4':
                    return "4to Diversificado"
                elif numero == '5':
                    return "5to Diversificado"
                elif numero == '6':
                    return "6to Diversificado"
            
            if 'basico' in grado_lower or 'básico' in grado_lower:
                if numero == '1':
                    return "1ro Básico"
                elif numero == '2':
                    return "2do Básico"
                elif numero == '3':
                    return "3ro Básico"
        
        if 'graduado' in grado_lower and 'diversificado' in grado_lower:
            return "Graduado Diversificado"
        
        if grado_str in self.diccionario['grados']:
            return self.diccionario['grados'][grado_str]
        
        normalizado = grado_str
        self.diccionario['grados'][grado_str] = normalizado
        return normalizado
    
    def unificar_columnas(self, df):
        """Unifica columnas duplicadas"""
        self.log("\n🔄 Unificando columnas...")
        
        # Unificar Grado Académico
        grado_cols = [col for col in df.columns if col == 'Grado Académico' or col.startswith('Grado Académico.')]
        
        if len(grado_cols) >= 2:
            df['Grado_Temp'] = df[grado_cols[0]].fillna('').astype(str)
            df.loc[df['Grado_Temp'] == '', 'Grado_Temp'] = df[grado_cols[1]].fillna('')
            df['___GRADO_UNIFICADO___'] = df['Grado_Temp']
            df.drop('Grado_Temp', axis=1, inplace=True)
            self.log(f"✅ Unificadas: {grado_cols[0]} + {grado_cols[1]}")
        elif len(grado_cols) == 1:
            df['___GRADO_UNIFICADO___'] = df[grado_cols[0]].fillna('')
            self.log(f"✅ Una columna de grado: {grado_cols[0]}")
        else:
            df['___GRADO_UNIFICADO___'] = ''
            self.log("⚠️ No se encontró Grado Académico")
        
        # Unificar Colegio
        colegio_col1 = 'Colegio Actual'
        colegio_col2 = 'En qué colegio estudias actualmente?'
        
        if colegio_col1 in df.columns:
            df['Colegio_Temp1'] = df[colegio_col1].fillna('').astype(str)
        else:
            df['Colegio_Temp1'] = ''
            
        if colegio_col2 in df.columns:
            df['Colegio_Temp2'] = df[colegio_col2].fillna('').astype(str)
        else:
            df['Colegio_Temp2'] = ''
        
        df['___COLEGIO_UNIFICADO___'] = df['Colegio_Temp1']
        df.loc[df['___COLEGIO_UNIFICADO___'] == '', '___COLEGIO_UNIFICADO___'] = df['Colegio_Temp2']
        
        df.drop(['Colegio_Temp1', 'Colegio_Temp2'], axis=1, inplace=True)
        
        self.log("✅ Columnas unificadas")
        return df
    
    def extraer_primer_form(self, texto):
        """Extrae el primer formulario de un texto con múltiples forms"""
        if not texto or pd.isna(texto):
            return "Otro"
        
        texto_str = str(texto).strip().lower()
        
        if ';' in texto_str:
            forms = [f.strip() for f in texto_str.split(';')]
            forms = [f for f in forms if f and f != '.elementor-form' and 'elementor' not in f]
            if forms:
                return forms[0]
        
        if '.elementor-form' not in texto_str:
            return texto_str
        
        return "Otro"
    
    def preguntar_carrera_form(self, form_name):
        """Pregunta al usuario a qué carrera pertenece un formulario"""
        print(f"\n{'='*60}")
        print(f"📝 FORMULARIO NO RECONOCIDO")
        print(f"Formulario: {form_name}")
        print(f"{'='*60}")
        print("\n¿A qué carrera pertenece?")
        print("1. Administración de Empresas")
        print("2. Ciencia de la Administración")
        print("3. International Marketing and Business Analytics")
        print("4. Comunicación Estratégica")
        print("5. Maestrías")
        print("6. Sin especificar")
        
        while True:
            respuesta = input("\nSelecciona (1-6): ").strip()
            
            carreras = {
                '1': 'Administración de Empresas',
                '2': 'Ciencia de la Administración',
                '3': 'International Marketing and Business Analytics',
                '4': 'Comunicación Estratégica',
                '5': 'Maestrías',
                '6': 'Sin especificar'
            }
            
            if respuesta in carreras:
                carrera = carreras[respuesta]
                
                if 'formularios' not in self.diccionario:
                    self.diccionario['formularios'] = {}
                self.diccionario['formularios'][form_name.lower()] = carrera
                
                self.log(f"✅ Formulario mapeado: '{form_name}' → '{carrera}'")
                self.formularios_nuevos.append(f"Form: {form_name} → {carrera}")
                
                return carrera
            else:
                print("⚠️ Opción inválida. Selecciona 1-6.")
    
    def mapear_form_a_carrera(self, form, modo_interactivo=True):
        """Mapea formulario a carrera"""
        if not form or pd.isna(form) or form == "Otro":
            return None
        
        form_str = str(form).strip().lower()
        
        # Buscar en diccionario de formularios
        if 'formularios' in self.diccionario and form_str in self.diccionario['formularios']:
            return self.diccionario['formularios'][form_str]
        
        # Buscar en mapeo predefinido
        for key, carrera in MAPEO_FORMULARIOS.items():
            if key in form_str:
                if 'formularios' not in self.diccionario:
                    self.diccionario['formularios'] = {}
                self.diccionario['formularios'][form_str] = carrera
                return carrera
        
        # Si contiene "uvg bridge" no mapear (ya tiene carrera)
        if 'uvg bridge' in form_str or 'bridge' in form_str:
            return None
        
        # Si es modo interactivo, preguntar
        if modo_interactivo:
            return self.preguntar_carrera_form(form)
        
        return None
    
    def categorizar_url(self, url, modo_interactivo=True):
        """Categoriza URL por palabras clave - VERSIÓN MEJORADA"""
        if not url or pd.isna(url):
            return "Otro"
        
        url_str = str(url).strip().lower()
        
        if not url_str:
            return "Otro"
        
        # 1. Buscar en diccionario
        if 'urls' in self.diccionario and url_str in self.diccionario['urls']:
            return self.diccionario['urls'][url_str]
        
        # 2. Patrones de clasificación
        patterns = {
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
        
        # 3. Casos especiales "Otro"
        casos_otro = [
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
        
        for caso in casos_otro:
            if caso in url_str:
                return 'Otro'
        
        # 4. Buscar coincidencias
        for carrera, patrones_carrera in patterns.items():
            for patron in patrones_carrera:
                if patron in url_str:
                    if 'urls' not in self.diccionario:
                        self.diccionario['urls'] = {}
                    self.diccionario['urls'][url_str] = carrera
                    return carrera
        
        # 5. Bridge Principal
        if 'uvgbridge.gt' in url_str:
            tiene_carrera = False
            for patrones_carrera in patterns.values():
                if any(patron in url_str for patron in patrones_carrera):
                    tiene_carrera = True
                    break
            
            if not tiene_carrera:
                if re.search(r'uvgbridge\.gt/?(\?|$)', url_str):
                    return 'Bridge Principal'
        
        # 6. Modo interactivo
        if modo_interactivo and 'uvgbridge.gt' in url_str:
            return self.preguntar_categoria_url(url_str)
        
        return 'Otro'
    
    def preguntar_categoria_url(self, url):
        """Pregunta al usuario a qué categoría pertenece una URL"""
        print(f"\n{'='*60}")
        print(f"🔗 URL NO RECONOCIDA")
        print(f"URL: {url}")
        print(f"{'='*60}")
        print("\n¿A qué categoría pertenece?")
        print("1. Administración de Empresas")
        print("2. Ciencia de la Administración")
        print("3. International Marketing and Business Analytics")
        print("4. Comunicación Estratégica")
        print("5. Maestrías")
        print("6. Bridge Principal")
        print("7. Otro")
        
        while True:
            respuesta = input("\nSelecciona (1-7): ").strip()
            
            categorias = {
                '1': 'Administración de Empresas',
                '2': 'Ciencia de la Administración',
                '3': 'International Marketing and Business Analytics',
                '4': 'Comunicación Estratégica',
                '5': 'Maestrías',
                '6': 'Bridge Principal',
                '7': 'Otro'
            }
            
            if respuesta in categorias:
                categoria = categorias[respuesta]
                
                if 'urls' not in self.diccionario:
                    self.diccionario['urls'] = {}
                self.diccionario['urls'][url] = categoria
                
                self.log(f"✅ URL categorizada: '{url}' → '{categoria}'")
                self.urls_nuevas.append(f"URL: {url} → {categoria}")
                return categoria
            else:
                print("⚠️ Opción inválida. Selecciona 1-7.")
    
    def validar_respuesta_claude(self, texto_original, normalizado):
        """Valida que Claude no haya respondido con texto de sistema"""
        if len(normalizado) > 150:
            self.log(f"⚠️ Respuesta muy larga: '{texto_original}' → 'Otro'")
            return "Otro"
        
        frases_sistema = [
            'estoy listo para', 'por favor proporciona',
            'entendido', 'necesito más información',
            'no puedo', 'dame más contexto'
        ]
        
        normalizado_lower = normalizado.lower()
        for frase in frases_sistema:
            if frase in normalizado_lower:
                self.log(f"⚠️ Respuesta de sistema: '{texto_original}' → 'Otro'")
                return "Otro"
        
        if normalizado.count('\n') > 2:
            self.log(f"⚠️ Respuesta con formato: '{texto_original}' → 'Otro'")
            return "Otro"
        
        return normalizado
    
    def procesar_leads(self, modo_validacion=True):
        """Proceso principal"""
        self.log("\n" + "="*60)
        self.log("🚀 INICIANDO NORMALIZACIÓN")
        self.log("="*60)
        
        # 1. Leer CSV
        self.log(f"\n📂 Leyendo: {INPUT_FILE}")
        try:
            df = pd.read_csv(INPUT_FILE, encoding='utf-8')
            self.log(f"✅ Leído: {len(df)} leads")
        except Exception as e:
            self.log(f"❌ Error: {e}")
            return
        
        # 2. Unificar columnas
        df = self.unificar_columnas(df)
        
        # 3. Normalizar colegios
        self.log("\n🏫 Normalizando colegios...")
        colegios_unicos = df['___COLEGIO_UNIFICADO___'].unique()
        colegios_unicos = [c for c in colegios_unicos if c and str(c).strip()]
        
        self.log(f"Colegios únicos: {len(colegios_unicos)}")
        
        for idx, colegio in enumerate(colegios_unicos):
            validar = modo_validacion and idx < 20
            self.normalizar_colegio(colegio, modo_validacion=validar)
        
        df['___COLEGIO_NORMALIZADO___'] = df['___COLEGIO_UNIFICADO___'].apply(
            lambda x: self.normalizar_colegio(x, modo_validacion=False)
        )
        
        # 4. Normalizar grados
        self.log("\n🎓 Normalizando grados...")
        df['___GRADO_NORMALIZADO___'] = df['___GRADO_UNIFICADO___'].apply(self.normalizar_grado)
        
        # 5. Procesar formularios
        self.log("\n📝 Procesando formularios...")
        if 'Associated Form Submission' in df.columns:
            df['___FORM_LIMPIO___'] = df['Associated Form Submission'].apply(self.extraer_primer_form)
        else:
            df['___FORM_LIMPIO___'] = 'Otro'
        
        if modo_validacion:
            self.log("\n🎓 Identificando formularios...")
            formularios_unicos = df['___FORM_LIMPIO___'].unique()
            formularios_unicos = [f for f in formularios_unicos if f and f != "Otro" and str(f).strip()]
            
            self.log(f"Formularios únicos: {len(formularios_unicos)}")
            
            for form in formularios_unicos:
                self.mapear_form_a_carrera(form, modo_interactivo=True)
        
        # 6. Completar Carrera
        self.log("\n🎯 Completando Carrera de Interés...")
        if 'Carrera de Interés' in df.columns:
            def completar_carrera(row):
                carrera_actual = row.get('Carrera de Interés', '')
                
                if carrera_actual and str(carrera_actual).strip() and str(carrera_actual) != 'nan':
                    return carrera_actual
                
                form_limpio = row.get('___FORM_LIMPIO___', '')
                carrera_mapeada = self.mapear_form_a_carrera(form_limpio, modo_interactivo=False)
                
                if carrera_mapeada:
                    return carrera_mapeada
                
                return "Sin especificar"
            
            df['___CARRERA_COMPLETADA___'] = df.apply(completar_carrera, axis=1)
        
        # 7. Identificar URLs
        if modo_validacion:
            self.log("\n🔗 Identificando URLs...")
            urls_first = df['First Page Seen'].dropna().unique() if 'First Page Seen' in df.columns else []
            urls_last = df['Last Page Seen'].dropna().unique() if 'Last Page Seen' in df.columns else []
            urls_unicas = set(list(urls_first) + list(urls_last))
            
            self.log(f"URLs únicas: {len(urls_unicas)}")
            
            for url in urls_unicas:
                self.categorizar_url(url, modo_interactivo=True)
        
        # 8. Categorizar URLs
        self.log("\n🔗 Categorizando URLs...")
        if 'First Page Seen' in df.columns:
            df['___PRIMERA_PAGINA___'] = df['First Page Seen'].apply(
                lambda x: self.categorizar_url(x, modo_interactivo=False)
            )
        if 'Last Page Seen' in df.columns:
            df['___ULTIMA_PAGINA___'] = df['Last Page Seen'].apply(
                lambda x: self.categorizar_url(x, modo_interactivo=False)
            )
        
        # 9. Reemplazar columnas originales
        grado_cols = [col for col in df.columns if col == 'Grado Académico' or col.startswith('Grado Académico.')]
        if grado_cols:
            df[grado_cols[0]] = df['___GRADO_NORMALIZADO___']
            self.log(f"✅ Reemplazada: {grado_cols[0]}")
            
            if len(grado_cols) > 1:
                for col_duplicada in grado_cols[1:]:
                    df.drop(col_duplicada, axis=1, inplace=True)
                    self.log(f"✅ Eliminada: {col_duplicada}")
        
        if 'Colegio Actual' in df.columns:
            df['Colegio Actual'] = df['___COLEGIO_NORMALIZADO___']
            self.log("✅ Reemplazada: Colegio Actual")
        
        if 'En qué colegio estudias actualmente?' in df.columns:
            df.drop('En qué colegio estudias actualmente?', axis=1, inplace=True)
            self.log("✅ Eliminada columna redundante")
        
        if 'Associated Form Submission' in df.columns:
            df['Associated Form Submission'] = df['___FORM_LIMPIO___']
            self.log("✅ Reemplazada: Associated Form Submission")
        
        if 'Carrera de Interés' in df.columns and '___CARRERA_COMPLETADA___' in df.columns:
            df['Carrera de Interés'] = df['___CARRERA_COMPLETADA___']
            self.log("✅ Reemplazada: Carrera de Interés")
        
        if 'First Page Seen' in df.columns and '___PRIMERA_PAGINA___' in df.columns:
            df['First Page Seen'] = df['___PRIMERA_PAGINA___']
            self.log("✅ Reemplazada: First Page Seen")
        if 'Last Page Seen' in df.columns and '___ULTIMA_PAGINA___' in df.columns:
            df['Last Page Seen'] = df['___ULTIMA_PAGINA___']
            self.log("✅ Reemplazada: Last Page Seen")
        
        # 10. Eliminar columnas temporales
        columnas_temporales = [
            '___ES_NUEVO___', '___COLEGIO_UNIFICADO___', '___COLEGIO_NORMALIZADO___',
            '___GRADO_UNIFICADO___', '___GRADO_NORMALIZADO___', '___FORM_LIMPIO___',
            '___CARRERA_COMPLETADA___', '___PRIMERA_PAGINA___', '___ULTIMA_PAGINA___'
        ]
        df.drop([c for c in columnas_temporales if c in df.columns], axis=1, inplace=True)
        
        # 11. Guardar resultado
        self.log(f"\n💾 Guardando: {OUTPUT_FILE}")
        df.to_csv(OUTPUT_FILE, index=False, encoding='utf-8-sig')
        
        # 12. Guardar diccionario
        self.log("\n💾 Guardando diccionario...")
        self.guardar_diccionario()
        
        # 13. Resumen
        self.log("\n" + "="*60)
        self.log("✅ PROCESO COMPLETADO")
        self.log("="*60)
        self.log(f"📊 Leads procesados: {len(df)}")
        self.log(f"🆕 Normalizaciones (colegios): {len(self.normalizaciones_nuevas)}")
        self.log(f"🔗 URLs categorizadas: {len(self.urls_nuevas)}")
        self.log(f"📝 Formularios mapeados: {len(self.formularios_nuevos)}")
        self.log(f"🤖 Tokens usados: {self.tokens_usados}")
        costo = (self.tokens_usados / 1_000_000) * 3
        self.log(f"💰 Costo: ${costo:.4f}")
        
        if self.normalizaciones_nuevas:
            self.log("\n📝 NUEVAS NORMALIZACIONES:")
            for norm in self.normalizaciones_nuevas:
                self.log(f"  • {norm}")
        
        if self.urls_nuevas:
            self.log("\n🔗 NUEVAS URLs:")
            for url in self.urls_nuevas:
                self.log(f"  • {url}")
        
        if self.formularios_nuevos:
            self.log("\n📝 NUEVOS FORMULARIOS:")
            for form in self.formularios_nuevos:
                self.log(f"  • {form}")
        
        self.log(f"\n✅ Archivo guardado: {OUTPUT_FILE}")
        self.log("🎉 ¡Listo para Power BI!")

def main():
    print("""
╔═══════════════════════════════════════════════════════════╗
║  NORMALIZADOR DE LEADS - URLs Mejoradas                  ║
╚═══════════════════════════════════════════════════════════╝
    """)
    
    if not os.path.exists(INPUT_FILE):
        print(f"❌ ERROR: No se encontró {INPUT_FILE}")
        input("\nPresiona Enter para salir...")
        return
    
    if not os.getenv('ANTHROPIC_API_KEY'):
        print("❌ ERROR: No se encontró ANTHROPIC_API_KEY")
        input("\nPresiona Enter para salir...")
        return
    
    print("\n¿Validar normalizaciones?")
    print("s = Sí (recomendado)")
    print("n = No (automático)")
    
    while True:
        respuesta = input("\nValidar (s/n): ").lower().strip()
        if respuesta == 's':
            validar = True
            break
        elif respuesta == 'n':
            validar = False
            break
        else:
            print("⚠️ Respuesta inválida.")
    
    normalizador = NormalizadorLeads()
    normalizador.procesar_leads(modo_validacion=validar)
    
    input("\n\nPresiona Enter para salir...")

if __name__ == "__main__":
    main()