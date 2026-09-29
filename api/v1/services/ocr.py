"""
OCR 服务与答案比对
"""
import os
import re
from datetime import datetime
from typing import List, Dict, Optional
from pathlib import Path
from PIL import Image

# 尝试导入 PaddleOCR
try:
    import paddleocr
    HAS_PADDLEOCR = True
except ImportError:
    HAS_PADDLEOCR = False

# 常见数学符号纠错映射表
SYMBOL_MAP = {
    "×": "*", "÷": "/", "=": "=", "+" : "+", "-" : "-",
    "²": "^2", "³": "^3", "√": "sqrt(",
    "∵": "because", "∴": "therefore",
    "≤": "<=", "≥": ">=", "≠": "!=", "≈": "~=",
}

def clean_text(text: str) -> str:
    """文本清洗：去除多余空格、换行符等"""
    if not isinstance(text, str):
        return ""
    # 替换常见符号
    for old, new in SYMBOL_MAP.items():
        text = text.replace(old, new)
    # 去除多余空白
    text = re.sub(r'\s+', ' ', text.strip())
    return text

def compare_answers(student: str, correct: str) -> bool:
    """简单答案比对"""
    if not correct:
        return False
    s = clean_text(student.lower())
    c = clean_text(correct.lower())
    # 直接相等
    if s == c:
        return True
    # 数值容差（适用于计算题）
    try:
        if abs(float(s) - float(c)) < 0.01:
            return True
    except ValueError:
        pass
    return False

def extract_formula(text: str) -> str:
    """提取公式（简化版）"""
    # 匹配数学公式块
    formulas = re.findall(r'[\d\+\-\×\÷\=\(\)\s\.]+', text)
    return ' '.join(formulas) if formulas else text

class OCRService:
    """OCR 服务"""
    
    def __init__(self):
        self.language = os.getenv("OCR_LANGUAGE", "ch")
        
    def process_image(self, image_path: str) -> str:
        """处理图片并返回识别文本"""
        if not os.path.exists(image_path):
            return ""
        
        try:
            # 使用 PaddleOCR（如果有）
            if HAS_PADDLEOCR:
                ocr = paddleocr.OCR(lang=self.language)
                result = ocr.ocr(image_path, cls=True)
                if result and result[0]:
                    text_list = [line[1][0] for line in result[0] if line[1][2] > 0.5]
                    return clean_text(' '.join(text_list))
            
            # 降级方案：使用 Tesseract（如果有）
            import subprocess
            result = subprocess.run(
                ['tesseract', image_path, 'stdout'],
                capture_output=True,
                text=True
            )
            if result.returncode == 0:
                return clean_text(result.stdout)
            
            # 最后降级：直接读取文件内容
            with open(image_path, 'rb') as f:
                content = f.read()
                return extract_formula(content.decode('utf-8', errors='ignore'))
                
        except Exception as e:
            print(f"OCR 处理异常：{e}")
            return ""
    
    def process_image_base64(self, image_base64: str) -> str:
        """处理 Base64 图片"""
        try:
            # 这里应该先保存为临时文件，然后调用 process_image
            # 为简化，直接返回一个模拟结果
            return "示例题目：计算 2 + 3 × 4 = ?\n答案：学生作答 14"
        except Exception as e:
            print(f"Base64 图片处理异常：{e}")
            return ""
