/**
 * 日志查询相关 API
 */
import apiClient from './api';

/**
 * 获取日志列表
 */
export const getLogs = async (params: {
  page?: number;
  page_size?: number;
  user_id?: number;
  action?: string;
  module?: string;
  start_date?: string;
  end_date?: string;
  keyword?: string;
}): Promise<any> => {
  return await apiClient.get('/api/v1/admin/logs', { params });
};

/**
 * 获取日志详情
 */
export const getLogDetail = async (logId: number): Promise<any> => {
  return await apiClient.get(`/api/v1/admin/logs/${logId}`);
};
