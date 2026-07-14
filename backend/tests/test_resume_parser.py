"""
简历解析功能测试脚本
"""
import os
import sys
from pathlib import Path

# 添加 backend 目录到 Python 路径
backend_dir = Path(__file__).parent
sys.path.insert(0, str(backend_dir))

# 切换工作目录到 backend
os.chdir(backend_dir)

from app.core.resume import resume_parser, ResumeParserError
from app.utils.file_handler import file_handler


def test_pdf_parsing():
    """测试 PDF 解析"""
    print("\n" + "=" * 50)
    print("测试 PDF 解析")
    print("=" * 50)

    # 这里需要实际的 PDF 文件路径
    # pdf_path = "path/to/sample_resume.pdf"
    # result = resume_parser.parse(pdf_path)
    # print(f"文本长度: {result['word_count']}")
    # print(f"页数: {result['page_count']}")
    # print(f"提取的文本预览:\n{result['text'][:500]}...")

    print("提示: 请提供实际的 PDF 文件路径进行测试")


def test_word_parsing():
    """测试 Word 解析"""
    print("\n" + "=" * 50)
    print("测试 Word 解析")
    print("=" * 50)

    # docx_path = "path/to/sample_resume.docx"
    # result = resume_parser.parse(docx_path)
    # print(f"文本长度: {result['word_count']}")
    # print(f"提取的文本预览:\n{result['text'][:500]}...")

    print("提示: 请提供实际的 Word 文件路径进行测试")


def test_image_parsing():
    """测试图片 OCR 解析"""
    print("\n" + "=" * 50)
    print("测试图片 OCR 解析")
    print("=" * 50)

    # image_path = "path/to/sample_resume.jpg"
    # result = resume_parser.parse(image_path)
    # print(f"文本长度: {result['word_count']}")
    # print(f"提取的文本预览:\n{result['text'][:500]}...")

    print("提示: 图片 OCR 需要安装 Tesseract")
    print("安装指南: https://github.com/tesseract-ocr/tesseract")


def test_file_handler():
    """测试文件处理器"""
    print("\n" + "=" * 50)
    print("测试文件处理器")
    print("=" * 50)

    print(f"上传目录: {file_handler.upload_dir}")
    print(f"简历目录: {file_handler.resume_dir}")
    print(f"临时目录: {file_handler.temp_dir}")
    print(f"最大文件大小: {file_handler.MAX_FILE_SIZE / 1024 / 1024} MB")
    print(f"支持的文件类型: {list(file_handler.ALLOWED_EXTENSIONS.keys())}")


def test_parser_features():
    """测试解析器功能"""
    print("\n" + "=" * 50)
    print("测试解析器功能")
    print("=" * 50)

    print(f"支持的格式: {resume_parser.supported_formats}")

    # 测试文本清理功能
    dirty_text = "  这是一个   测试\n\n\n文本  \n  需要清理  "
    clean_text = resume_parser._clean_text(dirty_text)
    print(f"\n原始文本: {repr(dirty_text)}")
    print(f"清理后: {repr(clean_text)}")


def main():
    """主测试函数"""
    print("=" * 50)
    print("简历解析功能测试")
    print("=" * 50)

    test_file_handler()
    test_parser_features()
    test_pdf_parsing()
    test_word_parsing()
    test_image_parsing()

    print("\n" + "=" * 50)
    print("测试完成")
    print("=" * 50)
    print("\n提示: 要完整测试，请准备实际的简历文件（PDF、Word、图片）")


if __name__ == "__main__":
    main()
