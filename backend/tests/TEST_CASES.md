# 测试用例文档

## 运行方式

### 1. 交互式对话测试（推荐）

```bash
cd backend
python tests/interactive_interview.py
```

**使用说明**:
- 输入岗位、候选人姓名、第一个问题（或直接回车使用默认值）
- 开始与AI面试官对话
- AI会自动追问、评价，并在评价后自动生成下一题
- 输入 `end` 结束面试查看总结报告
- 输入 `quit` 退出

---

### 2. pytest单元测试

```bash
cd backend
python -m pytest tests/test_interactive_interview.py -v -s
```

---

## 测试用例

### 测试1: 开始面试会话

```python
result = langchain_interview_service.start_session(
    job_title="Python后端开发工程师",
    initial_question="请先做一下自我介绍",
    candidate_name="测试候选人"
)

# 验证
assert result["success"] is True
assert "session_id" in result
assert result["question_number"] == 1
```

**预期结果**: 成功创建会话，返回session_id和开场白

---

### 测试2: 完整面试流程

```python
# 1. 开始面试
start_result = langchain_interview_service.start_session(
    job_title="Java后端开发工程师",
    initial_question="请介绍一下你的项目经验",
    candidate_name="张三"
)
session_id = start_result["session_id"]

# 2. 候选人回答（提到项目）
answer1 = """
我之前在一家电商公司工作，主要负责订单系统的开发。
我们的订单系统日均处理10万单，使用Spring Boot + MySQL + Redis的技术栈。
我主要负责订单创建、订单查询和订单状态流转的功能。
"""

result = await langchain_interview_service.continue_conversation(
    session_id=session_id,
    candidate_answer=answer1
)

# 3. AI会追问或评价
# response_type 可能是: "follow_up", "project_deep_dive", "evaluation"
```

**预期结果**: 
- AI识别到项目经验，进行深挖
- 或者AI直接评价并自动提出下一个问题

---

### 测试3: AI自动生成下一题

```python
# 候选人表示回答完毕
answer = "没有了，我觉得这个问题回答得差不多了"

result = await langchain_interview_service.continue_conversation(
    session_id=session_id,
    candidate_answer=answer
)

# 验证AI自动生成下一题
assert result["response_type"] == "evaluation"
assert "?" in result["interviewer_message"] or "？" in result["interviewer_message"]
```

**预期结果**: AI给出评价（优点、不足、评分）并自动提出下一个面试问题

---

### 测试4: 项目深挖

```python
answer = """
我做过一个支付系统的项目，需要保证分布式事务的一致性。
我们使用了TCC模式来解决这个问题。
"""

result = await langchain_interview_service.continue_conversation(
    session_id=session_id,
    candidate_answer=answer
)

# AI应该追问项目细节
assert any(keyword in result["interviewer_message"] 
          for keyword in ["项目", "具体", "详细", "如何", "为什么"])
```

**预期结果**: AI识别到项目关键词，自动深挖项目细节

---

### 测试5: 获取会话信息

```python
session_info = langchain_interview_service.get_session_info(session_id)

assert session_info is not None
assert session_info["job_title"] == "前端开发工程师"
assert session_info["status"] == "active"
assert isinstance(session_info["conversation_history"], list)
```

**预期结果**: 返回会话信息，包括岗位、状态、对话历史

---

### 测试6: 结束面试

```python
end_result = await langchain_interview_service.end_session(session_id)

assert end_result["success"] is True
assert "interview_summary" in end_result
assert end_result["total_questions"] >= 1
```

**预期结果**: 生成完整的面试评估报告，包括总体评价、优点、不足、改进建议

---

## 验证的功能

### LangChain标准组件
✅ `ChatOpenAI` - 通义千问API集成  
✅ `ChatPromptTemplate` - 提示词模板  
✅ `MessagesPlaceholder` - 历史消息占位符  
✅ `RunnableWithMessageHistory` - 带历史的可运行链  
✅ `StrOutputParser` - 字符串输出解析  
✅ `InMemoryChatMessageHistory` - 内存对话历史  
✅ `streaming=True` - 流式输出  

### AI面试官能力
✅ **对话记忆** - 记住所有历史对话  
✅ **智能追问** - 根据回答深度自动追问细节  
✅ **项目深挖** - 识别项目经验自动深入询问  
✅ **自动评价** - 判断回答完整性并打分  
✅ **自动出题** - 评价后根据岗位自动生成下一题  

---

## 示例对话流程

```
面试官: 你好！欢迎参加Python后端开发工程师的技术面试。
       第一个问题：请介绍一下你的项目经验

候选人: 我做过一个电商项目，使用多线程处理订单导入

面试官: [🎯 深挖项目] 
       能详细说说这个电商项目吗？订单规模有多大？
       你具体负责哪个模块？

候选人: 日均10万订单，我负责用ThreadPoolExecutor处理批量导入

面试官: [🔍 追问细节]
       为什么选择20个线程？有做过性能测试吗？

候选人: 做过测试，20个线程吞吐量最高，性能提升4倍

面试官: [💬 询问补充]
       还有其他想补充的吗？

候选人: 没有了，回答完了

面试官: [📊 评价并自动出下一题]
       ## 本题回答总结
       ...
       ## 评分：85分
       
       接下来我们看下一个问题。
       你是否了解什么是装饰器？能否举一个实际应用的例子？

候选人: 装饰器是一个函数，可以在不修改原函数的情况下增强功能...
```

---

## 快速开始

```bash
# 1. 启动交互式测试
cd backend
python tests/interactive_interview.py

# 2. 全部回车使用默认值

# 3. 开始对话，体验AI的智能追问和自动出题！
```
