/**
 * 用户信息页面
 * 显示用户ID、名字、使用次数、保存版本等信息
 */
import React, { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import {
  Card,
  Descriptions,
  Space,
  Typography,
  Statistic,
  Row,
  Col,
  Tag,
  Button,
  Avatar,
} from 'antd';
import {
  UserOutlined,
  FileTextOutlined,
  HistoryOutlined,
  TrophyOutlined,
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
  const { user } = useAppStore();
  const [loading, setLoading] = useState(false);
  const [stats, setStats] = useState<UserStats | null>(null);

  useEffect(() => {
    loadUserInfo();
  }, []);

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
                {stats?.real_name || stats?.username || `用户 #${user?.userId || 1}`}
              </Title>
              <Space>
                <Text type="secondary">@{stats?.username || '-'}</Text>
                <Tag color={roleMap[stats?.role || 'student']?.color || 'default'}>
                  {roleMap[stats?.role || 'student']?.label || stats?.role}
                </Tag>
              </Space>
            </div>
          </Space>
        </Card>

        <Card title={<>使用统计</>} loading={loading}>
          <Row gutter={16}>
            <Col span={8}>
              <Statistic
                title="简历总数"
                value={stats?.resume_count || 0}
                prefix={<FileTextOutlined />}
                suffix="份"
              />
            </Col>
            <Col span={8}>
              <Statistic
                title="保存版本"
                value={stats?.version_count || 0}
                prefix={<HistoryOutlined />}
                suffix="个"
              />
            </Col>
            <Col span={8}>
              <Statistic
                title="岗位匹配次数"
                value={stats?.match_count || 0}
                prefix={<TrophyOutlined />}
                suffix="次"
              />
            </Col>
          </Row>
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
            <Descriptions.Item label="注册时间">
              {formatDate(stats?.created_at || '')}
            </Descriptions.Item>
            <Descriptions.Item label="账户状态">
              <Tag color="green">正常</Tag>
            </Descriptions.Item>
            <Descriptions.Item label="总使用次数" span={2}>
              {(stats?.resume_count || 0) + (stats?.match_count || 0)} 次
            </Descriptions.Item>
          </Descriptions>
        </Card>
      </Space>
    </div>
  );
};

export default UserProfile;