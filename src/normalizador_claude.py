"""
normalizador_claude.py
Interacción con Claude API para normalización de datos
"""

from anthropic import Anthropic


class NormalizadorClaude:
    """Manejador de interacciones con Claude API"""
    
    def __init__(self, api_key, logger):
        """
        Inicializa el normalizador con Claude
        
        Args:
            api_key: API key de Anthropic
            logger: Instancia de Logger para registrar mensajes
        """
        self.client = Anthropic(api_key=api_key) if api_key else None
        self.logger = logger
        self.tokens_usados = 0
        # ⭐ NUEVO: Tracking de uso de web_search
        self.llamadas_con_web_search = 0
        self.llamadas_sin_web_search = 0
        self.llamadas_totales = 0
    
    def normalizar_con_claude(self, texto, tipo):
        """Usa Claude API para normalizar - VERSIÓN MEJORADA CON PROMPT CONSERVADOR"""
        if not self.client:
            self.logger.log("⚠️ No hay API key")
            return texto
        
        # ⭐ PROMPT COMPLETAMENTE REESCRITO - MÁS AGRESIVO CON "OTRO"
        prompts = {
            'colegio': f"""Eres un clasificador ESTRICTO de instituciones educativas guatemaltecas.

TEXTO A CLASIFICAR: "{texto}"

🔍 CUÁNDO USAR WEB_SEARCH:
- Si ves SIGLAS desconocidas (IGA, IPGA, IMB-PC, IEMCOOP, ISEA, CED-IECA, CEPREC, UDEO, CCB, etc.)
- Si el nombre es poco común y no estás 100% seguro
- Si necesitas verificar si una institución existe en Guatemala

📐 REGLAS DE CLASIFICACIÓN:

A) RESPUESTAS INVÁLIDAS → "Otro":
   ❌ "no", "ninguno", "no estudio", "ya me gradué", "graduado", "terminado"
   ❌ "prueba", "test", "demo", "ejemplo", "aaa", "xxx", "123"
   ❌ Carreras: "perito en...", "bachillerato", "magisterio"
   ❌ Sin información: "hola", "finalizado", "xd"

B) PATRONES = COLEGIO (NO universidad):
   ✅ Si inicia con: "Liceo", "Instituto", "Colegio", "Escuela", "INED", "INEB", "Centro Educativo"
   ✅ Ejemplo: "Liceo Frater" → "Liceo Frater" (colegio, NO universidad)
   ✅ Ejemplo: "Instituto Nacional de Educación Diversificada" → "Instituto Nacional de Educación Diversificada (INED)"

C) UNIVERSIDADES GUATEMALTECAS:
   ✅ USAC, URL, UMG, Galileo, Da Vinci, UVG, Panamericana, Mariano Gálvez, Rafael Landívar
   ✅ ITEC UVG = Universidad del Valle de Guatemala
   ✅ Si dice "Universidad" verifica que exista en Guatemala

D) ERRORES COMUNES A EVITAR:
   ❌ "escuela de formación secretarial" → "Escuela de Formación Secretarial" (NO universidad)
   ❌ "Liceo comercial entre valles" → mantenerlo o investigar (NO es UVG automáticamente)
   ❌ "mo" sin contexto → "Otro" (no inventes)
   ❌ IGA = Instituto Guatemalteco Americano (colegio real, NO "Otro")
   ❌ IPGA = Instituto Privado Guatemala Americano (investiga si no estás seguro)

E) SIGLAS - USA WEB_SEARCH:
   🔍 Si ves siglas y no estás 100% seguro del nombre completo, USA web_search
   ✅ Si es colegio relevante conocido en Guatemala, expándelo
   ❌ Si no encuentras información confiable, mantén la sigla (NO pongas "Otro")

F) NÚMEROS EN NOMBRES:
   ⚠️ NO CAMBIES números: "Escuela No. 5" → "Escuela Nacional de Ciencias Comerciales No. 5"
   ❌ NO cambies 5 por 3 u otro número

G) CUÁNDO TENGAS DUDA → "Otro":
   Si hay CUALQUIER incertidumbre sobre si es una institución real, responde "Otro".
   Mejor clasificar como "Otro" que dar un nombre incorrecto.

📤 RESPONDE SOLO CON:
- El nombre normalizado limpio
- "Otro" si es respuesta inválida
- NO agregues explicaciones

Nombre normalizado:""",

            'grado': f"""Grado académico: "{texto}"

REGLAS:
- Básicos: 1ro Básico, 2do Básico, 3ro Básico
- Diversificado: 4to Diversificado, 5to Diversificado, 6to Diversificado  
- Bachillerato: 4to Bachillerato, 5to Bachillerato, 6to Bachillerato
- Universitario: "Estudiante Universitario"
- Graduados: "Graduado Diversificado", "Graduado Universitario"
- Técnico: "Técnico Universitario"

SOLO el grado normalizado, sin explicaciones."""
        }
        
        try:
            self.logger.log(f"🤖 Consultando Claude: '{texto}'")
            
            # ⭐ AUMENTADO max_tokens para permitir web_search
            response = self.client.messages.create(
                model="claude-sonnet-4-20250514",
                max_tokens=300,  # Aumentado de 150 a 300
                messages=[{
                    "role": "user",
                    "content": prompts.get(tipo, texto)
                }]
            )
            
            # Actualizar contadores
            self.tokens_usados += response.usage.input_tokens + response.usage.output_tokens
            self.llamadas_totales += 1
            
            # ⭐ NUEVO: Detectar si usó web_search
            uso_web_search = False
            if hasattr(response, 'content'):
                for block in response.content:
                    if hasattr(block, 'type') and block.type == 'tool_use':
                        if hasattr(block, 'name') and block.name == 'web_search':
                            uso_web_search = True
                            break
            
            if uso_web_search:
                self.llamadas_con_web_search += 1
            else:
                self.llamadas_sin_web_search += 1
            
            # Extraer texto de la respuesta
            normalizado = response.content[0].text.strip()
            
            # ⭐ VALIDACIÓN MEJORADA
            normalizado = self.validar_respuesta_claude(texto, normalizado, tipo)
            
            return normalizado
            
        except Exception as e:
            self.logger.log(f"❌ Error Claude: {e}")
            return texto
    
    def validar_respuesta_claude(self, texto_original, normalizado, tipo='colegio'):
        """Valida que Claude no haya respondido con texto de sistema - VERSIÓN MEJORADA"""
        
        # Validación 1: Respuesta muy larga
        if len(normalizado) > 200:
            self.logger.log(f"⚠️ Respuesta muy larga: '{texto_original}' → 'Otro'")
            return "Otro"
        
        # Validación 2: Frases de sistema
        frases_sistema = [
            'estoy listo para', 'por favor proporciona',
            'entendido', 'necesito más información',
            'no puedo', 'dame más contexto', 'no encontré',
            'no tengo información', 'necesito que me proporciones'
        ]
        
        normalizado_lower = normalizado.lower()
        for frase in frases_sistema:
            if frase in normalizado_lower:
                self.logger.log(f"⚠️ Respuesta de sistema: '{texto_original}' → 'Otro'")
                return "Otro"
        
        # Validación 3: Formato con múltiples líneas
        if normalizado.count('\n') > 2:
            self.logger.log(f"⚠️ Respuesta con formato: '{texto_original}' → 'Otro'")
            return "Otro"
        
        # ⭐ NUEVA Validación 4: Respuestas de prueba deben ser "Otro"
        if tipo == 'colegio':
            texto_lower = texto_original.lower().strip()
            respuestas_prueba = ['prueba', 'test', 'testing', 'demo', 'ejemplo']
            if texto_lower in respuestas_prueba and normalizado.lower() != "otro":
                self.logger.log(f"⚠️ Respuesta de prueba corregida: '{texto_original}' → 'Otro'")
                return "Otro"
        
        # ⭐ NUEVA Validación 5: Patrón "Liceo/Instituto" no debe convertirse en Universidad
        if tipo == 'colegio':
            texto_lower = texto_original.lower().strip()
            patrones_colegio = ['liceo', 'instituto', 'escuela', 'colegio']
            
            if any(texto_lower.startswith(patron) for patron in patrones_colegio):
                if 'universidad' in normalizado.lower():
                    self.logger.log(f"⚠️ Error: Colegio convertido en Universidad: '{texto_original}' → mantener formato colegio")
                    # Mantener el patrón original pero limpiar
                    return texto_original.strip().title()
        
        # ⭐ NUEVA Validación 6: Siglas sin sentido → "Otro"
        if tipo == 'colegio':
            texto_lower = texto_original.lower().strip()
            siglas_sin_sentido = ['mo', 'xd', 'aaa', 'xxx', 'zzz', 'asdf']
            
            if texto_lower in siglas_sin_sentido:
                if normalizado.lower() != "otro" and len(normalizado) > 10:
                    self.logger.log(f"⚠️ Sigla sin sentido: '{texto_original}' → 'Otro'")
                    return "Otro"
        
        # ⭐ NUEVA Validación 7: Verificar que no cambió números en nombres
        import re
        numeros_original = re.findall(r'\d+', texto_original)
        numeros_normalizado = re.findall(r'\d+', normalizado)
        
        if numeros_original and numeros_normalizado:
            if numeros_original != numeros_normalizado:
                self.logger.log(f"⚠️ Advertencia: Números cambiados de {numeros_original} a {numeros_normalizado}")
                # No forzar cambio, solo advertir
        
        return normalizado
    
    def validar_normalizacion(self, original, propuesta, tipo):
        """Valida normalización con usuario - MANTIENE FUNCIONALIDAD ORIGINAL"""
        print(f"\n{'='*60}")
        print(f"📝 {tipo.upper()}")
        print(f"Original: {original}")
        print(f"Propuesta: {propuesta}")
        print(f"{'='*60}")
        print("\n1. Aceptar propuesta")
        print("2. Ingresar manualmente")
        print("3. Omitir (mantener original)")
        
        while True:
            opcion = input("\nSelecciona (1-3): ").strip()
            
            if opcion == '1':
                return propuesta
            elif opcion == '2':
                manual = input("Ingresa el valor correcto: ").strip()
                if manual:
                    return manual
                print("⚠️ No puede estar vacío")
            elif opcion == '3':
                return original
            else:
                print("⚠️ Opción inválida. Selecciona 1-3.")
    
    def preguntar_carrera_form(self, form_name, diccionario, formularios_nuevos):
        """Pregunta al usuario a qué carrera pertenece un formulario - MANTIENE FUNCIONALIDAD ORIGINAL"""
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
    
    def get_tokens_usados(self):
        """Retorna el total de tokens usados - FUNCIONALIDAD ORIGINAL"""
        return self.tokens_usados
    
    def get_estadisticas(self):
        """
        Retorna estadísticas detalladas del uso de Claude - NUEVO
        
        Returns:
            dict: Diccionario con métricas de uso
        """
        porcentaje_web = 0
        if self.llamadas_totales > 0:
            porcentaje_web = (self.llamadas_con_web_search / self.llamadas_totales) * 100
        
        return {
            'tokens_totales': self.tokens_usados,
            'llamadas_totales': self.llamadas_totales,
            'llamadas_con_web_search': self.llamadas_con_web_search,
            'llamadas_sin_web_search': self.llamadas_sin_web_search,
            'porcentaje_web_search': round(porcentaje_web, 1)
        }