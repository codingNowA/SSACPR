/**
 * 全局状态管理
 */
import { create } from 'zustand';
import type { ResumeData, DiagnosisResult } from '../types';

interface AppState {
  // 当前用户ID（模拟登录）
  userId: number | null;
  setUserId: (id: number | null) => void;

  // 当前简历ID
  currentResumeId: number | null;
  setCurrentResumeId: (id: number | null) => void;

  // 简历数据
  resumeData: ResumeData | null;
  setResumeData: (data: ResumeData | null) => void;

  // 诊断结果
  diagnosisResult: DiagnosisResult | null;
  setDiagnosisResult: (result: DiagnosisResult | null) => void;

  // 加载状态
  loading: boolean;
  setLoading: (loading: boolean) => void;

  // 重置状态
  reset: () => void;
}

export const useAppStore = create<AppState>((set) => ({
  userId: 1, // 开发阶段默认用户，接入登录后改为 null
  setUserId: (id) => set({ userId: id }),

  currentResumeId: null,
  setCurrentResumeId: (id) => set({ currentResumeId: id }),

  resumeData: null,
  setResumeData: (data) => set({ resumeData: data }),

  diagnosisResult: null,
  setDiagnosisResult: (result) => set({ diagnosisResult: result }),

  loading: false,
  setLoading: (loading) => set({ loading }),

  reset: () =>
    set({
      currentResumeId: null,
      resumeData: null,
      diagnosisResult: null,
      loading: false,
    }),
}));
