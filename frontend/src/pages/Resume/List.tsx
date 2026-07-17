/**
 * 我的简历列表页面
 */
import React, { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import {
  Card,
  Table,
  Button,
  Space,
  Typography,
  Tag,
  message,
  Popconfirm,
  Empty,
  Tooltip,
} from 'antd';
import {
  FileTextOutlined,
  EyeOutlined,
  DeleteOutlined,
  HistoryOutlined,
  StarOutlined,
  StarFilled,
  PlusOutlined,
} from '@ant-design/icons';
import apiClient from '../../services/api';
import { useStore } from '../../store';
import { formatDate } from '../../utils';
import type { ColumnsType } from 'antd/es/table';

const { Title, Text } = Typography;

interface Resume {
  id: number;
  file_path: string;
  file_type: string;
  version: number;
  status: string;
  created_at: string;
  updated_at: string;
}

const ResumeList: React.FC = () => {
  const navigate = useNavigate();
  const { currentResumeId, setCurrentResumeId } = useStore();
  const [resumes, setResumes] = useState<Resume[]>([]);
  const [loading, setLoading] = useState(false);
  const [total, setTotal] = useState(0);
  const [page, setPage] = useState(1);
  const [pageSize, setPageSize] = useState(10);

  useEffect(() => {
    loadResumes();
  }, [page, pageSize]);

  const loadResumes = async () => {
    setLoading(true);
    try {
      const response = await apiClient.get('/api/v1/resume/list', {
        params: { page, page_size: pageSize },
      });

      if (response && typeof response === 'object') {
        setResumes(response.items || []);
        setTotal(response.total || 0);
      }
    } catch (error: any) {
      message.error(error || '加载简历列表失败');
    } finally {
      setLoading(false);
    }
  };

  const handleSetCurrent = (resumeId: number) => {
    setCurrentResumeId(resumeId);
    message.success('已设置为当前简历');
  };

  const handleDelete = async (resumeId: number) => {
    try {
      await apiClient.delete(`/api/v1/resume/${resumeId}`);
      message.success('删除成功');
      if (currentResumeId === resumeId) {
        setCurrentResumeId(null);
      }
      loadResumes();
    } catch (error: any) {
      message.error(error || '删除失败');
    }
  };

  const getFileName = (filePath: string) => {
    return filePath.split('/').pop() || filePath;
  };

  const columns: ColumnsType<Resume> = [
    {
      title: '简历文件',
      dataIndex: 'file_path',
      key: 'file_path',
      render: (path: string, record: Resume) => (
        <Space>
          {record.id === currentResumeId && (
            <StarFilled style={{ color: '#faad14' }} />
          )}
          <FileTextOutlined />
          <Text>{getFileName(path)}</Text>
        </Space>
      ),
    },
    {
      title: '文件类型',
      dataIndex: 'file_type',
      key: 'file_type',
      width: 100,
      render: (type: string) => {
        const colorMap: Record<string, string> = {
          pdf: 'red',
          docx: 'blue',
          doc: 'blue',
          png: 'green',
          jpg: 'green',
          jpeg: 'green',
        };
        return <Tag color={colorMap[type] || 'default'}>{type.toUpperCase()}</Tag>;
      },
    },
    {
      title: '状态',
      dataIndex: 'status',
      key: 'status',
      width: 100,
      render: (status: string) => {
        const config: Record<string, { color: string; text: string }> = {
          draft: { color: 'default', text: '草稿' },
          active: { color: 'success', text: '活跃' },
          archived: { color: 'warning', text: '已归档' },
        };
        const { color, text } = config[status] || { color: 'default', text: status };
        return <Tag color={color}>{text}</Tag>;
      },
    },
    {
      title: '版本数',
      dataIndex: 'version',
      key: 'version',
      width: 80,
      align: 'center',
    },
    {
      title: '上传时间',
      dataIndex: 'created_at',
      key: 'created_at',
      width: 180,
      render: (date: string) => formatDate(date),
    },
    {
      title: '操作',
      key: 'action',
      width: 260,
      render: (_, record: Resume) => (
        <Space>
          {record.id !== currentResumeId && (
            <Tooltip title="设置为当前简历">
              <Button
                type="link"
                size="small"
                icon={<StarOutlined />}
                onClick={() => handleSetCurrent(record.id)}
              >
                设为当前
              </Button>
            </Tooltip>
          )}
          <Button
            type="link"
            size="small"
            icon={<EyeOutlined />}
            onClick={() => navigate(`/resume/diagnosis/${record.id}`)}
          >
            查看诊断
          </Button>
          <Button
            type="link"
            size="small"
            icon={<HistoryOutlined />}
            onClick={() => navigate(`/resume/versions/${record.id}`)}
          >
            版本历史
          </Button>
          <Popconfirm
            title="确定删除这份简历吗？"
            description="删除后将无法恢复，包括所有版本记录"
            onConfirm={() => handleDelete(record.id)}
            okText="确定"
            cancelText="取消"
          >
            <Button type="link" size="small" danger icon={<DeleteOutlined />}>
              删除
            </Button>
          </Popconfirm>
        </Space>
      ),
    },
  ];

  return (
    <div style={{ padding: '24px', maxWidth: '1400px', margin: '0 auto' }}>
      <Card>
        <Space direction="vertical" size="large" style={{ width: '100%' }}>
          {/* 头部 */}
          <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
            <div>
              <Title level={2}>
                <FileTextOutlined /> 我的简历
              </Title>
              <Text type="secondary">
                管理你的所有简历，查看诊断结果和版本历史
                {currentResumeId && (
                  <Tag color="gold" style={{ marginLeft: 8 }}>
                    <StarFilled /> 当前简历 ID: {currentResumeId}
                  </Tag>
                )}
              </Text>
            </div>
            <Button
              type="primary"
              icon={<PlusOutlined />}
              onClick={() => navigate('/resume/upload')}
            >
              上传新简历
            </Button>
          </div>

          {/* 表格 */}
          <Table
            columns={columns}
            dataSource={resumes}
            rowKey="id"
            loading={loading}
            pagination={{
              current: page,
              pageSize: pageSize,
              total: total,
              showSizeChanger: true,
              showQuickJumper: true,
              showTotal: (total) => `共 ${total} 份简历`,
              onChange: (page, pageSize) => {
                setPage(page);
                setPageSize(pageSize);
              },
            }}
            locale={{
              emptyText: (
                <Empty
                  description="还没有上传简历"
                  image={Empty.PRESENTED_IMAGE_SIMPLE}
                >
                  <Button type="primary" onClick={() => navigate('/resume/upload')}>
                    立即上传
                  </Button>
                </Empty>
              ),
            }}
          />
        </Space>
      </Card>
    </div>
  );
};

export default ResumeList;
