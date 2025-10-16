"""
logger.py
Sistema de logging para el Normalizador de Leads
"""

import os
from datetime import datetime


class Logger:
    """Manejador de logs para consola y archivo"""
    
    def __init__(self, log_file):
        """
        Inicializa el logger
        
        Args:
            log_file: Ruta del archivo de log
        """
        self.log_file = log_file
        
        # Crear carpeta de logs si no existe
        log_dir = os.path.dirname(log_file)
        if log_dir:
            os.makedirs(log_dir, exist_ok=True)
    
    def log(self, mensaje):
        """
        Registra un mensaje en consola y archivo
        
        Args:
            mensaje: Texto a registrar
        """
        timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        log_msg = f"[{timestamp}] {mensaje}"
        
        # Mostrar en consola
        print(mensaje)
        
        # Escribir en archivo
        try:
            with open(self.log_file, 'a', encoding='utf-8') as f:
                f.write(log_msg + '\n')
        except Exception as e:
            print(f"⚠️ Error al escribir log: {e}")