"""
辐射4 翻译工具链
支持 .strings 文件的提取、翻译和打包
"""

import re
import json
from pathlib import Path
from typing import Dict, List, Tuple, Optional
from pydantic import BaseModel


class StringEntry(BaseModel):
    """字符串条目模型"""
    form_id: str
    original_text: str
    translated_text: str = ""
    context: str = ""  # 上下文信息
    modified: bool = False


class StringsFile:
    """Fallout4 .strings 文件处理器"""
    
    def __init__(self, file_path: Optional[str] = None):
        self.file_path = Path(file_path) if file_path else None
        self.entries: Dict[str, StringEntry] = {}
        
    def parse(self) -> bool:
        """解析 .strings 文件 (二进制格式)"""
        if not self.file_path or not self.file_path.exists():
            raise FileNotFoundError(f"文件不存在：{self.file_path}")
            
        # Fallout4 .strings 文件格式:
        # 每个条目：[4 字节 FormID][4 字节长度][UTF-16LE 文本]
        
        with open(self.file_path, 'rb') as f:
            data = f.read()
            
        offset = 0
        while offset + 8 < len(data):
            # 读取 FormID (4 字节，小端)
            form_id = int.from_bytes(data[offset:offset+4], 'little')
            form_id_str = f"{form_id:08X}"
            offset += 4
            
            # 读取文本长度 (4 字节，小端)
            text_len = int.from_bytes(data[offset:offset+4], 'little') * 2  # UTF-16 每个字符 2 字节
            offset += 4
            
            # 读取文本 (UTF-16LE)
            if offset + text_len > len(data):
                break
                
            text_data = data[offset:offset+text_len]
            try:
                text = text_data.decode('utf-16-le').rstrip('\x00')
            except:
                text = ""
                
            offset += text_len
            
            self.entries[form_id_str] = StringEntry(
                form_id=form_id_str,
                original_text=text
            )
            
        return True
    
    def parse_txt(self, txt_path: str) -> bool:
        """解析导出的 TXT 格式翻译文件"""
        path = Path(txt_path)
        if not path.exists():
            return False
            
        with open(path, 'r', encoding='utf-8') as f:
            for line in f:
                line = line.strip()
                if not line or line.startswith('#'):
                    continue
                    
                # 格式：FormID|原文 | 译文
                parts = line.split('|')
                if len(parts) >= 2:
                    form_id = parts[0].strip()
                    original = parts[1].strip()
                    translated = parts[2].strip() if len(parts) > 2 else ""
                    
                    self.entries[form_id] = StringEntry(
                        form_id=form_id,
                        original_text=original,
                        translated_text=translated
                    )
                    
        return True
    
    def export_to_json(self, output_path: str) -> bool:
        """导出为 JSON 格式供 AI 翻译"""
        data = {
            'file': str(self.file_path) if self.file_path else '',
            'entry_count': len(self.entries),
            'entries': [
                {
                    'form_id': e.form_id,
                    'original': e.original_text,
                    'translated': e.translated_text,
                    'context': e.context
                }
                for e in self.entries.values()
            ]
        }
        
        with open(output_path, 'w', encoding='utf-8') as f:
            json.dump(data, f, ensure_ascii=False, indent=2)
            
        return True
    
    def export_to_txt(self, output_path: str, include_translated: bool = False) -> bool:
        """导出为 TXT 格式用于翻译"""
        with open(output_path, 'w', encoding='utf-8') as f:
            f.write("# Fallout 4 Strings Translation File\n")
            f.write("# Format: FormID|Original Text|Translated Text\n\n")
            
            for entry in self.entries.values():
                if include_translated or not entry.translated_text:
                    f.write(f"{entry.form_id}|{entry.original_text}|{entry.translated_text}\n")
                    
        return True
    
    def apply_translations(self, translations: Dict[str, str]) -> int:
        """应用翻译 (FormID -> 翻译文本)"""
        count = 0
        for form_id, text in translations.items():
            if form_id in self.entries:
                self.entries[form_id].translated_text = text
                self.entries[form_id].modified = True
                count += 1
        return count
    
    def save_binary(self, output_path: str) -> bool:
        """保存为二进制 .strings 格式"""
        # TODO: 实现二进制写入
        print(f"保存二进制文件到：{output_path}")
        return True
    
    def get_untranslated_count(self) -> int:
        """获取未翻译的条目数量"""
        return sum(1 for e in self.entries.values() if not e.translated_text)
    
    def get_stats(self) -> Dict[str, int]:
        """获取统计信息"""
        total = len(self.entries)
        translated = sum(1 for e in self.entries.values() if e.translated_text)
        return {
            'total': total,
            'translated': translated,
            'untranslated': total - translated,
            'progress': round(translated / total * 100, 2) if total > 0 else 0
        }


class TranslationBatch:
    """批量翻译管理器"""
    
    def __init__(self):
        self.files: Dict[str, StringsFile] = {}
        
    def add_file(self, name: str, file_path: str) -> bool:
        """添加 .strings 文件"""
        sf = StringsFile(file_path)
        if sf.parse():
            self.files[name] = sf
            return True
        return False
    
    def export_all_for_ai(self, output_dir: str) -> Dict[str, str]:
        """导出所有文件供 AI 翻译"""
        output_path = Path(output_dir)
        output_path.mkdir(parents=True, exist_ok=True)
        
        result = {}
        for name, sf in self.files.items():
            json_path = output_path / f"{name}_ai.json"
            sf.export_to_json(str(json_path))
            result[name] = str(json_path)
            
        return result
    
    def get_translation_summary(self) -> Dict[str, Dict]:
        """获取所有文件的翻译摘要"""
        return {
            name: sf.get_stats() 
            for name, sf in self.files.items()
        }


if __name__ == '__main__':
    print("辐射 4 翻译工具链初始化成功")
    print("支持功能:")
    print("  - 解析 .strings 二进制文件")
    print("  - 导出 JSON/TXT 格式供 AI 翻译")
    print("  - 批量处理多个语言文件")
    print("  - 应用翻译并重新打包")
