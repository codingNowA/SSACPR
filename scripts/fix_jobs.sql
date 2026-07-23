-- 更新 industry
UPDATE jobs SET industry = CASE
  WHEN id IN (1,3,4,5,6,7,8,17,18,19,20,21,22) THEN '互联网'
  WHEN id IN (9,10) THEN '金融'
  WHEN id IN (11,12) THEN '制造业'
  WHEN id IN (13,14) THEN '教育'
  WHEN id IN (15,16) THEN '医疗'
  ELSE industry
END;

-- 更新 job_profile（直接设置 skills 数组，不需要外层大括号）
UPDATE jobs SET job_profile = CASE
  WHEN id = 1 THEN '["Java", "Spring Boot", "MySQL", "Redis", "微服务"]'::jsonb
  WHEN id = 3 THEN '["Python", "Django", "PostgreSQL", "Redis", "Kafka"]'::jsonb
  WHEN id = 4 THEN '["SQL", "Python", "Pandas", "Tableau", "数据可视化"]'::jsonb
  WHEN id = 5 THEN '["Python", "TensorFlow", "PyTorch", "机器学习", "推荐算法"]'::jsonb
  WHEN id = 17 THEN '["产品设计", "用户研究", "数据分析", "项目管理", "UI/UX"]'::jsonb
  WHEN id = 21 THEN '["Flink", "Kafka", "Java", "实时计算", "大数据"]'::jsonb
  ELSE job_profile
END;