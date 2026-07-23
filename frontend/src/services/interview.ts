/**
 * 面试准备服务
 */
import apiClient from './api';

export interface InterviewPrepResponse {
  job_id: number;
  job_title: string;
  company: string;
  resume_id: number;
  candidate_name: string;
  technical_prep: {
    mastered_required: string[];
    missing_required: string[];
    mastered_bonus: string[];
    focus_areas: string[];
    preparation_tips: string[];
  };
  project_prep: {
    key_projects: Array<{
      company: string;
      position: string;
      duration: string;
      highlights: string[];
    }>;
    preparation_tips: string[];
  };
  common_questions: Array<{
    question: string;
    tips: string;
  }>;
  technical_questions: Array<{
    question_id: number;
    question: string;
    difficulty: string;
    tags: string[];
    answer_hint: string;
  }>;
  behavioral_questions: Array<{
    question: string;
    tips: string;
  }>;
  swot_analysis: {
    strengths: string[];
    weaknesses: string[];
    opportunities: string[];
    threats: string[];
  };
  recommendations: string[];
}

/**
 * 获取面试准备方案
 */
export const getInterviewPrep = async (
  jobId: number,
  resumeId: number
): Promise<InterviewPrepResponse> => {
  const response = await apiClient.get(`/api/v1/interview-prep/prepare`, {
    params: { job_id: jobId, resume_id: resumeId },
  });
  return response.data;
};
