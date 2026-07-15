-- SSACPR 岗位测试数据
-- 执行方式: docker cp scripts\seed_jobs.sql career-postgres:/tmp/seed_jobs.sql && docker-compose exec -T postgres psql -U career_user -d career_planning -f /tmp/seed_jobs.sql
-- 清理方式: DELETE FROM jobs WHERE source = 'seed_test';

-- 先清理旧测试数据
DELETE FROM jobs WHERE source = 'seed_test';

-- 互联网/软件
INSERT INTO jobs (title, company, industry, location, salary_range, experience_required, education_required, description, requirements, job_profile, company_type, source) VALUES
('Python后端开发工程师', '字节跳动', '互联网', '北京', '20K-35K', '1-3年', '本科',
 '负责公司核心业务后端系统设计与开发，参与高并发场景下的服务架构优化。',
 '精通Python语言，熟悉FastAPI/Django/Flask框架；熟悉PostgreSQL/MySQL数据库；了解Redis、消息队列等中间件；有微服务架构经验优先。',
 '{"skills": ["Python", "FastAPI", "Django", "PostgreSQL", "Redis", "Docker", "Kubernetes", "微服务"]}'::jsonb, '民营', 'seed_test'),

('前端开发工程师', '腾讯科技', '互联网', '深圳', '18K-30K', '1-3年', '本科',
 '负责腾讯云控制台前端开发，使用React技术栈构建高性能Web应用。',
 '精通JavaScript/TypeScript；熟练使用React/Vue框架；熟悉Webpack/Vite构建工具；了解HTML/CSS/Sass；有前端工程化经验。',
 '{"skills": ["JavaScript", "TypeScript", "React", "Vue", "Webpack", "Vite", "HTML", "CSS", "Sass"]}'::jsonb, '民营', 'seed_test'),

('全栈开发工程师', '阿里巴巴', '互联网', '杭州', '25K-40K', '3-5年', '本科',
 '负责阿里云数据平台全栈开发，涵盖前端可视化与后端数据处理服务。',
 '精通Python和JavaScript；熟悉React前端框架和Flask后端框架；熟悉MySQL、Redis、MongoDB；有大数据处理经验优先。',
 '{"skills": ["Python", "JavaScript", "React", "Flask", "MySQL", "Redis", "MongoDB", "Hadoop", "Spark"]}'::jsonb, '民营', 'seed_test'),

('Java高级开发工程师', '美团', '互联网', '北京', '25K-45K', '3-5年', '本科',
 '负责美团外卖核心交易系统开发，保障高可用、高并发场景下的系统稳定性。',
 '精通Java语言，深入理解Spring/SpringBoot框架；熟悉MySQL/PostgreSQL数据库；熟悉Kafka消息队列；有分布式系统设计经验。',
 '{"skills": ["Java", "Spring", "SpringBoot", "MySQL", "PostgreSQL", "Kafka", "分布式", "微服务", "Redis"]}'::jsonb, '民营', 'seed_test'),

('DevOps工程师', '华为技术', '互联网', '成都', '18K-28K', '1-3年', '本科',
 '负责华为云CI/CD流水线建设与维护，推动容器化部署与自动化运维。',
 '熟悉Linux操作系统；精通Docker/Kubernetes容器技术；熟悉Jenkins/GitHub Actions CI/CD工具；了解Terraform基础设施编排。',
 '{"skills": ["Docker", "Kubernetes", "K8s", "Linux", "Jenkins", "CI/CD", "Terraform", "Nginx", "Git"]}'::jsonb, '民营', 'seed_test'),

-- 金融
('量化研究员', '中信证券', '金融', '上海', '30K-50K', '1-3年', '硕士',
 '开展量化策略研究与回测，开发alpha因子模型，优化交易信号。',
 '精通Python数据分析（Pandas/NumPy）；了解机器学习算法（Scikit-learn）；熟悉SQL数据库查询；有统计学或数学建模背景。',
 '{"skills": ["Python", "Pandas", "NumPy", "Scikit-learn", "SQL", "Machine Learning", "MATLAB", "R"]}'::jsonb, '国企', 'seed_test'),

('数据分析师', '招商银行', '金融', '深圳', '15K-25K', '应届', '本科',
 '负责银行零售业务数据分析，搭建数据报表体系，提供业务决策支持。',
 '熟练使用SQL查询；熟悉Python数据分析工具；了解Tableau/Power BI可视化工具；有统计学基础。',
 '{"skills": ["SQL", "Python", "Pandas", "Excel", "Power BI", "Tableau"]}'::jsonb, '国企', 'seed_test'),

-- 外企
('Software Engineer (Backend)', 'Microsoft', '互联网', '上海', '30K-55K', '1-3年', '本科',
 'Join the Azure Cloud team to build scalable backend services powering millions of users worldwide.',
 'Proficient in Python or Go; experience with PostgreSQL/Redis; familiar with Docker/Kubernetes; understanding of distributed systems and microservices.',
 '{"skills": ["Python", "Go", "Golang", "PostgreSQL", "Redis", "Docker", "Kubernetes", "分布式", "微服务", "Azure"]}'::jsonb, '外企', 'seed_test'),

('Machine Learning Engineer', 'Google', '互联网', '北京', '40K-70K', '3-5年', '硕士',
 'Build and deploy large-scale ML models for search ranking and recommendation systems.',
 'Strong Python skills; deep experience with TensorFlow/PyTorch; understanding of NLP and Deep Learning; familiar with Spark/Hadoop for distributed training.',
 '{"skills": ["Python", "TensorFlow", "PyTorch", "NLP", "Deep Learning", "Machine Learning", "Spark", "Hadoop", "Kubernetes"]}'::jsonb, '外企', 'seed_test'),

-- 教育
('教育产品开发经理', '好未来', '教育', '北京', '15K-25K', '1-3年', '本科',
 '负责K12在线教育产品设计，协调研发团队推进产品迭代。',
 '熟悉教育行业；了解Python/SQL数据分析；有产品管理经验；良好的沟通协调能力。',
 '{"skills": ["Python", "SQL", "Excel", "Agile", "Scrum"]}'::jsonb, '民营', 'seed_test'),

-- 国企/通信
('系统运维工程师', '中国电信', '通信', '成都', '8K-15K', '应届', '本科',
 '负责核心业务系统日常运维，监控系统稳定性，处理故障告警。',
 '熟悉Linux操作系统；了解Python/Shell脚本编程；了解Nginx/Tomcat等中间件；有网络基础知识。',
 '{"skills": ["Linux", "Python", "Nginx", "Tomcat", "Docker", "Git"]}'::jsonb, '国企', 'seed_test'),

('大数据开发工程师', '中国移动', '通信', '北京', '15K-25K', '1-3年', '本科',
 '参与大数据平台开发与维护，负责数据ETL流程设计与优化。',
 '熟悉Hadoop/Spark/Hive大数据生态；掌握Python/Java编程；了解Kafka消息队列；有数据仓库经验优先。',
 '{"skills": ["Hadoop", "Spark", "Hive", "Kafka", "Python", "Java", "SQL", "Airflow"]}'::jsonb, '国企', 'seed_test'),

-- 不同薪资区间
('初级Python开发', '创业公司A', '互联网', '成都', '6K-10K', '应届', '本科',
 '参与公司SaaS产品后端开发，学习并实践FastAPI+PostgreSQL技术栈。',
 '了解Python编程；了解基本数据库操作；有学习意愿；了解Git基本操作。',
 '{"skills": ["Python", "FastAPI", "PostgreSQL", "Git", "REST"]}'::jsonb, '民营', 'seed_test'),

('技术总监', '某独角兽企业', '互联网', '北京', '50K-80K', '5-10年', '硕士',
 '全面负责技术团队管理与架构决策，推动技术创新与业务发展。',
 '深入理解分布式系统/微服务架构；精通Python/Java/Go多种语言；熟悉云原生技术栈；有团队管理经验。',
 '{"skills": ["Python", "Java", "Go", "Kubernetes", "分布式", "微服务", "AWS", "设计模式", "Agile"]}'::jsonb, '民营', 'seed_test'),

-- 不同城市
('Go后端开发工程师', 'B站', '互联网', '上海', '20K-35K', '1-3年', '本科',
 '负责B站视频处理服务后端开发，使用Go语言构建高性能API。',
 '精通Go语言；熟悉Gin/Echo框架；了解MySQL/Redis；熟悉Docker/K8s容器化部署。',
 '{"skills": ["Go", "Golang", "MySQL", "Redis", "Docker", "Kubernetes", "微服务", "gRPC"]}'::jsonb, '民营', 'seed_test'),

('数据工程师', '京东', '互联网', '北京', '20K-35K', '1-3年', '本科',
 '负责京东物流数据平台开发，构建实时数据处理流水线。',
 '精通Python/Java；熟悉Spark/Flink流批处理；了解Kafka消息队列；熟悉数据仓库建模。',
 '{"skills": ["Python", "Java", "Spark", "Flink", "Kafka", "Hive", "Airflow", "SQL"]}'::jsonb, '民营', 'seed_test'),

-- 其他行业
('医疗AI算法工程师', '联影智能', '医疗', '上海', '25K-45K', '1-3年', '硕士',
 '从事医学影像AI算法研发，开发基于深度学习的辅助诊断系统。',
 '精通Python；熟悉PyTorch/TensorFlow深度学习框架；了解计算机视觉和医学影像处理；有论文发表经验优先。',
 '{"skills": ["Python", "PyTorch", "TensorFlow", "Computer Vision", "Deep Learning", "NumPy", "Pandas"]}'::jsonb, '民营', 'seed_test'),

('网络安全工程师', '奇安信', '安全', '成都', '15K-25K', '1-3年', '本科',
 '负责企业安全产品研发，开发入侵检测与防御系统。',
 '熟悉Python/Go编程；了解网络协议与安全攻防；熟悉Linux系统；有渗透测试经验优先。',
 '{"skills": ["Python", "Go", "Linux", "计算机网络", "Docker", "Nginx"]}'::jsonb, '民营', 'seed_test'),

('嵌入式软件工程师', '大疆创新', '硬件', '深圳', '18K-30K', '1-3年', '本科',
 '负责无人机飞控系统嵌入式软件开发，优化实时控制算法。',
 '精通C/C++语言；了解RTOS操作系统；熟悉Linux嵌入式开发；了解传感器与控制算法。',
 '{"skills": ["C++", "Linux", "算法", "数据结构", "操作系统"]}'::jsonb, '民营', 'seed_test'),

('产品经理（技术方向）', '网易', '互联网', '杭州', '20K-35K', '3-5年', '本科',
 '负责网易云音乐技术产品规划，推动AI推荐策略落地。',
 '熟悉Python/SQL数据分析；了解机器学习/NLP基本概念；有互联网产品经验；良好的数据分析能力。',
 '{"skills": ["Python", "SQL", "Excel", "Tableau", "Machine Learning", "Agile"]}'::jsonb, '民营', 'seed_test');
