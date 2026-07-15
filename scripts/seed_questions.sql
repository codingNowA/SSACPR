-- =====================================================
-- 示例面试题数据（题库管理用）
-- =====================================================

INSERT INTO interview_questions (category, difficulty, question, answer_points, related_skills, created_at) VALUES
('Java', 'medium', '请说明 Java 中 HashMap 和 Hashtable 的区别', '1. 线程安全性不同\n2. 是否允许 null key/value\n3. 继承的父类不同\n4. 扩容机制不同', '["Java", "HashMap", "Hashtable"]', NOW()),
('Java', 'hard', '请描述 Spring Boot 自动配置原理', '1. @EnableAutoConfiguration 注解\n2. spring.factories 文件\n3. Conditional 条件注解', '["Spring Boot", "自动配置", "Conditional"]', NOW()),
('Python', 'easy', 'Python 中的列表和元组有什么区别？', '1. 列表可变，元组不可变\n2. 列表有更多方法\n3. 元组内存占用更小', '["Python", "列表", "元组"]', NOW()),
('Python', 'medium', '解释 Python 的 GIL 是什么？', 'GIL 是全局解释器锁，限制同一时刻只能有一个线程执行 Python 字节码', '["Python", "GIL", "多线程"]', NOW()),
('数据分析', 'easy', '什么是数据清洗？', '数据清洗是数据预处理的重要步骤，包括处理缺失值、异常值、重复数据、格式统一等', '["数据分析", "数据清洗", "预处理"]', NOW()),
('数据分析', 'medium', '请说明 SQL 中 JOIN 和 UNION 的区别', 'JOIN 用于横向合并（添加列），UNION 用于纵向合并（添加行）', '["SQL", "JOIN", "UNION"]', NOW());