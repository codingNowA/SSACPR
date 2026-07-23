/**
 * 主布局组件
 */
import React from 'react';
import { Outlet, useNavigate, useLocation } from 'react-router-dom';
import { Layout, Menu, Typography, Space } from 'antd';
import {
  HomeOutlined,
  FileTextOutlined,
  ThunderboltOutlined,
  UserOutlined,
} from '@ant-design/icons';

const { Header, Content, Footer } = Layout;
const { Title } = Typography;

const MainLayout: React.FC = () => {
  const navigate = useNavigate();
  const location = useLocation();

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
      key: '/about',
      icon: <UserOutlined />,
      label: '关于',
    },
  ];

  return (
    <Layout style={{ minHeight: '100vh' }}>
      <Header style={{
        display: 'flex',
        alignItems: 'center',
        background: '#001529',
        padding: '0 50px'
      }}>
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
          style={{ flex: 1, minWidth: 0 }}
        />
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
