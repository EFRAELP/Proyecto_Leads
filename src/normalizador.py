"""
normalizador.py
Clase principal del Normalizador de Leads
Orquesta todos los módulos para el procesamiento completo
"""

import os
import pandas as pd
import re
from datetime import datetime

# Importar todos los módulos
from . import config
from .logger import Logger
from .diccionario_manager import DiccionarioManager
from .validadores import Validadores
from .normalizador_claude import NormalizadorClaude
from .url_categorizer import URLCategorizer
from .form_mapper import FormMapper


class NormalizadorLeads:
    """Clase principal que orquesta la normalización de leads"""
    
    def __init__(self):
        """Inicializa todos los componentes del normalizador"""
        # Crear carpetas necesarias
        config.crear_carpetas()
        
        # Inicializar logger
        self.logger = Logger(config.LOG_FILE)
        
        # Inicializar gestor de diccionario
        self.dict_manager = DiccionarioManager(
            config.DICCIONARIO_FILE,
            config.BACKUP_DIR,
            self.logger
        )
        
        # Cargar diccionario
        self.diccionario = self.dict_manager.cargar_diccionario()
        
        # Inicializar validadores
        self.validadores = Validadores(config, self.logger)
        
        # Inicializar normalizador de Claude
        self.normalizador_claude = NormalizadorClaude(config.API_KEY, self.logger)
        
        # Inicializar categorizador de URLs
        self.url_categorizer = URLCategorizer(config, self.logger)
        
        # Inicializar mapeador de formularios
        self.form_mapper = FormMapper(config, self.logger)
        
        # Contadores y listas de seguimiento
        self.normalizaciones_nuevas = []
        self.urls_nuevas = []
        self.formularios_nuevos = []
    
    def unificar_columnas(self, df):
        """Unifica columnas duplicadas"""
        self.logger.log("\n🔄 Unificando columnas...")
        
        # Unificar Grado Académico
        grado_cols = [col for col in df.columns if col == 'Grado Académico' or col.startswith('Grado Académico.')]
        
        if len(grado_cols) >= 2:
            df['Grado_Temp'] = df[grado_cols[0]].fillna('').astype(str)
            df.loc[df['Grado_Temp'] == '', 'Grado_Temp'] = df[grado_cols[1]].fillna('')
            df['___GRADO_UNIFICADO___'] = df['Grado_Temp']
            df.drop('Grado_Temp', axis=1, inplace=True)
            self.logger.log(f"✅ Unificadas: {grado_cols[0]} + {grado_cols[1]}")
        elif len(grado_cols) == 1:
            df['___GRADO_UNIFICADO___'] = df[grado_cols[0]].fillna('')
            self.logger.log(f"✅ Una columna de grado: {grado_cols[0]}")
        else:
            df['___GRADO_UNIFICADO___'] = ''
            self.logger.log("⚠️ No se encontró Grado Académico")
        
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
        
        self.logger.log("✅ Columnas unificadas")
        return df
    
    def normalizar_colegio(self, colegio, modo_validacion=True):
        """Normaliza nombre de colegio"""
        if not colegio or pd.isna(colegio):
            return "Otro"
        
        colegio_str = str(colegio).strip()
        if not colegio_str:
            return "Otro"
        
        if self.validadores.detectar_respuesta_invalida(colegio_str):
            self.logger.log(f"⚠️ Respuesta inválida detectada: '{colegio_str}' → 'Otro'")
            self.diccionario['colegios'][colegio_str] = 'Otro'
            return "Otro"
        
        if self.validadores.detectar_no_es_colegio(colegio_str):
            self.logger.log(f"⚠️ No es un colegio detectado: '{colegio_str}' → 'Otro'")
            self.diccionario['colegios'][colegio_str] = 'Otro'
            return "Otro"
        
        if colegio_str in self.diccionario['colegios']:
            return self.diccionario['colegios'][colegio_str]
        
        universidad = self.validadores.buscar_universidad_conocida(colegio_str)
        if universidad:
            self.logger.log(f"🎓 Universidad detectada: '{colegio_str}' → '{universidad}'")
            self.diccionario['colegios'][colegio_str] = universidad
            self.normalizaciones_nuevas.append(f"Colegio: {colegio_str} → {universidad}")
            return universidad
        
        match = self.validadores.fuzzy_match(colegio_str, 'colegios', self.diccionario)
        if match:
            self.logger.log(f"✓ Fuzzy match: '{colegio_str}' → '{match}'")
            return match
        
        if self.validadores.es_sigla_ambigua(colegio_str):
            self.logger.log(f"🔍 Sigla ambigua detectada: '{colegio_str}'")
            if modo_validacion:
                normalizado = self.normalizador_claude.validar_normalizacion(
                    colegio_str,
                    colegio_str,
                    'colegio (SIGLA AMBIGUA)'
                )
                self.diccionario['colegios'][colegio_str] = normalizado
                self.normalizaciones_nuevas.append(f"Colegio (sigla): {colegio_str} → {normalizado}")
                return normalizado
            else:
                return colegio_str
        
        normalizado = self.normalizador_claude.normalizar_con_claude(colegio_str, 'colegio')
        
        if modo_validacion:
            normalizado = self.normalizador_claude.validar_normalizacion(colegio_str, normalizado, 'colegio')
        
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
    
    def procesar_leads(self, modo_validacion=True):
        """Proceso principal de normalización"""
        self.logger.log("\n" + "="*60)
        self.logger.log("🚀 INICIANDO NORMALIZACIÓN")
        self.logger.log("="*60)
        
        # 1. Leer CSV
        self.logger.log(f"\n📂 Leyendo: {config.INPUT_FILE}")
        try:
            df = pd.read_csv(config.INPUT_FILE, encoding='utf-8')
            self.logger.log(f"✅ Leído: {len(df)} leads")
        except Exception as e:
            self.logger.log(f"❌ Error: {e}")
            return
        
        # 2. Unificar columnas
        df = self.unificar_columnas(df)
        
        # 3. Normalizar colegios
        self.logger.log("\n🏫 Normalizando colegios...")
        colegios_unicos = df['___COLEGIO_UNIFICADO___'].unique()
        colegios_unicos = [c for c in colegios_unicos if c and str(c).strip()]
        
        self.logger.log(f"Colegios únicos: {len(colegios_unicos)}")
        
        for idx, colegio in enumerate(colegios_unicos):
            validar = modo_validacion and idx < 20
            self.normalizar_colegio(colegio, modo_validacion=validar)
        
        df['___COLEGIO_NORMALIZADO___'] = df['___COLEGIO_UNIFICADO___'].apply(
            lambda x: self.normalizar_colegio(x, modo_validacion=False)
        )
        
        # 4. Normalizar grados
        self.logger.log("\n🎓 Normalizando grados académicos...")
        df['___GRADO_NORMALIZADO___'] = df['___GRADO_UNIFICADO___'].apply(self.normalizar_grado)
        
        # 5. Procesar formularios
        self.logger.log("\n📝 Procesando Associated Form Submission...")
        if 'Associated Form Submission' in df.columns:
            df['___FORM_LIMPIO___'] = df['Associated Form Submission'].apply(self.form_mapper.extraer_primer_form)
        else:
            df['___FORM_LIMPIO___'] = 'Otro'
        
        if modo_validacion:
            self.logger.log("\n🎓 Identificando formularios únicos...")
            formularios_unicos = df['___FORM_LIMPIO___'].unique()
            formularios_unicos = [f for f in formularios_unicos if f and f != "Otro" and str(f).strip()]
            
            self.logger.log(f"Formularios únicos encontrados: {len(formularios_unicos)}")
            
            for form in formularios_unicos:
                self.form_mapper.mapear_form_a_carrera(
                    form, 
                    self.diccionario, 
                    self.formularios_nuevos, 
                    modo_interactivo=True
                )
        
        # 6. Completar Carrera
        self.logger.log("\n🎯 Completando Carrera de Interés...")
        if 'Carrera de Interés' in df.columns:
            def completar_carrera(row):
                carrera_actual = row.get('Carrera de Interés', '')
                
                if carrera_actual and str(carrera_actual).strip() and str(carrera_actual) != 'nan':
                    return carrera_actual
                
                form_limpio = row.get('___FORM_LIMPIO___', '')
                carrera_mapeada = self.form_mapper.mapear_form_a_carrera(
                    form_limpio,
                    self.diccionario,
                    self.formularios_nuevos,
                    modo_interactivo=False
                )
                
                if carrera_mapeada:
                    return carrera_mapeada
                
                return "Sin especificar"
            
            df['___CARRERA_COMPLETADA___'] = df.apply(completar_carrera, axis=1)
        
        # 7. Identificar URLs
        if modo_validacion:
            self.logger.log("\n🔗 Identificando URLs únicas...")
            urls_first = df['First Page Seen'].dropna().unique() if 'First Page Seen' in df.columns else []
            urls_last = df['Last Page Seen'].dropna().unique() if 'Last Page Seen' in df.columns else []
            urls_unicas = set(list(urls_first) + list(urls_last))
            
            self.logger.log(f"URLs únicas encontradas: {len(urls_unicas)}")
            
            for url in urls_unicas:
                self.url_categorizer.categorizar_url(
                    url,
                    self.diccionario,
                    self.urls_nuevas,
                    modo_interactivo=True
                )
        
        # 8. Categorizar URLs
        self.logger.log("\n🔗 Categorizando URLs...")
        if 'First Page Seen' in df.columns:
            df['___PRIMERA_PAGINA___'] = df['First Page Seen'].apply(
                lambda x: self.url_categorizer.categorizar_url(
                    x, 
                    self.diccionario, 
                    self.urls_nuevas, 
                    modo_interactivo=False
                )
            )
        if 'Last Page Seen' in df.columns:
            df['___ULTIMA_PAGINA___'] = df['Last Page Seen'].apply(
                lambda x: self.url_categorizer.categorizar_url(
                    x,
                    self.diccionario,
                    self.urls_nuevas,
                    modo_interactivo=False
                )
            )
        
        # 9. Reemplazar columnas originales
        grado_cols = [col for col in df.columns if col == 'Grado Académico' or col.startswith('Grado Académico.')]
        if grado_cols:
            df[grado_cols[0]] = df['___GRADO_NORMALIZADO___']
            self.logger.log(f"✅ Reemplazada columna: {grado_cols[0]}")
            
            if len(grado_cols) > 1:
                for col_duplicada in grado_cols[1:]:
                    df.drop(col_duplicada, axis=1, inplace=True)
                    self.logger.log(f"✅ Eliminada columna duplicada: {col_duplicada}")
        
        if 'Colegio Actual' in df.columns:
            df['Colegio Actual'] = df['___COLEGIO_NORMALIZADO___']
            self.logger.log("✅ Reemplazada columna: Colegio Actual")
        
        if 'En qué colegio estudias actualmente?' in df.columns:
            df.drop('En qué colegio estudias actualmente?', axis=1, inplace=True)
            self.logger.log("✅ Eliminada columna redundante: En qué colegio estudias actualmente?")
        
        if 'Associated Form Submission' in df.columns:
            df['Associated Form Submission'] = df['___FORM_LIMPIO___']
            self.logger.log("✅ Reemplazada columna: Associated Form Submission")
        
        if 'Carrera de Interés' in df.columns and '___CARRERA_COMPLETADA___' in df.columns:
            df['Carrera de Interés'] = df['___CARRERA_COMPLETADA___']
            self.logger.log("✅ Reemplazada columna: Carrera de Interés")
        
        if 'First Page Seen' in df.columns and '___PRIMERA_PAGINA___' in df.columns:
            df['First Page Seen'] = df['___PRIMERA_PAGINA___']
            self.logger.log("✅ Reemplazada columna: First Page Seen")
        if 'Last Page Seen' in df.columns and '___ULTIMA_PAGINA___' in df.columns:
            df['Last Page Seen'] = df['___ULTIMA_PAGINA___']
            self.logger.log("✅ Reemplazada columna: Last Page Seen")
        
        # 10. Eliminar columnas temporales
        columnas_temporales = [
            '___COLEGIO_UNIFICADO___', '___COLEGIO_NORMALIZADO___',
            '___GRADO_UNIFICADO___', '___GRADO_NORMALIZADO___', '___FORM_LIMPIO___',
            '___CARRERA_COMPLETADA___', '___PRIMERA_PAGINA___', '___ULTIMA_PAGINA___'
        ]
        df.drop([c for c in columnas_temporales if c in df.columns], axis=1, inplace=True)
        
        # 11. Guardar resultado
        self.logger.log(f"\n💾 Guardando archivo limpio: {config.OUTPUT_FILE}")
        df.to_csv(config.OUTPUT_FILE, index=False, encoding='utf-8-sig')
        
        # 12. Guardar diccionario
        self.logger.log("\n💾 Guardando diccionario...")
        self.dict_manager.guardar_diccionario(self.diccionario)
        
        # 13. Resumen
        self.logger.log("\n" + "="*60)
        self.logger.log("✅ PROCESO COMPLETADO")
        self.logger.log("="*60)
        self.logger.log(f"📊 Total de leads procesados: {len(df)}")
        self.logger.log(f"🆕 Normalizaciones nuevas: {len(self.normalizaciones_nuevas)}")
        self.logger.log(f"🤖 Tokens usados: {self.normalizador_claude.get_tokens_usados()}")
        costo = (self.normalizador_claude.get_tokens_usados() / 1_000_000) * 3
        self.logger.log(f"💰 Costo aproximado: ${costo:.4f}")
        
        if self.normalizaciones_nuevas:
            self.logger.log("\n📝 NUEVAS NORMALIZACIONES:")
            for norm in self.normalizaciones_nuevas:
                self.logger.log(f"  • {norm}")
        
        if self.urls_nuevas:
            self.logger.log("\n🔗 NUEVAS URLs:")
            for url in self.urls_nuevas:
                self.logger.log(f"  • {url}")
        
        if self.formularios_nuevos:
            self.logger.log("\n📝 NUEVOS FORMULARIOS:")
            for form in self.formularios_nuevos:
                self.logger.log(f"  • {form}")
        
        self.logger.log(f"\n✅ Archivo guardado: {config.OUTPUT_FILE}")
        self.logger.log("🎉 ¡Listo para Power BI!")


def main():
    """Función principal de ejecución"""
    print("""
╔═══════════════════════════════════════════════════════════╗
║  NORMALIZADOR DE LEADS - HubSpot                         ║
╚═══════════════════════════════════════════════════════════╝
    """)
    
    if not os.path.exists(config.INPUT_FILE):
        print(f"❌ ERROR: No se encontró {config.INPUT_FILE}")
        input("\nPresiona Enter para salir...")
        return
    
    if not config.API_KEY:
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