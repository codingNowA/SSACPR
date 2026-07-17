/**
 * 路由配置
 */
import { createBrowserRouter, Navigate } from 'react-router-dom';
import MainLayout from '../components/layout/MainLayout';
import Home from '../pages/Home';
import Login from '../pages/Login';
import ResumeUpload from '../pages/Resume/Upload';
import ResumeDiagnosis from '../pages/Resume/Diagnosis';
import ResumeVersions from '../pages/Resume/Versions';
import JobMatch from '../pages/Job/Match';
import JobList from '../pages/Job/List';
import JobInterpret from '../pages/Job/Interpret';
import InterviewPrep from '../pages/Interview/Prep';
import MockInterview from '../pages/Interview/Mock';
import Analytics from '../pages/Analytics';
import JobAdmin from '../pages/Admin/JobAdmin';
import QuestionAdmin from '../pages/Admin/QuestionAdmin';
import LogQuery from '../pages/Admin/LogQuery';
import { useStore } from '../store';

// 路由守卫：需要登录
const ProtectedRoute = ({ children }: { children: React.ReactNode }) => {
  const user = useStore((state) => state.user);

  if (!user) {
    return <Navigate to="/login" replace />;
  }

  return <>{children}</>;
};

// 路由守卫：需要管理员权限
const AdminRoute = ({ children }: { children: React.ReactNode }) => {
  const user = useStore((state) => state.user);

  if (!user) {
    return <Navigate to="/login" replace />;
  }

  if (user.role !== 'admin') {
    return <Navigate to="/" replace />;
  }

  return <>{children}</>;
};

export const router = createBrowserRouter([
  {
    path: '/login',
    element: <Login />,
  },
  {
    path: '/',
    element: (
      <ProtectedRoute>
        <MainLayout />
      </ProtectedRoute>
    ),
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
        path: 'job',
        children: [
          {
            path: 'list',
            element: <JobList />,
          },
          {
            path: 'interpret/:jobId',
            element: <JobInterpret />,
          },
        ],
      },
      {
        path: 'interview',
        children: [
          {
            path: 'prep',
            element: <InterviewPrep />,
          },
          {
            path: 'mock',
            element: <MockInterview />,
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
            element: (
              <AdminRoute>
                <JobAdmin />
              </AdminRoute>
            ),
          },
          {
            path: 'questions',
            element: (
              <AdminRoute>
                <QuestionAdmin />
              </AdminRoute>
            ),
          },
          {
            path: 'logs',
            element: (
              <AdminRoute>
                <LogQuery />
              </AdminRoute>
            ),
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
