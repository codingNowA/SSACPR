/**
 * 数据分析相关 API
 */
import apiClient from './api';

/**
 * 获取岗位热词
 */
export const getHotwords = async (params: {
  limit?: number;
  category?: string;
}): Promise<any> => {
  return await apiClient.get('/api/v1/analytics/hotwords', { params });
};

/**
 * 获取技能趋势
 */
export const getSkillTrend = async (params: {
  skill: string;
  months?: number;
  period?: string;
}): Promise<any> => {
  return await apiClient.get('/api/v1/analytics/skill-trend', { params });
};

/**
 * 获取薪资分布
 */
export const getSalaryDistribution = async (params: {
  dimension?: string;
  limit?: number;
}): Promise<any> => {
  return await apiClient.get('/api/v1/analytics/salary-distribution', { params });
};

/**
 * 获取维度对比
 */
export const getComparison = async (params: {
  dimension?: string;
  metric?: string;
  limit?: number;
}): Promise<any> => {
  return await apiClient.get('/api/v1/analytics/comparison', { params });
};

/**
 * 获取技能排行榜
 */
export const getSkillRank = async (params: {
  limit?: number;
  industry?: string;
}): Promise<any> => {
  return await apiClient.get('/api/v1/analytics/skill-rank', { params });
};

/**
 * 获取趋势变化
 */
export const getTrendChange = async (params: {
  months?: number;
  metric?: string;
  dimension?: string;
}): Promise<any> => {
  return await apiClient.get('/api/v1/analytics/trend-change', { params });
};
