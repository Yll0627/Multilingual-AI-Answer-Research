import os
from deepl import Translator
from dotenv import load_dotenv
from typing import Dict

# 加载环境变量
load_dotenv()

class TranslationManager:
    def __init__(self):
        self.deepl_client = Translator(os.getenv("DEEPL_API_KEY"))
        
        # 使用 DeepL 支持的目标语言代码
        self.target_langs = ["EN-US", "FR", "DE", "ZH-HANS", "RU"]
        
        self.lang_display_names = {
        "EN-US": "English-US",
        "RU": "Russian",
        "DE": "German",
        "FR": "French",
        "ZH-HANS": "Simplified Chinese"
    }
        # DeepL 支持的源语言列表
        self.valid_source_langs = {'BG', 'CS', 'DA', 'DE', 'EL', 'EN', 'ES', 'ET', 'FI', 'FR', 
                                  'HU', 'ID', 'IT', 'JA', 'KO', 'LT', 'LV', 'NB', 'NL', 'PL', 
                                  'PT', 'RO', 'RU', 'SK', 'SL', 'SV', 'TR', 'UK', 'ZH'}

    def get_user_input(self) -> str:
        """在终端获取用户输入"""
        while True:
            user_input = input("请输入一句话（按 Ctrl+C 退出）: ").strip()
            if user_input:
                return user_input
            print("输入不能为空，请重新输入。")

    def detect_source_lang(self, text: str) -> str:
        """检测输入文本的源语言（返回标准代码）"""
        result = self.deepl_client.translate_text(text, target_lang="EN-US")
        detected_lang = result.detected_source_lang.upper()
        
        # 标准化语言代码
        lang_mapping = {
            "NB": "EN",   # Norwegian Bokmål 映射到英语
            "ZH-HANS": "ZH"  # 简体中文统一用 ZH
        }
        detected_lang = lang_mapping.get(detected_lang, detected_lang)
        
        # 如果检测到不支持的语言，默认回退到英语
        return detected_lang if detected_lang in self.valid_source_langs else "EN"

    def translate_text(self, text: str, source_lang: str, target_lang: str) -> str:
        """调用 DeepL 翻译单条文本（严格验证语言代码）"""
        # 检查源语言是否有效
        if source_lang not in self.valid_source_langs:
            raise ValueError(f"不支持的源语言代码: {source_lang}")
        
        # 处理特殊语言代码
        target_lang = "ZH-HANS" if target_lang == "ZH" else target_lang  

        result = self.deepl_client.translate_text(
            text,
            source_lang=source_lang,
            target_lang=target_lang
        )
        return result.text

    def build_translation_dict(self, text: str) -> dict:
        """构建翻译字典（自动处理语言代码转换）"""
        source_lang = self.detect_source_lang(text)
        translation_dict = {
            "源语言lang": source_lang,
            "翻译语言": {}
        }

        for target_lang in self.target_langs:
            src_code = source_lang.split("-")[0]  # 处理 EN-US -> EN 之类的情况
            tgt_code = target_lang.split("-")[0]

            # **如果目标语言和源语言相同，则直接使用原文本**
            if src_code == tgt_code or source_lang == target_lang:
                translation_dict["翻译语言"][target_lang] = text
                continue

            try:
                translated_text = self.translate_text(text, source_lang, target_lang)
                translation_dict["翻译语言"][target_lang] = translated_text
            except Exception as e:
                print(f"翻译到 {target_lang} 失败: {str(e)}")
                translation_dict["翻译语言"][target_lang] = None

        return translation_dict
    
    def translate_answers_to_english(self, ai_response2: Dict, original_text: str) -> Dict:
        """
        将 AI 生成的回答翻译成英文（EN-US）。
        - 如果目标语言已经是 EN-US，直接保留原内容，不翻译。
        - 如果回答内容与原文相同，直接保留原文。
        - 仅在目标语言不为 EN-US 且内容不同于原文时，调用 DeepL 进行翻译。
        """
        final_result = {
            "源语言lang": ai_response2["源语言lang"],
            "翻译语言": {}
        }

        for lang, content in ai_response2["翻译语言"].items():
            if not content["回答内容"]:
                continue  # 跳过空内容

            # 如果目标语言已经是 EN-US，直接保留
            if lang == "EN-US":
                final_result["翻译语言"][lang] = {
                    "翻译内容": content["翻译内容"],
                    "回答内容": content["回答内容"],
                    "回答内容EN": content["回答内容"]  # 直接复用原内容
                }
                continue

            # 如果翻译内容与原文相同，直接保留原文
            if content["回答内容"] == original_text:
                final_result["翻译语言"][lang] = {
                    "翻译内容": content["翻译内容"],
                    "回答内容": content["回答内容"],
                    "回答内容EN": original_text  # 直接使用原文本
                }
                continue

            # 需要翻译的情况
            try:
                answer_en = self.translate_text(
                    content["回答内容"], 
                    source_lang=lang.split("-")[0],  # 获取主语言代码
                    target_lang="EN-US"
                )
                final_result["翻译语言"][lang] = {
                    "翻译内容": content["翻译内容"],
                    "回答内容": content["回答内容"],
                    "回答内容EN": answer_en if answer_en else "Translation unavailable"
                }
            except Exception as e:
                print(f"翻译回答到英文失败（{lang}）: {str(e)}")
                final_result["翻译语言"][lang] = {
                    "翻译内容": content["翻译内容"],
                    "回答内容": content["回答内容"],
                    "回答内容EN": None
                }

        return final_result


if __name__ == "__main__":
    manager = TranslationManager()
    input_text = manager.get_user_input()
    translation_dict = manager.build_translation_dict(input_text)
    print("\n翻译结果:")
    print(translation_dict)
