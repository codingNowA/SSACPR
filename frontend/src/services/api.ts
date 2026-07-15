/**
 * API 客户端配置
 */
import axios from 'axios';

// 开发环境默认指向本地后端；生产构建未显式配置时使用相对路径（由 Nginx/反向代理转发 /api）
const API_BASE_URL =
  import.meta.env.VITE_API_BASE_URL ??
  (import.meta.env.DEV ? 'http://localhost:8000' : '');

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
    const payload = response.data;
    // 统一处理 ApiResponse 信封格式 { code, message, data }
    if (payload && typeof payload === 'object' && 'code' in payload) {
      if (payload.code === 200) {
        return payload.data;
      }
      // 业务错误：后端可能以 HTTP 200 返回 { code: 400, data: null }，此处转为 reject，避免页面拿到空数据崩溃
      return Promise.reject(payload.message || payload.detail || '请求失败');
    }
    // 非信封响应（如 analytics / admin 直接返回数据模型）原样返回
    return payload;
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
