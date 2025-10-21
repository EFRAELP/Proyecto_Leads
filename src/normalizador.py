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
        
        # ⭐ NUEVO: Contadores de estadísticas detalladas
        self.stats_validaciones_locales = 0
        self.stats_diccionario = 0
        self.stats_respuestas_invalidas = 0
        self.stats_colegios_conocidos = 0
        self.stats_universidades = 0
        self.stats_patrones = 0
        self.stats_claude = 0
        self.stats_validaciones_manuales = 0
        self.stats_validaciones_aceptadas = 0
        self.stats_validaciones_modificadas = 0
        self.stats_validaciones_omitidas = 0
    
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
    
    def validar_colegio_localmente(self, colegio_str):
        """
        Valida el colegio localmente usando diccionarios y patrones
        Retorna (valor_normalizado, metodo_usado) o (None, None) si no se pudo resolver
        """
        texto_lower = colegio_str.lower().strip()
        
        # 1. Verificar si ya está en diccionario
        if colegio_str in self.diccionario['colegios']:
            self.stats_diccionario += 1
            return self.diccionario['colegios'][colegio_str], 'diccionario'
        
        # 2. Verificar si es respuesta inválida
        if self.validadores.detectar_respuesta_invalida(colegio_str):
            self.stats_respuestas_invalidas += 1
            self.logger.log(f"⚠️ Respuesta inválida detectada: '{colegio_str}' → 'Otro'")
            return "Otro", 'respuesta_invalida'
        
        # ⭐ 2.5 NUEVO: Verificar si es un título/carrera académica
        if self.validadores.detectar_titulo_carrera(colegio_str):
            self.stats_respuestas_invalidas += 1
            self.logger.log(f"⚠️ Título académico detectado: '{colegio_str}' → 'Otro'")
            return "Otro", 'titulo_carrera'
        
        # 3. Verificar si NO es colegio
        if self.validadores.detectar_no_es_colegio(colegio_str):
            self.stats_respuestas_invalidas += 1
            self.logger.log(f"⚠️ No es un colegio detectado: '{colegio_str}' → 'Otro'")
            return "Otro", 'no_es_colegio'
        
        # 4. Verificar si está en COLEGIOS_CONOCIDOS
        if texto_lower in config.COLEGIOS_CONOCIDOS:
            valor = config.COLEGIOS_CONOCIDOS[texto_lower]
            self.stats_colegios_conocidos += 1
            self.logger.log(f"✅ Colegio conocido: '{colegio_str}' → '{valor}'")
            return valor, 'colegio_conocido'
        
        # 5. Verificar si es universidad conocida
        universidad = self.validadores.buscar_universidad_conocida(colegio_str)
        if universidad:
            self.stats_universidades += 1
            self.logger.log(f"🎓 Universidad detectada: '{colegio_str}' → '{universidad}'")
            return universidad, 'universidad'
        
        # 6. Verificar patrones de colegio (Liceo, Instituto, Escuela, etc.)
        for patron in config.PATRONES_COLEGIO:
            if texto_lower.startswith(patron):
                # Es un colegio, formatear el nombre
                nombre_formateado = colegio_str.strip().title()
                self.stats_patrones += 1
                self.logger.log(f"📚 Patrón colegio detectado: '{colegio_str}' → '{nombre_formateado}'")
                return nombre_formateado, 'patron_colegio'
        
        # 7. Fuzzy matching en diccionario
        match = self.validadores.fuzzy_match(colegio_str, 'colegios', self.diccionario)
        if match:
            self.stats_diccionario += 1
            self.logger.log(f"✓ Fuzzy match: '{colegio_str}' → '{match}'")
            return match, 'fuzzy_match'
        
        # No se pudo resolver localmente
        return None, None
    
    def normalizar_colegio(self, colegio, modo_validacion=True):
        """Normaliza nombre de colegio - VERSIÓN MEJORADA"""
        if not colegio or pd.isna(colegio):
            return "Otro"
        
        colegio_str = str(colegio).strip()
        if not colegio_str:
            return "Otro"
        
        # ⭐ PRIMERO: Intentar validación local
        valor_local, metodo = self.validar_colegio_localmente(colegio_str)
        
        if valor_local is not None:
            # Se resolvió localmente
            self.stats_validaciones_locales += 1
            
            # Guardar en diccionario si no estaba
            if colegio_str not in self.diccionario['colegios']:
                self.diccionario['colegios'][colegio_str] = valor_local
                self.normalizaciones_nuevas.append(f"Colegio: {colegio_str} → {valor_local}")
            
            # ⭐ VALIDACIÓN MANUAL SELECTIVA: Solo para patrones de colegio si es modo validación
            if metodo == 'patron_colegio' and modo_validacion:
                self.stats_validaciones_manuales += 1
                valor_validado = self.normalizador_claude.validar_normalizacion(
                    colegio_str,
                    valor_local,
                    f'colegio (patrón {metodo})'
                )
                # Actualizar diccionario con valor validado
                self.diccionario['colegios'][colegio_str] = valor_validado
                return valor_validado
            
            return valor_local
        
        # ⭐ SEGUNDO: Si no se resolvió localmente, verificar siglas ambiguas
        if self.validadores.es_sigla_ambigua(colegio_str):
            self.logger.log(f"🔍 Sigla ambigua detectada: '{colegio_str}'")
            if modo_validacion:
                self.stats_validaciones_manuales += 1
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
        
        # ⭐ TERCERO: Llamar a Claude (solo si no se resolvió localmente)
        self.stats_claude += 1
        normalizado = self.normalizador_claude.normalizar_con_claude(colegio_str, 'colegio')
        
        # ⭐ VALIDACIÓN MANUAL SELECTIVA: Solo si NO es "Otro" Y modo validación está activo
        if modo_validacion and normalizado.lower() != "otro":
            self.stats_validaciones_manuales += 1
            normalizado = self.normalizador_claude.validar_normalizacion(colegio_str, normalizado, 'colegio')
        
        # Guardar en diccionario
        self.diccionario['colegios'][colegio_str] = normalizado
        self.normalizaciones_nuevas.append(f"Colegio: {colegio_str} → {normalizado}")
        
        return normalizado
    
    def normalizar_grado(self, grado, modo_validacion=True):
        """
        Normaliza grado académico con detección completa de patrones
        
        Args:
            grado: Valor del grado a normalizar
            modo_validacion: Si True, pregunta al usuario en casos ambiguos
            
        Returns:
            Grado normalizado
        """
        # Importar funciones auxiliares
        from .validadores import es_valor_basura, detectar_graduacion_implicita, validar_grado_manual
        
        # ========================================
        # PASO 1: Pre-procesamiento
        # ========================================
        
        # Verificar si es nulo o vacío
        if grado is None or pd.isna(grado):
            if modo_validacion:
                self.logger.log(f"⚠️ Valor nulo/vacío detectado - solicitando clasificación manual")
                return validar_grado_manual("(vacío)", config.GRADOS_OPCIONES, self.logger)
            else:
                return "Sin especificar"
        
        # Convertir a string y limpiar
        grado_str = str(grado).strip()
        
        # Verificar si está vacío después de strip
        if not grado_str:
            if modo_validacion:
                self.logger.log(f"⚠️ Valor vacío detectado - solicitando clasificación manual")
                return validar_grado_manual("(vacío)", config.GRADOS_OPCIONES, self.logger)
            else:
                return "Sin especificar"
        
        # Buscar en diccionario primero (si ya fue clasificado antes)
        if grado_str in self.diccionario['grados']:
            return self.diccionario['grados'][grado_str]
        
        # Normalizar formato: lowercase y quitar tildes
        grado_lower = grado_str.lower()
        grado_normalizado = grado_lower.replace('á', 'a').replace('é', 'e').replace('í', 'i').replace('ó', 'o').replace('ú', 'u').replace('ñ', 'n')
        
        # Reemplazar guiones bajos por espacios
        grado_normalizado = grado_normalizado.replace('_', ' ')
        
        # ========================================
        # PASO 2: Detectar Graduado Universitario
        # ========================================
        if 'graduado' in grado_normalizado and 'universitario' in grado_normalizado:
            self.diccionario['grados'][grado_str] = "Graduado Universitario"
            self.normalizaciones_nuevas.append(f"Grado: {grado_str} → Graduado Universitario")
            return "Graduado Universitario"
        
        # ========================================
        # PASO 3: Detectar Graduado Diversificado
        # ========================================
        if 'graduado' in grado_normalizado and 'diversificado' in grado_normalizado:
            self.diccionario['grados'][grado_str] = "Graduado Diversificado"
            self.normalizaciones_nuevas.append(f"Grado: {grado_str} → Graduado Diversificado")
            return "Graduado Diversificado"
        
        # Detectar graduación implícita (finalizado, terminado, egresado)
        if detectar_graduacion_implicita(grado_normalizado, config):
            self.diccionario['grados'][grado_str] = "Graduado Diversificado"
            self.normalizaciones_nuevas.append(f"Grado: {grado_str} → Graduado Diversificado")
            return "Graduado Diversificado"
        
        # ========================================
        # PASO 4: Detectar Estudiante Universitario
        # ========================================
        contador_keywords_universitario = 0
        for keyword in config.KEYWORDS_UNIVERSITARIO:
            if keyword in grado_normalizado:
                contador_keywords_universitario += 1
        
        if contador_keywords_universitario >= 1:
            self.diccionario['grados'][grado_str] = "Estudiante Universitario"
            self.normalizaciones_nuevas.append(f"Grado: {grado_str} → Estudiante Universitario")
            return "Estudiante Universitario"
        
        # ========================================
        # PASO 5: Extraer número del texto
        # ========================================
        numero_extraido = None
        
        # 5.1 Buscar ordinales (4to, 5to, 6to, 7mo, 1ro, 2do, 3ro)
        match_ordinal = re.search(r'(\d+)(to|mo|ro|do)\.?', grado_normalizado)
        if match_ordinal:
            numero_extraido = match_ordinal.group(1)
        
        # 5.2 Si no encontró ordinal, buscar números en texto
        if not numero_extraido:
            for texto_num, digito in config.NUMEROS_TEXTO.items():
                if texto_num in grado_normalizado:
                    numero_extraido = digito
                    break
        
        # 5.3 Si no encontró número en texto, buscar dígito solo
        if not numero_extraido:
            match_digito = re.search(r'\b([1-7])\b', grado_normalizado)
            if match_digito:
                numero_extraido = match_digito.group(1)
        
        # ========================================
        # PASO 6: Clasificar por número
        # ========================================
        if numero_extraido:
            # Convertir a int para comparar
            num = int(numero_extraido)
            
            # BÁSICOS (1-3)
            if num in [1, 2, 3]:
                # Verificar si tiene contexto de "básico"
                tiene_basico = any(keyword in grado_normalizado for keyword in config.KEYWORDS_BASICO)
                
                if tiene_basico:
                    # Formatear según el número
                    if num == 1:
                        resultado = "1ro. Básico"
                    elif num == 2:
                        resultado = "2do. Básico"
                    else:  # num == 3
                        resultado = "3ro. Básico"
                    
                    self.diccionario['grados'][grado_str] = resultado
                    self.normalizaciones_nuevas.append(f"Grado: {grado_str} → {resultado}")
                    return resultado
                else:
                    # No tiene contexto, preguntar
                    if modo_validacion:
                        self.logger.log(f"⚠️ Número {num} sin contexto - solicitando clasificación manual")
                        resultado = validar_grado_manual(grado_str, config.GRADOS_OPCIONES, self.logger)
                        self.diccionario['grados'][grado_str] = resultado
                        self.normalizaciones_nuevas.append(f"Grado: {grado_str} → {resultado}")
                        return resultado
                    else:
                        # Sin modo validación, asumir básico
                        if num == 1:
                            resultado = "1ro. Básico"
                        elif num == 2:
                            resultado = "2do. Básico"
                        else:
                            resultado = "3ro. Básico"
                        
                        self.diccionario['grados'][grado_str] = resultado
                        return resultado
            
            # DIVERSIFICADO (4-7)
            elif num in [4, 5, 6, 7]:
                # Formatear según el número
                if num == 4:
                    resultado = "4to. Diversificado"
                elif num == 5:
                    resultado = "5to. Diversificado"
                elif num == 6:
                    resultado = "6to. Diversificado"
                else:  # num == 7
                    resultado = "7mo. Diversificado"
                
                self.diccionario['grados'][grado_str] = resultado
                self.normalizaciones_nuevas.append(f"Grado: {grado_str} → {resultado}")
                return resultado
        
        # ========================================
        # PASO 7: Detectar diversificado SIN número
        # ========================================
        tiene_keyword_diversificado = any(keyword in grado_normalizado for keyword in config.KEYWORDS_DIVERSIFICADO)
        
        if tiene_keyword_diversificado:
            resultado = "5to. Diversificado"
            self.diccionario['grados'][grado_str] = resultado
            self.normalizaciones_nuevas.append(f"Grado: {grado_str} → {resultado}")
            return resultado
        
        # ========================================
        # PASO 8: Detectar valores basura
        # ========================================
        if es_valor_basura(grado_normalizado, config):
            resultado = "5to. Diversificado"
            self.diccionario['grados'][grado_str] = resultado
            self.normalizaciones_nuevas.append(f"Grado: {grado_str} → {resultado} (basura)")
            return resultado
        
        # ========================================
        # PASO 9: Default - no coincide con nada
        # ========================================
        resultado = "5to. Diversificado"
        self.diccionario['grados'][grado_str] = resultado
        self.normalizaciones_nuevas.append(f"Grado: {grado_str} → {resultado} (default)")
        return resultado
    
    def completar_carrera(self, row):
        """
        Completa la carrera de interés - VERSIÓN MEJORADA
        Procesa valores del CSV (con underscores) y desde formularios
        """
        # 1. Revisar si ya tiene un valor en "Carrera de Interés"
        carrera_actual = row.get('Carrera de Interés', '')
        
        if carrera_actual and str(carrera_actual).strip() and str(carrera_actual) != 'nan':
            carrera_str = str(carrera_actual).strip().lower()
            
            # Reemplazar espacios por underscores para buscar en mapeo
            carrera_con_underscores = carrera_str.replace(' ', '_')
            
            # Buscar en mapeo de carreras CSV
            if carrera_con_underscores in config.MAPEO_CARRERAS_CSV:
                return config.MAPEO_CARRERAS_CSV[carrera_con_underscores]
            
            # También buscar sin underscores
            if carrera_str in config.MAPEO_CARRERAS_CSV:
                return config.MAPEO_CARRERAS_CSV[carrera_str]
            
            # Si no está en el mapeo pero tiene valor, devolverlo limpio
            carrera_limpia = str(carrera_actual).replace('_', ' ').title()
            return carrera_limpia
        
        # 2. Si no tiene carrera, intentar mapear desde formulario
        form_limpio = row.get('___FORM_LIMPIO___', '')
        carrera_mapeada = self.form_mapper.mapear_form_a_carrera(
            form_limpio,
            self.diccionario,
            self.formularios_nuevos,
            modo_interactivo=False
        )
        
        if carrera_mapeada:
            return carrera_mapeada
        
        # 3. Si no se pudo mapear
        return "Sin especificar"
    
    def mostrar_resumen_estadisticas(self):
        """Muestra resumen detallado de estadísticas de normalización"""
        # Obtener estadísticas de Claude
        stats_claude = self.normalizador_claude.get_estadisticas()
        
        total_colegios = self.stats_validaciones_locales + self.stats_claude
        porcentaje_local = 0
        porcentaje_claude = 0
        
        if total_colegios > 0:
            porcentaje_local = (self.stats_validaciones_locales / total_colegios) * 100
            porcentaje_claude = (self.stats_claude / total_colegios) * 100
        
        self.logger.log("\n" + "━"*60)
        self.logger.log("📊 ESTADÍSTICAS DE NORMALIZACIÓN DE COLEGIOS")
        self.logger.log("━"*60)
        self.logger.log(f"\nTotal de colegios procesados: {total_colegios}")
        
        self.logger.log(f"\n🏠 VALIDACIONES LOCALES (sin Claude): {self.stats_validaciones_locales} ({porcentaje_local:.1f}%)")
        self.logger.log(f"  ├─ En diccionario previo: {self.stats_diccionario}")
        self.logger.log(f"  ├─ Respuestas inválidas → 'Otro': {self.stats_respuestas_invalidas}")
        self.logger.log(f"  ├─ Colegios conocidos: {self.stats_colegios_conocidos}")
        self.logger.log(f"  ├─ Universidades conocidas: {self.stats_universidades}")
        self.logger.log(f"  └─ Patrones automáticos: {self.stats_patrones}")
        
        self.logger.log(f"\n🤖 CONSULTAS A CLAUDE API: {self.stats_claude} ({porcentaje_claude:.1f}%)")
        self.logger.log(f"  ├─ Sin web_search: {stats_claude['llamadas_sin_web_search']}")
        self.logger.log(f"  ├─ Con web_search: {stats_claude['llamadas_con_web_search']}")
        self.logger.log(f"  └─ % con web_search: {stats_claude['porcentaje_web_search']}%")
        
        if self.stats_validaciones_manuales > 0:
            self.logger.log(f"\n✋ VALIDACIONES MANUALES: {self.stats_validaciones_manuales}")
        
        self.logger.log(f"\n💡 Tokens usados: {stats_claude['tokens_totales']:,}")
        costo = (stats_claude['tokens_totales'] / 1_000_000) * 3
        self.logger.log(f"💰 Costo aproximado: ${costo:.4f}")
        self.logger.log("━"*60)
    
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
        
        # Normalizar todos los colegios únicos primero
        for colegio in colegios_unicos:
            self.normalizar_colegio(colegio, modo_validacion=modo_validacion)
        
        # Aplicar normalizaciones a todas las filas
        df['___COLEGIO_NORMALIZADO___'] = df['___COLEGIO_UNIFICADO___'].apply(
            lambda x: self.normalizar_colegio(x, modo_validacion=False)
        )
        
        # 4. Normalizar grados
        self.logger.log("\n🎓 Normalizando grados académicos...")
        df['___GRADO_NORMALIZADO___'] = df['___GRADO_UNIFICADO___'].apply(self.normalizar_grado)
        
        # 5. Procesar formularios
        self.logger.log("\n📝 Procesando Associated Form Submission...")
        
        # Buscar la columna de formularios sin importar mayúsculas
        form_col_input = None
        for col in df.columns:
            if col.lower() == 'associated form submission':
                form_col_input = col
                break
        
        if form_col_input:
            self.logger.log(f"✓ Columna encontrada: '{form_col_input}'")
            df['___FORM_LIMPIO___'] = df[form_col_input].apply(self.form_mapper.extraer_primer_form)
            self.logger.log(f"✓ Procesados {len(df)} formularios")
        else:
            self.logger.log("⚠️ No se encontró columna de formularios, usando 'Otro'")
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
        
        # Buscar la columna de carrera sin importar mayúsculas
        carrera_col_input = None
        for col in df.columns:
            if col.lower() == 'carrera de interés':
                carrera_col_input = col
                break
        
        if carrera_col_input:
            self.logger.log(f"✓ Columna encontrada: '{carrera_col_input}'")
            df['Carrera de Interés'] = df[carrera_col_input]
            df['___CARRERA_COMPLETADA___'] = df.apply(self.completar_carrera, axis=1)
        else:
            self.logger.log("⚠️ No se encontró columna 'Carrera de Interés'")
            df['___CARRERA_COMPLETADA___'] = 'Sin especificar'
        
        # 7. Identificar URLs únicas
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
        else:
            self.logger.log("⚠️ No se encontró First Page Seen")
            df['___PRIMERA_PAGINA___'] = 'Otro'
        
        if 'Last Page Seen' in df.columns:
            df['___ULTIMA_PAGINA___'] = df['Last Page Seen'].apply(
                lambda x: self.url_categorizer.categorizar_url(
                    x, 
                    self.diccionario, 
                    self.urls_nuevas, 
                    modo_interactivo=False
                )
            )
        else:
            self.logger.log("⚠️ No se encontró Last Page Seen")
            df['___ULTIMA_PAGINA___'] = 'Otro'
        
        # 9. Reemplazar columnas originales
        self.logger.log("\n🔄 Reemplazando columnas originales...")
        
        # Grado Académico
        if 'Grado Académico' in df.columns:
            df['Grado Académico'] = df['___GRADO_NORMALIZADO___']
            self.logger.log("✅ Reemplazada columna: Grado Académico")
        
        if 'Grado Académico.1' in df.columns:
            df.drop('Grado Académico.1', axis=1, inplace=True)
            self.logger.log("✅ Eliminada columna duplicada: Grado Académico.1")
        
        # Colegio Actual
        if 'Colegio Actual' in df.columns:
            df['Colegio Actual'] = df['___COLEGIO_NORMALIZADO___']
            self.logger.log("✅ Reemplazada columna: Colegio Actual")
        
        if 'En qué colegio estudias actualmente?' in df.columns:
            df.drop('En qué colegio estudias actualmente?', axis=1, inplace=True)
            self.logger.log("✅ Eliminada columna redundante: En qué colegio estudias actualmente?")
        
        # ⭐ Associated Form Submission - CON DEBUGGING
        form_col = None
        for col in df.columns:
            if col.lower() == 'associated form submission':
                form_col = col
                break
        
        if form_col and '___FORM_LIMPIO___' in df.columns:
            # Mostrar valores antes y después para debug
            self.logger.log(f"✓ Reemplazando '{form_col}'...")
            self.logger.log(f"  Ejemplo ANTES: {df[form_col].iloc[0] if len(df) > 0 else 'N/A'}")
            self.logger.log(f"  Ejemplo PROCESADO: {df['___FORM_LIMPIO___'].iloc[0] if len(df) > 0 else 'N/A'}")
            
            df[form_col] = df['___FORM_LIMPIO___']
            
            self.logger.log(f"  Ejemplo DESPUÉS: {df[form_col].iloc[0] if len(df) > 0 else 'N/A'}")
            self.logger.log(f"✅ Reemplazada columna: {form_col}")
        else:
            if not form_col:
                self.logger.log("❌ ERROR: No se encontró columna 'Associated Form Submission'")
                self.logger.log(f"   Columnas disponibles: {list(df.columns)}")
            else:
                self.logger.log("❌ ERROR: No se encontró columna temporal '___FORM_LIMPIO___'")
        
        # ⭐ Carrera de Interés - CON DEBUGGING
        carrera_col = None
        for col in df.columns:
            if col.lower() == 'carrera de interés':
                carrera_col = col
                break
        
        if carrera_col and '___CARRERA_COMPLETADA___' in df.columns:
            self.logger.log(f"✓ Reemplazando '{carrera_col}'...")
            df[carrera_col] = df['___CARRERA_COMPLETADA___']
            self.logger.log(f"✅ Reemplazada columna: {carrera_col}")
        else:
            if not carrera_col:
                self.logger.log("❌ ERROR: No se encontró columna 'Carrera de Interés'")
            else:
                self.logger.log("❌ ERROR: No se encontró columna temporal '___CARRERA_COMPLETADA___'")
        # First Page Seen
        if 'First Page Seen' in df.columns and '___PRIMERA_PAGINA___' in df.columns:
            df['First Page Seen'] = df['___PRIMERA_PAGINA___']
            self.logger.log("✅ Reemplazada columna: First Page Seen")
        
        # Last Page Seen
        if 'Last Page Seen' in df.columns and '___ULTIMA_PAGINA___' in df.columns:
            df['Last Page Seen'] = df['___ULTIMA_PAGINA___']
            self.logger.log("✅ Reemplazada columna: Last Page Seen")
        
        # 10. Eliminar columnas temporales
        self.logger.log("\n🗑️ Eliminando columnas temporales...")
        columnas_temporales = [
            '___COLEGIO_UNIFICADO___', '___COLEGIO_NORMALIZADO___',
            '___GRADO_UNIFICADO___', '___GRADO_NORMALIZADO___', '___FORM_LIMPIO___',
            '___CARRERA_COMPLETADA___', '___PRIMERA_PAGINA___', '___ULTIMA_PAGINA___'
        ]
        df.drop([c for c in columnas_temporales if c in df.columns], axis=1, inplace=True)
        self.logger.log(f"✅ Eliminadas {len([c for c in columnas_temporales if c in df.columns])} columnas temporales")
        
        # 11. Guardar resultado
        self.logger.log(f"\n💾 Guardando archivo limpio: {config.OUTPUT_FILE}")
        df.to_csv(config.OUTPUT_FILE, index=False, encoding='utf-8-sig')
        
        # 12. Guardar diccionario
        self.logger.log("\n💾 Guardando diccionario...")
        self.dict_manager.guardar_diccionario(self.diccionario)
        
        # 13. Mostrar estadísticas detalladas
        self.mostrar_resumen_estadisticas()
        
        # 14. Resumen tradicional
        self.logger.log("\n" + "="*60)
        self.logger.log("✅ PROCESO COMPLETADO")
        self.logger.log("="*60)
        self.logger.log(f"📊 Total de leads procesados: {len(df)}")
        self.logger.log(f"🆕 Normalizaciones nuevas: {len(self.normalizaciones_nuevas)}")
        
        if self.normalizaciones_nuevas:
            self.logger.log("\n📝 NUEVAS NORMALIZACIONES:")
            for norm in self.normalizaciones_nuevas[:20]:  # Mostrar solo las primeras 20
                self.logger.log(f"  • {norm}")
            if len(self.normalizaciones_nuevas) > 20:
                self.logger.log(f"  ... y {len(self.normalizaciones_nuevas) - 20} más")
        
        if self.urls_nuevas:
            self.logger.log("\n🔗 NUEVAS URLs:")
            for url in self.urls_nuevas[:10]:  # Mostrar solo las primeras 10
                self.logger.log(f"  • {url}")
            if len(self.urls_nuevas) > 10:
                self.logger.log(f"  ... y {len(self.urls_nuevas) - 10} más")
        
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