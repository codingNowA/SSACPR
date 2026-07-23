# 三大功能实现计划

## 任务概览
1. 增加登录界面，分为管理员和用户，用户无法管理题库和岗位数据
2. 岗位匹配改为本地模型，会参考岗位数据变化权重
3. 增加岗位解读和为用户提供面试准备功能

---

## 任务1：登录界面与权限管理

### 后端改造

#### 1.1 用户管理服务 (`backend/app/services/user_service.py` - 新建)
- 创建用户CRUD操作
- 密码哈希验证（使用bcrypt）
- 用户角色管理（admin, user）

#### 1.2 增强认证API (`backend/app/api/v1/auth.py`)
- 修改现有登录逻辑，连接数据库验证用户
- 添加用户注册接口
- 添加获取当前用户信息接口
- JWT token中包含role信息

#### 1.3 权限依赖 (`backend/app/core/auth.py`)
- 新增 `require_admin` 依赖函数
- 检查用户role是否为admin

#### 1.4 保护管理接口
修改以下API，添加 `Depends(require_admin)`：
- `/api/v1/admin/jobs` (岗位管理)
- `/api/v1/admin/questions` (题库管理)
- `/api/v1/admin/logs` (日志查询)

### 前端改造

#### 1.5 登录页面 (`frontend/src/pages/Login/index.tsx` - 新建)
- 用户名密码表单
- 调用 `/api/v1/auth/login`
- 存储token到localStorage
- 跳转到首页

#### 1.6 用户状态管理 (`frontend/src/store/index.ts`)
- 添加用户状态：username, role, token
- 添加登录/登出actions

#### 1.7 路由守卫 (`frontend/src/router/index.tsx`)
- 添加登录路由
- 保护管理页面，检查role

#### 1.8 导航栏调整 (`frontend/src/components/layout/MainLayout.tsx`)
- 根据用户role显示/隐藏管理菜单
- 添加登出按钮
- 显示当前用户名

---

## 任务2：本地模型岗位匹配

### 2.1 本地匹配算法 (`backend/app/services/local_match_service.py` - 新建)

**核心思路：**
- 不依赖LLM API
- 基于规则+权重计算匹配度
- 可根据岗位数据分布动态调整权重

**评分维度（总分100）：**
1. **技能匹配（40分）**
   - 必需技能覆盖率：30分
   - 加分技能覆盖率：10分

2. **经验匹配（25分）**
   - 工作年限匹配：15分
   - 行业经验匹配：10分

3. **学历匹配（15分）**
   - 学历要求满足度

4. **地点偏好（10分）**
   - 期望城市匹配

5. **薪资匹配（10分）**
   - 期望薪资与岗位薪资匹配度

**动态权重调整：**
- 统计岗位数据分布（技能热度、薪资范围、地域分布）
- 稀缺技能加权：热门技能降权，稀缺技能加权
- 薪资合理性：偏离市场均值的岗位降权

### 2.2 权重配置 (`backend/app/config/match_weights.py` - 新建)
```python
MATCH_WEIGHTS = {
    "skill_required": 0.30,
    "skill_bonus": 0.10,
    "experience_years": 0.15,
    "experience_industry": 0.10,
    "education": 0.15,
    "location": 0.10,
    "salary": 0.10,
}

# 动态调整因子
DYNAMIC_FACTORS = {
    "rare_skill_boost": 1.2,  # 稀缺技能加成
    "common_skill_decay": 0.8,  # 常见技能衰减
    "salary_outlier_penalty": 0.9,  # 薪资异常惩罚
}
```

### 2.3 修改匹配API (`backend/app/api/v1/match.py`)
- 添加 `use_local_model` 参数（默认true）
- 当 `use_local_model=true` 时调用本地算法
- 保留LLM匹配作为可选增强

### 2.4 前端匹配页面调整 (`frontend/src/pages/Job/Match.tsx`)
- 添加匹配模式选择（本地算法 / LLM增强）
- 显示各维度评分详情
- 可视化匹配度雷达图

---

## 任务3：岗位解读与面试准备

### 3.1 岗位解读API (`backend/app/api/v1/job_analysis.py` - 新建)

#### 3.1.1 岗位详细解读 (`POST /api/v1/job-analysis/interpret`)
**输入：**
- job_id

**输出：**
- 岗位关键信息提取（核心职责、必备技能、加分项）
- 岗位发展路径分析
- 薪资竞争力分析
- 公司背景与文化
- 适合人群画像

**实现方式：**
- 结构化解析岗位描述
- 对比市场数据（同类岗位薪资、技能要求）
- LLM增强：生成发展路径建议（可选）

#### 3.1.2 面试准备 (`POST /api/v1/job-analysis/interview-prep`)
**输入：**
- job_id
- resume_id

**输出：**
```json
{
  "technical_questions": [
    {
      "question": "请介绍你在Python方面的项目经验",
      "preparation_tips": "准备1-2个具体项目，突出技术栈和解决的问题",
      "difficulty": "medium"
    }
  ],
  "behavioral_questions": [
    {
      "question": "描述一次你解决技术难题的经历",
      "preparation_tips": "使用STAR法则（情境、任务、行动、结果）",
      "difficulty": "medium"
    }
  ],
  "company_questions": [
    "为什么选择我们公司？",
    "你对这个岗位的理解是什么？"
  ],
  "weakness_analysis": [
    {
      "skill": "Docker",
      "importance": "high",
      "suggestion": "快速学习Docker基础，准备简单的容器化项目"
    }
  ],
  "strength_highlights": [
    "Python开发经验丰富",
    "有完整的项目经验"
  ]
}
```

**生成逻辑：**
1. 从题库中匹配相关技术问题
2. 根据岗位和简历的gap生成针对性问题
3. 提供STAR法则回答模板
4. 突出简历优势，准备劣势应对

### 3.2 服务层实现

#### 3.2.1 岗位分析服务 (`backend/app/services/job_analysis_service.py` - 新建)
- `analyze_job_posting()` - 解析岗位信息
- `compare_with_market()` - 市场数据对比
- `generate_career_path()` - 职业路径建议

#### 3.2.2 面试准备服务 (`backend/app/services/interview_prep_service.py` - 新建)
- `generate_technical_questions()` - 技术问题
- `generate_behavioral_questions()` - 行为问题
- `analyze_resume_gaps()` - 简历短板分析
- `suggest_preparation_plan()` - 准备计划

### 3.3 前端页面实现

#### 3.3.1 岗位解读页面 (`frontend/src/pages/Job/Interpret.tsx` - 新建)
- 岗位信息卡片
- 核心要求可视化（技能树）
- 薪资竞争力对比图
- 职业发展路径时间线
- 适配度评分

#### 3.3.2 面试准备页面 (`frontend/src/pages/Job/InterviewPrep.tsx` - 新建)
- 技术问题清单（可标记准备状态）
- 行为问题模板
- 短板补强建议
- 优势话术准备
- 公司背景调研清单
- 模拟面试倒计时

#### 3.3.3 路由整合
从岗位匹配结果页面可跳转到：
1. 岗位解读（点击岗位卡片"详细解读"）
2. 面试准备（点击"准备面试"）

---

## 实现顺序

### Phase 1: 登录与权限（优先级：高）
1. 后端用户服务
2. 认证API改造
3. 权限依赖
4. 前端登录页
5. 路由守卫
6. 导航栏调整

### Phase 2: 本地匹配算法（优先级：高）
1. 本地匹配服务
2. 权重配置
3. 匹配API调整
4. 前端匹配页调整

### Phase 3: 岗位解读（优先级：中）
1. 岗位分析服务
2. 岗位解读API
3. 前端岗位解读页

### Phase 4: 面试准备（优先级：中）
1. 面试准备服务
2. 面试准备API
3. 前端面试准备页
4. 路由整合

---

## 数据库变更

### 用户表已存在，需要初始化测试数据
```sql
-- 插入测试用户
INSERT INTO users (username, password_hash, email, role, real_name)
VALUES 
  ('admin', '$2b$12$...(admin123加密)', 'admin@example.com', 'admin', '管理员'),
  ('user1', '$2b$12$...(user123加密)', 'user1@example.com', 'student', '测试用户');
```

### 新增表：岗位分析缓存（可选）
```sql
CREATE TABLE IF NOT EXISTS job_analysis_cache (
    id SERIAL PRIMARY KEY,
    job_id INT REFERENCES jobs(id) ON DELETE CASCADE,
    analysis_data JSONB,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
```

---

## 技术栈
- **认证**: JWT (jose), bcrypt
- **匹配算法**: 纯Python数学计算
- **前端状态**: zustand
- **UI组件**: antd (Progress, Radar, Timeline, Collapse)

---

## 风险点
1. 本地匹配算法准确性需要调优（通过A/B测试对比LLM结果）
2. 权限控制需要全面覆盖所有管理接口
3. 面试问题生成质量依赖题库完整度

---

## 待确认问题
1. 本地匹配算法的权重配置是否需要可视化后台管理界面？
2. 岗位解读是否需要使用LLM增强，还是纯规则？
3. 面试准备功能是否需要用户保存准备进度？
