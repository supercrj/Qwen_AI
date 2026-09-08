"""
AI 智能代理引擎
支持 Mod 分析、翻译、差错检测和自动修改
"""

import json
from typing import Dict, List, Any, Optional
from pydantic import BaseModel


class AITask(BaseModel):
    """AI 任务模型"""
    task_type: str  # translate, fix_errors, merge_mods, sort_load_order, create_content
    input_data: Dict[str, Any]
    context: str = ""
    priority: int = 1


class AIResponse(BaseModel):
    """AI 响应模型"""
    success: bool
    result: Any
    message: str
    suggestions: List[str] = []


class ModAIAgent:
    """Mod AI 智能代理"""
    
    def __init__(self, api_key: Optional[str] = None, model: str = "gpt-4"):
        self.api_key = api_key
        self.model = model
        self.task_history: List[AITask] = []
        
    def analyze_mod(self, mod_json: Dict[str, Any]) -> AIResponse:
        """分析 Mod 文件结构"""
        # 模拟 AI 分析逻辑
        record_count = mod_json.get('record_count', 0)
        records = mod_json.get('records', [])
        
        # 统计记录类型
        type_counts = {}
        for record in records:
            rec_type = record.get('record_type', 'UNKNOWN')
            type_counts[rec_type] = type_counts.get(rec_type, 0) + 1
        
        analysis = {
            'total_records': record_count,
            'record_types': type_counts,
            'has_scripts': any(r.get('record_type') == 'SCPT' for r in records),
            'has_texts': any('FULL' in r.get('data', {}) for r in records),
            'complexity': 'high' if record_count > 1000 else 'medium' if record_count > 100 else 'low'
        }
        
        return AIResponse(
            success=True,
            result=analysis,
            message=f"分析完成：共{record_count}条记录，涉及{len(type_counts)}种类型",
            suggestions=[
                "建议检查冲突记录",
                "可以优化大型记录组",
                "考虑添加翻译支持"
            ]
        )
    
    def translate_texts(self, texts: List[Dict[str, str]], target_lang: str = "zh-CN") -> AIResponse:
        """翻译文本内容"""
        translations = {}
        
        for item in texts:
            form_id = item.get('form_id', '')
            original = item.get('original', '')
            
            # 模拟翻译 (实际应调用 LLM API)
            translated = self._mock_translate(original, target_lang)
            
            if translated:
                translations[form_id] = translated
        
        return AIResponse(
            success=True,
            result=translations,
            message=f"完成{len(translations)}条文本的翻译",
            suggestions=[
                "建议人工校对专业术语",
                "检查上下文一致性",
                "验证特殊字符编码"
            ]
        )
    
    def detect_errors(self, mod_json: Dict[str, Any], reference_mods: List[Dict] = None) -> AIResponse:
        """检测 Mod 错误和冲突"""
        errors = []
        warnings = []
        
        records = mod_json.get('records', [])
        
        # 检查重复 FormID
        form_ids = [r.get('form_id') for r in records]
        duplicates = set([x for x in form_ids if form_ids.count(x) > 1])
        if duplicates:
            errors.append({
                'type': 'duplicate_form_id',
                'severity': 'critical',
                'details': f"发现{len(duplicates)}个重复的 FormID",
                'affected_ids': list(duplicates)[:10]
            })
        
        # 检查缺失的 Master 依赖
        # TODO: 实现完整的依赖检查
        
        # 检查空引用
        empty_refs = [r for r in records if not r.get('editor_id')]
        if empty_refs:
            warnings.append({
                'type': 'empty_editor_id',
                'severity': 'low',
                'details': f"发现{len(empty_refs)}个缺少 EditorID 的记录",
                'count': len(empty_refs)
            })
        
        return AIResponse(
            success=len(errors) == 0,
            result={'errors': errors, 'warnings': warnings},
            message=f"检测完成：{len(errors)}个错误，{len(warnings)}个警告",
            suggestions=[
                "修复所有 critical 级别错误",
                "检查冲突的 FormID",
                "验证 Master 依赖关系"
            ] if errors else ["Mod 结构良好，无明显问题"]
        )
    
    def suggest_load_order(self, mods: List[Dict[str, Any]]) -> AIResponse:
        """建议最优加载顺序"""
        # 简单的依赖排序算法
        sorted_mods = []
        
        # 按依赖关系排序 (简化版)
        # 实际应构建完整的依赖图
        for mod in mods:
            mod_name = mod.get('name', 'unknown')
            is_master = mod.get('is_master', False)
            
            if is_master:
                sorted_mods.insert(0, mod_name)
            else:
                sorted_mods.append(mod_name)
        
        return AIResponse(
            success=True,
            result={'load_order': sorted_mods},
            message=f"已为{len(mods)}个 Mod 生成加载顺序",
            suggestions=[
                "Master 文件应放在最前面",
                "检查循环依赖",
                "使用 LOOT 验证排序结果"
            ]
        )
    
    def generate_content(self, prompt: str, context: Dict[str, Any] = None) -> AIResponse:
        """根据自然语言生成 Mod 内容"""
        # 解析用户意图
        content_type = self._detect_intent(prompt)
        
        generated = {
            'type': content_type,
            'records': [],
            'description': f"根据提示生成的{content_type}内容"
        }
        
        # 示例：生成一个新物品
        if content_type == 'weapon':
            generated['records'] = [{
                'form_id': '0001ABCD',
                'record_type': 'WEAP',
                'editor_id': 'MyCustomWeapon',
                'data': {
                    'FULL': '自定义武器',
                    'DESC': '由 AI 生成的强力武器'
                }
            }]
        
        return AIResponse(
            success=True,
            result=generated,
            message=f"已生成{content_type}类型的内容",
            suggestions=[
                "审查生成的 FormID 是否冲突",
                "调整数值平衡",
                "添加适当的依赖关系"
            ]
        )
    
    def _mock_translate(self, text: str, target_lang: str) -> str:
        """模拟翻译 (实际应调用 OpenAI/Anthropic API)"""
        # 这里只是示例，实际应调用 LLM
        if target_lang == "zh-CN":
            return f"[中文]{text}"  # 占位符
        return text
    
    def _detect_intent(self, prompt: str) -> str:
        """检测用户意图"""
        prompt_lower = prompt.lower()
        
        if any(word in prompt_lower for word in ['武器', 'weapon', '枪', 'sword']):
            return 'weapon'
        elif any(word in prompt_lower for word in ['盔甲', 'armor', '护甲']):
            return 'armor'
        elif any(word in prompt_lower for word in ['npc', '角色', 'character']):
            return 'npc'
        elif any(word in prompt_lower for word in ['任务', 'quest', 'mission']):
            return 'quest'
        else:
            return 'generic'
    
    def execute_task(self, task: AITask) -> AIResponse:
        """执行 AI 任务"""
        self.task_history.append(task)
        
        if task.task_type == 'analyze':
            return self.analyze_mod(task.input_data)
        elif task.task_type == 'translate':
            return self.translate_texts(task.input_data.get('texts', []))
        elif task.task_type == 'detect_errors':
            return self.detect_errors(task.input_data)
        elif task.task_type == 'sort_load_order':
            return self.suggest_load_order(task.input_data.get('mods', []))
        elif task.task_type == 'generate':
            return self.generate_content(
                task.input_data.get('prompt', ''),
                task.context
            )
        else:
            return AIResponse(
                success=False,
                result=None,
                message=f"未知的任务类型：{task.task_type}"
            )


if __name__ == '__main__':
    print("AI 智能代理引擎初始化成功")
    print("支持功能:")
    print("  - Mod 结构分析")
    print("  - 自动翻译文本")
    print("  - 错误和冲突检测")
    print("  - 智能加载顺序排序")
    print("  - 自然语言生成 Mod 内容")
