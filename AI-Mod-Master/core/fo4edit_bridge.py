"""
FO4Edit 桥接器模块
提供与 FO4Edit 命令行工具的交互接口
用于 ESP/ESM 文件的导出和分析
"""

import subprocess
import json
import os
from pathlib import Path
from typing import Dict, List, Any, Optional, Tuple


class FO4EditBridge:
    """FO4Edit 命令行桥接器"""
    
    def __init__(self, fo4edit_path: str):
        """
        初始化 FO4Edit 桥接器
        
        Args:
            fo4edit_path: FO4Edit.exe 的完整路径
        """
        self.fo4edit_path = Path(fo4edit_path)
        if not self.fo4edit_path.exists():
            raise FileNotFoundError(f"FO4Edit 未找到：{fo4edit_path}")
    
    def validate_path(self, mod_path: str) -> Tuple[bool, str]:
        """
        验证 Mod 文件路径
        
        Returns:
            (是否有效，消息)
        """
        path = Path(mod_path)
        if not path.exists():
            return False, f"文件不存在：{mod_path}"
        
        if not path.suffix.lower() in ['.esp', '.esm']:
            return False, f"不支持的文件类型：{path.suffix}"
        
        return True, "文件验证通过"
    
    def export_to_json(self, mod_path: str, output_path: Optional[str] = None) -> Optional[Dict[str, Any]]:
        """
        使用 FO4Edit 导出 Mod 为 JSON 格式
        
        Args:
            mod_path: Mod 文件路径
            output_path: 输出 JSON 文件路径（可选）
            
        Returns:
            JSON 数据字典，失败返回 None
        """
        mod_file = Path(mod_path)
        
        # 临时输出文件
        if output_path:
            json_output = Path(output_path)
        else:
            json_output = mod_file.with_suffix('.json')
        
        # FO4Edit 命令行参数
        # -script: 运行导出脚本
        # -quiet: 静默模式
        args = [
            str(self.fo4edit_path),
            mod_path,
            "-script:ExportToJSON",
            f"-output:{json_output}",
            "-quiet"
        ]
        
        try:
            # 启动 FO4Edit 进程
            process = subprocess.Popen(
                args,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                cwd=str(self.fo4edit_path.parent)
            )
            
            # 等待完成（带超时）
            stdout, stderr = process.communicate(timeout=300)
            
            if process.returncode != 0:
                print(f"FO4Edit 执行失败：{stderr.decode('utf-8', errors='ignore')}")
                return None
            
            # 读取 JSON 结果
            if json_output.exists():
                with open(json_output, 'r', encoding='utf-8') as f:
                    return json.load(f)
            else:
                print("FO4Edit 未生成输出文件")
                return None
                
        except subprocess.TimeoutExpired:
            process.kill()
            print("FO4Edit 执行超时")
            return None
        except Exception as e:
            print(f"FO4Edit 调用异常：{e}")
            return None
    
    def get_mod_info(self, mod_path: str) -> Optional[Dict[str, Any]]:
        """
        获取 Mod 基本信息（无需完全导出）
        
        Returns:
            包含文件名、大小、Master 列表等信息的字典
        """
        path = Path(mod_path)
        if not path.exists():
            return None
        
        info = {
            'file_name': path.name,
            'file_size': path.stat().st_size,
            'is_master': path.suffix.lower() == '.esm',
            'masters': []
        }
        
        # 尝试从文件头读取 Master 信息
        try:
            with open(path, 'rb') as f:
                # 跳过 TES4 头
                f.read(4)  # TES4
                header_size = int.from_bytes(f.read(4), 'little')
                f.read(header_size)
                
                # 读取 HEDR 子记录
                rec_type = f.read(4).decode('ascii', errors='ignore')
                if rec_type == 'HEDR':
                    rec_size = int.from_bytes(f.read(2), 'little')
                    hedr_data = f.read(rec_size)
                    # 解析版本和记录数
                    version = float.from_bytes(hedr_data[0:4], 'little')
                    record_count = int.from_bytes(hedr_data[4:8], 'little')
                    info['version'] = version
                    info['record_count'] = record_count
                
                # 读取 MAST 记录（Master 依赖）
                while True:
                    rec_type = f.read(4).decode('ascii', errors='ignore')
                    if not rec_type or rec_type == 'TES4':
                        break
                    
                    rec_size = int.from_bytes(f.read(2), 'little')
                    
                    if rec_type == 'MAST':
                        mast_data = f.read(rec_size)
                        mast_name = mast_data.decode('utf-8', errors='ignore').strip('\x00')
                        info['masters'].append(mast_name)
                    else:
                        f.read(rec_size)
                        
        except Exception as e:
            print(f"读取 Mod 信息失败：{e}")
        
        return info
    
    def analyze_conflicts(self, mod_paths: List[str]) -> Dict[str, Any]:
        """
        分析多个 Mod 之间的冲突
        
        Args:
            mod_paths: Mod 文件路径列表（按加载顺序）
            
        Returns:
            冲突分析报告
        """
        conflicts = {
            'total_mods': len(mod_paths),
            'conflicts': [],
            'warnings': []
        }
        
        # 简化的冲突检测逻辑
        # 实际应使用 FO4Edit 的脚本功能进行深度分析
        form_ids = {}
        
        for i, mod_path in enumerate(mod_paths):
            info = self.get_mod_info(mod_path)
            if not info:
                continue
            
            conflicts['warnings'].append({
                'mod': Path(mod_path).name,
                'message': f"加载位置：{i+1}, Masters: {info['masters']}"
            })
        
        return conflicts
    
    @staticmethod
    def find_fo4edit() -> Optional[str]:
        """
        自动查找 FO4Edit 安装位置
        
        Returns:
            FO4Edit.exe 路径，未找到返回 None
        """
        # 常见安装路径
        search_paths = [
            Path(r"C:\Games\FO4Edit\FO4Edit.exe"),
            Path(r"C:\Program Files\FO4Edit\FO4Edit.exe"),
            Path.home() / "Games" / "FO4Edit" / "FO4Edit.exe",
            Path(os.environ.get('PROGRAMFILES', '')) / "FO4Edit" / "FO4Edit.exe",
        ]
        
        for path in search_paths:
            if path.exists():
                return str(path)
        
        # 尝试从注册表查找（仅 Windows）
        if os.name == 'nt':
            try:
                import winreg
                with winreg.OpenKey(winreg.HKEY_LOCAL_MACHINE, r"SOFTWARE\FO4Edit") as key:
                    install_path = winreg.QueryValueEx(key, "InstallPath")[0]
                    exe_path = Path(install_path) / "FO4Edit.exe"
                    if exe_path.exists():
                        return str(exe_path)
            except Exception:
                pass
        
        return None


# 模拟 FO4Edit 功能（当 FO4Edit 不可用时）
class MockFO4EditBridge:
    """FO4Edit 桥接器的模拟实现（用于测试和无 FO4Edit 环境）"""
    
    def __init__(self, fo4edit_path: str = ""):
        self.fo4edit_path = Path(fo4edit_path) if fo4edit_path else None
    
    def validate_path(self, mod_path: str) -> Tuple[bool, str]:
        path = Path(mod_path)
        if not path.exists():
            return False, f"文件不存在：{mod_path}"
        if not path.suffix.lower() in ['.esp', '.esm']:
            return False, f"不支持的文件类型：{path.suffix}"
        return True, "文件验证通过（模拟模式）"
    
    def export_to_json(self, mod_path: str, output_path: Optional[str] = None) -> Optional[Dict[str, Any]]:
        """模拟导出 JSON"""
        print(f"[模拟] 导出 {mod_path} 为 JSON")
        
        # 返回模拟数据
        return {
            'header': {
                'signature': 'TES4',
                'version': 0.94,
                'game': 'Fallout4'
            },
            'record_count': 150,
            'records': [
                {
                    'form_id': '00001234',
                    'editor_id': 'TestRecord',
                    'record_type': 'WEAP',
                    'flags': 0,
                    'data': {
                        'FULL': 'Test Weapon',
                        'DESC': 'A test weapon for demonstration'
                    }
                }
            ],
            'masters': ['Fallout4.esm', 'DLCRobot.esm']
        }
    
    def get_mod_info(self, mod_path: str) -> Optional[Dict[str, Any]]:
        """模拟获取 Mod 信息"""
        path = Path(mod_path)
        if not path.exists():
            return None
        
        return {
            'file_name': path.name,
            'file_size': path.stat().st_size,
            'is_master': path.suffix.lower() == '.esm',
            'masters': ['Fallout4.esm'],
            'version': 0.94,
            'record_count': 100
        }
    
    def analyze_conflicts(self, mod_paths: List[str]) -> Dict[str, Any]:
        """模拟冲突分析"""
        return {
            'total_mods': len(mod_paths),
            'conflicts': [],
            'warnings': [{'mod': Path(p).name, 'message': '模拟模式：未检测到冲突'} for p in mod_paths]
        }
    
    @staticmethod
    def find_fo4edit() -> Optional[str]:
        """总是返回 None（模拟模式）"""
        return None


if __name__ == '__main__':
    print("FO4Edit 桥接器模块")
    print("支持功能:")
    print("  - 调用 FO4Edit 命令行导出 JSON")
    print("  - 获取 Mod 基本信息")
    print("  - 分析 Mod 冲突")
    print("  - 自动查找 FO4Edit 安装位置")
    print("\n注意：需要安装 FO4Edit 才能使用完整功能")
    print("如无 FO4Edit，可使用 MockFO4EditBridge 进行测试")
