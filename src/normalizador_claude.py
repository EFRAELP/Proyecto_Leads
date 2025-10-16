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
    
    def normalizar_con_claude(self, texto, tipo):
        """Usa Claude API para normalizar"""
        if not self.client:
            self.logger.log("⚠️ No hay API key")
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
            self.logger.log(f"🤖 Consultando Claude: '{texto}'")
            
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
            self.logger.log(f"❌ Error Claude: {e}")
            return texto
    
    def validar_respuesta_claude(self, texto_original, normalizado):
        """Valida que Claude no haya respondido con texto de sistema"""
        if len(normalizado) > 150:
            self.logger.log(f"⚠️ Respuesta muy larga: '{texto_original}' → 'Otro'")
            return "Otro"
        
        frases_sistema = [
            'estoy listo para', 'por favor proporciona',
            'entendido', 'necesito más información',
            'no puedo', 'dame más contexto'
        ]
        
        normalizado_lower = normalizado.lower()
        for frase in frases_sistema:
            if frase in normalizado_lower:
                self.logger.log(f"⚠️ Respuesta de sistema: '{texto_original}' → 'Otro'")
                return "Otro"
        
        if normalizado.count('\n') > 2:
            self.logger.log(f"⚠️ Respuesta con formato: '{texto_original}' → 'Otro'")
            return "Otro"
        
        return normalizado
    
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
    
    def get_tokens_usados(self):
        """Retorna el total de tokens usados"""
        return self.tokens_usados