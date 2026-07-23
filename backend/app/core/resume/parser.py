"""
简历解析器核心模块
支持 PDF、Word、图片等格式的简历文本提取
"""
import re
from pathlib import Path
from typing import Any, Dict, Optional, Tuple

import docx
from PyPDF2 import PdfReader

from app.ai.ocr import ocr_reader, OCRError
from app.utils.file_handler import FileHandlerError


class ResumeParserError(Exception):
    """简历解析异常"""
    pass


class ResumeParser:
    """简历解析器 - 负责从各种格式中提取文本"""

    def __init__(self):
        self.supported_formats = ['pdf', 'doc', 'docx', 'png', 'jpg', 'jpeg']

    def parse(self, file_path: str, file_type: Optional[str] = None) -> Dict[str, Any]:
        """
        解析简历文件

        Args:
            file_path: 文件路径
            file_type: 文件类型（如果为 None，则从文件名推断）

        Returns:
            解析结果字典，包含：
            - text: 提取的文本内容
            - file_type: 文件类型
            - file_path: 文件路径
            - page_count: 页数（仅 PDF）
            - word_count: 字数

        Raises:
            ResumeParserError: 解析失败
        """
        path = Path(file_path)
        if not path.exists():
            raise ResumeParserError(f"文件不存在: {file_path}")

        # 确定文件类型
        if not file_type:
            file_type = path.suffix[1:].lower()

        if file_type not in self.supported_formats:
            raise ResumeParserError(f"不支持的文件类型: {file_type}")

        # 根据文件类型选择解析方法
        try:
            if file_type == 'pdf':
                text, page_count = self._parse_pdf(file_path)
            elif file_type in ['doc', 'docx']:
                text = self._parse_word(file_path)
                page_count = None
            elif file_type in ['png', 'jpg', 'jpeg']:
                text = self._parse_image(file_path)
                page_count = None
            else:
                raise ResumeParserError(f"不支持的文件类型: {file_type}")

            # 清理文本
            text = self._clean_text(text)

            if not text or len(text.strip()) < 10:
                raise ResumeParserError("提取的文本内容过少，请检查文件是否包含有效内容")

            return {
                'text': text,
                'file_type': file_type,
                'file_path': file_path,
                'page_count': page_count,
                'word_count': len(text),
                'char_count': len(text.replace(' ', '').replace('\n', '')),
            }

        except Exception as e:
            if isinstance(e, ResumeParserError):
                raise
            raise ResumeParserError(f"解析失败: {str(e)}")

    def _parse_pdf(self, file_path: str) -> Tuple[str, int]:
        """
        解析 PDF 文件

        Args:
            file_path: PDF 文件路径

        Returns:
            (提取的文本内容, 页数) —— 只打开并解析一次 PDF
        """
        try:
            reader = PdfReader(file_path)
            page_count = len(reader.pages)
            text_parts = []

            for page in reader.pages:
                page_text = page.extract_text()
                if page_text:
                    text_parts.append(page_text)

            text = '\n\n'.join(text_parts)

            # 如果 PDF 提取失败或内容太少，尝试 OCR
            if not text or len(text.strip()) < 50:
                if ocr_reader:
                    try:
                        # 注意：这里简化处理，实际应该将 PDF 转为图片后 OCR
                        # 可以使用 pdf2image 库
                        pass
                    except OCRError:
                        pass

            return text, page_count

        except Exception as e:
            raise ResumeParserError(f"PDF 解析失败: {str(e)}")

    def _parse_word(self, file_path: str) -> str:
        """
        解析 Word 文件（.doc 和 .docx）

        Args:
            file_path: Word 文件路径

        Returns:
            提取的文本内容
        """
        try:
            # python-docx 只支持 .docx 格式
            path = Path(file_path)
            if path.suffix.lower() == '.doc':
                raise ResumeParserError(
                    ".doc 格式需要转换为 .docx 格式。"
                    "建议使用 Microsoft Word 或 LibreOffice 转换。"
                )

            doc = docx.Document(file_path)
            text_parts = []

            # 提取段落文本
            for paragraph in doc.paragraphs:
                if paragraph.text.strip():
                    text_parts.append(paragraph.text)

            # 提取表格文本
            for table in doc.tables:
                for row in table.rows:
                    row_text = []
                    for cell in row.cells:
                        if cell.text.strip():
                            row_text.append(cell.text.strip())
                    if row_text:
                        text_parts.append(' | '.join(row_text))

            return '\n'.join(text_parts)

        except Exception as e:
            raise ResumeParserError(f"Word 文档解析失败: {str(e)}")

    def _parse_image(self, file_path: str) -> str:
        """
        解析图片文件（使用 OCR）

        Args:
            file_path: 图片文件路径

        Returns:
            提取的文本内容
        """
        if not ocr_reader:
            raise ResumeParserError(
                "OCR 功能未启用。请安装 pytesseract 和 Tesseract OCR。\n"
                "安装指南：https://github.com/tesseract-ocr/tesseract"
            )

        try:
            text = ocr_reader.read_image(file_path)
            return text
        except OCRError as e:
            raise ResumeParserError(f"图片 OCR 识别失败: {str(e)}")

    def _clean_text(self, text: str) -> str:
        """
        清理提取的文本，包括修复常见的 OCR 识别错误

        Args:
            text: 原始文本

        Returns:
            清理后的文本
        """
        if not text:
            return ""

        # 修复常见的 OCR 识别错误（在任何处理之前先修复）
        # 修复 "基于" 的常见错误识别（使用多种匹配模式确保覆盖）
        # 1. 后面跟空格
        text = re.sub(r'JEF\s+', '基于 ', text)
        text = re.sub(r'J£F\s+', '基于 ', text)  # £ 英镑符号
        text = re.sub(r'J\$F\s+', '基于 ', text)
        text = re.sub(r'JtF\s+', '基于 ', text)
        text = re.sub(r'J&F\s+', '基于 ', text)
        text = re.sub(r'J@F\s+', '基于 ', text)

        # 2. 后面跟大写字母
        text = re.sub(r'JEF(?=[A-Z])', '基于', text)
        text = re.sub(r'J£F(?=[A-Z])', '基于', text)

        # 3. 不区分大小写的通用匹配
        text = re.sub(r'jef\s+', '基于 ', text, flags=re.IGNORECASE)
        text = re.sub(r'j£f\s+', '基于 ', text, flags=re.IGNORECASE)

        # 修复常见技术名称的 OCR 错误
        text = re.sub(r'\bSping\b', 'Spring', text)  # Sping → Spring
        text = re.sub(r'\bSpirng\b', 'Spring', text)  # Spirng → Spring
        text = re.sub(r'\bMybatis\b', 'MyBatis', text)  # 统一大小写

        # 修复邮箱常见错误（@ 后缺少点号）
        # 例如：lichen@emailcom → lichen@email.com
        text = re.sub(r'@gmailcom\b', '@gmail.com', text)
        text = re.sub(r'@emailcom\b', '@email.com', text)
        text = re.sub(r'@qqcom\b', '@qq.com', text)
        text = re.sub(r'@163com\b', '@163.com', text)
        text = re.sub(r'@126com\b', '@126.com', text)
        text = re.sub(r'@outlookcom\b', '@outlook.com', text)

        # 移除多余的空白字符
        text = re.sub(r'\s+', ' ', text)

        # 移除多余的换行
        text = re.sub(r'\n\s*\n', '\n\n', text)

        # 移除首尾空白
        text = text.strip()

        return text

# 全局简历解析器实例
resume_parser = ResumeParser()
