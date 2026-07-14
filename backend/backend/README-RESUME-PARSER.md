# 简历解析功能说明

## 功能概述

本模块实现了对多种格式简历的解析功能，支持：
- **PDF** 格式（.pdf）
- **Word** 格式（.docx，不支持 .doc）
- **图片** 格式（.png, .jpg, .jpeg，需要 OCR）

## 核心模块

### 1. 文件处理器 (`app/utils/file_handler.py`)
负责文件上传、验证和存储：
- 文件类型验证（扩展名和 MIME 类型）
- 文件大小限制（默认 10MB）
- 唯一文件名生成
- 文件保存和删除

### 2. 简历解析器 (`app/core/resume/parser.py`)
负责从各种格式中提取文本：
- PDF 文本提取（使用 PyPDF2）
- Word 文档解析（使用 python-docx）
- 图片 OCR 识别（使用 pytesseract）
- 文本清理和标准化

### 3. OCR 模块 (`app/ai/ocr/reader.py`)
负责图片文字识别：
- 支持中文简体和英文
- 图片预处理
- 错误处理和提示

## API 接口

### 1. 上传简历
```http
POST /api/v1/resume/upload
Content-Type: multipart/form-data

file: <简历文件>
```

**响应示例：**
```json
{
  "code": 200,
  "message": "上传成功",
  "data": {
    "file_path": "uploads/resumes/resume_user123_abc123.pdf",
    "file_type": "pdf",
    "message": "文件上传成功"
  }
}
```

### 2. 解析简历（直接上传）
```http
POST /api/v1/resume/parse
Content-Type: multipart/form-data

file: <简历文件>
```

**响应示例：**
```json
{
  "code": 200,
  "message": "解析成功",
  "data": {
    "text": "简历文本内容...",
    "file_type": "pdf",
    "file_path": "uploads/temp/temp_xyz789.pdf",
    "page_count": 2,
    "word_count": 1523,
    "char_count": 1245,
    "message": "解析成功"
  }
}
```

### 3. 解析简历（通过路径）
```http
POST /api/v1/resume/parse-by-path
Content-Type: application/json

{
  "file_path": "uploads/resumes/resume_user123_abc123.pdf",
  "file_type": "pdf"
}
```

### 4. 获取支持的格式
```http
GET /api/v1/resume/formats
```

**响应示例：**
```json
{
  "code": 200,
  "message": "success",
  "data": {
    "formats": [
      {
        "extension": "pdf",
        "mime_types": ["application/pdf"],
        "description": "PDF 文档"
      },
      {
        "extension": "docx",
        "mime_types": ["application/vnd.openxmlformats-officedocument.wordprocessingml.document"],
        "description": "Word 文档（仅支持 .docx）"
      }
    ],
    "max_file_size": 10485760,
    "max_file_size_mb": 10.0
  }
}
```

## 使用示例

### Python 客户端

```python
import requests

# 上传并解析简历
with open('resume.pdf', 'rb') as f:
    files = {'file': f}
    response = requests.post('http://localhost:8000/api/v1/resume/parse', files=files)
    result = response.json()
    
    if result['code'] == 200:
        print(f"解析成功！")
        print(f"文本长度: {result['data']['word_count']}")
        print(f"提取的文本: {result['data']['text'][:200]}...")
    else:
        print(f"解析失败: {result['message']}")
```

### cURL 命令

```bash
# 上传简历
curl -X POST "http://localhost:8000/api/v1/resume/upload" \
  -H "Content-Type: multipart/form-data" \
  -F "file=@/path/to/resume.pdf"

# 解析简历
curl -X POST "http://localhost:8000/api/v1/resume/parse" \
  -H "Content-Type: multipart/form-data" \
  -F "file=@/path/to/resume.pdf"

# 获取支持的格式
curl -X GET "http://localhost:8000/api/v1/resume/formats"
```

### JavaScript 客户端

```javascript
// 上传并解析简历
async function parseResume(file) {
  const formData = new FormData();
  formData.append('file', file);
  
  const response = await fetch('http://localhost:8000/api/v1/resume/parse', {
    method: 'POST',
    body: formData
  });
  
  const result = await response.json();
  
  if (result.code === 200) {
    console.log('解析成功！');
    console.log('文本长度:', result.data.word_count);
    console.log('提取的文本:', result.data.text.substring(0, 200));
  } else {
    console.error('解析失败:', result.message);
  }
}
```

## 环境配置

### 基础配置（.env）

```bash
# 文件上传配置
UPLOAD_DIR=./uploads
MAX_UPLOAD_SIZE=10485760
ALLOWED_FILE_TYPES=pdf,doc,docx,png,jpg,jpeg

# OCR 配置（可选，用于图片解析）
OCR_PROVIDER=pytesseract
OCR_LANG=chi_sim+eng
```

### 图片 OCR 支持（可选）

如果需要解析图片格式的简历，需要安装 Tesseract OCR：

**Windows:**
1. 下载安装包：https://github.com/UB-Mannheim/tesseract/wiki
2. 安装后添加到系统 PATH
3. 下载中文语言包：`tessdata/chi_sim.traineddata`

**Linux:**
```bash
sudo apt-get update
sudo apt-get install tesseract-ocr tesseract-ocr-chi-sim
```

**macOS:**
```bash
brew install tesseract tesseract-lang
```

## 测试

运行测试脚本：
```bash
cd backend
python test_resume_parser.py
```

## 技术栈

- **FastAPI**: Web 框架
- **PyPDF2**: PDF 文本提取
- **python-docx**: Word 文档解析
- **Pillow**: 图片处理
- **pytesseract**: OCR 文字识别（可选）
- **Pydantic**: 数据验证

## 限制和注意事项

1. **文件大小**: 默认最大 10MB，可通过 `MAX_UPLOAD_SIZE` 配置
2. **Word 格式**: 仅支持 `.docx` 格式，不支持旧的 `.doc` 格式
3. **图片 OCR**: 需要安装 Tesseract OCR，识别准确率取决于图片质量
4. **PDF 安全性**: 加密或受保护的 PDF 可能无法解析
5. **扫描版 PDF**: 如果 PDF 是扫描件（图片），需要先 OCR 处理

## 下一步计划

- [ ] 实现简历结构化解析（提取姓名、教育、工作经历等）
- [ ] 添加简历评分功能
- [ ] 支持批量解析
- [ ] 添加解析缓存
- [ ] 支持更多格式（.doc、HTML 等）
- [ ] 改进 OCR 准确率（图片预处理、多引擎支持）

## API 文档

启动服务后访问：
- Swagger UI: http://localhost:8000/docs
- ReDoc: http://localhost:8000/redoc
