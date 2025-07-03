import os
import sys
import json

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from utils.translator import TranslationManager
from utils.ask_gpt import GPTResponseGenerator

def main():
    # 初始化翻译管理器和 GPT 响应生成器
    manager = TranslationManager()
    gpt = GPTResponseGenerator()

    # 获取用户输入
    input_text = manager.get_user_input()

    # 生成翻译字典
    translation_dict = manager.build_translation_dict(input_text)
    print("\n翻译结果:")
    print(json.dumps(translation_dict, indent=2, ensure_ascii=False))

    # 生成 ai回答1 和 ai回答2（需要传入原始文本）
    ai_response1 = gpt.analyze_translation_quality(translation_dict, input_text)
    ai_response2 = gpt.generate_multilingual_responses(translation_dict, input_text)

    print("\nai回答1（翻译质量分析）:")
    print(json.dumps(ai_response1, indent=2, ensure_ascii=False))

    print("\nai回答2（多语言回答）:")
    print(json.dumps(ai_response2, indent=2, ensure_ascii=False))

    # 将 ai回答2 的回答内容翻译成英文
    final_result = manager.translate_answers_to_english(ai_response2, input_text)
    print("\n最终结果:")
    print(json.dumps(final_result, indent=2, ensure_ascii=False))

if __name__ == "__main__":
    main()
