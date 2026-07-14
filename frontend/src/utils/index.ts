/**
 * 工具函数
 */

/**
 * 格式化日期
 */
export const formatDate = (date: string | Date): string => {
  if (!date) return '';
  const d = new Date(date);
  return d.toLocaleDateString('zh-CN');
};

/**
 * 获取匹配度等级颜色
 */
export const getScoreColor = (score: number): string => {
  if (score >= 80) return '#52c41a'; // 绿色
  if (score >= 60) return '#faad14'; // 橙色
  return '#ff4d4f'; // 红色
};

/**
 * 获取匹配度等级文本
 */
export const getScoreLevel = (score: number): string => {
  if (score >= 80) return '优秀';
  if (score >= 60) return '良好';
  if (score >= 40) return '一般';
  return '较差';
};

/**
 * 获取严重程度标签
 */
export const getSeverityTag = (severity: 'high' | 'medium' | 'low'): {
  color: string;
  text: string;
} => {
  const map = {
    high: { color: 'red', text: '重要' },
    medium: { color: 'orange', text: '中等' },
    low: { color: 'blue', text: '建议' },
  };
  return map[severity];
};

/**
 * 文件大小格式化
 */
export const formatFileSize = (bytes: number): string => {
  if (bytes === 0) return '0 B';
  const k = 1024;
  const sizes = ['B', 'KB', 'MB', 'GB'];
  const i = Math.floor(Math.log(bytes) / Math.log(k));
  return Math.round(bytes / Math.pow(k, i) * 100) / 100 + ' ' + sizes[i];
};

/**
 * 验证文件类型
 */
export const isValidResumeFile = (file: File): boolean => {
  const validTypes = [
    'application/pdf',
    'application/msword',
    'application/vnd.openxmlformats-officedocument.wordprocessingml.document',
    'image/png',
    'image/jpeg',
    'image/jpg',
  ];
  return validTypes.includes(file.type);
};

/**
 * 获取文件扩展名
 */
export const getFileExtension = (filename: string): string => {
  return filename.slice(((filename.lastIndexOf('.') - 1) >>> 0) + 2);
};

/**
 * 截断文本
 */
export const truncateText = (text: string, maxLength: number): string => {
  if (text.length <= maxLength) return text;
  return text.slice(0, maxLength) + '...';
};

/**
 * 解析薪资范围
 */
export const parseSalaryRange = (salaryRange: string): { min: number; max: number } | null => {
  if (!salaryRange) return null;
  const match = salaryRange.match(/(\d+)K?-(\d+)K?/i);
  if (match) {
    return {
      min: parseInt(match[1]),
      max: parseInt(match[2]),
    };
  }
  return null;
};
