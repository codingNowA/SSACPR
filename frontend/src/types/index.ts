/**
 * 类型定义
 */

// ==================== 基础类型 ====================

export interface ApiResponse<T = any> {
  code: number;
  message: string;
  data: T;
  timestamp: string;
}

// ==================== 简历相关 ====================

export interface BasicInfo {
  name?: string;
  phone?: string;
  email?: string;
  birth_date?: string;
  job_intention?: string;
  current_location?: string;
  years_of_experience?: string;
}

export interface Education {
  school?: string;
  major?: string;
  degree?: string;
  start_date?: string;
  end_date?: string;
  description?: string;
}

export interface WorkExperience {
  company?: string;
  position?: string;
  start_date?: string;
  end_date?: string;
  description?: string;
  achievements?: string[];
}

export interface ProjectExperience {
  name?: string;
  role?: string;
  start_date?: string;
  end_date?: string;
  description?: string;
  technologies?: string[];
  achievements?: string[];
}

export interface Skill {
  name: string;
  level?: string;
  category?: string;
}

export interface ResumeData {
  id?: number;
  user_id?: number;
  file_path?: string;
  file_type?: string;
  status?: string;
  // 后端 GET /resume/{id} 返回的包裹结构，真正的简历内容在 parsed_data 中
  parsed_data?: any;
  basic_info?: BasicInfo;
  education?: Education[];
  work_experience?: WorkExperience[];
  project_experience?: ProjectExperience[];
  skills?: Skill[];
  certifications?: string[];
  awards?: string[];
  self_evaluation?: string;
}

export interface ResumeScore {
  completeness: number;
  professionalism: number;
  quantification: number;
  project_depth: number;
  job_match: number;
  overall: number;
}

export interface SuggestionItem {
  category: string;
  severity: 'high' | 'medium' | 'low';
  issue: string;
  suggestion: string;
  example?: string;
}

export interface DiagnosisResult {
  resume_id: number;
  // 后端评分结构为嵌套对象（total_score / 各维度 {total_score} / dimensions[]），使用宽松类型
  scores: any;
  // 优化接口返回的优化建议（general_suggestions / priority_actions / overall_summary 等）
  optimization?: any;
  suggestions?: SuggestionItem[];
  optimized_sections?: {
    [key: string]: string;
  };
  created_at?: string;
}

export interface ResumeVersion {
  version_id: string;
  resume_id: number;
  version_name: string;
  created_at: string;
  file_path?: string;
}

// ==================== 岗位相关 ====================

export interface Job {
  id: number;
  title: string;
  company: string;
  industry?: string;
  location?: string;
  salary_range?: string;
  experience_required?: string;
  education_required?: string;
  description?: string;
  requirements?: string;
  skills?: string[];
  company_type?: string;
  status: string;
  source?: string;
  created_at: string;
}

export interface MatchPreferences {
  industries?: string[];
  cities?: string[];
  salary_min?: number;
  salary_max?: number;
  education?: string;
  experience?: string;
  company_types?: string[];
}

export type MatchCategory = 'highly_matched' | 'fairly_matched' | 'development_direction';

export interface JobMatchResult {
  job_id: number;
  job_title: string;
  company?: string;
  location?: string;
  salary_range?: string;
  match_score: number;
  matched_skills: string[];
  missing_skills: string[];
  match_reason: string;
  category: MatchCategory;
}

export interface JobMatchResponse {
  resume_id: number;
  total: number;
  highly_matched: JobMatchResult[];
  fairly_matched: JobMatchResult[];
  development_direction: JobMatchResult[];
}

export interface JobMatchRequest {
  resume_id: number;
  preferences?: MatchPreferences;
  top_k?: number;
}

// ==================== 上传相关 ====================

export interface UploadResponse {
  resume_id: number;
  file_path: string;
  file_type: string;
  message: string;
}
