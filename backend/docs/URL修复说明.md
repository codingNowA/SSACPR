# ✅ URL 问题已修复

## 问题原因

你的 `.env` 配置中 `LLM_BASE_URL` 已经包含了 `/v1`：
```
LLM_BASE_URL=https://ws-na94bnwsg0gbbinn.cn-beijing.maas.aliyuncs.com/compatible-mode/v1
```

但代码的 `_normalize_url()` 方法又自动添加了 `/v1`，导致最终 URL 变成：
```
https://...com/compatible-mode/v1/v1/chat/completions  ❌ 错误（重复 /v1）
```

## 修复内容

修改了 `app/ai/llm/client.py` 中的 `_normalize_url()` 方法：

```python
def _normalize_url(self, base_url: str) -> str:
    normalized = base_url.rstrip("/")
    if normalized.endswith("/chat/completions"):
        return normalized
    if normalized.endswith("/v1"):  # 新增：如果已经有 /v1，只添加 /chat/completions
        return f"{normalized}/chat/completions"
    return f"{normalized}/v1/chat/completions"
```

现在正确的 URL 是：
```
https://...com/compatible-mode/v1/chat/completions  ✅ 正确
```

## 🔄 重启服务

**必须重启服务才能生效！**

```bash
# 停止服务（Ctrl + C）
# 重新启动
cd backend
uvicorn main:app --host 0.0.0.0 --port 8000 --reload
```

## 🧪 测试

重启后测试：

1. 打开浏览器: `http://localhost:8000/docs`
2. 找到 `POST /api/v1/resume/extract`
3. 上传简历文件
4. 现在应该可以正常提取结构化数据了！

---

**修复时间**: 2026-07-14  
**状态**: ✅ 已修复，需要重启服务
