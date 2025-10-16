"""
form_mapper.py
Mapeo de formularios a carreras
"""

import pandas as pd
import re


class FormMapper:
    """Mapeador de formularios a carreras"""
    
    def __init__(self, config, logger):
        """
        Inicializa el mapeador de formularios
        
        Args:
            config: Módulo de configuración con constantes
            logger: Instancia de Logger para registrar mensajes
        """
        self.config = config
        self.logger = logger
    
    def extraer_primer_form(self, texto):
        """
        Extrae el primer formulario válido de un texto con múltiples forms
        ⭐ MODIFICADO: Filtra correctamente .elementor-form usando regex
        """
        if not texto or pd.isna(texto):
            return "Otro"
        
        texto_str = str(texto).strip()
        
        if not texto_str:
            return "Otro"
        
        # Separar por ; o ,
        elementos = re.split(r'[;,]', texto_str)
        
        # Buscar el primer elemento que NO sea .elementor-form
        for elem in elementos:
            elem_limpio = elem.strip()
            
            if not elem_limpio:
                continue
            
            # Si es SOLO .elementor-form o variaciones, saltarlo
            if re.match(r'^\.elementor-form[\s,\-\_]*$', elem_limpio, re.IGNORECASE):
                continue
            
            # Si contiene .elementor-form pero tiene más texto, limpiarlo
            elem_limpio = re.sub(r'[\s,]*\.elementor-form[\s,\-\_]*', '', elem_limpio, flags=re.IGNORECASE).strip()
            
            # Si después de limpiar queda algo, devolverlo
            if elem_limpio:
                return elem_limpio
        
        # Si todos los elementos eran .elementor-form
        return "Otro"
    
    def mapear_form_a_carrera(self, form, diccionario, formularios_nuevos, modo_interactivo=True):
        """Mapea formulario a carrera"""
        if not form or pd.isna(form) or form == "Otro":
            return None
        
        form_str = str(form).strip().lower()
        
        # Buscar en diccionario de formularios
        if 'formularios' in diccionario and form_str in diccionario['formularios']:
            return diccionario['formularios'][form_str]
        
        # Buscar en mapeo predefinido
        for key, carrera in self.config.MAPEO_FORMULARIOS.items():
            if key in form_str:
                if 'formularios' not in diccionario:
                    diccionario['formularios'] = {}
                diccionario['formularios'][form_str] = carrera
                return carrera
        
        # Si contiene "uvg bridge" no mapear (ya tiene carrera)
        if 'uvg bridge' in form_str or 'bridge' in form_str:
            return None
        
        # Si es modo interactivo, preguntar
        if modo_interactivo:
            return self.preguntar_carrera_form(form, diccionario, formularios_nuevos)
        
        return None
    
    def preguntar_carrera_form(self, form_name, diccionario, formularios_nuevos):
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
                
                if 'formularios' not in diccionario:
                    diccionario['formularios'] = {}
                diccionario['formularios'][form_name.lower()] = carrera
                
                self.logger.log(f"✅ Formulario mapeado: '{form_name}' → '{carrera}'")
                formularios_nuevos.append(f"Form: {form_name} → {carrera}")
                
                return carrera
            else:
                print("⚠️ Opción inválida. Selecciona 1-6.")