/**
 * API 客户端配置
 */
import axios from 'axios';

// 开发环境通过 Vite proxy 转发 /api，不需要完整 baseURL
// 生产环境由 Nginx 反向代理 /api，也不需要
const API_BASE_URL = import.meta.env.VITE_API_BASE_URL || '';

// 创建 axios 实例
export const apiClient = axios.create({
  baseURL: API_BASE_URL,
  timeout: 180000,
  headers: {
    'Content-Type': 'application/json',
  },
});

// 请求拦截器
apiClient.interceptors.request.use(
  (config) => {
    const token = localStorage.getItem('token');
    if (token) {
      config.headers.Authorization = `Bearer ${token}`;
    }
    return config;
  },
  (error) => {
    return Promise.reject(error);
  }
);

// 响应拦截器
apiClient.interceptors.response.use(
  (response) => {
    const payload = response.data;
    if (payload && typeof payload === 'object' && 'code' in payload) {
      if (payload.code === 200) {
        return payload.data;
      }
      return Promise.reject(payload.message || payload.detail || '请求失败');
    }
    return payload;
  },
  (error) => {
    if (error.response) {
      const { status, data } = error.response;
      if (status === 401) {
        localStorage.removeItem('token');
        window.location.href = '/login';
      }
      return Promise.reject(data?.detail || data?.message || '请求失败');
    }
    return Promise.reject(error.message || '网络错误');
  }
);

export default apiClient;
