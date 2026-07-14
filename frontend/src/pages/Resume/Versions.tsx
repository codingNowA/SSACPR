/**
 * 简历版本管理页面
 */
import React, { useState, useEffect } from 'react';
import { useParams, useNavigate } from 'react-router-dom';
import {
  Card,
  Table,
  Button,
  Space,
  Typography,
  Tag,
  Modal,
  message,
  Popconfirm,
} from 'antd';
import {
  HistoryOutlined,
  RollbackOutlined,
  DownloadOutlined,
  EyeOutlined,
} from '@ant-design/icons';
import { getResumeVersions, restoreResumeVersion } from '../../services/resume';
import { formatDate } from '../../utils';
import type { ResumeVersion } from '../../types';
import type { ColumnsType } from 'antd/es/table';

const { Title, Text } = Typography;

const ResumeVersions: React.FC = () => {
  const { resumeId } = useParams<{ resumeId: string }>();
  const navigate = useNavigate();

  const [versions, setVersions] = useState<ResumeVersion[]>([]);
  const [loading, setLoading] = useState(false);
  const [restoring, setRestoring] = useState(false);

  useEffect(() => {
    if (resumeId) {
      loadVersions();
    }
  }, [resumeId]);

  const loadVersions = async () => {
    if (!resumeId) return;

    setLoading(true);
    try {
      const data = await getResumeVersions(parseInt(resumeId));
      setVersions(data);
    } catch (error: any) {
      message.error(error || '加载版本列表失败');
    } finally {
      setLoading(false);
    }
  };

  const handleRestore = async (versionId: string) => {
    if (!resumeId) return;

    setRestoring(true);
    try {
      await restoreResumeVersion(parseInt(resumeId), versionId);
      message.success('版本恢复成功！');
      navigate(`/resume/${resumeId}/diagnosis`);
    } catch (error: any) {
      message.error(error || '恢复失败');
    } finally {
      setRestoring(false);
    }
  };

  const columns: ColumnsType<ResumeVersion> = [
    {
      title: '版本名称',
      dataIndex: 'version_name',
      key: 'version_name',
      render: (text) => <Text strong>{text}</Text>,
    },
    {
      title: '版本ID',
      dataIndex: 'version_id',
      key: 'version_id',
      render: (text) => <Tag color="blue">{text.slice(0, 8)}</Tag>,
    },
    {
      title: '创建时间',
      dataIndex: 'created_at',
      key: 'created_at',
      render: (text) => formatDate(text),
      sorter: (a, b) => new Date(b.created_at).getTime() - new Date(a.created_at).getTime(),
    },
    {
      title: '操作',
      key: 'action',
      render: (_, record) => (
        <Space>
          <Button
            type="link"
            icon={<EyeOutlined />}
            onClick={() => message.info('预览功能开发中')}
          >
            预览
          </Button>
          <Popconfirm
            title="确认恢复此版本？"
            description="恢复后将覆盖当前简历数据"
            onConfirm={() => handleRestore(record.version_id)}
            okText="确认"
            cancelText="取消"
          >
            <Button
              type="link"
              icon={<RollbackOutlined />}
              loading={restoring}
            >
              恢复
            </Button>
          </Popconfirm>
          <Button
            type="link"
            icon={<DownloadOutlined />}
            onClick={() => message.info('下载功能开发中')}
          >
            下载
          </Button>
        </Space>
      ),
    },
  ];

  return (
    <div style={{ padding: '24px', maxWidth: '1200px', margin: '0 auto' }}>
      <Space direction="vertical" size="large" style={{ width: '100%' }}>
        <Card>
          <Space direction="vertical" style={{ width: '100%' }}>
            <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
              <div>
                <Title level={2}>
                  <HistoryOutlined /> 版本历史
                </Title>
                <Text type="secondary">
                  简历ID: {resumeId} | 共 {versions.length} 个版本
                </Text>
              </div>
              <Button onClick={() => navigate(`/resume/${resumeId}/diagnosis`)}>
                返回诊断
              </Button>
            </div>
          </Space>
        </Card>

        <Card>
          <Table
            columns={columns}
            dataSource={versions}
            rowKey="version_id"
            loading={loading}
            pagination={{
              pageSize: 10,
              showSizeChanger: true,
              showTotal: (total) => `共 ${total} 个版本`,
            }}
          />
        </Card>
      </Space>
    </div>
  );
};

export default ResumeVersions;
