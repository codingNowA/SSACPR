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
  EyeOutlined,
  DeleteOutlined,
  ArrowLeftOutlined,
} from '@ant-design/icons';
import { getResumeVersions, getVersionDetail, deleteVersion } from '../../services/resume';
import { formatDate } from '../../utils';
import type { ResumeVersion } from '../../types';
import type { ColumnsType } from 'antd/es/table';

const { Title, Text } = Typography;

const ResumeVersions: React.FC = () => {
  const { resumeId } = useParams<{ resumeId: string }>();
  const navigate = useNavigate();

  const [versions, setVersions] = useState<any[]>([]);
  const [loading, setLoading] = useState(false);
  const [total, setTotal] = useState(0);
  const [page, setPage] = useState(1);
  const [pageSize, setPageSize] = useState(10);
  const [detailModalVisible, setDetailModalVisible] = useState(false);
  const [selectedVersion, setSelectedVersion] = useState<any>(null);

  useEffect(() => {
    if (resumeId) {
      loadVersions();
    }
  }, [resumeId, page, pageSize]);

  const loadVersions = async () => {
    if (!resumeId) return;

    setLoading(true);
    try {
      const response = await getResumeVersions(parseInt(resumeId), page, pageSize);
      console.log('=== Versions API Response:', response);
      console.log('=== Versions array:', response.versions);
      if (response.versions && response.versions.length > 0) {
        console.log('=== First version:', response.versions[0]);
      }
      setVersions(response.versions || []);
      setTotal(response.total || 0);
    } catch (error: any) {
      message.error(error || '加载版本列表失败');
    } finally {
      setLoading(false);
    }
  };

  const handleViewDetail = async (versionId: number) => {
    try {
      setDetailModalVisible(true);
      const detail = await getVersionDetail(versionId);
      console.log('Version detail:', detail);
      setSelectedVersion(detail);
    } catch (error: any) {
      setDetailModalVisible(false);
      message.error(error || '加载版本详情失败');
    }
  };

  const handleDelete = async (versionId: number) => {
    try {
      await deleteVersion(versionId);
      message.success('版本删除成功！');
      loadVersions();
    } catch (error: any) {
      message.error(error || '删除失败');
    }
  };

  const columns: ColumnsType<any> = [
    {
      title: '版本名称',
      dataIndex: 'version_name',
      key: 'version_name',
      render: (text) => <strong>{text}</strong>,
    },
    {
      title: '版本ID',
      dataIndex: 'id',
      key: 'id',
      render: (text) => <Tag color="blue">#{text}</Tag>,
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
            onClick={() => handleViewDetail(record.id)}
          >
            查看详情
          </Button>
          <Popconfirm
            title="确认删除此版本？"
            description="删除后无法恢复"
            onConfirm={() => handleDelete(record.id)}
            okText="确认"
            cancelText="取消"
          >
            <Button
              type="link"
              danger
              icon={<DeleteOutlined />}
            >
              删除
            </Button>
          </Popconfirm>
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
                <div style={{ color: 'rgba(0, 0, 0, 0.45)' }}>
                  简历ID: {resumeId} | 共 {total} 个版本
                </div>
              </div>
              <Button
                icon={<ArrowLeftOutlined />}
                onClick={() => navigate(`/resume/${resumeId}/diagnosis`)}
              >
                返回诊断
              </Button>
            </div>
          </Space>
        </Card>

        <Card>
          <Table
            columns={columns}
            dataSource={versions}
            rowKey="id"
            loading={loading}
            pagination={{
              current: page,
              pageSize: pageSize,
              total: total,
              showSizeChanger: true,
              showTotal: (total) => `共 ${total} 个版本`,
              onChange: (page, pageSize) => {
                setPage(page);
                setPageSize(pageSize);
              },
            }}
          />
        </Card>
      </Space>

      {/* 版本详情Modal */}
      <Modal
        title="版本详情"
        open={detailModalVisible}
        onCancel={() => {
          setDetailModalVisible(false);
          setSelectedVersion(null);
        }}
        footer={[
          <Button key="close" onClick={() => {
            setDetailModalVisible(false);
            setSelectedVersion(null);
          }}>
            关闭
          </Button>,
        ]}
        width={800}
        destroyOnClose
      >
        {selectedVersion && (
          <div style={{ padding: '16px' }}>
            <p><strong>版本名称：</strong> {selectedVersion.version_name || '未命名'}</p>
            <p><strong>创建时间：</strong> {selectedVersion.created_at ? formatDate(selectedVersion.created_at) : '未知'}</p>

            {selectedVersion.diagnostic_data?.scores && (
              <div style={{ marginTop: 16 }}>
                <strong>总分：</strong> {selectedVersion.diagnostic_data.scores.total_score}
              </div>
            )}

            <div style={{ marginTop: 16 }}>
              <strong>完整数据：</strong>
              <pre style={{
                marginTop: 8,
                padding: 12,
                background: '#f5f5f5',
                borderRadius: 4,
                maxHeight: 400,
                overflow: 'auto',
                fontSize: 12
              }}>
                {JSON.stringify(selectedVersion, null, 2)}
              </pre>
            </div>
          </div>
        )}
      </Modal>
    </div>
  );
};

export default ResumeVersions;
