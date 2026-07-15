# 前端调试指南

## 问题：上传简历后点击"开始分析"没有反应

### 调试步骤

#### 1. 打开浏览器开发者工具

访问 http://localhost:5173，按 F12 打开开发者工具。

#### 2. 检查控制台错误

切换到 **Console** 标签页，查看是否有红色错误信息。

常见错误：
- `Network Error` - 后端服务未启动
- `CORS Error` - 跨域问题
- `401 Unauthorized` - 认证问题
- `400 Bad Request` - 请求参数错误

#### 3. 检查网络请求

切换到 **Network** 标签页，执行上传操作，观察请求：

1. **上传请求** - `POST /api/v1/resume/upload`
   - 状态码应该是 200
   - 响应应该包含 `resume_id`

2. **解析请求** - `POST /api/v1/resume/{id}/parse`
   - 状态码应该是 200
   - 响应包含解析后的简历数据

3. **诊断请求** - `POST /api/v1/resume/{id}/diagnose`
   - 状态码应该是 200
   - 响应包含诊断结果

#### 4. 检查请求详情

点击任意失败的请求，查看：
- **Headers**: 检查 `Content-Type` 是否正确
- **Payload**: 检查发送的数据是否正确
- **Response**: 查看服务器返回的错误信息

### 常见问题解决

#### 问题 1: 文件类型不支持

**现象**: 提示"不支持的文件格式"

**解决**:
- 只支持 PDF、Word (doc/docx)、图片 (png/jpg/jpeg)
- 检查文件后缀名是否正确

#### 问题 2: 后端服务未响应

**现象**: 请求一直 pending 或超时

**检查后端**:
```bash
# 检查后端服务状态
docker-compose ps backend

# 查看后端日志
docker logs career-backend --tail 50

# 测试后端健康检查
curl http://localhost:8000/health
```

#### 问题 3: CORS 跨域错误

**现象**: Console 显示 `CORS policy` 错误

**检查**:
- 后端 `main.py` 中的 CORS 配置是否包含 `http://localhost:5173`
- 重启后端服务

#### 问题 4: API 返回 401 未授权

**现象**: 所有请求返回 401

**解决**:
- 检查 `backend/.env` 中 `JWT_SECRET_KEY` 是否被注释
- 检查 `docker-compose.yml` 中 `APP_ENV=development`
- 重启后端容器

#### 问题 5: 文件上传失败

**现象**: 上传请求返回 400 或 500

**检查**:
```bash
# 检查上传目录权限
docker exec career-backend ls -la /app/uploads/resumes

# 手动测试上传
curl -X POST http://localhost:8000/api/v1/resume/upload \
  -F "file=@你的简历.pdf" \
  -F "user_id=1"
```

### 手动测试 API

#### 1. 测试上传接口

```bash
curl -X POST http://localhost:8000/api/v1/resume/upload \
  -F "file=@test.pdf" \
  -F "user_id=1"
```

预期响应：
```json
{
  "code": 200,
  "message": "上传成功",
  "data": {
    "resume_id": 1,
    "file_path": "uploads/resumes/resume_xxx.pdf",
    "file_type": "pdf",
    "message": "文件上传成功"
  }
}
```

#### 2. 测试解析接口

```bash
curl -X POST http://localhost:8000/api/v1/resume/1/parse
```

#### 3. 测试诊断接口

```bash
curl -X POST http://localhost:8000/api/v1/resume/1/diagnose
```

### 前端代码调试

如果需要修改前端代码调试，编辑以下文件：

**上传逻辑**: `frontend/src/pages/Resume/Upload.tsx`

在 `handleUpload` 函数中添加 console.log：

```typescript
const handleUpload = async () => {
  console.log('开始上传，文件列表:', fileList);
  
  if (fileList.length === 0) {
    message.warning('请先选择文件');
    return;
  }

  const file = fileList[0].originFileObj as File;
  console.log('选中的文件:', file);

  if (!isValidResumeFile(file)) {
    console.log('文件类型验证失败:', file.type);
    message.error('不支持的文件格式，请上传 PDF、Word 或图片文件');
    return;
  }

  console.log('开始调用 API');
  
  try {
    console.log('步骤1: 上传文件');
    const uploadResult = await uploadResume(file, userId);
    console.log('上传结果:', uploadResult);
    
    // ... 后续步骤
  } catch (error) {
    console.error('上传失败:', error);
  }
};
```

保存后前端会自动热更新。

### 检查点清单

- [ ] 后端服务正常运行 (`docker-compose ps`)
- [ ] 后端健康检查通过 (`curl http://localhost:8000/health`)
- [ ] 前端服务正常运行 (`docker-compose ps frontend`)
- [ ] 前端页面可以访问 (`http://localhost:5173`)
- [ ] 浏览器控制台无错误
- [ ] 文件格式正确（PDF/Word/图片）
- [ ] 文件大小 < 10MB
- [ ] Network 标签页显示请求发送成功

### 快速验证命令

```bash
# 1. 检查所有服务状态
docker-compose ps

# 2. 检查后端健康
curl http://localhost:8000/health

# 3. 检查前端可访问
curl -I http://localhost:5173

# 4. 查看后端日志
docker logs career-backend --tail 50 -f

# 5. 查看前端日志
docker logs career-frontend --tail 50 -f
```

### 如果问题仍未解决

1. 截图浏览器 Console 和 Network 标签页
2. 复制完整的错误信息
3. 提供后端日志 (`docker logs career-backend`)
4. 说明具体操作步骤

### 联系方式

如需进一步帮助，请提供：
- 浏览器类型和版本
- 错误截图
- 控制台完整日志
- 具体操作步骤
