/**
 * 岗位和匹配相关 API
 */
import apiClient from './api';
import type { Job, JobMatchRequest, JobMatchResponse } from '../types';

/**
 * 获取岗位列表
 */
export const getJobList = async (params: {
  page?: number;
  page_size?: number;
  status?: string;
  industry?: string;
  location?: string;
}): Promise<{ total: number; items: Job[] }> => {
  const response = await apiClient.get('/api/v1/job/list', { params });
  return response;
};

/**
 * 获取岗位详情
 */
export const getJobDetail = async (jobId: number): Promise<Job> => {
  const response = await apiClient.get(`/api/v1/job/${jobId}`);
  return response;
};

/**
 * 计算岗位匹配
 */
export const calculateMatch = async (request: JobMatchRequest): Promise<JobMatchResponse> => {
  const response = await apiClient.post('/api/v1/match/calculate', request);
  return response;
};

/**
 * 获取匹配历史
 */
export const getMatchHistory = async (params: {
  resume_id?: number;
  user_id?: number;
  page?: number;
  page_size?: number;
}): Promise<any> => {
  const response = await apiClient.get('/api/v1/match/history', { params });
  return response;
};
