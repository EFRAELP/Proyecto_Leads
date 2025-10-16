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
    
    def buscar_universidad_conocida(self, texto):
        """Busca universidades guatemaltecas"""
        if not texto or pd.isna(texto):
            return None
        
        texto_limpio = str(texto).strip().lower()
        
        # ⭐ NUEVA VERIFICACIÓN: Verificar si es un colegio que NO es universidad
        if texto_limpio in self.config.COLEGIOS_NO_UNIVERSITARIOS:
            self.logger.log(f"⚠️ No es universidad: '{texto}' → 'Otro'")
            return None
        
        if texto_limpio in self.config.UNIVERSIDADES_GT:
            return self.config.UNIVERSIDADES_GT[texto_limpio]
        
        for key, universidad in self.config.UNIVERSIDADES_GT.items():
            if key in texto_limpio or texto_limpio in key:
                return universidad
        
        mejor_match = None
        mejor_score = 0
        
        for key, universidad in self.config.UNIVERSIDADES_GT.items():
            score = fuzz.ratio(texto_limpio, key)
            if score > mejor_score and score > 75:
                mejor_score = score
                mejor_match = universidad
        
        return mejor_match
    
    def fuzzy_match(self, texto, categoria, diccionario):
        """Fuzzy matching en diccionario"""
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
        
        if mejor_score > 85:
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