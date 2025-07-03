import os
import json
from openai import OpenAI
from typing import Dict, Any

class GPTResponseGenerator:
    def __init__(self):
        self.client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))
        self.gpt_model = "gpt-4-1106-preview"  # 替换为实际使用的模型名称

    def analyze_translation_quality(self, translation_dict: Dict, original_text: str) -> Dict:
        """
        生成 AI 回答 1：分析翻译的准确性（意义、语调、情感）
        """
        prompt = f"""
        请分析以下翻译是否准确。检查以下方面：
        1. 意义是否与原文一致
        2. 语调是否匹配
        3. 情感是否保留
        返回 JSON 格式的结果，键为语言代码，值为分析结论。

        原文（{translation_dict['源语言lang']}）: {original_text}
        翻译结果:
        {json.dumps(translation_dict['翻译语言'], indent=2, ensure_ascii=False)}
        """

        response = self.client.chat.completions.create(
            model=self.gpt_model,
            messages=[{"role": "user", "content": prompt}],
            temperature=0.3,
            response_format={"type": "json_object"}
        )
        return json.loads(response.choices[0].message.content)


    def generate_multilingual_responses(self, translation_dict: Dict, original_text: str) -> Dict:
        from .translator import TranslationManager
        lang_display_names = TranslationManager().lang_display_names
        ai_response2 = {
            "源语言lang": translation_dict["源语言lang"],
            "翻译语言": {}
        }

        # 添加语言代码到名称的映射
        lang_name_mapping = {
            "EN-US": "英语（美式）",
            "RU": "俄语", 
            "DE": "德语",
            "FR": "法语",
            "ZH-HANS": "简体中文"
        }

        for lang, translated_text in translation_dict["翻译语言"].items():
            if not translated_text: continue

            # 使用映射获取自然语言名称
            lang_name = lang_display_names.get(lang, lang)  # 关键修改

            prompt = f"""
            请用 {lang_name} 回答以下问题，要求：
            1. 使用{lang_name}直接回答，不要中文解释
            2. 内容简洁专业
            3. 不要直译原文，需自然表达

            问题：{translated_text}
            """

            try:
                response = self.client.chat.completions.create(
                    model=self.gpt_model,
                    messages=[{"role": "user", "content": prompt}],
                    temperature=0.5
                )
                answer = response.choices[0].message.content.strip()
            except Exception as e:
                print(f"GPT生成{lang}回答失败: {str(e)}")
                answer = None

            ai_response2["翻译语言"][lang] = {
                "翻译内容": translated_text,
                "回答内容": answer if answer else translated_text  # 失败时回退翻译文本
            }

        return ai_response2


if __name__ == "__main__":
    # 测试代码
    from translator import TranslationManager

    # 生成翻译字典
    manager = TranslationManager()
    input_text = manager.get_user_input()  # 原始输入文本
    translation_dict = manager.build_translation_dict(input_text)

    # 调用 GPT 分析
    gpt = GPTResponseGenerator()
    ai_response1 = gpt.analyze_translation_quality(translation_dict, input_text)
    ai_response2 = gpt.generate_multilingual_responses(translation_dict, input_text)

    print("\nai回答1（翻译质量分析）:")
    print(json.dumps(ai_response1, indent=2, ensure_ascii=False))

    print("\nai回答2（多语言回答）:")
    print(json.dumps(ai_response2, indent=2, ensure_ascii=False))
