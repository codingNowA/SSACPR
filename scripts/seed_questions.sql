-- =====================================================
-- 示例面试题数据（题库管理用）
-- =====================================================

INSERT INTO interview_questions (category, difficulty, question, answer_points, related_skills, created_at) VALUES
('Java', 'medium', '请说明 Java 中 HashMap 和 Hashtable 的区别', '1. 线程安全性不同\n2. 是否允许 null key/value\n3. 继承的父类不同\n4. 扩容机制不同', '["Java", "HashMap", "Hashtable"]', NOW()),
('Java', 'hard', '请描述 Spring Boot 自动配置原理', '1. @EnableAutoConfiguration 注解\n2. spring.factories 文件\n3. Conditional 条件注解', '["Spring Boot", "自动配置", "Conditional"]', NOW()),
('Python', 'easy', 'Python 中的列表和元组有什么区别？', '1. 列表可变，元组不可变\n2. 列表有更多方法\n3. 元组内存占用更小', '["Python", "列表", "元组"]', NOW()),
('Python', 'medium', '解释 Python 的 GIL 是什么？', 'GIL 是全局解释器锁，限制同一时刻只能有一个线程执行 Python 字节码', '["Python", "GIL", "多线程"]', NOW()),
('数据分析', 'easy', '什么是数据清洗？', '数据清洗是数据预处理的重要步骤，包括处理缺失值、异常值、重复数据、格式统一等', '["数据分析", "数据清洗", "预处理"]', NOW()),
('数据分析', 'medium', '请说明 SQL 中 JOIN 和 UNION 的区别', 'JOIN 用于横向合并（添加列），UNION 用于纵向合并（添加行）', '["SQL", "JOIN", "UNION"]', NOW()),

-- =====================================================
-- 新增面试题（覆盖更多分类与难度）
-- =====================================================
('Java', 'easy', 'Java 中 final、finally、finalize 的区别是什么？', '1. final 用于修饰类、方法、变量，表示不可继承/重写/修改\n2. finally 用于异常处理，保证代码块一定执行\n3. finalize 是 Object 的方法，在垃圾回收前调用（已弃用）', '["Java", "final", "finally", "finalize"]', NOW()),
('Java', 'medium', 'ConcurrentHashMap 如何实现线程安全？', '1. JDK 1.7 采用分段锁（Segment）\n2. JDK 1.8 采用 CAS + synchronized 锁链节点\n3. 读操作不加锁，通过 volatile 保证可见性\n4. 扩容时支持多线程并发迁移', '["Java", "ConcurrentHashMap", "线程安全", "CAS", "synchronized"]', NOW()),
('Java', 'hard', '请解释 JVM 的垃圾回收机制和常用 GC 算法', '1. 分代收集理论：年轻代（Minor GC）、老年代（Major/Full GC）\n2. 常用算法：标记-清除、标记-复制、标记-整理\n3. 常用收集器：G1、ZGC、CMS（已弃用）\n4. 调优参数：-Xms、-Xmx、-XX:+UseG1GC 等', '["Java", "JVM", "垃圾回收", "G1", "ZGC", "GC调优"]', NOW()),

('Python', 'easy', 'Python 中 __init__ 和 __new__ 的区别？', '1. __new__ 是构造函数，创建并返回实例对象\n2. __init__ 是初始化函数，在实例创建后被调用\n3. __new__ 一般用于不可变类型或单例模式', '["Python", "__init__", "__new__", "单例"]', NOW()),
('Python', 'medium', 'Python 中的装饰器是什么？如何实现一个带参数的装饰器？', '1. 装饰器是一个函数，用于在不修改原函数代码的情况下增加功能\n2. 带参数的装饰器需要外层函数来接收参数，内层函数来接收被装饰函数\n3. 常见应用：日志记录、性能计时、权限校验', '["Python", "装饰器", "闭包", "@符号"]', NOW()),
('Python', 'hard', 'Python 中的协程与线程的区别？asyncio 的原理是什么？', '1. 线程由操作系统调度，协程由事件循环（Event Loop）调度\n2. 协程是单线程的，通过 await 切换任务，适用于 IO 密集型\n3. asyncio 基于 async/await 语法，底层使用 Selector 或 Proactor 事件循环', '["Python", "协程", "asyncio", "async/await", "线程", "IO密集"]', NOW()),

('前端', 'easy', '什么是跨域？如何解决前端跨域问题？', '1. 跨域指浏览器同源策略（协议/域名/端口不同）带来的请求限制\n2. 常见解决方法：JSONP、CORS（后端设置 Access-Control-Allow-Origin）\n3. 开发环境可使用代理（proxy）', '["跨域", "CORS", "JSONP", "同源策略"]', NOW()),
('前端', 'medium', '请解释 React 中的虚拟 DOM 及其优势', '1. 虚拟 DOM 是 JS 对象表示的 DOM 结构，轻量且可批量更新\n2. 通过 Diff 算法比较新旧虚拟 DOM，最小化真实 DOM 操作\n3. 优势：提高性能、跨平台（React Native）', '["React", "虚拟DOM", "Diff算法", "性能优化"]', NOW()),
('前端', 'hard', 'Vue 3 的响应式原理与 Vue 2 有何不同？', '1. Vue 2 使用 Object.defineProperty 劫持对象属性，存在数组/对象新增属性的监听问题\n2. Vue 3 使用 Proxy 实现响应式，可监听动态增删属性\n3. Vue 3 支持 Composition API，逻辑复用更方便', '["Vue", "Vue3", "响应式", "Proxy", "Composition API"]', NOW()),

('数据分析', 'medium', '请简述 A/B 测试的原理和实施步骤', '1. A/B 测试用于对比两个版本的效果（如转化率）\n2. 步骤：确定目标→随机分流用户→收集数据→显著性检验→决策\n3. 常用统计方法：假设检验、置信区间', '["A/B测试", "假设检验", "数据分析", "统计学"]', NOW()),
('数据分析', 'hard', '如何处理大规模数据中的缺失值？有哪些策略？', '1. 删除缺失值（如 row-wise deletion）\n2. 填补缺失值：均值/中位数/众数填补、回归预测、多重插补\n3. 使用模型预测缺失值（如 KNN、随机森林）\n4. 保留缺失标识（创建新特征）', '["数据清洗", "缺失值", "填补", "插补", "机器学习"]', NOW()),

('数据库', 'easy', 'SQL 中 WHERE 和 HAVING 的区别？', '1. WHERE 用于过滤行，在分组前执行\n2. HAVING 用于过滤分组，在 GROUP BY 后执行\n3. HAVING 常与聚合函数（SUM、AVG）一起使用', '["SQL", "WHERE", "HAVING", "分组", "聚合函数"]', NOW()),
('数据库', 'medium', 'MySQL 索引的底层数据结构是什么？各有什么优缺点？', '1. B+Tree（主键索引、普通索引的默认结构）支持范围查询，但维护成本高\n2. Hash：只有等值查询快，不支持范围查询\n3. Full-text：全文索引，用于文本搜索', '["MySQL", "索引", "B+Tree", "Hash", "全文索引", "性能优化"]', NOW()),
('数据库', 'hard', '如何设计高并发下的数据库架构？', '1. 读写分离（主从复制）\n2. 分库分表（水平拆分、垂直拆分）\n3. 缓存层（Redis）\n4. 使用消息队列削峰\n5. 数据库连接池优化', '["数据库", "高并发", "读写分离", "分库分表", "缓存", "消息队列", "连接池"]', NOW()),

('运维/Docker', 'medium', 'Docker 容器与虚拟机有什么区别？', '1. Docker 共享宿主机内核，启动快，资源开销小\n2. 虚拟机模拟完整操作系统，需要 Hypervisor，资源占用大\n3. Docker 适合微服务，便于分发和版本管理', '["Docker", "容器", "虚拟机", "虚拟化", "隔离"]', NOW()),
('运维/Kubernetes', 'medium', 'Kubernetes 的核心组件有哪些？各有什么作用？', '1. API Server：提供 REST API 接口\n2. etcd：存储集群状态数据\n3. Scheduler：负责 Pod 调度\n4. Controller Manager：管理控制器（ReplicaSet、Deployment）\n5. Kubelet：运行在节点上，管理 Pod 生命周期\n6. Kube-Proxy：网络代理，实现 Service', '["Kubernetes", "K8s", "API Server", "etcd", "Scheduler", "Kubelet", "Service"]', NOW()),
('运维/Kubernetes', 'hard', '如何排查 Kubernetes 集群中的 Pod 启动失败问题？', '1. 使用 kubectl describe pod 查看事件与状态\n2. 查看 Pod 日志：kubectl logs <pod-name>\n3. 检查节点资源（CPU/内存）是否充足\n4. 检查镜像是否存在、拉取策略是否正确\n5. 检查网络插件（CNI）是否正常', '["Kubernetes", "Pod", "troubleshooting", "kubectl", "日志"]', NOW()),

('AI/机器学习', 'easy', '什么是过拟合？如何防止过拟合？', '1. 过拟合指模型在训练集表现好，测试集表现差，泛化能力弱\n2. 防止方法：增加训练数据、正则化（L1/L2）、Dropout、早停（Early Stopping）、交叉验证', '["过拟合", "正则化", "Dropout", "早停", "泛化"]', NOW()),
('AI/机器学习', 'medium', '请解释梯度下降算法的原理和变种', '1. 梯度下降用于优化损失函数，通过求导沿负梯度方向更新参数\n2. 变种：BGD（全批量）、SGD（随机）、Mini-batch GD\n3. 优化器：Momentum、Adam、RMSprop', '["梯度下降", "SGD", "Adam", "优化器", "深度学习"]', NOW()),
('AI/机器学习', 'hard', '请说明 Transformer 模型的核心机制和优势', '1. 核心是自注意力机制（Self-Attention），并行计算全局依赖\n2. 采用位置编码（Positional Encoding）处理序列顺序\n3. 优势：长程依赖建模能力强，训练速度快（并行）\n4. 变体：BERT（双向）、GPT（自回归）', '["Transformer", "自注意力", "BERT", "GPT", "位置编码", "NLP"]', NOW()),

('计算机基础', 'medium', 'HTTP 和 HTTPS 的区别？', '1. HTTP 明文传输，HTTPS 通过 SSL/TLS 加密\n2. HTTPS 需要 CA 证书，默认端口 443\n3. HTTPS 更安全，但握手开销大，速度略慢', '["HTTP", "HTTPS", "SSL", "TLS", "网络协议"]', NOW()),
('计算机基础', 'easy', 'TCP 三次握手的过程是什么？', '1. 第一次握手：客户端发送 SYN 包\n2. 第二次握手：服务端回复 SYN+ACK\n3. 第三次握手：客户端回复 ACK，建立连接', '["TCP", "三次握手", "网络协议"]', NOW());