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
  List,
  Tag,
  Button,
  Avatar,
} from 'antd';
import {
  UserOutlined,
  FileTextOutlined,
  HistoryOutlined,
  TrophyOutlined,
  ClockCircleOutlined,
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
  const [recentVersions, setRecentVersions] = useState<any[]>([]);

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

      try {
        const versionsResponse = await axios.get('/api/v1/resume/versions', {
          params: {
            user_id: user?.userId,
            page: 1,
            page_size: 5,
          },
          headers,
        });
        const versionsData = versionsResponse.data?.data || versionsResponse.data;
        setRecentVersions(versionsData?.versions || versionsData?.items || []);
      } catch {
        // 版本查询失败不阻塞页面
      }
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
            <Col span={6}>
              <Statistic
                title="简历总数"
                value={stats?.resume_count || 0}
                prefix={<FileTextOutlined />}
                suffix="份"
              />
            </Col>
            <Col span={6}>
              <Statistic
                title="保存版本"
                value={stats?.version_count || 0}
                prefix={<HistoryOutlined />}
                suffix="个"
              />
            </Col>
            <Col span={6}>
              <Statistic
                title="岗位匹配次数"
                value={stats?.match_count || 0}
                prefix={<TrophyOutlined />}
                suffix="次"
              />
            </Col>
            <Col span={6}>
              <Statistic
                title="最后登录"
                value={formatDate(stats?.last_login || '')}
                prefix={<ClockCircleOutlined />}
                valueStyle={{ fontSize: 14 }}
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

        <Card
          title="最近保存的简历版本"
          extra={
            <Button type="link" onClick={() => navigate('/resume/upload')}>
              查看全部
            </Button>
          }
        >
          {recentVersions.length === 0 ? (
            <Text type="secondary">暂无保存的简历版本</Text>
          ) : (
            <List
              dataSource={recentVersions}
              renderItem={(item) => (
                <List.Item
                  actions={[
                    <Button
                      type="link"
                      onClick={() => navigate(`/resume/${item.resume_id || item.id}/versions`)}
                    >
                      查看详情
                    </Button>,
                  ]}
                >
                  <List.Item.Meta
                    avatar={<Avatar icon={<FileTextOutlined />} />}
                    title={item.version_name || item.title || '未命名版本'}
                    description={
                      <Space>
                        <Text type="secondary">
                          创建时间：{formatDate(item.created_at)}
                        </Text>
                        {item.target_job && <Tag>{item.target_job}</Tag>}
                      </Space>
                    }
                  />
                </List.Item>
              )}
            />
          )}
        </Card>
      </Space>
    </div>
  );
};

export default UserProfile;
