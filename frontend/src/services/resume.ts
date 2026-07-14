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
  const response = await apiClient.post(`/api/v1/resume/${resumeId}/parse`);
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
    target_position: targetPosition,
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
 * 创建简历版本
 */
export const createResumeVersion = async (
  resumeId: number,
  versionName: string
): Promise<ResumeVersion> => {
  const response = await apiClient.post(`/api/v1/resume/${resumeId}/version`, {
    version_name: versionName,
  });
  return response;
};

/**
 * 获取简历版本列表
 */
export const getResumeVersions = async (resumeId: number): Promise<ResumeVersion[]> => {
  const response = await apiClient.get(`/api/v1/resume/${resumeId}/versions`);
  return response;
};

/**
 * 恢复简历版本
 */
export const restoreResumeVersion = async (
  resumeId: number,
  versionId: string
): Promise<ResumeData> => {
  const response = await apiClient.post(`/api/v1/resume/${resumeId}/version/${versionId}/restore`);
  return response;
};
