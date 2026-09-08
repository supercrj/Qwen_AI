"""
AI-Mod-Master 核心数据模型层 (Model)
定义标准化的数据结构，解耦业务逻辑与 UI
"""
from dataclasses import dataclass, field
from typing import List, Dict, Any, Optional
from enum import Enum
import hashlib

class RecordType(Enum):
    """Fallout 4 记录类型枚举 (去重精简版)"""
    GRUP = "GRUP"
    GMST = "GMST"
    KYWD = "KYWD"
    CLAS = "CLAS"
    FACT = "FACT"
    RACE = "RACE"
    SOUND = "SOUN"
    MGEF = "MGEF"
    SCPT = "SCPT"
    LTEX = "LTEX"
    EFSH = "EFSH"
    ENCH = "ENCH"
    SPEL = "SPEL"
    SCRL = "SCRL"
    ARMO = "ARMO"
    WEAP = "WEAP"
    AMMO = "AMMO"
    NPC_ = "NPC_"
    CREA = "CREA"
    LVLC = "LVLC"
    STAT = "STAT"
    DOOR = "DOOR"
    MISC = "MISC"
    WEAT = "WEAT"
    CLMT = "CLMT"
    REGN = "REGN"
    CELL = "CELL"
    REFR = "REFR"
    ACHR = "ACHR"
    WORL = "WORL"
    LAND = "LAND"
    DIAL = "DIAL"
    INFO = "INFO"
    QUST = "QUST"
    PACK = "PACK"
    LIGH = "LIGH"
    TREE = "TREE"
    FURN = "FURN"
    CONT = "CONT"
    ALCH = "ALCH"
    COBJ = "COBJ"
    OMOD = "OMOD"
    PERK = "PERK"
    IMGS = "IMGS"
    FLST = "FLST"
    SHOU = "SHOU"
    EQUP = "EQUP"
    LVLI = "LVLI"
    WTHR = "WTHR"
    ACTI = "ACTI"
    GLOB = "GLOB"
    MESG = "MESG"
    BOOK = "BOOK"
    NOTE = "NOTE"
    TERM = "TERM"
    PROJ = "PROJ"
    EXPL = "EXPL"
    DEBR = "DEBR"
    WATR = "WATR"
    EYES = "EYES"
    IDLE = "IDLE"
    ANIO = "ANIO"

@dataclass
class ModRecord:
    """单条 Mod 记录的数据模型"""
    form_id: str
    editor_id: str
    record_type: str
    flags: int
    size: int
    data: Dict[str, Any]
    sub_records: List['ModRecord'] = field(default_factory=list)
    
    def to_dict(self) -> Dict:
        return {
            "form_id": self.form_id,
            "editor_id": self.editor_id,
            "type": self.record_type,
            "flags": self.flags,
            "size": self.size,
            "data": self.data,
            "sub_records": [sr.to_dict() for sr in self.sub_records]
        }

@dataclass
class ModFile:
    """Mod 文件的整体数据模型"""
    filename: str
    file_path: str
    header_info: Dict[str, Any]
    records: List[ModRecord]
    masters: List[str]
    light_index: Optional[int] = None
    checksum: str = ""
    
    def calculate_checksum(self):
        """计算文件指纹"""
        # 简化版，实际应读取二进制流
        self.checksum = hashlib.sha256(self.file_path.encode()).hexdigest()[:16]
        
    def to_summary(self) -> Dict:
        return {
            "filename": self.filename,
            "masters": self.masters,
            "record_count": len(self.records),
            "light_index": self.light_index,
            "checksum": self.checksum
        }

@dataclass
class TranslationEntry:
    """翻译条目模型"""
    form_id: str
    original_text: str
    translated_text: str = ""
    status: str = "pending"  # pending, translated, reviewed
    
@dataclass
class UndoAction:
    """撤销动作模型"""
    action_type: str  # modify, delete, create
    target_file: str
    form_id: str
    old_data: Any
    new_data: Any
    timestamp: float
