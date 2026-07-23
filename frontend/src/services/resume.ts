/**
 * 简历相关 API
 */
import apiClient from './api';
import type {
  ResumeData,
  DiagnosisResult,
  ResumeVersion,
  UploadResponse,
} from '../types';

/**
 * 上传简历
 */
export const uploadResume = async (file: File, userId: number): Promise<UploadResponse> => {
  const formData = new FormData();
  formData.append('file', file);
  formData.append('user_id', userId.toString());

  const response = await apiClient.post('/api/v1/resume/upload', formData, {
    headers: {
      'Content-Type': 'multipart/form-data',
    },
  });
  return response;
};

/**
 * 解析简历
 */
export const parseResume = async (resumeId: number): Promise<ResumeData> => {
  const response = await apiClient.get(`/api/v1/resume/${resumeId}`);
  return response;
};

/**
 * 诊断简历
 */
export const diagnoseResume = async (resumeId: number): Promise<DiagnosisResult> => {
  const response = await apiClient.post(`/api/v1/resume/${resumeId}/diagnose`);
  return response;
};

/**
 * 优化简历
 */
export const optimizeResume = async (
  resumeId: number,
  targetPosition?: string
): Promise<DiagnosisResult> => {
  const response = await apiClient.post(`/api/v1/resume/${resumeId}/optimize`, {
    job_title: targetPosition,
  });
  return response;
};

/**
 * 获取简历数据
 */
export const getResumeData = async (resumeId: number): Promise<ResumeData> => {
  const response = await apiClient.get(`/api/v1/resume/${resumeId}`);
  return response;
};

/**
 * 保存简历版本（保存当前简历的快照）
 */
export const createResumeVersion = async (
  resumeId: number,
  versionName: string,
  scores?: any,
  optimization?: any
): Promise<any> => {
  const response = await apiClient.post(
    `/api/v1/resume/${resumeId}/snapshots`,
    {
      version_name: versionName,
      scores: scores,
      optimization: optimization,
    }
  );
  return response;
};

/**
 * 获取简历版本列表
 */
export const getResumeVersions = async (
  resumeId: number,
  page: number = 1,
  pageSize: number = 10
): Promise<any> => {
  const response = await apiClient.get(
    `/api/v1/resume/${resumeId}/snapshots?page=${page}&page_size=${pageSize}`
  );
  return response;
};

/**
 * 获取版本详情
 */
export const getVersionDetail = async (versionId: number): Promise<any> => {
  const response = await apiClient.get(`/api/v1/resume/snapshots/${versionId}`);
  return response;
};

/**
 * 删除版本
 */
export const deleteVersion = async (versionId: number): Promise<any> => {
  const response = await apiClient.delete(`/api/v1/resume/snapshots/${versionId}`);
  return response;
};