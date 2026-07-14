/**
 * 路由配置
 */
import { createBrowserRouter, Navigate } from 'react-router-dom';
import MainLayout from '../components/Layout/MainLayout';
import Home from '../pages/Home';
import ResumeUpload from '../pages/Resume/Upload';
import ResumeDiagnosis from '../pages/Resume/Diagnosis';
import ResumeVersions from '../pages/Resume/Versions';
import JobMatch from '../pages/Job/Match';

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
