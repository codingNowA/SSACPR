"""
SSACPR 岗位测试数据种子脚本
生成覆盖多种行业、城市、薪资、公司性质的岗位数据，用于岗位精准匹配测试。
"""
import asyncio
import asyncpg
import json
import os
from dotenv import load_dotenv

load_dotenv()

JOBS = [
    # --- 互联网/软件 ---
    {
        "title": "Python后端开发工程师",
        "company": "字节跳动",
        "industry": "互联网",
        "location": "北京",
        "salary_range": "20K-35K",
        "experience_required": "1-3年",
        "education_required": "本科",
        "description": "负责公司核心业务后端系统设计与开发，参与高并发场景下的服务架构优化。",
        "requirements": "精通Python语言，熟悉FastAPI/Django/Flask框架；熟悉PostgreSQL/MySQL数据库；了解Redis、消息队列等中间件；有微服务架构经验优先。",
        "skills": ["Python", "FastAPI", "Django", "PostgreSQL", "Redis", "Docker", "Kubernetes", "微服务"],
        "company_type": "民营",
    },
    {
        "title": "前端开发工程师",
        "company": "腾讯科技",
        "industry": "互联网",
        "location": "深圳",
        "salary_range": "18K-30K",
        "experience_required": "1-3年",
        "education_required": "本科",
        "description": "负责腾讯云控制台前端开发，使用React技术栈构建高性能Web应用。",
        "requirements": "精通JavaScript/TypeScript；熟练使用React/Vue框架；熟悉Webpack/Vite构建工具；了解HTML/CSS/Sass；有前端工程化经验。",
        "skills": ["JavaScript", "TypeScript", "React", "Vue", "Webpack", "Vite", "HTML", "CSS", "Sass"],
        "company_type": "民营",
    },
    {
        "title": "全栈开发工程师",
        "company": "阿里巴巴",
        "industry": "互联网",
        "location": "杭州",
        "salary_range": "25K-40K",
        "experience_required": "3-5年",
        "education_required": "本科",
        "description": "负责阿里云数据平台全栈开发，涵盖前端可视化与后端数据处理服务。",
        "requirements": "精通Python和JavaScript；熟悉React前端框架和Flask后端框架；熟悉MySQL、Redis、MongoDB；有大数据处理经验优先。",
        "skills": ["Python", "JavaScript", "React", "Flask", "MySQL", "Redis", "MongoDB", "Hadoop", "Spark"],
        "company_type": "民营",
    },
    {
        "title": "Java高级开发工程师",
        "company": "美团",
        "industry": "互联网",
        "location": "北京",
        "salary_range": "25K-45K",
        "experience_required": "3-5年",
        "education_required": "本科",
        "description": "负责美团外卖核心交易系统开发，保障高可用、高并发场景下的系统稳定性。",
        "requirements": "精通Java语言，深入理解Spring/SpringBoot框架；熟悉MySQL/PostgreSQL数据库；熟悉Kafka消息队列；有分布式系统设计经验。",
        "skills": ["Java", "Spring", "SpringBoot", "MySQL", "PostgreSQL", "Kafka", "分布式", "微服务", "Redis"],
        "company_type": "民营",
    },
    {
        "title": "DevOps工程师",
        "company": "华为技术",
        "industry": "互联网",
        "location": "成都",
        "salary_range": "18K-28K",
        "experience_required": "1-3年",
        "education_required": "本科",
        "description": "负责华为云CI/CD流水线建设与维护，推动容器化部署与自动化运维。",
        "requirements": "熟悉Linux操作系统；精通Docker/Kubernetes容器技术；熟悉Jenkins/GitHub Actions CI/CD工具；了解Terraform基础设施编排。",
        "skills": ["Docker", "Kubernetes", "K8s", "Linux", "Jenkins", "CI/CD", "Terraform", "Nginx", "Git"],
        "company_type": "民营",
    },
    # --- 金融 ---
    {
        "title": "量化研究员",
        "company": "中信证券",
        "industry": "金融",
        "location": "上海",
        "salary_range": "30K-50K",
        "experience_required": "1-3年",
        "education_required": "硕士",
        "description": "开展量化策略研究与回测，开发 alpha 因子模型，优化交易信号。",
        "requirements": "精通Python数据分析（Pandas/NumPy）；了解机器学习算法（Scikit-learn）；熟悉SQL数据库查询；有统计学或数学建模背景。",
        "skills": ["Python", "Pandas", "NumPy", "Scikit-learn", "SQL", "Machine Learning", "MATLAB", "R"],
        "company_type": "国企",
    },
    {
        "title": "数据分析师",
        "company": "招商银行",
        "industry": "金融",
        "location": "深圳",
        "salary_range": "15K-25K",
        "experience_required": "应届",
        "education_required": "本科",
        "description": "负责银行零售业务数据分析，搭建数据报表体系，提供业务决策支持。",
        "requirements": "熟练使用SQL查询；熟悉Python数据分析工具；了解Tableau/Power BI可视化工具；有统计学基础。",
        "skills": ["SQL", "Python", "Pandas", "Excel", "Power BI", "Tableau"],
        "company_type": "国企",
    },
    # --- 外企 ---
    {
        "title": "Software Engineer (Backend)",
        "company": "Microsoft",
        "industry": "互联网",
        "location": "上海",
        "salary_range": "30K-55K",
        "experience_required": "1-3年",
        "education_required": "本科",
        "description": "Join the Azure Cloud team to build scalable backend services powering millions of users worldwide.",
        "requirements": "Proficient in Python or Go; experience with PostgreSQL/Redis; familiar with Docker/Kubernetes; understanding of distributed systems and microservices.",
        "skills": ["Python", "Go", "Golang", "PostgreSQL", "Redis", "Docker", "Kubernetes", "分布式", "微服务", "Azure"],
        "company_type": "外企",
    },
    {
        "title": "Machine Learning Engineer",
        "company": "Google",
        "industry": "互联网",
        "location": "北京",
        "salary_range": "40K-70K",
        "experience_required": "3-5年",
        "education_required": "硕士",
        "description": "Build and deploy large-scale ML models for search ranking and recommendation systems.",
        "requirements": "Strong Python skills; deep experience with TensorFlow/PyTorch; understanding of NLP and Deep Learning; familiar with Spark/Hadoop for distributed training.",
        "skills": ["Python", "TensorFlow", "PyTorch", "NLP", "Deep Learning", "Machine Learning", "Spark", "Hadoop", "Kubernetes"],
        "company_type": "外企",
    },
    # --- 教育 ---
    {
        "title": "教育产品开发经理",
        "company": "好未来",
        "industry": "教育",
        "location": "北京",
        "salary_range": "15K-25K",
        "experience_required": "1-3年",
        "education_required": "本科",
        "description": "负责K12在线教育产品设计，协调研发团队推进产品迭代。",
        "requirements": "熟悉教育行业；了解Python/SQL数据分析；有产品管理经验；良好的沟通协调能力。",
        "skills": ["Python", "SQL", "Excel", "Agile", "Scrum"],
        "company_type": "民营",
    },
    # --- 国企/事业单位 ---
    {
        "title": "系统运维工程师",
        "company": "中国电信",
        "industry": "通信",
        "location": "成都",
        "salary_range": "8K-15K",
        "experience_required": "应届",
        "education_required": "本科",
        "description": "负责核心业务系统日常运维，监控系统稳定性，处理故障告警。",
        "requirements": "熟悉Linux操作系统；了解Python/Shell脚本编程；了解Nginx/Tomcat等中间件；有网络基础知识。",
        "skills": ["Linux", "Python", "Nginx", "Tomcat", "Docker", "Git"],
        "company_type": "国企",
    },
    {
        "title": "大数据开发工程师",
        "company": "中国移动",
        "industry": "通信",
        "location": "北京",
        "salary_range": "15K-25K",
        "experience_required": "1-3年",
        "education_required": "本科",
        "description": "参与大数据平台开发与维护，负责数据ETL流程设计与优化。",
        "requirements": "熟悉Hadoop/Spark/Hive大数据生态；掌握Python/Java编程；了解Kafka消息队列；有数据仓库经验优先。",
        "skills": ["Hadoop", "Spark", "Hive", "Kafka", "Python", "Java", "SQL", "Airflow"],
        "company_type": "国企",
    },
    # --- 不同薪资区间 ---
    {
        "title": "初级Python开发",
        "company": "创业公司A",
        "industry": "互联网",
        "location": "成都",
        "salary_range": "6K-10K",
        "experience_required": "应届",
        "education_required": "本科",
        "description": "参与公司SaaS产品后端开发，学习并实践FastAPI+PostgreSQL技术栈。",
        "requirements": "了解Python编程；了解基本数据库操作；有学习意愿；了解Git基本操作。",
        "skills": ["Python", "FastAPI", "PostgreSQL", "Git", "REST"],
        "company_type": "民营",
    },
    {
        "title": "技术总监",
        "company": "某独角兽企业",
        "industry": "互联网",
        "location": "北京",
        "salary_range": "50K-80K",
        "experience_required": "5-10年",
        "education_required": "硕士",
        "description": "全面负责技术团队管理与架构决策，推动技术创新与业务发展。",
        "requirements": "深入理解分布式系统/微服务架构；精通Python/Java/Go多种语言；熟悉云原生技术栈；有团队管理经验。",
        "skills": ["Python", "Java", "Go", "Kubernetes", "分布式", "微服务", "AWS", "设计模式", "Agile"],
        "company_type": "民营",
    },
    # --- 不同城市 ---
    {
        "title": "Go后端开发工程师",
        "company": "B站",
        "industry": "互联网",
        "location": "上海",
        "salary_range": "20K-35K",
        "experience_required": "1-3年",
        "education_required": "本科",
        "description": "负责B站视频处理服务后端开发，使用Go语言构建高性能API。",
        "requirements": "精通Go语言；熟悉Gin/Echo框架；了解MySQL/Redis；熟悉Docker/K8s容器化部署。",
        "skills": ["Go", "Golang", "MySQL", "Redis", "Docker", "Kubernetes", "微服务", "gRPC"],
        "company_type": "民营",
    },
    {
        "title": "数据工程师",
        "company": "京东",
        "industry": "互联网",
        "location": "北京",
        "salary_range": "20K-35K",
        "experience_required": "1-3年",
        "education_required": "本科",
        "description": "负责京东物流数据平台开发，构建实时数据处理流水线。",
        "requirements": "精通Python/Java；熟悉Spark/Flink流批处理；了解Kafka消息队列；熟悉数据仓库建模。",
        "skills": ["Python", "Java", "Spark", "Flink", "Kafka", "Hive", "Airflow", "SQL"],
        "company_type": "民营",
    },
    # --- 其他行业 ---
    {
        "title": "医疗AI算法工程师",
        "company": "联影智能",
        "industry": "医疗",
        "location": "上海",
        "salary_range": "25K-45K",
        "experience_required": "1-3年",
        "education_required": "硕士",
        "description": "从事医学影像AI算法研发，开发基于深度学习的辅助诊断系统。",
        "requirements": "精通Python；熟悉PyTorch/TensorFlow深度学习框架；了解计算机视觉和医学影像处理；有论文发表经验优先。",
        "skills": ["Python", "PyTorch", "TensorFlow", "Computer Vision", "Deep Learning", "NumPy", "Pandas"],
        "company_type": "民营",
    },
    {
        "title": "网络安全工程师",
        "company": "奇安信",
        "industry": "安全",
        "location": "成都",
        "salary_range": "15K-25K",
        "experience_required": "1-3年",
        "education_required": "本科",
        "description": "负责企业安全产品研发，开发入侵检测与防御系统。",
        "requirements": "熟悉Python/Go编程；了解网络协议与安全攻防；熟悉Linux系统；有渗透测试经验优先。",
        "skills": ["Python", "Go", "Linux", "计算机网络", "Docker", "Nginx"],
        "company_type": "民营",
    },
    {
        "title": "嵌入式软件工程师",
        "company": "大疆创新",
        "industry": "硬件",
        "location": "深圳",
        "salary_range": "18K-30K",
        "experience_required": "1-3年",
        "education_required": "本科",
        "description": "负责无人机飞控系统嵌入式软件开发，优化实时控制算法。",
        "requirements": "精通C/C++语言；了解RTOS操作系统；熟悉Linux嵌入式开发；了解传感器与控制算法。",
        "skills": ["C++", "Linux", "算法", "数据结构", "操作系统"],
        "company_type": "民营",
    },
    {
        "title": "产品经理（技术方向）",
        "company": "网易",
        "industry": "互联网",
        "location": "杭州",
        "salary_range": "20K-35K",
        "experience_required": "3-5年",
        "education_required": "本科",
        "description": "负责网易云音乐技术产品规划，推动AI推荐策略落地。",
        "requirements": "熟悉Python/SQL数据分析；了解机器学习/NLP基本概念；有互联网产品经验；良好的数据分析能力。",
        "skills": ["Python", "SQL", "Excel", "Tableau", "Machine Learning", "Agile"],
        "company_type": "民营",
    },
]


async def main():
    conn = await asyncpg.connect(
        host=os.getenv("POSTGRES_HOST", "localhost"),
        port=int(os.getenv("POSTGRES_PORT", "5432")),
        user=os.getenv("POSTGRES_USER", "career_user"),
        password=os.getenv("POSTGRES_PASSWORD", "your_strong_password_here"),
        database=os.getenv("POSTGRES_DB", "career_planning"),
    )

    # 清空旧岗位数据
    await conn.execute("DELETE FROM jobs WHERE source = 'seed_test'")
    print(f"已清空旧测试岗位数据")

    inserted = 0
    for job in JOBS:
        await conn.execute(
            """
            INSERT INTO jobs (title, company, industry, location, salary_range,
                            experience_required, education_required, description,
                            requirements, skills, company_type, source)
            VALUES ($1, $2, $3, $4, $5, $6, $7, $8, $9, $10::jsonb, $11, 'seed_test')
            """,
            job["title"], job["company"], job["industry"], job["location"],
            job["salary_range"], job["experience_required"], job["education_required"],
            job["description"], job["requirements"],
            json.dumps(job["skills"], ensure_ascii=False),
            job["company_type"],
        )
        inserted += 1
        print(f"  [{inserted:02d}] {job['title']} @ {job['company']} ({job['location']})")

    # 统计
    total = await conn.fetchval("SELECT COUNT(*) FROM jobs")
    print(f"\n✅ 完成！共插入 {inserted} 条测试岗位，数据库当前共 {total} 条岗位")

    await conn.close()


if __name__ == "__main__":
    asyncio.run(main())
