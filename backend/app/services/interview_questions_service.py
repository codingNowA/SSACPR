"""
面试题推荐服务
"""
from typing import List, Dict
from app.schemas.interview_questions import (
    InterviewQuestion,
    InterviewQuestionsRecommendation,
    InterviewQuestionsResponse
)
from app.services.job_extraction_service import job_info_extractor


class InterviewQuestionsService:
    """面试题推荐服务"""

    def __init__(self):
        # 面试题库 - 按技术栈和岗位类型组织
        self.question_bank = self._init_question_bank()

    def _init_question_bank(self) -> Dict[str, List[InterviewQuestion]]:
        """初始化面试题库"""
        return {
            "Java": [
                InterviewQuestion(
                    question="请介绍一下Java中的集合框架，以及常用集合类的特点",
                    category="基础知识",
                    difficulty="中等",
                    key_points=[
                        "Collection和Map两大接口体系",
                        "List（ArrayList、LinkedList）：有序可重复",
                        "Set（HashSet、TreeSet）：无序不重复",
                        "Queue（LinkedList、PriorityQueue）：队列操作",
                        "Map（HashMap、TreeMap、LinkedHashMap）：键值对映射"
                    ],
                    tags=["Java", "集合框架", "数据结构"]
                ),
                InterviewQuestion(
                    question="HashMap的底层实现原理是什么？JDK1.8做了哪些优化？",
                    category="基础知识",
                    difficulty="中等",
                    key_points=[
                        "底层：数组 + 链表 + 红黑树",
                        "Put流程：hash计算 → 数组定位 → 链表/树插入",
                        "JDK1.8优化：链表长度>8且数组>64时转红黑树",
                        "扩容机制：容量翻倍，rehash重新分布",
                        "负载因子0.75：空间与时间的平衡"
                    ],
                    tags=["Java", "HashMap", "数据结构"]
                ),
                InterviewQuestion(
                    question="Java中的多线程如何实现？线程池的核心参数有哪些？",
                    category="基础知识",
                    difficulty="中等",
                    key_points=[
                        "实现方式：继承Thread、实现Runnable、实现Callable",
                        "线程池核心参数：corePoolSize、maximumPoolSize、keepAliveTime、workQueue",
                        "拒绝策略：AbortPolicy、CallerRunsPolicy、DiscardPolicy、DiscardOldestPolicy",
                        "常用线程池：newFixedThreadPool、newCachedThreadPool、newSingleThreadExecutor"
                    ],
                    tags=["Java", "多线程", "线程池"]
                ),
                InterviewQuestion(
                    question="JVM内存结构是怎样的？垃圾回收算法有哪些？",
                    category="基础知识",
                    difficulty="困难",
                    key_points=[
                        "内存结构：堆、栈、方法区、程序计数器、本地方法栈",
                        "堆分代：新生代（Eden、Survivor）、老年代",
                        "GC算法：标记-清除、标记-整理、复制算法、分代收集",
                        "GC收集器：Serial、Parallel、CMS、G1"
                    ],
                    tags=["Java", "JVM", "垃圾回收"]
                ),
                InterviewQuestion(
                    question="Spring Boot的自动配置原理是什么？",
                    category="框架原理",
                    difficulty="中等",
                    key_points=[
                        "@SpringBootApplication = @Configuration + @EnableAutoConfiguration + @ComponentScan",
                        "自动配置通过spring.factories文件加载",
                        "@Conditional条件注解控制配置生效",
                        "可通过application.properties覆盖默认配置"
                    ],
                    tags=["Spring Boot", "自动配置", "框架"]
                ),
            ],
            "Python": [
                InterviewQuestion(
                    question="Python中的装饰器是什么？如何实现一个装饰器？",
                    category="基础知识",
                    difficulty="中等",
                    key_points=[
                        "装饰器本质：接收函数作为参数，返回新函数的高阶函数",
                        "使用@语法糖简化调用",
                        "应用场景：日志、权限校验、缓存、计时",
                        "可以叠加使用多个装饰器",
                        "functools.wraps保留原函数元信息"
                    ],
                    tags=["Python", "装饰器", "高阶函数"]
                ),
                InterviewQuestion(
                    question="解释一下Python的GIL（全局解释器锁）及其影响",
                    category="基础知识",
                    difficulty="困难",
                    key_points=[
                        "GIL：同一时刻只允许一个线程执行Python字节码",
                        "影响：多线程无法利用多核CPU进行计算密集型任务",
                        "解决方案：多进程（multiprocessing）、异步IO（asyncio）",
                        "IO密集型任务不受影响，计算密集型任务受限"
                    ],
                    tags=["Python", "GIL", "多线程"]
                ),
                InterviewQuestion(
                    question="Python中的生成器和迭代器有什么区别？",
                    category="基础知识",
                    difficulty="中等",
                    key_points=[
                        "迭代器：实现__iter__和__next__方法的对象",
                        "生成器：使用yield关键字的特殊迭代器",
                        "优势：惰性计算、节省内存",
                        "应用场景：处理大数据、流式数据",
                        "生成器表达式：类似列表推导式但更省内存"
                    ],
                    tags=["Python", "生成器", "迭代器"]
                ),
                InterviewQuestion(
                    question="Django和Flask有什么区别？分别适用于什么场景？",
                    category="框架对比",
                    difficulty="简单",
                    key_points=[
                        "Django：全栈框架，内置ORM、Admin、认证系统",
                        "Flask：轻量级框架，灵活性高，需自行选择组件",
                        "Django适合：快速开发、功能完整的Web应用",
                        "Flask适合：微服务、API、需要高度定制的项目"
                    ],
                    tags=["Python", "Django", "Flask", "框架"]
                ),
            ],
            "前端": [
                InterviewQuestion(
                    question="Vue和React有什么区别？各自的优缺点是什么？",
                    category="框架对比",
                    difficulty="中等",
                    key_points=[
                        "Vue：模板语法、双向绑定、渐进式框架",
                        "React：JSX语法、单向数据流、组件化思想",
                        "Vue优势：上手简单、文档友好、中文社区活跃",
                        "React优势：生态丰富、灵活性高、大厂背书",
                        "选择依据：团队技术栈、项目规模、学习曲线"
                    ],
                    tags=["前端", "Vue", "React", "框架"]
                ),
                InterviewQuestion(
                    question="什么是闭包？闭包的应用场景有哪些？",
                    category="基础知识",
                    difficulty="中等",
                    key_points=[
                        "闭包：函数可以访问其外部作用域的变量",
                        "形成条件：内部函数引用外部函数的变量",
                        "应用场景：数据私有化、柯里化、模块化",
                        "注意：可能导致内存泄漏，需注意释放"
                    ],
                    tags=["JavaScript", "闭包", "作用域"]
                ),
                InterviewQuestion(
                    question="ES6的新特性有哪些？",
                    category="基础知识",
                    difficulty="简单",
                    key_points=[
                        "let、const声明变量",
                        "箭头函数、模板字符串",
                        "解构赋值、扩展运算符",
                        "Promise、async/await异步处理",
                        "Class类、模块化import/export"
                    ],
                    tags=["JavaScript", "ES6", "语言特性"]
                ),
                InterviewQuestion(
                    question="浏览器的事件循环机制是什么？宏任务和微任务的区别？",
                    category="基础知识",
                    difficulty="困难",
                    key_points=[
                        "事件循环：执行栈 → 微任务队列 → 宏任务队列",
                        "宏任务：setTimeout、setInterval、I/O、UI渲染",
                        "微任务：Promise.then、MutationObserver",
                        "执行顺序：先清空所有微任务，再执行下一个宏任务"
                    ],
                    tags=["JavaScript", "事件循环", "异步"]
                ),
            ],
            "算法": [
                InterviewQuestion(
                    question="请实现快速排序算法，并分析其时间复杂度",
                    category="算法与数据结构",
                    difficulty="中等",
                    key_points=[
                        "思想：分治法，选择pivot，小于放左边，大于放右边",
                        "时间复杂度：平均O(nlogn)，最坏O(n²)",
                        "空间复杂度：O(logn)递归栈",
                        "优化：三数取中选pivot、尾递归优化"
                    ],
                    tags=["算法", "排序", "快速排序"]
                ),
                InterviewQuestion(
                    question="如何判断链表是否有环？如何找到环的入口？",
                    category="算法与数据结构",
                    difficulty="中等",
                    key_points=[
                        "判断有环：快慢指针，快指针走2步，慢指针走1步",
                        "相遇则有环，快指针为null则无环",
                        "找入口：相遇后，一指针从头开始，两指针每次走1步",
                        "再次相遇点即为环的入口"
                    ],
                    tags=["算法", "链表", "快慢指针"]
                ),
                InterviewQuestion(
                    question="二叉树的层序遍历如何实现？",
                    category="算法与数据结构",
                    difficulty="简单",
                    key_points=[
                        "使用队列（BFS广度优先搜索）",
                        "根节点入队，循环：出队、访问、左右子节点入队",
                        "记录每层节点数，可实现分层输出",
                        "应用：求树的最大宽度、最小深度"
                    ],
                    tags=["算法", "二叉树", "BFS"]
                ),
                InterviewQuestion(
                    question="动态规划和贪心算法有什么区别？",
                    category="算法与数据结构",
                    difficulty="中等",
                    key_points=[
                        "动态规划：全局最优，保存子问题结果，自底向上",
                        "贪心算法：局部最优，每步选择当前最优解",
                        "动态规划可解决贪心无法解决的问题",
                        "经典例题：背包问题（DP）、活动选择（贪心）"
                    ],
                    tags=["算法", "动态规划", "贪心"]
                ),
            ],
            "数据库": [
                InterviewQuestion(
                    question="MySQL的索引类型有哪些？B+树索引的优势是什么？",
                    category="数据库",
                    difficulty="中等",
                    key_points=[
                        "索引类型：B+树索引、Hash索引、全文索引",
                        "B+树优势：有序、范围查询快、叶子节点存数据",
                        "聚簇索引vs非聚簇索引",
                        "索引失效场景：like左模糊、or、函数计算、类型转换"
                    ],
                    tags=["数据库", "MySQL", "索引"]
                ),
                InterviewQuestion(
                    question="什么是事务？事务的四大特性（ACID）是什么？",
                    category="数据库",
                    difficulty="简单",
                    key_points=[
                        "事务：一组操作的原子单元",
                        "原子性（Atomicity）：要么全做，要么全不做",
                        "一致性（Consistency）：数据完整性约束不被破坏",
                        "隔离性（Isolation）：并发事务互不干扰",
                        "持久性（Durability）：提交后永久保存"
                    ],
                    tags=["数据库", "事务", "ACID"]
                ),
                InterviewQuestion(
                    question="MySQL的事务隔离级别有哪些？分别解决什么问题？",
                    category="数据库",
                    difficulty="中等",
                    key_points=[
                        "读未提交：脏读、不可重复读、幻读",
                        "读已提交：不可重复读、幻读（Oracle默认）",
                        "可重复读：幻读（MySQL默认，通过MVCC解决）",
                        "串行化：无并发问题，性能最差"
                    ],
                    tags=["数据库", "事务隔离级别", "并发"]
                ),
                InterviewQuestion(
                    question="Redis的数据类型有哪些？分别适用于什么场景？",
                    category="数据库",
                    difficulty="简单",
                    key_points=[
                        "String：缓存、计数器、分布式锁",
                        "Hash：存储对象、购物车",
                        "List：消息队列、时间轴",
                        "Set：标签、共同关注、去重",
                        "ZSet：排行榜、延时队列"
                    ],
                    tags=["Redis", "数据类型", "缓存"]
                ),
            ],
            "系统设计": [
                InterviewQuestion(
                    question="如何设计一个高并发的秒杀系统？",
                    category="系统设计",
                    difficulty="困难",
                    key_points=[
                        "前端：限流、防重复提交、CDN加速",
                        "后端：Redis库存预减、消息队列异步处理",
                        "数据库：乐观锁、分库分表",
                        "其他：验证码、动静分离、热点数据隔离"
                    ],
                    tags=["系统设计", "高并发", "秒杀"]
                ),
                InterviewQuestion(
                    question="什么是CAP定理？如何权衡？",
                    category="系统设计",
                    difficulty="中等",
                    key_points=[
                        "C（Consistency）：一致性",
                        "A（Availability）：可用性",
                        "P（Partition tolerance）：分区容错性",
                        "三者不可兼得，只能满足两个",
                        "分布式系统必须P，需在C和A中权衡"
                    ],
                    tags=["系统设计", "CAP", "分布式"]
                ),
                InterviewQuestion(
                    question="微服务架构的优缺点是什么？",
                    category="系统设计",
                    difficulty="中等",
                    key_points=[
                        "优点：独立部署、技术栈灵活、易于扩展",
                        "缺点：运维复杂、分布式事务、服务调用开销",
                        "适用场景：大型项目、多团队协作",
                        "关键组件：服务注册发现、配置中心、API网关"
                    ],
                    tags=["系统设计", "微服务", "架构"]
                ),
            ],
            "机器学习": [
                InterviewQuestion(
                    question="请解释过拟合和欠拟合，以及如何解决？",
                    category="基础知识",
                    difficulty="中等",
                    key_points=[
                        "过拟合：模型在训练集表现好，测试集差",
                        "欠拟合：模型在训练集和测试集都表现差",
                        "解决过拟合：增加数据、正则化、Dropout、Early Stopping",
                        "解决欠拟合：增加模型复杂度、增加特征、减少正则化"
                    ],
                    tags=["机器学习", "过拟合", "模型调优"]
                ),
                InterviewQuestion(
                    question="常见的损失函数有哪些？分别适用于什么任务？",
                    category="基础知识",
                    difficulty="中等",
                    key_points=[
                        "回归任务：MSE、MAE、Huber Loss",
                        "分类任务：交叉熵、Focal Loss",
                        "二分类：Binary Cross-Entropy",
                        "多分类：Categorical Cross-Entropy"
                    ],
                    tags=["机器学习", "损失函数", "深度学习"]
                ),
                InterviewQuestion(
                    question="什么是梯度下降？有哪些变体？",
                    category="基础知识",
                    difficulty="中等",
                    key_points=[
                        "梯度下降：沿梯度反方向更新参数，最小化损失",
                        "批量梯度下降（BGD）：全量数据",
                        "随机梯度下降（SGD）：单样本",
                        "小批量梯度下降（Mini-batch）：折中方案",
                        "优化器：Adam、RMSprop、AdaGrad"
                    ],
                    tags=["机器学习", "梯度下降", "优化器"]
                ),
                InterviewQuestion(
                    question="Transformer架构的核心是什么？相比RNN有什么优势？",
                    category="深度学习",
                    difficulty="困难",
                    key_points=[
                        "核心：Self-Attention机制",
                        "优势：并行计算、长距离依赖、可解释性",
                        "组成：Multi-Head Attention、Position Encoding、FFN",
                        "应用：BERT、GPT、Vision Transformer"
                    ],
                    tags=["深度学习", "Transformer", "NLP"]
                ),
            ],
            "项目经验": [
                InterviewQuestion(
                    question="请介绍一下你最有挑战性的项目，遇到了什么问题？如何解决的？",
                    category="项目经验",
                    difficulty="中等",
                    key_points=[
                        "STAR法则：Situation、Task、Action、Result",
                        "描述背景：项目规模、技术栈、团队角色",
                        "遇到的问题：技术难点、性能瓶颈、协作挑战",
                        "解决方案：具体措施、技术选型、优化效果",
                        "最终结果：量化指标、经验总结"
                    ],
                    tags=["项目经验", "问题解决", "STAR"]
                ),
                InterviewQuestion(
                    question="如果线上系统突然出现性能问题，你会如何排查？",
                    category="项目经验",
                    difficulty="中等",
                    key_points=[
                        "观察监控：QPS、响应时间、错误率、CPU、内存",
                        "日志分析：错误日志、慢查询日志",
                        "定位问题：接口耗时、数据库慢查询、缓存失效",
                        "应急处理：限流、降级、扩容",
                        "根本解决：优化代码、索引优化、架构调整"
                    ],
                    tags=["项目经验", "性能优化", "故障排查"]
                ),
                InterviewQuestion(
                    question="你如何保证代码质量？团队如何进行Code Review？",
                    category="项目经验",
                    difficulty="简单",
                    key_points=[
                        "编码规范：遵循团队规范、使用Lint工具",
                        "单元测试：核心逻辑覆盖率80%+",
                        "Code Review：至少一人审核、关注逻辑、性能、安全",
                        "CI/CD：自动化测试、自动部署",
                        "重构：定期清理技术债务"
                    ],
                    tags=["项目经验", "代码质量", "团队协作"]
                ),
            ],
        }

    def recommend(self, job_text: str, max_questions: int = 15) -> InterviewQuestionsResponse:
        """
        基于岗位信息推荐面试题

        Args:
            job_text: 岗位描述文本
            max_questions: 最多推荐题目数量

        Returns:
            InterviewQuestionsResponse: 推荐结果
        """
        # 1. 先提取岗位信息
        job_info = job_info_extractor.extract(job_text)
        extracted = job_info.extracted_info

        # 2. 分析岗位类型和所需技能
        job_title = extracted.job_title or ""
        skills = extracted.required_skills + extracted.preferred_skills
        industry = extracted.industry or ""

        # 3. 确定推荐策略
        selected_questions = []

        # 识别岗位类型
        job_type = self._identify_job_type(job_title, skills)

        # 根据技能推荐题目
        for skill in skills:
            if skill in self.question_bank:
                questions = self.question_bank[skill]
                selected_questions.extend(questions)

        # 如果是算法/AI岗位，添加算法题和机器学习题
        if any(kw in job_title.lower() or kw in industry.lower()
               for kw in ["算法", "ai", "人工智能", "机器学习", "深度学习"]):
            selected_questions.extend(self.question_bank.get("算法", []))
            selected_questions.extend(self.question_bank.get("机器学习", []))

        # 如果是前端岗位
        if any(kw in job_title.lower() for kw in ["前端", "frontend", "fe", "react", "vue"]):
            selected_questions.extend(self.question_bank.get("前端", []))

        # 添加通用题目
        selected_questions.extend(self.question_bank.get("数据库", [])[:2])  # 数据库基础题
        selected_questions.extend(self.question_bank.get("系统设计", [])[:2])  # 系统设计题
        selected_questions.extend(self.question_bank.get("项目经验", []))  # 项目经验题

        # 4. 去重并限制数量
        seen = set()
        unique_questions = []
        for q in selected_questions:
            if q.question not in seen:
                seen.add(q.question)
                unique_questions.append(q)
                if len(unique_questions) >= max_questions:
                    break

        # 5. 按分类统计
        questions_by_category = {}
        for q in unique_questions:
            questions_by_category[q.category] = questions_by_category.get(q.category, 0) + 1

        # 6. 构建推荐结果
        recommendation = InterviewQuestionsRecommendation(
            job_title=job_title,
            total_questions=len(unique_questions),
            questions_by_category=questions_by_category,
            questions=unique_questions
        )

        return InterviewQuestionsResponse(
            success=True,
            recommendation=recommendation,
            message=f"成功推荐{len(unique_questions)}道面试题"
        )

    def _identify_job_type(self, job_title: str, skills: List[str]) -> str:
        """识别岗位类型"""
        title_lower = job_title.lower()

        if any(kw in title_lower for kw in ["前端", "frontend", "fe", "react", "vue"]):
            return "前端"
        elif any(kw in title_lower for kw in ["后端", "backend", "be", "java", "python", "go"]):
            return "后端"
        elif any(kw in title_lower for kw in ["全栈", "fullstack"]):
            return "全栈"
        elif any(kw in title_lower for kw in ["算法", "ai", "机器学习", "深度学习"]):
            return "算法/AI"
        elif any(kw in title_lower for kw in ["测试", "qa", "test"]):
            return "测试"
        elif any(kw in title_lower for kw in ["运维", "devops", "sre"]):
            return "运维"
        else:
            return "通用"


# 创建全局实例
interview_service = InterviewQuestionsService()
