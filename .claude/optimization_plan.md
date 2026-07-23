# 代码优化计划

## 发现的主要冗余问题

### 1. 重复的API路由 - 面试题模块

**问题：**
- `backend/app/api/interview_questions.py` (146行)
- `backend/app/api/v1/interview_questions.py` (106行)
- 两个文件提供**几乎相同**的功能：
  - `/api/v1/interview-exam/questions` - 随机抽取题目
  - `/api/v1/interview-exam/questions/list` - 分页浏览题目
- 路径前缀相同，只是实现细节略有差异

**影响：**
- 前端调用：`Mock.tsx`, `QuestionBank.tsx`, `Exam.tsx` 都使用 `/api/v1/interview-exam/*`
- 旧版API (`backend/app/api/interview_questions.py`) 在 `main.py` 中未注册，属于**死代码**

**优化方案：**
- ✅ 删除 `backend/app/api/interview_questions.py`（死代码）
- ✅ 保留 `backend/app/api/v1/interview_questions.py`（正在使用）
- ✅ 从 `main.py` 移除已删除路由的导入

---

### 2. 简历API的职责分散

**问题：**
- `backend/app/api/v1/resume.py` - 1114行，包含上传、解析、提取、评分、优化、版本管理
- `backend/app/api/v1/resume_crud.py` - 373行，包含增删改查和诊断
- `backend/app/api/v1/versions.py` - 456行，专门处理版本快照

所有三个文件使用相同的 `prefix="/resume"`，导致路由定义分散。

**影响：**
- 路由定义分散，难以维护
- 功能重叠（例如版本管理在 resume.py 和 versions.py 都有）
- 前端调用时需要记住功能在哪个文件

**优化方案：**
- ⚠️ **暂不合并**（风险高，功能复杂）
- 📝 添加注释说明各文件职责边界
- 📝 未来重构建议：按业务功能拆分（upload、parse、diagnose、version）

---

### 3. 旧版API与新版API混用

**问题：**
- `backend/app/api/` 下有多个文件直接定义 `/api/v1/` 前缀
- `backend/app/api/v1/` 下也定义了相同前缀
- 结构混乱，不清楚哪些是新版哪些是旧版

**当前注册情况（main.py）：**
```python
app.include_router(analytics.router)     # /api/v1/analytics
app.include_router(questions.router)     # /api/v1/admin/questions
app.include_router(jobs.router)          # /api/v1/admin/jobs
app.include_router(logs.router)          # /api/v1/admin/logs
app.include_router(dictionary.router)    # /api/v1/admin/dictionary
app.include_router(api_v1_router)        # /api/v1/... (包含所有v1子路由)
```

**优化方案：**
- ✅ 保持现状（这些是独立的管理员功能模块）
- ✅ 确认没有路径冲突
- 📝 添加注释说明路由结构

---

### 4. 前端服务层重复调用

**问题：**
- 前端有独立的 `services/*.ts` 文件
- 但很多页面组件直接使用 `axios` 而不是通过 service 层
- 例如：`Mock.tsx`, `QuestionBank.tsx` 直接调用 axios

**影响：**
- API URL 硬编码在多个地方
- 接口变更需要改多处
- 错误处理不统一

**优化方案：**
- ✅ 创建统一的 `interview.ts` service（如果不存在）
- ✅ 重构页面组件使用 service 层而非直接 axios

---

### 5. 未使用的工具函数和依赖

**问题：**
- 需要检查是否有未使用的 import
- 需要检查是否有定义但未调用的函数

**优化方案：**
- 🔍 自动扫描未使用的 imports（低优先级）

---

## 优化优先级

### 高优先级（立即执行）
1. ✅ 删除死代码：`backend/app/api/interview_questions.py`
2. ✅ 清理 `main.py` 中对已删除路由的引用
3. ✅ 统一前端 interview 相关的 API 调用到 service 层

### 中优先级（本次完成）
4. 📝 为复杂模块添加职责说明注释（resume 相关文件）
5. ✅ 检查并移除未使用的 imports

### 低优先级（未来重构）
6. 📋 简历模块按功能重新组织（需要大量测试）
7. 📋 建立统一的错误处理机制

---

## 执行计划

### Phase 1: 删除死代码
- 删除 `backend/app/api/interview_questions.py`
- 验证前端功能正常（题库浏览、模拟面试）

### Phase 2: 前端Service层优化
- 检查 `frontend/src/services/interview.ts` 是否完整
- 重构 `Mock.tsx`, `QuestionBank.tsx`, `Exam.tsx` 使用 service
- 统一错误处理和响应格式

### Phase 3: 代码清理
- 移除未使用的 imports
- 添加必要的注释
- 格式化代码

### Phase 4: 测试验证
- 测试面试题相关功能
- 测试简历相关功能
- 确保所有API正常工作

---

## 预期收益

- **减少代码行数**: ~150 行（删除死代码）
- **提高可维护性**: 统一API调用方式
- **降低bug风险**: 减少重复代码
- **改善代码结构**: 清晰的职责划分

---

## 风险评估

### 低风险
- 删除未注册的API文件（不影响运行）
- 前端service层重构（不改变接口调用）

### 中风险
- 无

### 高风险
- 简历模块合并（本次不执行）

---

## 总结

本次优化聚焦于**安全的代码清理**和**结构优化**，不涉及业务逻辑变更。通过删除死代码、统一API调用方式，可以在不影响功能的前提下提升代码质量。
