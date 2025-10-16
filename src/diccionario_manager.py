"""
diccionario_manager.py
Gestión del diccionario de normalizaciones con backups
"""

import os
import json
import shutil
from datetime import datetime


class DiccionarioManager:
    """Manejador del diccionario de normalizaciones"""
    
    def __init__(self, diccionario_file, backup_dir, logger):
        """
        Inicializa el gestor de diccionario
        
        Args:
            diccionario_file: Ruta del archivo JSON del diccionario
            backup_dir: Carpeta donde guardar backups
            logger: Instancia de Logger para registrar mensajes
        """
        self.diccionario_file = diccionario_file
        self.backup_dir = backup_dir
        self.logger = logger
    
    def cargar_diccionario(self):
        """Carga el diccionario de normalizaciones previas"""
        if os.path.exists(self.diccionario_file):
            try:
                with open(self.diccionario_file, 'r', encoding='utf-8') as f:
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
    
    def guardar_diccionario(self, diccionario):
        """Guarda el diccionario actualizado con backup"""
        if os.path.exists(self.diccionario_file):
            timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
            backup_name = f'diccionario_backup_{timestamp}.json'
            backup_path = os.path.join(self.backup_dir, backup_name)
            
            try:
                shutil.copy2(self.diccionario_file, backup_path)
                self.logger.log(f"💾 Backup creado: {backup_name}")
            except Exception as e:
                self.logger.log(f"⚠️ No se pudo crear backup: {e}")
            
            self.limpiar_backups_antiguos()
        
        with open(self.diccionario_file, 'w', encoding='utf-8') as f:
            json.dump(diccionario, indent=2, ensure_ascii=False, fp=f)
        
        total_colegios = len(diccionario.get('colegios', {}))
        total_urls = len(diccionario.get('urls', {}))
        total_forms = len(diccionario.get('formularios', {}))
        
        self.logger.log(f"✅ Diccionario guardado:")
        self.logger.log(f"   • {total_colegios} colegios")
        self.logger.log(f"   • {total_urls} URLs")
        self.logger.log(f"   • {total_forms} formularios")
    
    def limpiar_backups_antiguos(self, max_backups=10):
        """Mantiene solo los últimos N backups"""
        try:
            backups = [f for f in os.listdir(self.backup_dir) if f.startswith('diccionario_backup_')]
            backups.sort(reverse=True)
            
            for backup in backups[max_backups:]:
                backup_path = os.path.join(self.backup_dir, backup)
                os.remove(backup_path)
                self.logger.log(f"🗑️ Backup antiguo eliminado: {backup}")
        except Exception as e:
            self.logger.log(f"⚠️ Error al limpiar backups: {e}")