# API 测试用例集 - Swagger 快速测试

本文档提供完整的 JSON 测试用例，可直接复制到 Swagger 文档（http://localhost:8000/docs）中进行测试。

---

## 一、岗位信息提取测试用例

### 测试用例 1：高级 Java 开发工程师（完整信息）

**接口**：POST /api/v1/job-extraction/extract

```json
{
  "job_text": "高级Java开发工程师\n\n岗位职责：\n1. 负责公司核心业务系统的开发和维护\n2. 参与系统架构设计和技术方案制定\n3. 优化系统性能，提升用户体验\n\n任职要求：\n- 本科及以上学历，计算机相关专业\n- 3-5年Java开发经验\n- 精通Spring Boot、微服务架构\n- 熟悉MySQL、Redis等数据库\n- 有大型互联网项目经验者优先\n\n薪资待遇：20k-35k\n工作地点：北京-朝阳区"
}
```

**预期结果**：提取出所有关键字段，置信度 1.0

---

### 测试用例 2：前端开发工程师（React）

**接口**：POST /api/v1/job-extraction/extract

```json
{
  "job_text": "前端开发工程师（React）\n\n我们正在寻找一位热爱前端技术的工程师加入团队！\n\n工作职责：\n- 使用React、TypeScript开发Web应用\n- 与设计师和后端工程师协作\n- 优化前端性能\n\n要求：\n本科学历，1-3年前端开发经验\n熟悉React、Vue、HTML、CSS、JavaScript\n了解Webpack、Node.js优先\n\n月薪12k-20k，上海张江，可远程办公"
}
```

**预期结果**：提取前端技能栈，识别远程办公模式

---

### 测试用例 3：AI 算法工程师（高端岗位）

**接口**：POST /api/v1/job-extraction/extract

```json
{
  "job_text": "高级算法工程师-深度学习方向\n\n岗位要求：\n硕士及以上学历，计算机、人工智能相关专业\n5年以上算法研发经验\n精通Python、PyTorch、TensorFlow\n有NLP或计算机视觉项目经验\n顶会论文发表者优先\n\n薪资：40万-70万/年\n地点：深圳南山区\n团队：20人规模，氛围开放"
}
```

**预期结果**：识别硕士学历、AI行业、高薪资

---

### 测试用例 4：Python 实习生（应届生岗位）

**接口**：POST /api/v1/job-extraction/extract

```json
{
  "job_text": "Python开发实习生\n\n要求：\n本科在读或应届毕业生\n熟悉Python基础语法\n了解Django或Flask框架\n有项目经验加分\n\n实习补贴：150元/天\n工作地点：杭州西湖区\n可转正，提供导师指导"
}
```

**预期结果**：识别应届生要求，无明确经验要求

---

### 测试用例 5：产品经理（信息不完整）

**接口**：POST /api/v1/job-extraction/extract

```json
{
  "job_text": "产品经理\n\n负责产品规划和需求分析\n与研发团队协作推进项目\n本科学历\n\n有互联网产品经验优先"
}
```

**预期结果**：置信度较低，缺少薪资、地点、经验等信息

---

## 二、岗位难度分析测试用例

### 测试用例 1：高级 Java 开发（较高难度）

**接口**：POST /api/v1/job-difficulty/analyze

```json
{
  "job_title": "高级Java开发工程师",
  "job_description": "负责公司核心业务系统的开发与维护",
  "requirements": "3-5年Java开发经验，熟悉Spring全家桶，了解微服务架构",
  "salary_range": "20k-35k",
  "education_requirement": "本科及以上",
  "experience_requirement": "3-5年",
  "industry": "互联网",
  "required_skills": ["Java", "Spring Boot", "微服务", "MySQL"]
}
```

**预期结果**：难度等级 hard，得分 70+ 分

---

### 测试用例 2：前端开发实习生（容易）

**接口**：POST /api/v1/job-difficulty/analyze

```json
{
  "job_title": "前端开发实习生",
  "requirements": "熟悉HTML、CSS、JavaScript基础",
  "salary_range": "3k-6k",
  "education_requirement": "本科",
  "experience_requirement": "应届生"
}
```

**预期结果**：难度等级 easy，得分 30 分左右

---

### 测试用例 3：Python 后端工程师（中等难度）

**接口**：POST /api/v1/job-difficulty/analyze

```json
{
  "job_title": "Python后端工程师",
  "requirements": "熟悉Django/Flask框架，数据库设计，RESTful API开发",
  "salary_range": "12k-20k",
  "education_requirement": "本科",
  "experience_requirement": "1-3年",
  "industry": "互联网",
  "required_skills": ["Python", "Django", "MySQL", "Redis"]
}
```

**预期结果**：难度等级 medium，得分 50 分左右

---

### 测试用例 4：算法工程师（很困难）

**接口**：POST /api/v1/job-difficulty/analyze

```json
{
  "job_title": "高级算法工程师",
  "requirements": "深度学习、计算机视觉、NLP，顶会论文发表经验",
  "salary_range": "40k-70k",
  "education_requirement": "硕士及以上",
  "experience_requirement": "5年以上",
  "industry": "人工智能",
  "required_skills": ["Python", "PyTorch", "TensorFlow", "深度学习"]
}
```

**预期结果**：难度等级 hard 或 very_hard，得分 75+ 分

---

### 测试用例 5：数据分析师（中低难度）

**接口**：POST /api/v1/job-difficulty/analyze

```json
{
  "job_title": "数据分析师",
  "requirements": "熟悉SQL、Python、Excel，具备数据可视化能力",
  "salary_range": "8k-15k",
  "education_requirement": "本科",
  "experience_requirement": "1年",
  "required_skills": ["SQL", "Python", "Excel"]
}
```

**预期结果**：难度等级 easy 或 medium，得分 35-45 分

---

## 三、批量分析测试用例

### 测试用例：对比三个不同难度岗位

**接口**：POST /api/v1/job-difficulty/batch-analyze

```json
{
  "初级前端": {
    "job_title": "前端开发实习生",
    "education_requirement": "本科",
    "experience_requirement": "应届生",
    "requirements": "熟悉HTML、CSS、JavaScript基础",
    "salary_range": "3k-6k"
  },
  "中级后端": {
    "job_title": "Python后端工程师",
    "education_requirement": "本科",
    "experience_requirement": "1-3年",
    "requirements": "熟悉Django/Flask框架，数据库设计，RESTful API开发",
    "salary_range": "12k-20k",
    "industry": "互联网"
  },
  "高级算法": {
    "job_title": "高级算法工程师",
    "education_requirement": "硕士",
    "experience_requirement": "5年以上",
    "requirements": "深度学习、计算机视觉、NLP，顶会论文发表经验",
    "salary_range": "40k-70k",
    "industry": "人工智能",
    "required_skills": ["PyTorch", "TensorFlow", "深度学习"]
  }
}
```

**预期结果**：返回三个岗位的难度分析，得分递增

---

### 测试用例：对比五个不同类型岗位

**接口**：POST /api/v1/job-difficulty/batch-analyze

```json
{
  "产品经理": {
    "job_title": "产品经理",
    "education_requirement": "本科",
    "experience_requirement": "2-3年",
    "requirements": "有完整产品生命周期经验，熟悉用户研究和数据分析",
    "salary_range": "15k-25k",
    "industry": "互联网"
  },
  "测试工程师": {
    "job_title": "测试工程师",
    "education_requirement": "本科",
    "experience_requirement": "1-3年",
    "requirements": "熟悉测试理论和方法，掌握自动化测试工具",
    "salary_range": "10k-18k"
  },
  "运维工程师": {
    "job_title": "运维工程师",
    "education_requirement": "本科",
    "experience_requirement": "2-4年",
    "requirements": "熟悉Linux系统，掌握Docker、Kubernetes",
    "salary_range": "15k-25k",
    "required_skills": ["Linux", "Docker", "Kubernetes"]
  },
  "UI设计师": {
    "job_title": "UI设计师",
    "education_requirement": "本科",
    "experience_requirement": "2-3年",
    "requirements": "精通Sketch、Figma，有移动端设计经验",
    "salary_range": "12k-20k"
  },
  "架构师": {
    "job_title": "技术架构师",
    "education_requirement": "本科及以上",
    "experience_requirement": "8年以上",
    "requirements": "精通系统架构设计，有大型分布式系统经验",
    "salary_range": "50k-80k",
    "required_skills": ["架构设计", "分布式", "微服务"]
  }
}
```

**预期结果**：返回五个岗位的详细分析，可以对比不同职位的难度

---

## 四、组合测试流程

### 完整流程：从文本提取到难度分析

#### 步骤 1：提取岗位信息

**接口**：POST /api/v1/job-extraction/extract

```json
{
  "job_text": "全栈工程师\n\n职责：独立完成前后端开发\n\n要求：\n本科，3年经验\n精通Vue、React、Node.js、Python\n熟悉MySQL、MongoDB\n\n薪资：18k-30k\n北京中关村"
}
```

#### 步骤 2：使用提取结果分析难度

将步骤 1 返回的 `extracted_info` 字段复制，作为步骤 2 的输入：

**接口**：POST /api/v1/job-difficulty/analyze

```json
{
  "job_title": "全栈工程师",
  "education_requirement": "本科",
  "experience_requirement": "3年",
  "salary_range": "18k-30k",
  "location": "北京中关村",
  "required_skills": ["Vue", "React", "Node.js", "Python", "MySQL", "MongoDB"]
}
```

**预期结果**：得到完整的难度评估报告

---

## 五、特殊场景测试

### 场景 1：最简信息（仅岗位名称）

**接口**：POST /api/v1/job-difficulty/analyze

```json
{
  "job_title": "软件工程师"
}
```

**预期结果**：给出基于岗位名称的基础评估

---

### 场景 2：超高薪资岗位

**接口**：POST /api/v1/job-difficulty/analyze

```json
{
  "job_title": "首席技术官(CTO)",
  "education_requirement": "硕士及以上",
  "experience_requirement": "10年以上",
  "salary_range": "100k-200k",
  "requirements": "负责公司整体技术战略规划"
}
```

**预期结果**：难度等级 very_hard，得分 90+ 分

---

### 场景 3：远程工作岗位

**接口**：POST /api/v1/job-extraction/extract

```json
{
  "job_text": "全职远程 - Golang开发工程师\n\n我们是一家全球化团队，支持远程办公\n\n要求：\n3年以上Go开发经验\n熟悉微服务架构\n英语流利\n\n薪资：25k-40k\n工作地点：远程（可在任何城市）"
}
```

**预期结果**：识别出工作模式为"远程"

---

## 使用说明

1. 打开 Swagger 文档：http://localhost:8000/docs
2. 找到对应的 API 接口
3. 点击 "Try it out"
4. 复制上述 JSON 测试用例到 Request body
5. 点击 "Execute"
6. 查看响应结果

## 测试检查清单

### 岗位信息提取
- [ ] 能够提取岗位名称
- [ ] 能够提取学历要求
- [ ] 能够提取经验要求
- [ ] 能够提取薪资范围
- [ ] 能够提取工作地点
- [ ] 能够识别技能关键词
- [ ] 能够识别行业分类
- [ ] 置信度评分合理

### 岗位难度分析
- [ ] 难度等级准确
- [ ] 难度得分在合理范围
- [ ] 各维度因素分析详细
- [ ] 建议内容针对性强
- [ ] 预估准备时间合理
- [ ] 适合人群描述准确
- [ ] 主要挑战识别正确
- [ ] 市场需求分析合理

### 批量分析
- [ ] 能够同时分析多个岗位
- [ ] 不同岗位返回不同结果
- [ ] 难度递增关系正确
