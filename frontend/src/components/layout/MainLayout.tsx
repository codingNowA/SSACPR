/**
 * 主布局组件
 */
import React from 'react';
import { Outlet, useNavigate, useLocation } from 'react-router-dom';
import { Layout, Menu, Space, Button } from 'antd';
import {
  HomeOutlined,
  FileTextOutlined,
  BarChartOutlined,
  SettingOutlined,
  UserOutlined,
  FileSearchOutlined,
  BankOutlined,
  TrophyOutlined,
  BookOutlined,
} from '@ant-design/icons';
import { useAppStore } from '../../store';

const { Header, Content, Footer } = Layout;

const MainLayout: React.FC = () => {
  const navigate = useNavigate();
  const location = useLocation();
  const { currentResumeId, user } = useAppStore();

  // 未登录跳转到登录页
  React.useEffect(() => {
    if (!user) {
      navigate('/login', { replace: true });
    }
  }, [user, navigate]);

  const isAdmin = user?.role === 'admin';

  const menuItems = [
    {
      key: '/',
      icon: <HomeOutlined />,
      label: '首页',
    },
    {
      key: '/resume/upload',
      icon: <FileTextOutlined />,
      label: '简历诊断',
    },
    {
      key: '/resume/list',
      icon: <FileTextOutlined />,
      label: '我的简历',
    },
    // 只有当前有简历时才显示诊断报告菜单
    ...(currentResumeId
      ? [
          {
            key: `/resume/diagnosis/${currentResumeId}`,
            icon: <FileSearchOutlined />,
            label: '诊断报告',
          },
        ]
      : []),
    {
      key: '/job/center',
      icon: <BankOutlined />,
      label: '岗位中心',
    },
    {
      key: '/interview',
      icon: <TrophyOutlined />,
      label: '面试',
    },
    {
      key: '/analytics',
      icon: <BarChartOutlined />,
      label: '数据分析',
    },
    // 仅管理员可见管理菜单
    ...(isAdmin
      ? [
          {
            key: 'admin',
            icon: <SettingOutlined />,
            label: '管理',
            children: [
              {
                key: '/admin/jobs',
                label: '岗位管理',
              },
              {
                key: '/admin/questions',
                label: '题库管理',
              },
              {
                key: '/admin/logs',
                label: '日志查询',
              },
            ],
          },
        ]
      : []),
  ];

  return (
    <Layout style={{ minHeight: '100vh' }}>
      <Header
        style={{
          display: 'flex',
          alignItems: 'center',
          background: '#001529',
          padding: '0 50px',
        }}
      >
        <div
          style={{
            color: 'white',
            fontSize: '20px',
            fontWeight: 'bold',
            marginRight: '50px',
            cursor: 'pointer',
          }}
          onClick={() => navigate('/')}
        >
          职业规划智能体系统
        </div>
        <Menu
          theme="dark"
          mode="horizontal"
          selectedKeys={[location.pathname]}
          items={menuItems}
          onClick={({ key }) => navigate(key)}
          style={{ flex: 1, minWidth: 0 }}
        />
        {user && (
          <Space style={{ marginLeft: '16px' }}>
            <span style={{ color: 'white', fontSize: '14px' }}>
              {user.realName || user.username}
            </span>
            <Button
              type="link"
              style={{ color: 'white', padding: 0 }}
              onClick={() => {
                useAppStore.getState().logout();
                navigate('/login', { replace: true });
              }}
            >
              退出
            </Button>
          </Space>
        )}
      </Header>
      <Content
        style={{
          padding: '0',
          background: '#f0f2f5',
          minHeight: 'calc(100vh - 134px)',
        }}
      >
        <Outlet />
      </Content>
      <Footer style={{ textAlign: 'center', background: '#fff' }}>
        <Space direction="vertical" size="small">
          <div>职业规划智能体系统 ©2026</div>
          <div style={{ fontSize: '12px', color: '#999' }}>
            基于大语言模型的简历智能诊断与岗位精准匹配系统
          </div>
        </Space>
      </Footer>
    </Layout>
  );
};

export default MainLayout;
