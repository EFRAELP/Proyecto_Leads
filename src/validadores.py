"""
validadores.py
Funciones de validación y detección para normalización de datos
"""

import pandas as pd
from rapidfuzz import fuzz


class Validadores:
    """Validadores para colegios, universidades y respuestas"""
    
    def __init__(self, config, logger):
        """
        Inicializa los validadores
        
        Args:
            config: Módulo de configuración con constantes
            logger: Instancia de Logger para registrar mensajes
        """
        self.config = config
        self.logger = logger
    
    def es_sigla_ambigua(self, texto):
        """Detecta siglas ambiguas"""
        if not texto or pd.isna(texto):
            return False
        
        texto_limpio = str(texto).strip().lower()
        
        if len(texto_limpio) <= 3 and texto_limpio not in ['usac', 'url', 'umg', 'ufm', 'uvg']:
            return True
        
        return texto_limpio in self.config.SIGLAS_AMBIGUAS
    
    def detectar_respuesta_invalida(self, texto):
        """Detecta respuestas inválidas"""
        if not texto or pd.isna(texto):
            return True
        
        texto_limpio = str(texto).strip().lower()
        
        if len(texto_limpio) < 2:
            return True
        
        if texto_limpio in self.config.RESPUESTAS_INVALIDAS:
            return True
        
        frases_invalidas = [
            'no estudio', 'no estoy', 'ninguno', 'ya me gradué',
            'solo necesito', 'trabajo en', 'certificado en'
        ]
        if any(frase in texto_limpio for frase in frases_invalidas):
            return True
        
        return False
    
    # ⭐ NUEVO: Detectar títulos académicos
    def detectar_titulo_carrera(self, texto):
        """
        Detecta si el texto es un título académico o carrera, no un colegio
        Retorna True si es un título/carrera que debe marcarse como "Otro"
        """
        if not texto or pd.isna(texto):
            return False
        
        texto_limpio = str(texto).strip().lower()
        
        # Lista de patrones que indican títulos académicos
        titulos = [
            'perito en', 'perito contador', 'perita en',
            'bachiller en', 'bachillerato en',
            'tecnico en', 'técnico en', 'tecnica en', 'técnica en',
            'licenciatura en', 'licenciado en', 'licenciada en',
            'maestria en', 'maestría en', 'master en',
            'ingeniero en', 'ingeniera en', 'ingenieria en', 'ingeniería en',
            'arquitecto', 'arquitecta', 'arquitectura',
            'doctor en', 'doctora en',
            'abogado', 'abogada',
            'contador', 'contadora',
        ]
        
        for titulo in titulos:
            if titulo in texto_limpio:
                return True
        
        return False
    
    def buscar_universidad_conocida(self, texto):
        """
        Busca universidades guatemaltecas
        ⭐ MODIFICADO: Verifica PRIMERO si es un colegio específico (como Instituto Rafael Landívar)
        antes de clasificarlo como universidad
        """
        if not texto or pd.isna(texto):
            return None
        
        texto_limpio = str(texto).strip().lower()
        
        # ⭐ PASO 1: Verificar si es un COLEGIO específico (antes de verificar universidades)
        # Esto evita que "instituto rafael landívar" sea clasificado como "Universidad Rafael Landívar"
        if hasattr(self.config, 'COLEGIOS_ESPECIFICOS'):
            for colegio_key, colegio_nombre in self.config.COLEGIOS_ESPECIFICOS.items():
                if colegio_key in texto_limpio:
                    self.logger.log(f"🏫 Colegio específico detectado: '{texto}' → '{colegio_nombre}'")
                    return colegio_nombre
        
        # ⭐ PASO 2: Verificar si es un colegio que NO es universidad
        if texto_limpio in self.config.COLEGIOS_NO_UNIVERSITARIOS:
            self.logger.log(f"⚠️ No es universidad: '{texto}' → 'Otro'")
            return None
        
        # PASO 3: Ahora sí buscar universidades (solo si NO es un colegio específico)
        if texto_limpio in self.config.UNIVERSIDADES_GT:
            return self.config.UNIVERSIDADES_GT[texto_limpio]
        
        for key, universidad in self.config.UNIVERSIDADES_GT.items():
            if key in texto_limpio or texto_limpio in key:
                return universidad
        
        # PASO 4: Fuzzy matching solo para universidades
        mejor_match = None
        mejor_score = 0
        
        for key, universidad in self.config.UNIVERSIDADES_GT.items():
            score = fuzz.ratio(texto_limpio, key)
            if score > mejor_score and score > 75:
                mejor_score = score
                mejor_match = universidad
        
        return mejor_match
    
    def fuzzy_match(self, texto, categoria, diccionario):
        """
        Fuzzy matching en diccionario
        ⭐ MODIFICADO: Umbral aumentado de 85 a 92 para ser más estricto
        """
        if not texto or pd.isna(texto):
            return None
            
        texto_limpio = str(texto).strip().lower()
        diccionario_cat = diccionario.get(categoria, {})
        
        mejor_match = None
        mejor_score = 0
        
        for key in diccionario_cat.keys():
            score = fuzz.ratio(texto_limpio, key.lower())
            if score > mejor_score:
                mejor_score = score
                mejor_match = key
        
        # ⭐ CAMBIADO: De 85 a 92 (más estricto)
        if mejor_score > 88:
            return diccionario_cat[mejor_match]
        
        return None
    
    def detectar_no_es_colegio(self, texto):
        """Detecta si NO es un colegio"""
        if not texto or pd.isna(texto):
            return False
        
        texto_limpio = str(texto).strip().lower()
        
        for institucion in self.config.NO_SON_COLEGIOS:
            if institucion in texto_limpio:
                return True
        
        return False

# ============================================================
# ⭐ NUEVAS FUNCIONES PARA NORMALIZACIÓN DE GRADOS ACADÉMICOS
# ============================================================

def es_valor_basura(texto, config):
    """
    Detecta si un valor es basura/prueba sin sentido
    
    Args:
        texto: Texto a validar
        config: Módulo de configuración con PATRONES_BASURA
        
    Returns:
        True si es basura, False si no
    """
    if not texto or pd.isna(texto):
        return False
    
    texto_str = str(texto).strip().lower()
    
    # Verificar si está vacío después de limpiar
    if not texto_str or len(texto_str) < 1:
        return False
    
    # 1. Verificar patrones de basura del config
    for patron in config.PATRONES_BASURA:
        if patron in texto_str:
            return True
    
    # 2. Detectar códigos alfanuméricos sin sentido (ABC123, XYZ999)
    import re
    if re.match(r'^[a-z]{2,}[0-9]{2,}$', texto_str):
        return True
    
    # 3. Detectar letras repetidas (aaa, xxx, asdf)
    if len(set(texto_str)) <= 2 and len(texto_str) >= 3:
        return True
    
    # 4. Detectar números largos sin sentido (más de 4 dígitos)
    if texto_str.isdigit() and len(texto_str) > 4:
        return True
    
    # 5. Solo símbolos
    if all(c in '-._ /\\|()[]{}' for c in texto_str):
        return True
    
    return False


def detectar_graduacion_implicita(texto, config):
    """
    Detecta si el texto implica que la persona ya se graduó
    
    Args:
        texto: Texto normalizado (minúsculas, sin tildes)
        config: Módulo de configuración con KEYWORDS_GRADUADO
        
    Returns:
        True si implica graduación, False si no
    """
    if not texto or pd.isna(texto):
        return False
    
    texto_str = str(texto).strip().lower()
    
    # Buscar keywords de graduación
    for keyword in config.KEYWORDS_GRADUADO:
        if keyword in texto_str:
            return True
    
    return False


def validar_grado_manual(grado_original, grados_opciones, logger):
    """
    Muestra menú interactivo para clasificar manualmente un grado académico
    
    Args:
        grado_original: Valor original que no se pudo clasificar
        grados_opciones: Lista de opciones disponibles (de config.GRADOS_OPCIONES)
        logger: Instancia de Logger para registrar la decisión
        
    Returns:
        El grado normalizado seleccionado por el usuario
    """
    print("\n" + "="*60)
    print(f"⚠️  NO SE PUDO CLASIFICAR AUTOMÁTICAMENTE: '{grado_original}'")
    print("="*60)
    print("\nSelecciona la clasificación correcta:\n")
    
    # Mostrar opciones numeradas
    for i, opcion in enumerate(grados_opciones, 1):
        print(f"  {i}. {opcion}")
    
    # Solicitar input del usuario
    while True:
        try:
            respuesta = input(f"\nElige una opción (1-{len(grados_opciones)}): ").strip()
            
            # Validar que sea un número
            opcion_num = int(respuesta)
            
            # Validar que esté en el rango
            if 1 <= opcion_num <= len(grados_opciones):
                grado_seleccionado = grados_opciones[opcion_num - 1]
                
                # Registrar en log
                logger.log(f"✅ Clasificación manual: '{grado_original}' → '{grado_seleccionado}'")
                
                print(f"\n✅ Guardado como: {grado_seleccionado}\n")
                return grado_seleccionado
            else:
                print(f"⚠️  Por favor, ingresa un número entre 1 y {len(grados_opciones)}")
                
        except ValueError:
            print("⚠️  Por favor, ingresa un número válido")
        except KeyboardInterrupt:
            print("\n\n⚠️  Proceso interrumpido por el usuario")
            logger.log(f"⚠️ Clasificación manual cancelada para: '{grado_original}'")
            return "Sin especificar"