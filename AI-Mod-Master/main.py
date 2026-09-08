"""
AI-Mod-Master 主程序
统一入口，整合所有功能模块
"""

import argparse
import json
import sys
from pathlib import Path

# 导入核心模块
from core.esp_parser import ESPParser, ModModifier
from translation.strings_processor import StringsFile, TranslationBatch
from ai_agent.mod_agent import ModAIAgent, AITask


def cmd_parse(args):
    """解析 Mod 文件命令"""
    print(f"正在解析 Mod 文件：{args.input}")
    
    parser = ESPParser(args.input)
    if parser.parse():
        print(f"✓ 解析成功：共{len(parser.records)}条记录")
        
        if args.output:
            json_data = parser.to_json()
            with open(args.output, 'w', encoding='utf-8') as f:
                json.dump(json_data, f, ensure_ascii=False, indent=2)
            print(f"✓ 已导出 JSON 到：{args.output}")
        
        if args.analyze:
            agent = ModAIAgent()
            response = agent.analyze_mod(parser.to_json())
            print(f"\nAI 分析结果:")
            print(f"  {response.message}")
            for suggestion in response.suggestions:
                print(f"  - {suggestion}")
    else:
        print("✗ 解析失败")
        return 1
    
    return 0


def cmd_translate(args):
    """翻译命令"""
    print(f"正在处理翻译：{args.input}")
    
    strings_file = StringsFile(args.input)
    if strings_file.parse():
        stats = strings_file.get_stats()
        print(f"✓ 加载成功：共{stats['total']}条字符串")
        print(f"  已翻译：{stats['translated']}, 未翻译：{stats['untranslated']}")
        
        # 导出供 AI 翻译
        if args.export:
            strings_file.export_to_json(args.export)
            print(f"✓ 已导出 JSON 到：{args.export}")
        
        # 使用 AI 翻译
        if args.ai_translate:
            agent = ModAIAgent(api_key=args.api_key)
            
            texts = [
                {'form_id': e.form_id, 'original': e.original_text}
                for e in strings_file.entries.values()
                if not e.translated_text
            ]
            
            if texts:
                print(f"正在调用 AI 翻译 {len(texts)} 条文本...")
                response = agent.translate_texts(texts, target_lang=args.lang)
                
                if response.success:
                    count = strings_file.apply_translations(response.result)
                    print(f"✓ 应用了{count}条翻译")
                    
                    if args.output:
                        strings_file.save_binary(args.output)
                        print(f"✓ 已保存到：{args.output}")
            else:
                print("没有需要翻译的文本")
    else:
        print("✗ 加载失败")
        return 1
    
    return 0


def cmd_analyze(args):
    """AI 分析命令"""
    print(f"正在分析 Mod：{args.input}")
    
    parser = ESPParser(args.input)
    if parser.parse():
        agent = ModAIAgent(api_key=args.api_key)
        
        # 分析结构
        response = agent.analyze_mod(parser.to_json())
        print(f"\n📊 Mod 分析报告:")
        print(f"  {response.message}")
        
        result = response.result
        print(f"\n详细信息:")
        print(f"  总记录数：{result.get('total_records', 0)}")
        print(f"  复杂度：{result.get('complexity', 'unknown')}")
        print(f"  包含脚本：{'是' if result.get('has_scripts') else '否'}")
        print(f"  包含文本：{'是' if result.get('has_texts') else '否'}")
        
        if result.get('record_types'):
            print(f"\n记录类型分布:")
            for rec_type, count in sorted(result['record_types'].items(), key=lambda x: x[1], reverse=True)[:10]:
                print(f"  {rec_type}: {count}")
        
        print(f"\n💡 建议:")
        for suggestion in response.suggestions:
            print(f"  - {suggestion}")
        
        # 错误检测
        if args.check_errors:
            print(f"\n🔍 错误检测:")
            error_response = agent.detect_errors(parser.to_json())
            result_data = error_response.result
            
            if result_data.get('errors'):
                print(f"  ✗ 发现{len(result_data['errors'])}个错误:")
                for error in result_data['errors']:
                    print(f"    [{error['severity'].upper()}] {error['details']}")
            
            if result_data.get('warnings'):
                print(f"  ⚠ 发现{len(result_data['warnings'])}个警告:")
                for warning in result_data['warnings']:
                    print(f"    [{warning['severity'].upper()}] {warning['details']}")
            
            print(f"\n{error_response.message}")
    else:
        print("✗ 解析失败")
        return 1
    
    return 0


def cmd_generate(args):
    """生成 Mod 内容命令"""
    print(f"根据提示生成内容：{args.prompt}")
    
    agent = ModAIAgent(api_key=args.api_key)
    response = agent.generate_content(args.prompt)
    
    if response.success:
        print(f"\n✓ {response.message}")
        result = response.result
        
        print(f"\n生成的内容:")
        print(f"  类型：{result.get('type', 'unknown')}")
        print(f"  描述：{result.get('description', '')}")
        
        if result.get('records'):
            print(f"\n生成的记录:")
            for record in result['records']:
                print(f"  - FormID: {record.get('form_id')}")
                print(f"    类型：{record.get('record_type')}")
                print(f"    名称：{record.get('data', {}).get('FULL', 'N/A')}")
        
        print(f"\n💡 建议:")
        for suggestion in response.suggestions:
            print(f"  - {suggestion}")
        
        # 保存结果
        if args.output:
            with open(args.output, 'w', encoding='utf-8') as f:
                json.dump(result, f, ensure_ascii=False, indent=2)
            print(f"\n✓ 已保存到：{args.output}")
    else:
        print(f"✗ 生成失败：{response.message}")
        return 1
    
    return 0


def main():
    parser = argparse.ArgumentParser(
        description='AI-Mod-Master: 辐射 4 Mod 智能重构与翻译平台',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
示例用法:
  %(prog)s parse mymod.esp --output mod.json --analyze
  %(prog)s translate Fallout4_Chinese.strings --ai-translate --api-key YOUR_KEY
  %(prog)s analyze mymod.esp --check-errors
  %(prog)s generate "创建一把激光步枪" --output new_weapon.json
        """
    )
    
    subparsers = parser.add_subparsers(dest='command', help='可用命令')
    
    # parse 命令
    parse_parser = subparsers.add_parser('parse', help='解析 Mod 文件')
    parse_parser.add_argument('input', help='输入的 .esp/.esm 文件')
    parse_parser.add_argument('--output', '-o', help='输出 JSON 文件路径')
    parse_parser.add_argument('--analyze', action='store_true', help='同时进行 AI 分析')
    parse_parser.set_defaults(func=cmd_parse)
    
    # translate 命令
    trans_parser = subparsers.add_parser('translate', help='翻译字符串文件')
    trans_parser.add_argument('input', help='输入的 .strings 文件')
    trans_parser.add_argument('--export', '-e', help='导出 JSON 文件路径')
    trans_parser.add_argument('--ai-translate', action='store_true', help='使用 AI 自动翻译')
    trans_parser.add_argument('--api-key', help='AI API 密钥')
    trans_parser.add_argument('--lang', default='zh-CN', help='目标语言 (默认：zh-CN)')
    trans_parser.add_argument('--output', '-o', help='输出翻译后的文件路径')
    trans_parser.set_defaults(func=cmd_translate)
    
    # analyze 命令
    analyze_parser = subparsers.add_parser('analyze', help='AI 分析 Mod')
    analyze_parser.add_argument('input', help='输入的 .esp/.esm 文件')
    analyze_parser.add_argument('--api-key', help='AI API 密钥')
    analyze_parser.add_argument('--check-errors', action='store_true', help='检查错误和冲突')
    analyze_parser.set_defaults(func=cmd_analyze)
    
    # generate 命令
    gen_parser = subparsers.add_parser('generate', help='生成 Mod 内容')
    gen_parser.add_argument('prompt', help='自然语言描述')
    gen_parser.add_argument('--api-key', help='AI API 密钥')
    gen_parser.add_argument('--output', '-o', help='输出 JSON 文件路径')
    gen_parser.set_defaults(func=cmd_generate)
    
    args = parser.parse_args()
    
    if not args.command:
        parser.print_help()
        return 0
    
    return args.func(args)


if __name__ == '__main__':
    sys.exit(main())
