/**
 * 岗位管理相关 API
 */
import apiClient from './api';

/**
 * 获取岗位列表（管理端）
 */
export const getAdminJobs = async (params: {
  page?: number;
  page_size?: number;
  title?: string;
  company?: string;
  industry?: string;
  location?: string;
  status?: string;
  keyword?: string;
}): Promise<any> => {
  return await apiClient.get('/api/v1/admin/jobs', { params });
};

/**
 * 获取岗位详情（管理端）
 */
export const getAdminJobDetail = async (jobId: number): Promise<any> => {
  return await apiClient.get(`/api/v1/admin/jobs/${jobId}`);
};

/**
 * 创建岗位
 */
export const createJob = async (data: any): Promise<any> => {
  return await apiClient.post('/api/v1/admin/jobs', data);
};

/**
 * 更新岗位
 */
export const updateJob = async (jobId: number, data: any): Promise<any> => {
  return await apiClient.put(`/api/v1/admin/jobs/${jobId}`, data);
};

/**
 * 删除岗位
 */
export const deleteJob = async (jobId: number): Promise<any> => {
  return await apiClient.delete(`/api/v1/admin/jobs/${jobId}`);
};
