# 简历解析功能测试指南

完整的测试流程和方法说明。

---

## 📋 目录

1. [快速开始](#快速开始)
2. [测试方法](#测试方法)
3. [常见问题](#常见问题)
4. [详细说明](#详细说明)

---

## 🚀 快速开始

### 1. 创建测试样本

```bash
cd backend
python create_test_samples.py
```

这会在 `backend/test_samples/` 目录下创建：
- `sample_resume.pdf` - PDF 格式测试简历
- `sample_resume.docx` - Word 格式测试简历
- `sample_resume.png` - 图片格式测试简历

### 2. 运行测试

```bash
python test_with_samples.py
```

---

## 🧪 测试方法

### 方法 1: 使用测试脚本（推荐）

**优点**: 自动化，覆盖所有格式

```bash
# 步骤 1: 创建测试样本
python create_test_samples.py

# 步骤 2: 运行测试
python test_with_samples.py
```

**输出示例**:
```
============================================================
测试 PDF 文件
============================================================
文件路径: backend/test_samples/sample_resume.pdf
文件类型: pdf
字数: 1234
字符数: 5678

✅ 测试通过
```

---

### 方法 2: 使用 Swagger UI（可视化）

**优点**: 可视化，适合手动测试和调试

1. **启动服务**
   ```bash
   uvicorn main:app --host 0.0.0.0 --port 8000 --reload
   ```

2. **打开浏览器**
   ```
   http://localhost:8000/docs
   ```

3. **测试步骤**
   - 找到 `POST /api/v1/resume/parse` 接口
   - 点击 "Try it out"
   - 点击 "Choose File" 上传文件
   - 点击 "Execute"
   - 查看响应结果

**响应示例**:
```json
{
  "code": 200,
  "message": "success",
  "data": {
    "text": "张伟\n软件工程师\n...",
    "file_type": "pdf",
    "file_path": "uploads/resumes/xxx.pdf",
    "word_count": 1234,
    "char_count": 5678,
    "page_count": 2
  }
}
```

---

### 方法 3: 使用 curl 命令（命令行）

**优点**: 自动化，适合 CI/CD

```bash
# 确保服务已启动
# uvicorn main:app --reload

# 测试 PDF
curl -X POST http://localhost:8000/api/v1/resume/parse \
  -F "file=@test_samples/sample_resume.pdf" \
  | python -m json.tool

# 测试 Word
curl -X POST http://localhost:8000/api/v1/resume/parse \
  -F "file=@test_samples/sample_resume.docx" \
  | python -m json.tool

# 测试图片
curl -X POST http://localhost:8000/api/v1/resume/parse \
  -F "file=@test_samples/sample_resume.png" \
  | python -m json.tool
```

---

### 方法 4: 使用 Python 代码

**优点**: 灵活，可自定义测试逻辑

```python
from app.core.resume.parser import ResumeParser

# 初始化解析器
parser = ResumeParser()

# 解析文件
result = parser.parse("test_samples/sample_resume.pdf", "pdf")

# 查看结果
print(f"提取的文本: {result['text']}")
print(f"字数: {result['word_count']}")
print(f"字符数: {result['char_count']}")
```

---

## ❓ 常见问题

### Q1: 测试样本创建失败

**问题**: `create_test_samples.py` 运行出错

**解决方案**:

1. **安装缺失的依赖**
   ```bash
   pip install python-docx Pillow reportlab
   ```

2. **如果 PDF 创建失败（缺少 reportlab）**
   - 这不影响其他格式的测试
   - 可以跳过 PDF，只测试 Word 和图片

3. **如果中文显示乱码**
   - Windows: 脚本会自动使用系统字体（微软雅黑、宋体等）
   - Linux/Mac: 需要安装中文字体包

---

### Q2: 图片 OCR 识别失败

**问题**: 测试图片格式时报错 "Tesseract not found"

**解决方案**:

1. **安装 Tesseract OCR**

   **Windows**:
   ```bash
   # 下载安装包
   https://github.com/UB-Mannheim/tesseract/wiki
   
   # 安装后添加到 PATH
   # 或在 .env 中配置
   TESSERACT_CMD=C:\Program Files\Tesseract-OCR\tesseract.exe
   ```

   **Linux**:
   ```bash
   sudo apt-get install tesseract-ocr tesseract-ocr-chi-sim
   ```

   **Mac**:
   ```bash
   brew install tesseract tesseract-lang
   ```

2. **安装 Python 包**
   ```bash
   pip install pytesseract
   ```

---

### Q3: API 连接失败

**问题**: `test_with_samples.py` API 测试失败

**解决方案**:

1. **确保服务已启动**
   ```bash
   uvicorn main:app --reload
   ```

2. **检查端口是否被占用**
   ```bash
   # Windows
   netstat -ano | findstr :8000
   
   # Linux/Mac
   lsof -i :8000
   ```

3. **尝试不同的端口**
   ```bash
   uvicorn main:app --port 8001 --reload
   ```

---

### Q4: 文件上传大小限制

**问题**: 上传文件时报错 "文件过大"

**解决方案**:

当前限制: **10 MB**

修改限制:
```python
# backend/app/utils/file_handler.py
class FileHandler:
    MAX_FILE_SIZE = 20 * 1024 * 1024  # 改为 20MB
```

---

## 📚 详细说明

### 支持的文件格式

| 格式 | 扩展名 | MIME 类型 | 说明 |
|------|--------|-----------|------|
| PDF | `.pdf` | `application/pdf` | 支持文本 PDF |
| Word | `.docx` | `application/vnd.openxmlformats-officedocument.wordprocessingml.document` | 仅支持 .docx（不支持 .doc） |
| PNG | `.png` | `image/png` | 需要 OCR |
| JPEG | `.jpg`, `.jpeg` | `image/jpeg` | 需要 OCR |

### 测试覆盖范围

测试脚本会验证：

1. ✅ **文件解析**
   - PDF 文本提取
   - Word 文档解析
   - 图片 OCR 识别

2. ✅ **文本处理**
   - 多余空白清理
   - 换行符规范化
   - 字数统计
   - 字符数统计

3. ✅ **API 功能**
   - 文件上传
   - 文件验证
   - 响应格式
   - 错误处理

4. ✅ **边界条件**
   - 文件大小限制
   - 文件类型验证
   - 空文件处理
   - 损坏文件处理

---

## 🎯 测试检查清单

测试前确认：

- [ ] Python 3.8+ 已安装
- [ ] 所有依赖已安装 (`pip install -r requirements.txt`)
- [ ] 测试样本已创建
- [ ] （可选）Tesseract OCR 已安装
- [ ] （API 测试）服务已启动

运行测试：

- [ ] 单元测试通过
- [ ] PDF 解析成功
- [ ] Word 解析成功
- [ ] 图片 OCR 成功（如果已安装 Tesseract）
- [ ] API 接口响应正常
- [ ] 错误处理正确

---

## 🔧 高级测试

### 性能测试

```python
import time
from app.core.resume.parser import ResumeParser

parser = ResumeParser()

start = time.time()
result = parser.parse("large_resume.pdf", "pdf")
duration = time.time() - start

print(f"解析耗时: {duration:.2f} 秒")
print(f"文件大小: {os.path.getsize('large_resume.pdf') / 1024:.2f} KB")
```

### 批量测试

```bash
# 测试目录下所有文件
for file in test_samples/*; do
    echo "Testing $file"
    curl -X POST http://localhost:8000/api/v1/resume/parse \
      -F "file=@$file"
done
```

---

## 📞 获取帮助

如果遇到问题：

1. 查看日志: `tail -f logs/app.log`
2. 检查错误信息
3. 参考 [README-RESUME-PARSER.md](README-RESUME-PARSER.md)
4. 查看 API 文档: http://localhost:8000/docs

---

**最后更新**: 2026-07-14
