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
 '{"skills": ["Python", "SQL", "Excel", "Tableau", "Machine Learning", "Agile"]}'::jsonb, '民营', 'seed_test'),

-- =====================================================
-- 新增岗位数据（涵盖更多行业、分布、薪资区间）
-- =====================================================

-- ----- 互联网 / 技术 -----
('Java微服务开发工程师', '京东科技', '互联网', '北京', '22K-38K', '3-5年', '本科',
 '负责京东金融微服务架构设计与核心模块开发，支持亿级用户高并发场景。',
 '精通Java、Spring Cloud；熟悉Docker/K8s；有分布式事务、服务治理经验。',
 '{"skills": ["Java", "Spring Cloud", "Docker", "Kubernetes", "Redis", "Kafka", "分布式"]}'::jsonb, '民营', 'seed_test'),

('React Native移动开发工程师', '滴滴出行', '互联网', '杭州', '18K-30K', '1-3年', '本科',
 '负责滴滴出行App的React Native跨平台开发，提升用户交互体验。',
 '精通JavaScript/TypeScript；熟悉React Native框架；了解原生iOS/Android开发基础。',
 '{"skills": ["JavaScript", "TypeScript", "React Native", "iOS", "Android"]}'::jsonb, '民营', 'seed_test'),

('数据库管理员(DBA)', '携程旅行', '互联网', '上海', '20K-35K', '3-5年', '本科',
 '负责携程数据库集群运维、性能调优、备份恢复和高可用架构设计。',
 '精通MySQL/PostgreSQL；熟悉Redis/MongoDB；有数据库分库分表、读写分离经验。',
 '{"skills": ["MySQL", "PostgreSQL", "Redis", "MongoDB", "分库分表", "读写分离"]}'::jsonb, '民营', 'seed_test'),

('NLP算法工程师', '字节跳动', '互联网', '北京', '35K-60K', '1-3年', '硕士',
 '负责抖音内容理解与推荐算法中的NLP模型研发，提升内容质量与用户粘性。',
 '精通Python；熟悉PyTorch/TensorFlow；有NLP/深度学习经验；了解Transformer、BERT等模型。',
 '{"skills": ["Python", "PyTorch", "TensorFlow", "NLP", "深度学习", "Transformer", "BERT"]}'::jsonb, '民营', 'seed_test'),

('运维开发工程师(DevOps)', '美团', '互联网', '北京', '20K-32K', '1-3年', '本科',
 '负责美团内部CI/CD流水线设计与优化，推动云原生架构落地。',
 '熟悉Linux/Shell/Python；精通Docker/K8s；有Jenkins/GitLab CI经验。',
 '{"skills": ["Linux", "Python", "Docker", "Kubernetes", "Jenkins", "CI/CD", "Git"]}'::jsonb, '民营', 'seed_test'),

('音视频开发工程师', '腾讯', '互联网', '深圳', '25K-45K', '3-5年', '本科',
 '负责腾讯会议音视频引擎开发，优化实时通信质量与性能。',
 '精通C++/Java；熟悉WebRTC/FFmpeg；了解音视频编解码、网络传输协议。',
 '{"skills": ["C++", "Java", "WebRTC", "FFmpeg", "音视频编解码", "网络协议"]}'::jsonb, '民营', 'seed_test'),

('区块链开发工程师', '蚂蚁集团', '互联网', '杭州', '30K-55K', '1-3年', '本科',
 '参与蚂蚁链底层平台开发，构建高性能、安全的区块链基础设施。',
 '精通Go/Rust；了解区块链原理（共识算法、智能合约）；有Hyperledger/Ethereum经验优先。',
 '{"skills": ["Go", "Rust", "区块链", "共识算法", "智能合约", "Hyperledger", "Ethereum"]}'::jsonb, '民营', 'seed_test'),

('AI训练平台开发工程师', '商汤科技', '互联网', '北京', '28K-50K', '3-5年', '硕士',
 '研发大规模AI训练平台，支持分布式训练、模型管理与部署。',
 '精通Python/Go；熟悉Kubernetes；了解分布式训练框架（Horovod/DeepSpeed）。',
 '{"skills": ["Python", "Go", "Kubernetes", "分布式训练", "Horovod", "DeepSpeed"]}'::jsonb, '民营', 'seed_test'),

('前端架构师', '百度', '互联网', '北京', '40K-70K', '5-10年', '本科',
 '负责百度搜索前端架构设计，优化首屏加载性能与代码可维护性。',
 '精通JavaScript/TypeScript；深入掌握React/Vue源码；有前端工程化、微前端经验。',
 '{"skills": ["JavaScript", "TypeScript", "React", "Vue", "Webpack", "微前端", "性能优化"]}'::jsonb, '民营', 'seed_test'),

('测试开发工程师', '华为', '互联网', '成都', '15K-25K', '1-3年', '本科',
 '负责华为云测试框架开发，实现自动化测试与质量分析。',
 '熟悉Python/Java；了解Selenium/Appium；有CI/CD集成经验。',
 '{"skills": ["Python", "Java", "Selenium", "Appium", "CI/CD", "自动化测试"]}'::jsonb, '民营', 'seed_test'),

-- ----- 金融 / 风控 -----
('风控策略分析师', '平安科技', '金融', '上海', '20K-35K', '1-3年', '硕士',
 '设计并优化信贷风控策略，建立风险模型与评分卡。',
 '精通Python/R；熟悉SQL；了解逻辑回归、决策树等建模方法；有金融行业背景优先。',
 '{"skills": ["Python", "R", "SQL", "逻辑回归", "决策树", "评分卡"]}'::jsonb, '民营', 'seed_test'),

('量化交易开发工程师', '九坤投资', '金融', '北京', '30K-60K', '1-3年', '硕士',
 '开发高频交易系统，实现低延迟数据接收与订单执行。',
 '精通C++/Python；熟悉网络编程与多线程；了解金融市场数据结构。',
 '{"skills": ["C++", "Python", "网络编程", "多线程", "低延迟", "高频交易"]}'::jsonb, '民营', 'seed_test'),

-- ----- 教育 -----
('在线教育课程产品经理', '猿辅导', '教育', '北京', '18K-30K', '3-5年', '本科',
 '负责猿辅导课程产品规划，设计用户体验路径，推动课程迭代。',
 '熟悉教育行业；了解数据分析；有产品设计或运营经验。',
 '{"skills": ["产品设计", "数据分析", "项目管理", "教育"]}'::jsonb, '民营', 'seed_test'),

-- ----- 医疗健康 -----
('医疗数据工程师', '微医集团', '医疗', '杭州', '15K-28K', '1-3年', '本科',
 '构建医疗大数据平台，整合病历数据与健康档案，支持临床决策。',
 '熟悉Python/Java；了解Hadoop/Spark；有医疗数据处理经验优先。',
 '{"skills": ["Python", "Java", "Hadoop", "Spark", "医疗数据", "ETL"]}'::jsonb, '民营', 'seed_test'),

('生物信息分析工程师', '华大基因', '医疗', '深圳', '20K-35K', '1-3年', '硕士',
 '分析基因组学数据，构建基因检测与疾病关联分析流程。',
 '精通Python/R；熟悉生物信息学工具（BWA/GATK）；了解统计学与机器学习。',
 '{"skills": ["Python", "R", "生物信息", "BWA", "GATK", "机器学习"]}'::jsonb, '民营', 'seed_test'),

-- ----- 制造业 / 硬件 -----
('工业机器人算法工程师', '新松机器人', '制造业', '沈阳', '18K-30K', '1-3年', '本科',
 '研发工业机器人运动规划与视觉引导算法，提升自动化生产效率。',
 '精通C++/Python；熟悉ROS；了解计算机视觉与路径规划。',
 '{"skills": ["C++", "Python", "ROS", "计算机视觉", "路径规划"]}'::jsonb, '民营', 'seed_test'),

('FPGA开发工程师', '海康威视', '硬件', '杭州', '18K-30K', '1-3年', '本科',
 '负责安防监控产品FPGA逻辑开发与验证，优化视频处理性能。',
 '精通Verilog/VHDL；熟悉Xilinx/Altera平台；了解数字信号处理。',
 '{"skills": ["Verilog", "VHDL", "FPGA", "数字信号处理", "Xilinx"]}'::jsonb, '民营', 'seed_test'),

-- ----- 通信 / 运营商 -----
('5G核心网开发工程师', '中兴通讯', '通信', '北京', '15K-28K', '1-3年', '本科',
 '参与5G核心网产品开发，负责网络功能虚拟化与协议栈实现。',
 '精通C/C++；了解TCP/IP/3GPP协议；熟悉Linux网络编程。',
 '{"skills": ["C++", "C", "TCP/IP", "3GPP", "Linux", "网络编程"]}'::jsonb, '国企', 'seed_test'),

-- ----- 国企 / 能源 -----
('能源数据分析师', '国家电网', '能源', '北京', '12K-20K', '应届', '本科',
 '分析电力负荷数据，辅助能源调度与规划决策。',
 '熟练使用Python/SQL；了解机器学习基础；有数据可视化能力。',
 '{"skills": ["Python", "SQL", "Pandas", "机器学习", "数据可视化"]}'::jsonb, '国企', 'seed_test'),

-- ----- 外企 -----
('Site Reliability Engineer (SRE)', 'Google', '互联网', '北京', '40K-70K', '3-5年', '本科',
 'Ensure reliability and performance of Google''s cloud services through automation and system engineering.',
 'Proficient in Python/Go; deep understanding of Linux systems; experience with Kubernetes and monitoring tools (Prometheus).',
 '{"skills": ["Python", "Go", "Linux", "Kubernetes", "Prometheus", "SRE"]}'::jsonb, '外企', 'seed_test'),

('Data Scientist', 'Amazon', '互联网', '上海', '35K-60K', '3-5年', '硕士',
 'Develop machine learning models for demand forecasting and supply chain optimization.',
 'Strong Python/R skills; experience with Spark; knowledge of time series analysis and causal inference.',
 '{"skills": ["Python", "R", "Spark", "时间序列", "因果推断", "机器学习"]}'::jsonb, '外企', 'seed_test'),

-- ----- 创业公司 / 新兴领域 -----
('AI绘画算法工程师', '某AI创业公司', '互联网', '深圳', '25K-50K', '1-3年', '硕士',
 '研发基于扩散模型的AI绘画生成算法，优化图像生成效果与速度。',
 '精通Python/PyTorch；熟悉Diffusion Models；有计算机视觉和生成式AI经验。',
 '{"skills": ["Python", "PyTorch", "扩散模型", "计算机视觉", "生成式AI"]}'::jsonb, '民营', 'seed_test'),

('Web3产品经理', 'Web3创业团队', '互联网', '远程', '20K-40K', '3-5年', '本科',
 '负责Web3钱包和DeFi产品规划，设计用户体验并推动开发。',
 '熟悉区块链基础知识；了解DeFi/NFT赛道；有产品管理经验。',
 '{"skills": ["区块链", "DeFi", "NFT", "产品设计", "项目管理"]}'::jsonb, '民营', 'seed_test'),

('自动驾驶感知算法工程师', '小鹏汽车', '制造业', '广州', '30K-60K', '3-5年', '硕士',
 '负责自动驾驶感知算法研发，包括目标检测、语义分割、多传感器融合。',
 '精通C++/Python；熟悉深度学习框架（PyTorch/TensorFlow）；有计算机视觉、点云处理经验。',
 '{"skills": ["C++", "Python", "PyTorch", "TensorFlow", "计算机视觉", "点云", "传感器融合"]}'::jsonb, '民营', 'seed_test'),

('云原生架构师', '阿里云', '互联网', '杭州', '45K-80K', '5-10年', '本科',
 '设计并落地云原生架构解决方案，推动企业客户业务上云。',
 '精通Kubernetes/Service Mesh；熟悉AWS/Azure/阿里云；有微服务治理、CI/CD经验。',
 '{"skills": ["Kubernetes", "Service Mesh", "AWS", "Azure", "微服务", "CI/CD"]}'::jsonb, '民营', 'seed_test');
