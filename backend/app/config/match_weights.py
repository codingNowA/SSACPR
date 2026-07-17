"""
本地匹配算法权重配置
"""

# 匹配维度权重（总和为1.0）
MATCH_WEIGHTS = {
    "skill_required": 0.30,      # 必需技能覆盖率（30%）
    "skill_bonus": 0.10,         # 加分技能覆盖率（10%）
    "experience_years": 0.15,    # 工作年限匹配（15%）
    "experience_industry": 0.10, # 行业经验匹配（10%）
    "education": 0.15,           # 学历匹配（15%）
    "location": 0.10,            # 地点偏好（10%）
    "salary": 0.10,              # 薪资匹配（10%）
}

# 动态调整因子
DYNAMIC_FACTORS = {
    "rare_skill_boost": 1.2,     # 稀缺技能加成（技能出现频率 < 10%）
    "common_skill_decay": 0.8,   # 常见技能衰减（技能出现频率 > 50%）
    "salary_outlier_penalty": 0.9,  # 薪资异常惩罚（偏离均值2倍标准差）
}

# 学历等级映射（用于比较）
EDUCATION_LEVELS = {
    "博士": 7,
    "硕士": 6,
    "本科": 5,
    "大专": 4,
    "高中": 3,
    "初中": 2,
    "不限": 1,
}

# 工作年限映射
EXPERIENCE_RANGES = {
    "不限": (0, 0),
    "应届生": (0, 0),
    "1年以下": (0, 1),
    "1-3年": (1, 3),
    "3-5年": (3, 5),
    "5-10年": (5, 10),
    "10年以上": (10, 100),
}

# 匹配度分类阈值
MATCH_THRESHOLDS = {
    "highly_matched": 75,        # 高度匹配：≥75分
    "fairly_matched": 60,        # 较为匹配：60-74分
    "development_direction": 45, # 发展方向：45-59分
}
