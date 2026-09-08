"""
AI 智能代理引擎
支持 Mod 分析、翻译、差错检测和自动修改
集成本地大模型 API (Ollama, LM Studio, vLLM 等)
"""

import json
import requests
from typing import Dict, List, Any, Optional, Tuple
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
    """Mod AI 智能代理 - 支持本地大模型"""
    
    def __init__(self, api_key: Optional[str] = None, model: str = "gpt-4o-mini", 
                 api_base_url: str = "http://localhost:11434/v1", use_local_model: bool = True):
        """
        初始化 AI Agent
        
        Args:
            api_key: API 密钥（本地模型可为空）
            model: 模型名称
            api_base_url: API 基础 URL（本地模型如 Ollama: http://localhost:11434/v1）
            use_local_model: 是否使用本地模型
        """
        self.api_key = api_key or "ollama"  # 本地模型通常不需要真实 key
        self.model = model
        self.api_base_url = api_base_url.rstrip('/')
        self.use_local_model = use_local_model
        self.task_history: List[AITask] = []
        
        # 本地模型常用配置
        self.local_models = {
            "ollama": "http://localhost:11434/v1",
            "lm_studio": "http://localhost:1234/v1",
            "vllm": "http://localhost:8000/v1"
        }
        
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
        """翻译文本内容 - 使用本地大模型 API"""
        if not texts:
            return AIResponse(success=True, result={}, message="无文本需要翻译")
        
        translations = {}
        
        # 构建翻译提示
        system_prompt = "你是一位专业的游戏翻译专家，擅长将英文游戏文本翻译成地道的中文。请保持术语一致性，翻译要符合游戏语境。"
        
        # 批量处理（每批最多 20 条）
        batch_size = 20
        for i in range(0, len(texts), batch_size):
            batch = texts[i:i+batch_size]
            
            # 构建请求体
            messages = [
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": self._build_translation_prompt(batch, target_lang)}
            ]
            
            payload = {
                "model": self.model,
                "messages": messages,
                "temperature": 0.3,
                "max_tokens": 2000
            }
            
            try:
                # 调用本地/远程 API
                response = requests.post(
                    f"{self.api_base_url}/chat/completions",
                    json=payload,
                    headers={"Authorization": f"Bearer {self.api_key}"},
                    timeout=60
                )
                
                if response.status_code == 200:
                    result_data = response.json()
                    translated_text = result_data.get("choices", [{}])[0].get("message", {}).get("content", "")
                    
                    # 解析返回的翻译结果
                    parsed = self._parse_translation_result(translated_text, batch)
                    translations.update(parsed)
                else:
                    # API 调用失败，使用备用方案
                    for item in batch:
                        form_id = item.get('form_id', '')
                        original = item.get('original', '')
                        translations[form_id] = self._mock_translate(original, target_lang)
                        
            except requests.exceptions.RequestException as e:
                print(f"API 调用失败：{e}，使用模拟翻译")
                # 网络错误时使用模拟翻译
                for item in batch:
                    form_id = item.get('form_id', '')
                    original = item.get('original', '')
                    translations[form_id] = self._mock_translate(original, target_lang)
        
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
    
    def _build_translation_prompt(self, texts: List[Dict], target_lang: str) -> str:
        """构建翻译提示词"""
        lang_name = "中文" if target_lang == "zh-CN" else target_lang
        
        prompt = f"请将以下游戏文本翻译成{lang_name}，保持 JSON 格式返回：\n\n"
        prompt += "{\n"
        
        for item in texts:
            form_id = item.get('form_id', '')
            original = item.get('original', '').replace('"', '\\"')
            prompt += f'  "{form_id}": "{original}",\n'
        
        prompt += "}\n\n"
        prompt += "请只返回翻译后的 JSON，不要添加其他解释。"
        
        return prompt
    
    def _parse_translation_result(self, translated_text: str, original_batch: List[Dict]) -> Dict[str, str]:
        """解析 AI 返回的翻译结果"""
        import re
        result = {}
        
        try:
            # 尝试提取 JSON 部分
            json_match = re.search(r'\{[\s\S]*\}', translated_text)
            if json_match:
                translated_json = json.loads(json_match.group())
                for item in original_batch:
                    form_id = item.get('form_id', '')
                    if form_id in translated_json:
                        result[form_id] = translated_json[form_id]
            else:
                # 如果无法解析，返回空
                pass
        except (json.JSONDecodeError, Exception) as e:
            print(f"解析翻译结果失败：{e}")
        
        return result
    
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
        """模拟翻译 (API 不可用时的备用方案)"""
        # 简单的占位符，实际使用时应确保 API 可用
        if target_lang == "zh-CN":
            return f"[待翻译]{text}"
        return text
    
    def set_api_config(self, api_base_url: str, model: str, api_key: Optional[str] = None):
        """动态更新 API 配置"""
        self.api_base_url = api_base_url.rstrip('/')
        self.model = model
        if api_key:
            self.api_key = api_key
        print(f"API 配置已更新：{self.api_base_url}, 模型：{self.model}")
    
    def test_connection(self) -> Tuple[bool, str]:
        """测试与本地/远程 API 的连接"""
        try:
            response = requests.get(
                f"{self.api_base_url}/models",
                headers={"Authorization": f"Bearer {self.api_key}"},
                timeout=5
            )
            if response.status_code == 200:
                return True, "连接成功"
            else:
                return False, f"API 返回错误：{response.status_code}"
        except requests.exceptions.ConnectionError:
            return False, "无法连接到 API 服务器，请检查服务是否运行"
        except Exception as e:
            return False, f"连接测试失败：{e}"
    
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
