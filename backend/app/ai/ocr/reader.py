"""
OCR 图片文字识别模块
支持使用 pytesseract 进行图片文字提取
"""
import io
from pathlib import Path
from typing import Optional

from PIL import Image

try:
    import pytesseract
    PYTESSERACT_AVAILABLE = True
except ImportError:
    PYTESSERACT_AVAILABLE = False

from config.settings import get_setting


class OCRError(Exception):
    """OCR 异常"""
    pass


class OCRReader:
    """OCR 图片文字识别器"""

    def __init__(self):
        self.lang = get_setting('OCR_LANG', 'chi_sim+eng')  # 中文简体+英文

        if not PYTESSERACT_AVAILABLE:
            raise OCRError("pytesseract 未安装，请先安装: pip install pytesseract")

    def read_image(self, image_path: str) -> str:
        """
        从图片中提取文字

        Args:
            image_path: 图片文件路径

        Returns:
            提取的文本内容

        Raises:
            OCRError: OCR 识别失败
        """
        try:
            with Image.open(image_path) as image:
                return self._extract_text(image)
        except OCRError:
            raise
        except Exception as e:
            raise OCRError(f"图片读取失败: {str(e)}")

    def read_image_bytes(self, image_bytes: bytes) -> str:
        """
        从图片字节流中提取文字

        Args:
            image_bytes: 图片字节数据

        Returns:
            提取的文本内容
        """
        try:
            with Image.open(io.BytesIO(image_bytes)) as image:
                return self._extract_text(image)
        except OCRError:
            raise
        except Exception as e:
            raise OCRError(f"图片字节流读取失败: {str(e)}")

    def _extract_text(self, image: Image.Image) -> str:
        """
        从 PIL Image 对象中提取文字

        Args:
            image: PIL Image 对象

        Returns:
            提取的文本内容
        """
        try:
            # 转换为 RGB 模式（如果需要）
            if image.mode != 'RGB':
                image = image.convert('RGB')

            # 使用 pytesseract 进行 OCR
            text = pytesseract.image_to_string(image, lang=self.lang)
            return text.strip()

        except pytesseract.TesseractNotFoundError:
            raise OCRError(
                "Tesseract 未安装或未找到。\n"
                "请安装 Tesseract OCR：\n"
                "- Windows: 下载安装 https://github.com/UB-Mannheim/tesseract/wiki\n"
                "- Linux: sudo apt-get install tesseract-ocr tesseract-ocr-chi-sim\n"
                "- macOS: brew install tesseract tesseract-lang"
            )
        except Exception as e:
            raise OCRError(f"OCR 识别失败: {str(e)}")

    def preprocess_image(self, image: Image.Image) -> Image.Image:
        """
        图片预处理（提高 OCR 准确率）

        Args:
            image: 原始图片

        Returns:
            预处理后的图片
        """
        # 转换为灰度图
        image = image.convert('L')

        # 可以添加更多预处理步骤，如：
        # - 二值化
        # - 去噪
        # - 倾斜校正

        return image


# 全局 OCR 读取器实例
ocr_reader = OCRReader() if PYTESSERACT_AVAILABLE else None
