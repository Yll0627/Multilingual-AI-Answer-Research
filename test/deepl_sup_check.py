from deepl import Translator
from dotenv import load_dotenv

# 加载环境变量
load_dotenv()

import os

translator = Translator(os.getenv("DEEPL_API_KEY"))
print("支持的源语言:", [lang.code for lang in translator.get_source_languages()])
print("支持的目标语言:", [lang.code for lang in translator.get_target_languages()])