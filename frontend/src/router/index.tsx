/**
 * 路由配置
 */
import { createBrowserRouter, Navigate } from 'react-router-dom';
import MainLayout from '../components/layout/MainLayout';
import Home from '../pages/Home';
import ResumeUpload from '../pages/Resume/Upload';
import ResumeDiagnosis from '../pages/Resume/Diagnosis';
import ResumeVersions from '../pages/Resume/Versions';
import JobMatch from '../pages/Job/Match';
import Analytics from '../pages/Analytics';
import JobAdmin from '../pages/Admin/JobAdmin';
import QuestionAdmin from '../pages/Admin/QuestionAdmin';
import LogQuery from '../pages/Admin/LogQuery';

export const router = createBrowserRouter([
  {
    path: '/',
    element: <MainLayout />,
    children: [
      {
        index: true,
        element: <Home />,
      },
      {
        path: 'resume',
        children: [
          {
            path: 'upload',
            element: <ResumeUpload />,
          },
          {
            path: ':resumeId/diagnosis',
            element: <ResumeDiagnosis />,
          },
          {
            path: ':resumeId/versions',
            element: <ResumeVersions />,
          },
          {
            path: ':resumeId/match',
            element: <JobMatch />,
          },
        ],
      },
      {
        path: 'analytics',
        element: <Analytics />,
      },
      {
        path: 'admin',
        children: [
          {
            path: 'jobs',
            element: <JobAdmin />,
          },
          {
            path: 'questions',
            element: <QuestionAdmin />,
          },
          {
            path: 'logs',
            element: <LogQuery />,
          },
        ],
      },
      {
        path: 'about',
        element: <div style={{ padding: '50px', textAlign: 'center' }}>关于页面开发中...</div>,
      },
      {
        path: '*',
        element: <Navigate to="/" replace />,
      },
    ],
  },
]);
