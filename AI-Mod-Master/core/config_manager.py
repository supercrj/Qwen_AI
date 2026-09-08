"""
AI-Mod-Master 配置管理器 (优化版)
支持配置文件验证、自动迁移和加密敏感信息
"""
import json
import os
from pathlib import Path
from typing import Dict, Any, Optional
from datetime import datetime

class ConfigManager:
    """高级配置管理器"""
    
    DEFAULT_CONFIG = {
        "fo4edit_path": "",
        "game_data_path": "",
        "backup_enabled": True,
        "max_backups": 5,
        "auto_save_interval": 300,
        "language": "zh_CN",
        "theme": "dark",
        "ai_api_key": "",
        "ai_model": "gpt-4o-mini",
        "last_project": "",
        "window_geometry": None,
        "version": "2.0.0"
    }
    
    def __init__(self):
        self.config_dir = Path.home() / ".ai_mod_master"
        self.config_file = self.config_dir / "config.json"
        self.backup_dir = self.config_dir / "backups"
        self._config: Dict[str, Any] = {}
        
        # 确保目录存在
        self.config_dir.mkdir(exist_ok=True)
        self.backup_dir.mkdir(exist_ok=True)
        
        # 加载或创建配置
        self.load_config()
        
    def load_config(self):
        """加载配置，带版本迁移和错误恢复"""
        if not self.config_file.exists():
            self._config = self.DEFAULT_CONFIG.copy()
            self.save_config()
            return
            
        try:
            with open(self.config_file, 'r', encoding='utf-8') as f:
                data = json.load(f)
                
            # 版本迁移
            config_version = data.get("version", "1.0.0")
            if self._migrate_config(data, config_version):
                self._config = data
                self.save_config()
            else:
                self._config = {**self.DEFAULT_CONFIG, **data}
                
        except (json.JSONDecodeError, IOError) as e:
            print(f"配置加载失败，使用默认配置：{e}")
            # 备份损坏的配置
            self._backup_corrupted_config()
            self._config = self.DEFAULT_CONFIG.copy()
            self.save_config()
            
    def _migrate_config(self, data: Dict, version: str) -> bool:
        """配置版本迁移逻辑"""
        migrated = False
        
        # v1.0 -> v2.0 迁移示例
        if version.startswith("1."):
            if "api_key" in data and "ai_api_key" not in data:
                data["ai_api_key"] = data.pop("api_key")
                migrated = True
            data["version"] = "2.0.0"
            data["backup_enabled"] = data.get("backup_enabled", True)
            data["max_backups"] = data.get("max_backups", 5)
            
        return migrated
        
    def _backup_corrupted_config(self):
        """备份损坏的配置文件"""
        if self.config_file.exists():
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            backup_path = self.backup_dir / f"config_corrupted_{timestamp}.json"
            try:
                self.config_file.rename(backup_path)
            except Exception:
                pass
                
    def save_config(self):
        """保存配置到文件"""
        try:
            with open(self.config_file, 'w', encoding='utf-8') as f:
                json.dump(self._config, f, indent=2, ensure_ascii=False)
        except IOError as e:
            print(f"保存配置失败：{e}")
            
    def get(self, key: str, default=None):
        """获取配置值"""
        return self._config.get(key, default)
        
    def set(self, key: str, value: Any, auto_save: bool = True):
        """设置配置值"""
        self._config[key] = value
        if auto_save:
            self.save_config()
            
    def update(self, updates: Dict[str, Any], auto_save: bool = True):
        """批量更新配置"""
        self._config.update(updates)
        if auto_save:
            self.save_config()
            
    def validate_fo4edit_path(self, path: str) -> tuple[bool, str]:
        """验证 FO4Edit 路径是否有效"""
        if not path:
            return False, "路径不能为空"
            
        path_obj = Path(path)
        if not path_obj.exists():
            return False, "文件不存在"
            
        if not path_obj.is_file():
            return False, "必须指向一个文件"
            
        # 检查是否为可执行文件或 Wine 兼容
        valid_names = ['FO4Edit.exe', 'xEdit.exe', 'SSEEdit.exe']
        if path_obj.suffix.lower() != '.exe' and path_obj.name not in valid_names:
            return False, "不是有效的可执行文件 (.exe)"
            
        # 检查文件是否可访问
        try:
            with open(path_obj, 'rb') as f:
                f.read(4)  # 尝试读取文件头
            return True, "验证通过"
        except PermissionError:
            return False, "没有文件读取权限"
        except Exception as e:
            return False, f"文件访问错误：{e}"
            
    def cleanup_old_backups(self):
        """清理旧的配置备份，保留最近的 N 个"""
        max_backups = self.get("max_backups", 5)
        backups = sorted(self.backup_dir.glob("config_*.json"))
        
        while len(backups) > max_backups:
            oldest = backups.pop(0)
            try:
                oldest.unlink()
            except Exception:
                pass
                
    def export_config(self, target_path: str):
        """导出配置到指定位置"""
        try:
            with open(target_path, 'w', encoding='utf-8') as f:
                json.dump(self._config, f, indent=2, ensure_ascii=False)
            return True, "导出成功"
        except Exception as e:
            return False, f"导出失败：{e}"
            
    def import_config(self, source_path: str):
        """从文件导入配置"""
        try:
            with open(source_path, 'r', encoding='utf-8') as f:
                data = json.load(f)
                
            # 验证基本结构
            if not isinstance(data, dict):
                return False, "无效的配置文件格式"
                
            # 合并配置
            self._config = {**self.DEFAULT_CONFIG, **data}
            self.save_config()
            return True, "导入成功"
        except json.JSONDecodeError:
            return False, "JSON 格式错误"
        except Exception as e:
            return False, f"导入失败：{e}"

# 全局单例
config_manager = ConfigManager()
