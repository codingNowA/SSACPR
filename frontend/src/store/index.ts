/**
 * 全局状态管理
 */
import { create } from 'zustand';
import type { ResumeData, DiagnosisResult } from '../types';

interface UserInfo {
  userId: number;
  username: string;
  role: string;
  realName?: string;
  token: string;
}

interface AppState {
  // 用户信息
  user: UserInfo | null;
  setUser: (user: UserInfo | null) => void;
  logout: () => void;

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

// 从localStorage初始化用户信息
const loadUserFromStorage = (): UserInfo | null => {
  try {
    const token = localStorage.getItem('token');
    const userStr = localStorage.getItem('user');
    if (token && userStr) {
      const user = JSON.parse(userStr);
      return { ...user, token };
    }
  } catch (e) {
    console.error('Failed to load user from localStorage:', e);
  }
  return null;
};

export const useStore = create<AppState>((set) => ({
  user: loadUserFromStorage(),
  setUser: (user) => set({ user }),
  logout: () => {
    localStorage.removeItem('token');
    localStorage.removeItem('user');
    set({
      user: null,
      currentResumeId: null,
      resumeData: null,
      diagnosisResult: null,
    });
  },

  currentResumeId: (() => {
    const stored = localStorage.getItem('currentResumeId');
    return stored ? parseInt(stored, 10) : null;
  })(),
  setCurrentResumeId: (id) => {
    if (id !== null) {
      localStorage.setItem('currentResumeId', id.toString());
    } else {
      localStorage.removeItem('currentResumeId');
    }
    set({ currentResumeId: id });
  },

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

// 保留旧的导出以兼容现有代码
export const useAppStore = useStore;
