# 快速调试步骤

## 请按以下步骤操作并告诉我结果：

### 步骤 1: 检查浏览器控制台
1. 打开 http://localhost:5173
2. 按 F12 打开开发者工具
3. 切换到 **Console** 标签
4. 是否有红色错误信息？如果有，请复制给我

### 步骤 2: 检查文件选择
1. 点击上传区域选择文件
2. 文件是否显示在"已选择文件"区域？
3. "开始分析"按钮是否变为可点击状态（蓝色）？

### 步骤 3: 检查网络请求
1. 在开发者工具中切换到 **Network** 标签
2. 点击"开始分析"按钮
3. 是否看到网络请求发出？
4. 如果有请求，状态码是什么？（200、401、500？）

### 步骤 4: 简单测试
在浏览器控制台（Console）中运行以下代码：

```javascript
// 测试 API 连接
fetch('http://localhost:8000/health')
  .then(r => r.json())
  .then(d => console.log('后端连接正常:', d))
  .catch(e => console.error('后端连接失败:', e));
```

## 可能的原因

### 原因 1: 文件类型不支持
- 只支持: PDF, Word (doc/docx), 图片 (png/jpg/jpeg)
- 不支持: txt, zip, rar 等

### 原因 2: 后端 CORS 问题
检查命令:
```bash
curl -v http://localhost:8000/health 2>&1 | grep -i cors
```

### 原因 3: 认证问题
检查命令:
```bash
docker exec career-backend printenv | grep JWT_SECRET_KEY
# 应该没有输出（开发模式）
```

### 原因 4: 前端代码未加载
检查命令:
```bash
curl http://localhost:5173 | grep "职业规划"
# 应该有输出
```

## 请告诉我以上步骤的结果
