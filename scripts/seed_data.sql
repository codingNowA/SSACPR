-- =====================================================
-- 示例岗位数据（就业数据分析用）
-- =====================================================

INSERT INTO jobs (title, company, industry, location, salary_range, experience_required, education_required, description, requirements, job_profile, status, created_at, updated_at) VALUES

-- 互联网/IT 行业
('Java开发工程师', '阿里巴巴', '互联网', '杭州', '20k-35k', '3-5年', '本科', '负责电商平台后端系统开发与维护', '熟悉Java、Spring Boot、微服务架构', '{"skills": ["Java", "Spring Boot", "MySQL", "Redis", "微服务"], "job_type": "全职"}', 'active', NOW(), NOW()),
('前端开发工程师', '腾讯', '互联网', '深圳', '18k-30k', '3-5年', '本科', '负责微信小程序和Web前端开发', '熟悉React、Vue、TypeScript', '{"skills": ["React", "Vue", "TypeScript", "CSS", "Webpack"], "job_type": "全职"}', 'active', NOW(), NOW()),
('Python开发工程师', '字节跳动', '互联网', '北京', '25k-40k', '3-5年', '本科', '负责推荐系统后台开发', '熟悉Python、Django、数据处理', '{"skills": ["Python", "Django", "PostgreSQL", "Redis", "Kafka"], "job_type": "全职"}', 'active', NOW(), NOW()),
('数据分析师', '美团', '互联网', '北京', '15k-25k', '1-3年', '本科', '负责业务数据分析与可视化', '熟悉SQL、Python、数据可视化工具', '{"skills": ["SQL", "Python", "Pandas", "Tableau", "数据可视化"], "job_type": "全职"}', 'active', NOW(), NOW()),
('算法工程师', '百度', '互联网', '北京', '30k-50k', '3-5年', '硕士', '负责搜索推荐算法研发', '熟悉机器学习、深度学习、Python', '{"skills": ["Python", "TensorFlow", "PyTorch", "机器学习", "推荐算法"], "job_type": "全职"}', 'active', NOW(), NOW()),
('Go开发工程师', '滴滴出行', '互联网', '北京', '20k-35k', '3-5年', '本科', '负责高并发后端服务开发', '熟悉Go、微服务、分布式系统', '{"skills": ["Go", "gRPC", "MySQL", "Redis", "分布式系统"], "job_type": "全职"}', 'active', NOW(), NOW()),
('测试开发工程师', '华为', '互联网', '深圳', '15k-25k', '1-3年', '本科', '负责自动化测试框架开发', '熟悉Python、自动化测试、CI/CD', '{"skills": ["Python", "Selenium", "Jenkins", "自动化测试", "Shell"], "job_type": "全职"}', 'active', NOW(), NOW()),
('运维工程师', '网易', '互联网', '杭州', '12k-20k', '1-3年', '本科', '负责云平台运维与监控', '熟悉Linux、Docker、Kubernetes', '{"skills": ["Linux", "Docker", "Kubernetes", "Shell", "监控"], "job_type": "全职"}', 'active', NOW(), NOW()),

-- 金融/咨询行业
('金融分析师', '中信证券', '金融', '上海', '25k-40k', '3-5年', '硕士', '负责行业研究与投资分析', '熟悉财务分析、估值建模、Wind', '{"skills": ["财务分析", "估值建模", "Excel", "Wind", "研究报告"], "job_type": "全职"}', 'active', NOW(), NOW()),
('量化研究员', '中金公司', '金融', '北京', '30k-50k', '3-5年', '硕士', '负责量化交易策略研发', '熟悉Python、金融工程、统计分析', '{"skills": ["Python", "量化交易", "金融工程", "统计分析", "机器学习"], "job_type": "全职"}', 'active', NOW(), NOW()),

-- 制造业
('机械设计工程师', '三一重工', '制造业', '长沙', '10k-18k', '3-5年', '本科', '负责工程机械产品设计', '熟悉CAD、SolidWorks、机械原理', '{"skills": ["CAD", "SolidWorks", "机械设计", "材料力学", "Pro/E"], "job_type": "全职"}', 'active', NOW(), NOW()),
('自动化工程师', '格力电器', '制造业', '珠海', '8k-15k', '1-3年', '本科', '负责PLC控制系统设计', '熟悉PLC、自动化控制、电气设计', '{"skills": ["PLC", "自动化控制", "电气设计", "SCADA", "工业机器人"], "job_type": "全职"}', 'active', NOW(), NOW()),

-- 教育行业
('学科教研员', '新东方', '教育', '北京', '12k-20k', '3-5年', '硕士', '负责课程研发与教学研究', '熟悉教育学、课程设计、教材编写', '{"skills": ["教育学", "课程设计", "教材编写", "教学研究", "项目管理"], "job_type": "全职"}', 'active', NOW(), NOW()),
('在线教育产品经理', '好未来', '教育', '北京', '15k-25k', '3-5年', '本科', '负责在线教育产品规划', '熟悉产品设计、用户研究、数据分析', '{"skills": ["产品设计", "用户研究", "数据分析", "项目管理", "教育产品"], "job_type": "全职"}', 'active', NOW(), NOW()),

-- 医疗健康
('临床数据管理员', '药明康德', '医疗', '上海', '15k-25k', '3-5年', '本科', '负责临床试验数据管理', '熟悉临床数据管理、SAS、CDISC', '{"skills": ["临床数据", "SAS", "CDISC", "SQL", "药理学"], "job_type": "全职"}', 'active', NOW(), NOW()),
('医疗器械研发工程师', '迈瑞医疗', '医疗', '深圳', '18k-30k', '3-5年', '硕士', '负责医疗器械设计与研发', '熟悉生物医学工程、医疗器械法规', '{"skills": ["生物医学工程", "医疗器械", "ISO13485", "SolidWorks", "电路设计"], "job_type": "全职"}', 'active', NOW(), NOW()),

-- 更多互联网岗位
('产品经理', '小米', '互联网', '北京', '20k-35k', '3-5年', '本科', '负责手机产品规划与设计', '熟悉产品设计、用户需求分析', '{"skills": ["产品设计", "用户研究", "数据分析", "项目管理", "UI/UX"], "job_type": "全职"}', 'active', NOW(), NOW()),
('UI/UX设计师', '字节跳动', '互联网', '上海', '15k-28k', '3-5年', '本科', '负责产品界面与交互设计', '熟悉Figma、UI设计、用户体验', '{"skills": ["Figma", "UI设计", "UX设计", "Sketch", "设计系统"], "job_type": "全职"}', 'active', NOW(), NOW()),
('Android开发工程师', 'OPPO', '互联网', '深圳', '18k-30k', '3-5年', '本科', '负责Android系统应用开发', '熟悉Java、Kotlin、Android SDK', '{"skills": ["Java", "Kotlin", "Android SDK", "Gradle", "MVP/MVVM"], "job_type": "全职"}', 'active', NOW(), NOW()),
('iOS开发工程师', 'vivo', '互联网', '深圳', '18k-30k', '3-5年', '本科', '负责iOS应用开发', '熟悉Swift、Objective-C、iOS SDK', '{"skills": ["Swift", "Objective-C", "iOS SDK", "CocoaPods", "MVVM"], "job_type": "全职"}', 'active', NOW(), NOW()),

-- 上海地区岗位
('Flink工程师', '携程', '互联网', '上海', '20k-35k', '3-5年', '本科', '负责实时计算平台开发', '熟悉Flink、Kafka、实时数据处理', '{"skills": ["Flink", "Kafka", "Java", "实时计算", "大数据"], "job_type": "全职"}', 'active', NOW(), NOW()),
('Spark工程师', '哔哩哔哩', '互联网', '上海', '20k-35k', '3-5年', '本科', '负责大数据处理与分析平台', '熟悉Spark、Hive、数据仓库', '{"skills": ["Spark", "Hive", "Scala", "数据仓库", "SQL"], "job_type": "全职"}', 'active', NOW(), NOW()),
('全栈开发工程师', '京东', '互联网', '北京', '20k-35k', '3-5年', '本科', '负责电商平台前后端开发', '熟悉Java、React、微服务', '{"skills": ["Java", "React", "Spring Boot", "MySQL", "Redis"], "job_type": "全职"}', 'active', NOW(), NOW());