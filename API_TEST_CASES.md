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

---

## 六、面试题推荐测试用例

### 测试用例 1：Java后端开发工程师

**接口**：POST /api/v1/interview/recommend

```json
{
  "job_text": "岗位：Java后端开发工程师\n\n岗位要求：\n1. 本科及以上学历，计算机相关专业\n2. 3年以上Java开发经验\n3. 熟练掌握Java、Spring Boot、MyBatis\n4. 熟悉MySQL、Redis等数据库\n5. 了解微服务架构\n\n薪资：15k-25k",
  "max_questions": 15
}
```

**预期结果**：
- 推荐15道面试题
- 包含Java基础知识题（集合框架、JVM、多线程等）
- 包含Spring Boot框架题
- 包含数据库题（MySQL、Redis）
- 包含系统设计题和项目经验题
- 每道题都有分类、难度、答案要点、技术标签

---

### 测试用例 2：Python开发工程师

**接口**：POST /api/v1/interview/recommend

```json
{
  "job_text": "Python开发工程师\n\n要求：\n- 熟悉Python、Django或Flask框架\n- 了解数据库MySQL、MongoDB\n- 有API开发经验\n\n待遇：12k-20k",
  "max_questions": 12
}
```

**预期结果**：
- 推荐12道面试题
- 包含Python基础题（装饰器、生成器、GIL等）
- 包含Django/Flask框架对比题
- 包含数据库相关题
- 包含项目经验题

---

### 测试用例 3：前端开发工程师

**接口**：POST /api/v1/interview/recommend

```json
{
  "job_text": "前端开发工程师\n\n职责：\n- 负责公司Web前端开发\n- 使用React或Vue框架\n- 与后端API对接\n\n要求：\n- 熟练掌握HTML、CSS、JavaScript\n- 熟悉React或Vue\n- 了解Webpack、Node.js\n\n薪资：10k-18k",
  "max_questions": 10
}
```

**预期结果**：
- 推荐10道面试题
- 包含JavaScript基础题（闭包、ES6、事件循环等）
- 包含React/Vue框架对比题
- 包含前端性能优化、工程化相关题

---

### 测试用例 4：AI算法工程师

**接口**：POST /api/v1/interview/recommend

```json
{
  "job_text": "AI算法工程师\n\n岗位职责：\n- 负责机器学习算法研发\n- 模型训练和优化\n\n任职要求：\n- 硕士及以上学历\n- 熟悉Python、TensorFlow或PyTorch\n- 熟悉深度学习、NLP或计算机视觉\n- 扎实的算法和数据结构基础\n\n薪资：20k-35k",
  "max_questions": 20
}
```

**预期结果**：
- 推荐20道面试题
- 包含机器学习基础题（过拟合、损失函数、梯度下降等）
- 包含深度学习题（Transformer、CNN、RNN等）
- 包含算法题（排序、链表、二叉树、动态规划等）
- 包含Python编程题

---

### 测试用例 5：全栈开发工程师

**接口**：POST /api/v1/interview/recommend

```json
{
  "job_text": "全栈开发工程师\n\n要求：\n- 前端：Vue或React\n- 后端：Node.js或Python\n- 数据库：MySQL、MongoDB\n- 有完整项目开发经验\n\n薪资：18k-30k",
  "max_questions": 15
}
```

**预期结果**：
- 推荐15道面试题
- 同时包含前端和后端相关题目
- 覆盖JavaScript、数据库、系统设计等多个方面

---

### 测试用例 6：最少题目数量（边界测试）

**接口**：POST /api/v1/interview/recommend

```json
{
  "job_text": "Java开发工程师，要求熟悉Java、Spring Boot、MySQL",
  "max_questions": 5
}
```

**预期结果**：
- 严格返回5道面试题
- 优先推荐最核心的Java和数据库题目

---

### 测试用例 7：最多题目数量（边界测试）

**接口**：POST /api/v1/interview/recommend

```json
{
  "job_text": "高级Java开发工程师\n要求：Java、Spring Boot、微服务、MySQL、Redis、Kafka、Docker、Kubernetes",
  "max_questions": 50
}
```

**预期结果**：
- 返回题目数量 ≤ 50
- 覆盖所有提到的技术栈
- 包含基础、进阶、架构设计等多个层次

---

### 测试用例 8：文本过短（异常测试）

**接口**：POST /api/v1/interview/recommend

```json
{
  "job_text": "Java",
  "max_questions": 10
}
```

**预期结果**：
- HTTP 400 错误
- 错误信息："岗位描述文本过短，请提供更详细的信息"

---

### 测试用例 9：无效题目数量（异常测试）

**接口**：POST /api/v1/interview/recommend

```json
{
  "job_text": "Python开发工程师，熟悉Django、MySQL",
  "max_questions": 3
}
```

**预期结果**：
- HTTP 422 错误
- 验证失败：max_questions 必须 >= 5

---

### 测试用例 10：无技术关键词的岗位

**接口**：POST /api/v1/interview/recommend

```json
{
  "job_text": "软件开发工程师\n\n要求：\n- 本科以上学历\n- 有开发经验\n- 良好的沟通能力\n\n薪资：10k-15k",
  "max_questions": 10
}
```

**预期结果**：
- 返回通用的面试题
- 包含数据库基础题、系统设计题、项目经验题
- 即使没有明确技术栈，也能提供有价值的题目

---

## 七、面试题推荐功能说明

### 响应结构示例

```json
{
  "success": true,
  "recommendation": {
    "job_title": "Java后端开发工程师",
    "total_questions": 15,
    "questions_by_category": {
      "基础知识": 6,
      "框架原理": 2,
      "数据库": 2,
      "算法与数据结构": 2,
      "系统设计": 1,
      "项目经验": 2
    },
    "questions": [
      {
        "question": "请介绍一下Java中的集合框架，以及常用集合类的特点",
        "category": "基础知识",
        "difficulty": "中等",
        "key_points": [
          "Collection和Map两大接口体系",
          "List（ArrayList、LinkedList）：有序可重复",
          "Set（HashSet、TreeSet）：无序不重复",
          "Queue（LinkedList、PriorityQueue）：队列操作",
          "Map（HashMap、TreeMap、LinkedHashMap）：键值对映射"
        ],
        "tags": ["Java", "集合框架", "数据结构"]
      }
    ]
  },
  "message": "成功推荐15道面试题"
}
```

### 字段说明
- **success**: 推荐是否成功
- **recommendation**: 推荐结果对象
  - **job_title**: 识别出的岗位名称
  - **total_questions**: 推荐的题目总数
  - **questions_by_category**: 按分类统计的题目数量
  - **questions**: 面试题列表
    - **question**: 面试题内容
    - **category**: 分类（基础知识、框架原理、算法与数据结构、系统设计、项目经验等）
    - **difficulty**: 难度（简单、中等、困难）
    - **key_points**: 参考答案要点（每条一个核心点）
    - **tags**: 技术标签
- **message**: 响应消息

### 题目分类说明
- **基础知识**：语言特性、核心概念
- **框架原理**：框架使用、底层实现
- **框架对比**：不同框架的对比分析
- **算法与数据结构**：编程能力、算法思维
- **数据库**：SQL、索引、事务、缓存
- **系统设计**：架构设计、高并发、分布式
- **深度学习**：机器学习、神经网络相关
- **项目经验**：问题解决、团队协作

### 难度分级
- **简单**：基础概念、定义类题目
- **中等**：需要理解原理、有一定深度
- **困难**：需要系统思考、综合运用

### 使用建议

**题目数量选择**：
- **应届生/初级**：10-15道题，覆盖基础知识
- **中级**：15-20道题，增加框架和项目经验题
- **高级/架构师**：20-30道题，增加系统设计和架构题

**如何使用答案要点**：
- 每道题的`key_points`是答案的核心要点
- 面试时应该围绕这些要点展开，加入自己的理解和实践经验
- 建议每个要点准备1-2分钟的详细说明

---

## 测试检查清单（更新）

### 面试题推荐
- [ ] 能够根据岗位推荐相关面试题
- [ ] 题目数量控制准确（5-50范围）
- [ ] 题目与岗位技能栈匹配
- [ ] 每道题都有完整的结构（题目、分类、难度、要点、标签）
- [ ] 答案要点清晰具体
- [ ] 题目分类统计正确
- [ ] 难度分级合理
- [ ] 支持多种岗位类型（前端、后端、算法、全栈等）
- [ ] 异常情况处理正确（文本过短、数量越界等）

### AI模拟面试
- [ ] 能够评估用户的面试回答
- [ ] 评分合理（0-100分）
- [ ] 能够识别回答的优点和不足
- [ ] 提供具体的改进建议
- [ ] 列出遗漏的关键要点
- [ ] 支持批量评估多道题
- [ ] 计算平均分和整体评价
- [ ] 生成整体总结和改进方向

---

## 八、AI模拟面试问答测试用例

### 测试用例 1：Java集合框架回答评估

**接口**：POST /api/v1/mock-interview/evaluate

```json
{
  "question": "请介绍一下Java中的集合框架",
  "user_answer": "Java集合框架主要分为两大体系：Collection和Map。\n\nCollection接口下包括：\n1. List：有序可重复，常用ArrayList和LinkedList\n2. Set：无序不重复，常用HashSet和TreeSet\n3. Queue：队列操作，常用LinkedList和PriorityQueue\n\nMap接口是键值对映射，常用HashMap、TreeMap等。\n\n选择时要考虑是否需要有序、是否允许重复、查询和插入的性能要求。"
}
```

**预期结果**：
- 得分：70-80分
- 评价：良好/一般
- 优点：覆盖核心要点、结构清晰
- 不足：可以补充具体案例
- 参考答案：返回集合框架的完整要点

---

### 测试用例 2：简短回答评估（低分）

**接口**：POST /api/v1/mock-interview/evaluate

```json
{
  "question": "什么是HashMap？",
  "user_answer": "HashMap是Java中的一个键值对集合。"
}
```

**预期结果**：
- 得分：< 70分
- 评价：需改进/一般
- 不足：回答过于简短、遗漏重要知识点
- 建议：展开详细说明、补充底层原理

---

### 测试用例 3：优秀回答评估（高分）

**接口**：POST /api/v1/mock-interview/evaluate

```json
{
  "question": "请解释Python中的装饰器",
  "user_answer": "装饰器是Python中的一个重要特性，本质上是一个高阶函数，它接收一个函数作为参数，返回一个新的函数。\n\n使用@语法糖可以简化装饰器的调用。例如：\n@login_required\ndef view_profile():\n    pass\n\n常见应用场景包括：\n- 日志记录\n- 权限校验\n- 性能计时\n- 缓存\n\n装饰器可以叠加使用，执行顺序从下到上。使用functools.wraps可以保留原函数的元信息。"
}
```

**预期结果**：
- 得分：≥ 85分
- 评价：优秀/良好
- 优点：有案例、结构清晰、详细充分
- 不足：可以补充带参数的装饰器

---

### 测试用例 4：算法题回答评估

**接口**：POST /api/v1/mock-interview/evaluate

```json
{
  "question": "请介绍一下快速排序算法",
  "user_answer": "快速排序是一种基于分治思想的高效排序算法。\n\n核心思想：\n1. 选择一个pivot（基准值）\n2. 将小于pivot的元素放左边，大于pivot的放右边\n3. 递归对左右两部分进行排序\n\n时间复杂度：\n- 平均：O(nlogn)\n- 最坏：O(n²)，当数组已经有序时\n\n空间复杂度：O(logn)，主要是递归栈的开销\n\n优化方法：\n- 三数取中法选择pivot，避免最坏情况\n- 当子数组较小时，切换到插入排序\n- 尾递归优化\n\n实际应用：快速排序是实践中最常用的排序算法之一，例如Java的Arrays.sort()对基本类型就使用了快排的变种。\n\n相比归并排序，快排的优势是原地排序，不需要额外空间；缺点是不稳定排序。"
}
```

**预期结果**：
- 得分：≥ 85分
- 评价：优秀/良好
- 优点：有案例、有对比、结构清晰、详细充分
- 所有加分项都满足

---

### 测试用例 5：批量评估

**接口**：POST /api/v1/mock-interview/batch-evaluate

```json
{
  "answers": [
    {
      "question": "请介绍一下Java中的集合框架",
      "user_answer": "Java集合框架包括Collection和Map两大体系。Collection包括List、Set、Queue。",
      "question_category": "基础知识",
      "question_difficulty": "中等"
    },
    {
      "question": "什么是HashMap？",
      "user_answer": "HashMap是基于哈希表的Map接口实现，底层是数组+链表+红黑树。",
      "question_category": "基础知识",
      "question_difficulty": "中等"
    },
    {
      "question": "Python装饰器是什么？",
      "user_answer": "装饰器是高阶函数，用于修改或增强函数功能，常用于日志、权限校验等场景。",
      "question_category": "基础知识",
      "question_difficulty": "中等"
    }
  ]
}
```

**预期结果**：
- total_questions: 3
- average_score: 60-75分
- overall_evaluation: 一般/良好
- feedbacks: 包含3个详细反馈
- summary: 整体优缺点总结和改进建议

---

### 测试用例 6：遗漏要点识别

**接口**：POST /api/v1/mock-interview/evaluate

```json
{
  "question": "请说明MySQL的事务隔离级别",
  "user_answer": "MySQL有四个事务隔离级别，分别是读未提交和读已提交。"
}
```

**预期结果**：
- 得分：< 70分
- missing_points: 包含"可重复读"、"串行化"等
- 建议：补充遗漏的隔离级别

---

### 测试用例 7：文本过短（异常测试）

**接口**：POST /api/v1/mock-interview/evaluate

```json
{
  "question": "什么是HashMap？",
  "user_answer": "集合"
}
```

**预期结果**：
- HTTP 400 错误
- 错误信息："回答内容过短，请提供至少10个字符的回答"

---

### 测试用例 8：批量评估超出限制（异常测试）

**接口**：POST /api/v1/mock-interview/batch-evaluate

```json
{
  "answers": [
    {
      "question": "题目1",
      "user_answer": "回答内容至少10个字符..."
    }
    // ... 共21道题
  ]
}
```

**预期结果**：
- HTTP 400 错误
- 错误信息："单次最多评估20道题目"

---

## 九、AI模拟面试功能说明

### 评分维度

1. **要点覆盖度（60分）**
   - 完全覆盖：60分
   - 部分覆盖：按比例计分
   - 未覆盖：0分

2. **回答长度（10分）**
   - ≥ 200字：10分
   - ≥ 100字：7分
   - ≥ 50字：5分

3. **案例说明（10分）**
   - 有具体案例或示例：10分
   - 无：0分

4. **对比分析（10分）**
   - 有对比分析：10分
   - 无：0分

5. **结构清晰（10分）**
   - 有分点阐述、逻辑清晰：10分
   - 无：0分

### 评价等级

- **优秀**：90-100分
- **良好**：75-89分
- **一般**：60-74分
- **需改进**：< 60分

### 响应结构示例

```json
{
  "success": true,
  "feedback": {
    "score": 85,
    "evaluation": "良好",
    "strengths": [
      "回答覆盖了4个核心要点，内容全面",
      "回答结构清晰，逻辑完整",
      "回答详细充分，表达完整"
    ],
    "weaknesses": [
      "缺少具体案例或实际应用场景说明"
    ],
    "suggestions": [
      "准备1-2个实际项目中的使用案例"
    ],
    "missing_points": [],
    "improvement_advice": "回答较好地覆盖了核心内容。建议进一步深入底层原理，并结合实际项目经验进行说明。"
  },
  "reference_answer": [
    "Collection和Map两大接口体系",
    "List（ArrayList、LinkedList）：有序可重复",
    "Set（HashSet、TreeSet）：无序不重复",
    "Queue（LinkedList、PriorityQueue）：队列操作",
    "Map（HashMap、TreeMap、LinkedHashMap）：键值对映射",
    "选择依据：是否有序、是否重复、查询/插入性能"
  ],
  "message": "答题反馈生成成功"
}
```

### 使用建议

1. **回答技巧**
   - 覆盖核心要点（最重要）
   - 提供具体案例或实际应用场景
   - 进行对比分析（展现深度）
   - 采用结构化表达（分点阐述）
   - 详细充分（200字以上为佳）

2. **改进方向**
   - 根据`missing_points`补充遗漏内容
   - 参考`reference_answer`完善知识体系
   - 按照`suggestions`针对性改进
   - 多做练习，形成答题模板

3. **批量评估场景**
   - 完成一套模拟面试后整体评估
   - 阶段性学习成果检验
   - 识别知识体系中的薄弱环节
   - 跟踪学习进度
