/**
 * 路由配置
 */
import { createBrowserRouter, Navigate } from 'react-router-dom';
import MainLayout from '../components/layout/MainLayout';
import Home from '../pages/Home';
import Login from '../pages/Login';
import ResumeUpload from '../pages/Resume/Upload';
import ResumeList from '../pages/Resume/List';
import ResumeEdit from '../pages/Resume/Edit';
import ResumeDiagnosis from '../pages/Resume/Diagnosis';
import ResumeVersions from '../pages/Resume/Versions';
import JobMatch from '../pages/Job/Match';
import JobList from '../pages/Job/List';
import JobInterpret from '../pages/Job/Interpret';
import JobCenter from '../pages/Job/Center';
import InterviewPrep from '../pages/Interview/Prep';
import InterviewIndex from '../pages/Interview/Index';
import QuestionBank from '../pages/Interview/QuestionBank';
import UserProfile from '../pages/User/Profile';
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
            path: 'list',
            element: <ResumeList />,
          },
          {
            path: 'upload',
            element: <ResumeUpload />,
          },
          {
            path: 'edit/:resumeId',
            element: <ResumeEdit />,
          },
          {
            path: 'diagnosis/:resumeId',
            element: <ResumeDiagnosis />,
          },
          {
            path: 'versions/:resumeId',
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
            path: 'center',
            element: <JobCenter />,
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
            index: true,
            element: <InterviewIndex />,
          },
          {
            path: 'prep',
            element: <InterviewPrep />,
          },
          {
            path: 'questions',
            element: <QuestionBank />,
          },
        ],
      },
      {
        path: 'analytics',
        element: <Analytics />,
      },
      {
        path: 'user',
        children: [
          {
            path: 'profile',
            element: <UserProfile />,
          },
        ],
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
