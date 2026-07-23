/**
 * API 客户端配置
 */
import axios from 'axios';

const API_BASE_URL = import.meta.env.VITE_API_BASE_URL || 'http://localhost:8000';

// 创建 axios 实例
export const apiClient = axios.create({
  baseURL: API_BASE_URL,
  timeout: 180000, // 增加到3分钟，匹配计算可能需要较长时间
  headers: {
    'Content-Type': 'application/json',
  },
});

// 请求拦截器
apiClient.interceptors.request.use(
  (config) => {
    // 如果需要 JWT 认证，在这里添加 token
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
    // 统一处理 ApiResponse 格式
    if (response.data && response.data.code === 200) {
      return response.data.data;
    }
    return response.data;
  },
  (error) => {
    // 统一错误处理
    if (error.response) {
      const { status, data } = error.response;
      if (status === 401) {
        // 未授权，清除 token
        localStorage.removeItem('token');
        window.location.href = '/login';
      }
      return Promise.reject(data?.detail || data?.message || '请求失败');
    }
    return Promise.reject(error.message || '网络错误');
  }
);

export default apiClient;
