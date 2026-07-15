/**
 * 题库管理相关 API
 */
import apiClient from './api';

/**
 * 获取题目列表
 */
export const getQuestions = async (params: {
  page?: number;
  page_size?: number;
  category?: string;
  difficulty?: string;
  keyword?: string;
}): Promise<any> => {
  return await apiClient.get('/api/v1/admin/questions', { params });
};

/**
 * 获取题目详情
 */
export const getQuestionDetail = async (questionId: number): Promise<any> => {
  return await apiClient.get(`/api/v1/admin/questions/${questionId}`);
};

/**
 * 创建题目
 */
export const createQuestion = async (data: any): Promise<any> => {
  return await apiClient.post('/api/v1/admin/questions', data);
};

/**
 * 更新题目
 */
export const updateQuestion = async (questionId: number, data: any): Promise<any> => {
  return await apiClient.put(`/api/v1/admin/questions/${questionId}`, data);
};

/**
 * 删除题目
 */
export const deleteQuestion = async (questionId: number): Promise<any> => {
  return await apiClient.delete(`/api/v1/admin/questions/${questionId}`);
};
