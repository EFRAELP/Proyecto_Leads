"""
url_categorizer.py
Categorización de URLs por palabras clave y patrones
"""

import pandas as pd
import re
from urllib.parse import unquote


class URLCategorizer:
    """Categorizador de URLs para leads"""
    
    def __init__(self, config, logger):
        """
        Inicializa el categorizador de URLs
        
        Args:
            config: Módulo de configuración con constantes
            logger: Instancia de Logger para registrar mensajes
        """
        self.config = config
        self.logger = logger
    
    def categorizar_url(self, url, diccionario, urls_nuevas, modo_interactivo=True):
        """Categoriza URL por palabras clave - VERSIÓN MEJORADA con decodificación"""
        if not url or pd.isna(url):
            return "Otro"
        
        url_str = str(url).strip().lower()
        
        if not url_str:
            return "Otro"
        
        # 1. Buscar en diccionario
        if 'urls' in diccionario and url_str in diccionario['urls']:
            return diccionario['urls'][url_str]
        
        # ⭐ 2. DECODIFICAR URL (convertir %2B a +, %25C3%25B1 a ñ, etc.)
        url_decoded = unquote(url_str)
        
        # 3. Casos especiales "Otro"
        casos_otro = self.config.URL_CASOS_OTRO
        
        for caso in casos_otro:
            if caso in url_decoded:
                return 'Otro'
        
        # 4. Buscar coincidencias en AMBAS versiones (original y decodificada)
        patterns = self.config.URL_PATTERNS
        
        for carrera, patrones_carrera in patterns.items():
            for patron in patrones_carrera:
                # Buscar en URL original Y en URL decodificada
                if patron in url_str or patron in url_decoded:
                    if 'urls' not in diccionario:
                        diccionario['urls'] = {}
                    diccionario['urls'][url_str] = carrera
                    return carrera
        
        # 5. Bridge Principal
        if 'uvgbridge.gt' in url_decoded:
            tiene_carrera = False
            for patrones_carrera in patterns.values():
                if any(patron in url_decoded for patron in patrones_carrera):
                    tiene_carrera = True
                    break
            
            if not tiene_carrera:
                if re.search(r'uvgbridge\.gt/?(\?|$)', url_decoded):
                    return 'Bridge Principal'
        
        # 6. Modo interactivo
        if modo_interactivo and 'uvgbridge.gt' in url_decoded:
            return self.preguntar_categoria_url(url_str, diccionario, urls_nuevas)
        
        return 'Otro'
    
    def preguntar_categoria_url(self, url, diccionario, urls_nuevas):
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
                
                if 'urls' not in diccionario:
                    diccionario['urls'] = {}
                diccionario['urls'][url] = categoria
                
                self.logger.log(f"✅ URL categorizada: '{url}' → '{categoria}'")
                urls_nuevas.append(f"URL: {url} → {categoria}")
                return categoria
            else:
                print("⚠️ Opción inválida. Selecciona 1-7.")