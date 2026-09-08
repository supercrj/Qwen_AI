"""
FO4Edit 核心解析引擎的 Python 实现
支持 .esp/.esm 文件的读取、解析和写入
"""

import struct
from pathlib import Path
from typing import Dict, List, Any, Optional
from pydantic import BaseModel


class FormRecord(BaseModel):
    """表单记录模型"""
    form_id: str
    editor_id: str
    record_type: str
    flags: int
    data: Dict[str, Any]
    modified: bool = False


class ESPParser:
    """ESP/ESM 文件解析器"""
    
    def __init__(self, file_path: str):
        self.file_path = Path(file_path)
        self.records: List[FormRecord] = []
        self.header: Dict[str, Any] = {}
        
    def parse(self) -> bool:
        """解析 ESP/ESM 文件"""
        if not self.file_path.exists():
            raise FileNotFoundError(f"文件不存在：{self.file_path}")
            
        with open(self.file_path, 'rb') as f:
            # 读取文件头
            self._read_header(f)
            
            # 读取所有记录
            while f.tell() < self.file_path.stat().st_size:
                record = self._read_record(f)
                if record:
                    self.records.append(record)
                    
        return True
    
    def _read_header(self, f):
        """读取文件头"""
        # TES4 头部标识
        header_sig = f.read(4)
        if header_sig != b'TES4':
            raise ValueError("无效的 ESP/ESM 文件格式")
            
        # 读取头部大小和数据
        header_size = struct.unpack('<I', f.read(4))[0]
        header_data = f.read(header_size)
        
        self.header = {
            'signature': header_sig.decode('ascii'),
            'size': header_size,
            'raw_data': header_data.hex()
        }
    
    def _read_record(self, f) -> Optional[FormRecord]:
        """读取单个记录"""
        try:
            # 记录类型 (4 字节)
            rec_type = f.read(4).decode('ascii', errors='ignore')
            
            # 记录大小 (4 字节)
            rec_size = struct.unpack('<I', f.read(4))[0]
            
            # 标志位 (4 字节)
            flags = struct.unpack('<I', f.read(4))[0]
            
            # FormID (4 字节)
            form_id = struct.unpack('<I', f.read(4))[0]
            form_id_str = f"{form_id:08X}"
            
            # 保留字段 (2 字节)
            f.read(2)
            
            # 读取记录数据
            rec_data = f.read(rec_size)
            
            # 解析子记录
            parsed_data = self._parse_subrecords(rec_data)
            
            return FormRecord(
                form_id=form_id_str,
                editor_id=parsed_data.get('EDID', ''),
                record_type=rec_type,
                flags=flags,
                data=parsed_data
            )
        except Exception as e:
            print(f"读取记录失败：{e}")
            return None
    
    def _parse_subrecords(self, data: bytes) -> Dict[str, Any]:
        """解析子记录"""
        result = {}
        offset = 0
        
        while offset < len(data):
            if offset + 6 > len(data):
                break
                
            # 子记录类型 (4 字节)
            sub_type = data[offset:offset+4].decode('ascii', errors='ignore')
            offset += 4
            
            # 子记录大小 (2 字节)
            sub_size = struct.unpack('<H', data[offset:offset+2])[0]
            offset += 2
            
            # 子记录数据
            sub_data = data[offset:offset+sub_size]
            offset += sub_size
            
            # 根据类型解析数据
            if sub_type == 'EDID':  # Editor ID
                result['EDID'] = sub_data.decode('utf-8', errors='ignore').strip('\x00')
            elif sub_type == 'FULL':  # 名称 (用于翻译)
                result['FULL'] = sub_data.decode('utf-8', errors='ignore').strip('\x00')
            elif sub_type == 'DESC':  # 描述
                result['DESC'] = sub_data.decode('utf-8', errors='ignore').strip('\x00')
            else:
                # 其他数据保存为 hex
                result[sub_type] = sub_data.hex()
                
        return result
    
    def to_json(self) -> Dict[str, Any]:
        """导出为 JSON 格式供 AI 分析"""
        return {
            'header': self.header,
            'record_count': len(self.records),
            'records': [
                {
                    'form_id': r.form_id,
                    'editor_id': r.editor_id,
                    'record_type': r.record_type,
                    'flags': r.flags,
                    'data': r.data
                }
                for r in self.records
            ]
        }
    
    def find_records_by_type(self, record_type: str) -> List[FormRecord]:
        """按类型查找记录"""
        return [r for r in self.records if r.record_type == record_type]
    
    def find_records_by_text(self, search_text: str) -> List[FormRecord]:
        """按文本内容查找记录 (用于翻译定位)"""
        results = []
        for r in self.records:
            for key, value in r.data.items():
                if isinstance(value, str) and search_text.lower() in value.lower():
                    results.append(r)
                    break
        return results


class ModModifier:
    """Mod 修改器"""
    
    def __init__(self, parser: ESPParser):
        self.parser = parser
        
    def update_text(self, form_id: str, new_text: str, field: str = 'FULL') -> bool:
        """更新文本字段 (用于翻译)"""
        for record in self.parser.records:
            if record.form_id == form_id:
                if field in record.data:
                    record.data[field] = new_text
                    record.modified = True
                    return True
        return False
    
    def add_record(self, record: FormRecord) -> bool:
        """添加新记录"""
        # 检查是否已存在
        for r in self.parser.records:
            if r.form_id == record.form_id:
                return False
        self.parser.records.append(record)
        return True
    
    def delete_record(self, form_id: str) -> bool:
        """删除记录"""
        for i, record in enumerate(self.parser.records):
            if record.form_id == form_id:
                del self.parser.records[i]
                return True
        return False
    
    def save(self, output_path: str) -> bool:
        """保存修改后的文件"""
        try:
            with open(output_path, 'wb') as f:
                # 写入文件头
                self._write_header(f)
                
                # 写入所有记录
                for record in self.parser.records:
                    self._write_record(f, record)
            
            return True
        except Exception as e:
            print(f"保存失败：{e}")
            return False
    
    def _write_header(self, f):
        """写入 TES4 文件头"""
        f.write(b'TES4')
        
        # 构建头部数据
        header_data = b''
        # 添加 HEDR 子记录（版本信息）
        hedr_content = struct.pack('<f', 0.94)  # 版本号
        hedr_content += struct.pack('<I', len(self.parser.records))  # 记录数
        hedr_content += struct.pack('<I', 0)  # 未知字段
        
        f.write(struct.pack('<I', len(hedr_content)))  # 头部大小
        f.write(hedr_content)
    
    def _write_record(self, f, record: FormRecord):
        """写入单个记录"""
        # 构建记录数据
        rec_data = b''
        
        # 添加 Editor ID (EDID)
        if record.editor_id:
            edid_bytes = record.editor_id.encode('utf-8') + b'\x00'
            rec_data += b'EDID'
            rec_data += struct.pack('<H', len(edid_bytes))
            rec_data += edid_bytes
        
        # 添加其他数据字段
        for key, value in record.data.items():
            if key in ['FULL', 'DESC'] and isinstance(value, str):
                text_bytes = value.encode('utf-8') + b'\x00'
                rec_data += key.encode('ascii')
                rec_data += struct.pack('<H', len(text_bytes))
                rec_data += text_bytes
            elif key not in ['EDID', 'FULL', 'DESC']:
                # 其他数据从 hex 恢复
                if isinstance(value, str):
                    bin_data = bytes.fromhex(value)
                    rec_data += key.encode('ascii')
                    rec_data += struct.pack('<H', len(bin_data))
                    rec_data += bin_data
        
        # 写入记录头
        f.write(record.record_type.encode('ascii').ljust(4)[:4])
        f.write(struct.pack('<I', len(rec_data)))
        f.write(struct.pack('<I', record.flags))
        f.write(struct.pack('<I', int(record.form_id, 16)))
        f.write(struct.pack('<H', 0))  # 保留字段
        
        # 写入记录数据
        f.write(rec_data)


if __name__ == '__main__':
    # 测试示例
    print("FO4Edit Python Core 初始化成功")
    print("支持功能:")
    print("  - 解析 .esp/.esm 文件")
    print("  - 导出 JSON 格式供 AI 分析")
    print("  - 查找和修改记录")
    print("  - 文本翻译支持")
