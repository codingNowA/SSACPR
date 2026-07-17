/**
 * 主布局组件
 */
import React from 'react';
import { Outlet, useNavigate, useLocation } from 'react-router-dom';
import { Layout, Menu, Space, Dropdown, Avatar, message } from 'antd';
import {
  HomeOutlined,
  FileTextOutlined,
  BarChartOutlined,
  SettingOutlined,
  UserOutlined,
  FileSearchOutlined,
  LogoutOutlined,
  BankOutlined,
  CommentOutlined,
} from '@ant-design/icons';
import type { MenuProps } from 'antd';
import { useStore } from '../../store';

const { Header, Content, Footer } = Layout;

const MainLayout: React.FC = () => {
  const navigate = useNavigate();
  const location = useLocation();
  const { user, currentResumeId, logout } = useStore();

  const handleLogout = () => {
    logout();
    message.success('已登出');
    navigate('/login');
  };

  const userMenuItems: MenuProps['items'] = [
    {
      key: 'username',
      label: user?.realName || user?.username || '用户',
      disabled: true,
    },
    {
      key: 'role',
      label: `角色: ${user?.role === 'admin' ? '管理员' : '用户'}`,
      disabled: true,
    },
    {
      type: 'divider',
    },
    {
      key: 'logout',
      icon: <LogoutOutlined />,
      label: '退出登录',
      onClick: handleLogout,
    },
  ];

  // 根据用户角色动态生成菜单
  const menuItems = [
    {
      key: '/',
      icon: <HomeOutlined />,
      label: '首页',
    },
    {
      key: 'resume',
      icon: <FileTextOutlined />,
      label: '简历管理',
      children: [
        {
          key: '/resume/list',
          label: '我的简历',
        },
        {
          key: '/resume/upload',
          label: '上传简历',
        },
        // 只有当前有简历时才显示诊断报告
        ...(currentResumeId ? [{
          key: `/resume/diagnosis/${currentResumeId}`,
          label: '当前简历诊断',
        }] : []),
      ],
    },
    {
      key: '/job/list',
      icon: <BankOutlined />,
      label: '岗位中心',
    },
    {
      key: '/interview/mock',
      icon: <CommentOutlined />,
      label: '模拟面试',
    },
    {
      key: '/analytics',
      icon: <BarChartOutlined />,
      label: '数据分析',
    },
    // 只有管理员才显示管理菜单
    ...(user?.role === 'admin' ? [{
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
    }] : []),
  ];

  return (
    <Layout style={{ minHeight: '100vh' }}>
      <Header style={{
        display: 'flex',
        alignItems: 'center',
        background: '#001529',
        padding: '0 50px',
        justifyContent: 'space-between'
      }}>
        <div style={{ display: 'flex', alignItems: 'center', flex: 1 }}>
          <div style={{
            color: 'white',
            fontSize: '20px',
            fontWeight: 'bold',
            marginRight: '50px',
            cursor: 'pointer'
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
            style={{ flex: 1, minWidth: 0, border: 'none' }}
          />
        </div>

        <Dropdown menu={{ items: userMenuItems }} placement="bottomRight">
          <div style={{ cursor: 'pointer', display: 'flex', alignItems: 'center', gap: '8px' }}>
            <Avatar icon={<UserOutlined />} style={{ backgroundColor: '#1890ff' }} />
            <span style={{ color: 'white' }}>{user?.realName || user?.username}</span>
          </div>
        </Dropdown>
      </Header>
      <Content style={{ padding: '0', background: '#f0f2f5', minHeight: 'calc(100vh - 134px)' }}>
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
