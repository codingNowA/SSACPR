/**
 * 用户信息页面
 * 显示用户ID、名字、使用次数、保存版本等信息
 */
import React, { useState, useEffect } from 'react';
import { useNavigate, useLocation } from 'react-router-dom';
import {
  Card,
  Descriptions,
  Space,
  Typography,
  Tag,
  Avatar,
} from 'antd';
import {
  UserOutlined,
} from '@ant-design/icons';
import { useAppStore } from '../../store';
import axios from 'axios';

const { Title, Text } = Typography;

interface UserStats {
  user_id: number;
  username: string;
  role: string;
  email: string;
  real_name: string;
  resume_count: number;
  version_count: number;
  match_count: number;
  created_at: string;
  last_login: string;
}

const UserProfile: React.FC = () => {
  const navigate = useNavigate();
  const location = useLocation();
  const { user } = useAppStore();
  const [loading, setLoading] = useState(false);
  const [stats, setStats] = useState<UserStats | null>(null);

  useEffect(() => {
    loadUserInfo();
  }, [location.key]); // 监听路由变化，每次进入页面都刷新数据

  const loadUserInfo = async () => {
    setLoading(true);
    try {
      const token = localStorage.getItem('token');
      const headers: any = {};
      if (token) headers.Authorization = `Bearer ${token}`;

      const statsResponse = await axios.get('/api/v1/auth/stats', {
        params: { user_id: user?.userId },
        headers,
      });
      const statsData = statsResponse.data?.data || statsResponse.data;
      setStats(statsData);
    } catch (error) {
      console.error('加载用户信息失败:', error);
    } finally {
      setLoading(false);
    }
  };

  const formatDate = (dateStr: string) => {
    if (!dateStr) return '-';
    return new Date(dateStr).toLocaleString('zh-CN');
  };

  const roleMap: Record<string, { label: string; color: string }> = {
    student: { label: '学生', color: 'blue' },
    teacher: { label: '教师', color: 'green' },
    admin: { label: '管理员', color: 'red' },
  };

  return (
    <div style={{ padding: '24px', maxWidth: '1200px', margin: '0 auto' }}>
      <Space direction="vertical" size="large" style={{ width: '100%' }}>
        <Card>
          <Space size="large">
            <Avatar size={80} icon={<UserOutlined />} style={{ backgroundColor: '#1890ff' }} />
            <div>
              <Title level={2} style={{ margin: 0 }}>
                {stats?.username || `用户${user?.userId || ''}`}
              </Title>
              <Space>
                <Text type="secondary">{stats?.email || '-'}</Text>
                <Tag color={roleMap[stats?.role || 'student']?.color || 'default'}>
                  {roleMap[stats?.role || 'student']?.label || stats?.role}
                </Tag>
              </Space>
            </div>
          </Space>
        </Card>

        <Card title="详细信息">
          <Descriptions column={2} bordered>
            <Descriptions.Item label="用户ID">{stats?.user_id || user?.userId}</Descriptions.Item>
            <Descriptions.Item label="用户名">{stats?.username || '-'}</Descriptions.Item>
            <Descriptions.Item label="邮箱">{stats?.email || '-'}</Descriptions.Item>
            <Descriptions.Item label="角色">
              <Tag color={roleMap[stats?.role || 'student']?.color || 'default'}>
                {roleMap[stats?.role || 'student']?.label || stats?.role}
              </Tag>
            </Descriptions.Item>
            <Descriptions.Item label="账户状态" span={2}>
              <Tag color="green">正常</Tag>
            </Descriptions.Item>
          </Descriptions>
        </Card>
      </Space>
    </div>
  );
};

export default UserProfile;