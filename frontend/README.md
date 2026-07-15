# 前端项目说明

## 项目概述

基于 React + TypeScript + Ant Design 构建的职业规划智能体系统前端应用。

## 技术栈

- **框架**: React 18.3
- **语言**: TypeScript 5.6
- **UI 组件库**: Ant Design 5.22
- **路由**: React Router 6.26
- **状态管理**: Zustand 5.0
- **HTTP 客户端**: Axios 1.7
- **构建工具**: Vite 5.4
- **Hooks 工具**: ahooks 3.8

## 项目结构

```
frontend/src/
├── components/          # 公共组件
│   └── Layout/         # 布局组件
│       └── MainLayout.tsx
├── pages/              # 页面组件
│   ├── Home/          # 首页
│   │   └── index.tsx
│   ├── Resume/        # 简历相关页面
│   │   ├── Upload.tsx      # 简历上传
│   │   ├── Diagnosis.tsx   # 诊断结果
│   │   └── Versions.tsx    # 版本管理
│   └── Job/           # 岗位相关页面
│       └── Match.tsx       # 岗位匹配
├── services/          # API 服务层
│   ├── api.ts        # API 客户端配置
│   ├── resume.ts     # 简历相关 API
│   └── job.ts        # 岗位相关 API
├── store/            # 状态管理
│   └── index.ts      # Zustand 全局状态
├── types/            # TypeScript 类型定义
│   └── index.ts
├── utils/            # 工具函数
│   └── index.ts
├── router/           # 路由配置
│   └── index.tsx
├── main.tsx          # 应用入口
└── index.css         # 全局样式
```

## 核心功能模块

### 1. 简历智能诊断

**路由**: `/resume/upload`

**功能**:
- 上传简历文件（支持 PDF、Word、图片）
- 自动解析简历内容
- 智能诊断与评分
- 展示诊断结果

**流程**:
1. 用户上传简历文件
2. 调用 `/api/v1/resume/upload` 上传文件
3. 调用 `/api/v1/resume/{id}/parse` 解析内容
4. 调用 `/api/v1/resume/{id}/diagnose` 进行诊断
5. 跳转到诊断结果页面

### 2. 诊断结果展示

**路由**: `/resume/:resumeId/diagnosis`

**功能**:
- 展示综合评分（完整性、专业性、量化程度、项目深度、岗位匹配）
- 显示优化建议列表
- 一键优化功能
- 保存简历版本
- 查看简历详细信息

**交互**:
- 点击"一键优化"调用 `/api/v1/resume/{id}/optimize`
- 点击"保存版本"调用 `/api/v1/resume/{id}/version`
- 点击"岗位匹配"跳转到匹配页面
- 点击"版本历史"查看所有版本

### 3. 岗位精准匹配

**路由**: `/resume/:resumeId/match`

**功能**:
- 基于简历数据智能匹配岗位
- 支持偏好筛选（行业、城市、薪资、学历、经验、公司类型）
- 分层展示匹配结果：
  - 高度匹配
  - 较为匹配
  - 发展方向
- 显示匹配度分数、命中技能、缺失技能、推荐理由

**交互**:
- 点击"开始匹配"调用 `/api/v1/match/calculate`
- 使用筛选条件重新匹配
- 查看每个岗位的详细匹配信息

### 4. 版本管理

**路由**: `/resume/:resumeId/versions`

**功能**:
- 查看所有简历版本
- 恢复历史版本
- 下载版本文件

**交互**:
- 点击"恢复"调用 `/api/v1/resume/{id}/version/{versionId}/restore`
- 点击"下载"下载版本文件

## API 接口对接

### 简历相关接口

```typescript
// 上传简历
POST /api/v1/resume/upload
Content-Type: multipart/form-data
Body: { file: File, user_id: number }

// 解析简历
POST /api/v1/resume/{id}/parse

// 诊断简历
POST /api/v1/resume/{id}/diagnose

// 优化简历
POST /api/v1/resume/{id}/optimize
Body: { target_position?: string }

// 获取简历数据
GET /api/v1/resume/{id}

// 创建版本
POST /api/v1/resume/{id}/version
Body: { version_name: string }

// 获取版本列表
GET /api/v1/resume/{id}/versions

// 恢复版本
POST /api/v1/resume/{id}/version/{versionId}/restore
```

### 岗位相关接口

```typescript
// 获取岗位列表
GET /api/v1/job/list?page=1&page_size=20

// 计算岗位匹配
POST /api/v1/match/calculate
Body: {
  resume_id: number,
  preferences?: MatchPreferences,
  top_k?: number
}
```

## 状态管理

使用 Zustand 管理全局状态：

```typescript
interface AppState {
  userId: number;              // 当前用户ID
  currentResumeId: number | null;  // 当前简历ID
  resumeData: ResumeData | null;   // 简历数据
  diagnosisResult: DiagnosisResult | null;  // 诊断结果
  loading: boolean;            // 加载状态
}
```

## 开发指南

### 本地开发

```bash
cd frontend
npm install
npm run dev
```

访问: http://localhost:5173

### 生产构建

```bash
npm run build
```

构建产物在 `dist/` 目录

### Docker 部署

```bash
docker-compose up -d frontend
```

访问: http://localhost:5173

## 环境变量

在 `.env` 文件中配置：

```env
VITE_API_BASE_URL=http://localhost:8000
VITE_APP_ENV=development
```

## 待优化项

1. **错误边界**: 添加 Error Boundary 组件捕获运行时错误
2. **加载骨架屏**: 为页面添加骨架屏提升用户体验
3. **响应式优化**: 优化移动端适配
4. **国际化**: 支持多语言切换
5. **主题切换**: 支持亮色/暗色主题
6. **单元测试**: 添加组件测试覆盖
7. **性能优化**: 
   - 路由懒加载
   - 图片懒加载
   - 代码分割
8. **埋点统计**: 添加用户行为分析
9. **PWA**: 支持离线使用
10. **文件预览**: 在浏览器中预览简历文件

## 注意事项

1. **认证**: 当前为开发模式，JWT 认证已禁用。生产环境需要启用认证。
2. **CORS**: 后端已配置 CORS 允许 `http://localhost:5173`。
3. **文件上传**: 文件大小限制为 10MB。
4. **浏览器兼容**: 建议使用现代浏览器（Chrome、Edge、Firefox、Safari 最新版）。

## 常见问题

### 1. API 请求失败

检查后端服务是否正常运行：
```bash
curl http://localhost:8000/health
```

### 2. 前端无法访问

检查 Docker 容器状态：
```bash
docker-compose ps frontend
docker logs career-frontend
```

### 3. 样式异常

清除浏览器缓存或强制刷新（Ctrl+Shift+R）。
