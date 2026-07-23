/**
 * 认证相关API服务
 */
import apiClient from './api';

export interface LoginResponse {
  access_token: string;
  token_type: string;
  user_id: number;
  username: string;
  role: string;
  real_name?: string;
}

export interface RegisterRequest {
  username: string;
  password: string;
  email: string;
  real_name?: string;
}

export interface UserInfo {
  user_id: number;
  username: string;
  role: string;
  email?: string;
  real_name?: string;
}

/**
 * 用户登录
 */
export const login = async (username: string, password: string): Promise<LoginResponse> => {
  const response = await apiClient.post('/api/v1/auth/login', {
    username,
    password,
  });
  return response;
};

/**
 * 用户注册
 */
export const register = async (data: RegisterRequest): Promise<LoginResponse> => {
  const response = await apiClient.post('/api/v1/auth/register', data);
  return response;
};

/**
 * 获取当前用户信息
 */
export const getCurrentUser = async (): Promise<UserInfo> => {
  const response = await apiClient.get('/api/v1/auth/me');
  return response;
};

/**
 * 登出（清除本地token）
 */
export const logout = () => {
  localStorage.removeItem('token');
  localStorage.removeItem('user');
};
