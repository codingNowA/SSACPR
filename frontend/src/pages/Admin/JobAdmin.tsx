/**
 * 岗位管理页面
 */
import React, { useState, useEffect } from 'react';
import {
  Card,
  Table,
  Button,
  Space,
  Typography,
  Tag,
  Modal,
  Form,
  Input,
  Select,
  message,
  Popconfirm,
  Row,
  Col,
} from 'antd';
import {
  PlusOutlined,
  EditOutlined,
  DeleteOutlined,
  ReloadOutlined,
  SearchOutlined,
} from '@ant-design/icons';
import { getAdminJobs, createJob, updateJob, deleteJob } from '../../services/jobAdmin';
import type { ColumnsType } from 'antd/es/table';

const { Title, Text } = Typography;
const { Option } = Select;
const { TextArea } = Input;

const JobAdmin: React.FC = () => {
  const [form] = Form.useForm();
  const [searchForm] = Form.useForm();
  const [jobs, setJobs] = useState<any[]>([]);
  const [loading, setLoading] = useState(false);
  const [modalVisible, setModalVisible] = useState(false);
  const [editingJob, setEditingJob] = useState<any>(null);
  const [total, setTotal] = useState(0);
  const [page, setPage] = useState(1);
  const [pageSize, setPageSize] = useState(20);

  useEffect(() => {
    loadJobs();
  }, [page, pageSize]);

  const loadJobs = async (searchParams?: any) => {
    setLoading(true);
    try {
      const params = {
        page,
        page_size: pageSize,
        ...searchParams,
      };
      const response = await getAdminJobs(params);
      const data = response?.data || response;
      setJobs(data?.items || []);
      setTotal(data?.total || 0);
    } catch (error: any) {
      message.error(error || '加载岗位列表失败');
    } finally {
      setLoading(false);
    }
  };

  const handleSearch = (values: any) => {
    setPage(1);
    loadJobs(values);
  };

  const handleCreate = () => {
    setEditingJob(null);
    form.resetFields();
    setModalVisible(true);
  };

  const handleEdit = (record: any) => {
    setEditingJob(record);
    form.setFieldsValue(record);
    setModalVisible(true);
  };

  const handleSubmit = async () => {
    try {
      const values = await form.validateFields();
      if (editingJob) {
        await updateJob(editingJob.id, values);
        message.success('更新成功！');
      } else {
        await createJob(values);
        message.success('创建成功！');
      }
      setModalVisible(false);
      loadJobs();
    } catch (error: any) {
      message.error(error || '操作失败');
    }
  };

  const handleDelete = async (id: number) => {
    try {
      await deleteJob(id);
      message.success('删除成功！');
      loadJobs();
    } catch (error: any) {
      message.error(error || '删除失败');
    }
  };

  const columns: ColumnsType<any> = [
    {
      title: 'ID',
      dataIndex: 'id',
      key: 'id',
      width: 80,
    },
    {
      title: '岗位名称',
      dataIndex: 'title',
      key: 'title',
      width: 200,
      render: (text) => <Text strong>{text}</Text>,
    },
    {
      title: '公司',
      dataIndex: 'company',
      key: 'company',
      width: 150,
    },
    {
      title: '行业',
      dataIndex: 'industry',
      key: 'industry',
      width: 100,
    },
    {
      title: '地点',
      dataIndex: 'location',
      key: 'location',
      width: 100,
    },
    {
      title: '薪资',
      dataIndex: 'salary_range',
      key: 'salary_range',
      width: 120,
    },
    {
      title: '状态',
      dataIndex: 'status',
      key: 'status',
      width: 100,
      render: (status) => (
        <Tag color={status === 'active' ? 'green' : status === 'inactive' ? 'red' : 'default'}>
          {status === 'active' ? '激活' : status === 'inactive' ? '未激活' : '已过期'}
        </Tag>
      ),
    },
    {
      title: '操作',
      key: 'action',
      width: 150,
      fixed: 'right',
      render: (_, record) => (
        <Space size="small">
          <Button
            type="link"
            icon={<EditOutlined />}
            onClick={() => handleEdit(record)}
            size="small"
          >
            编辑
          </Button>
          <Popconfirm
            title="确认删除？"
            onConfirm={() => handleDelete(record.id)}
            okText="确认"
            cancelText="取消"
          >
            <Button type="link" danger icon={<DeleteOutlined />} size="small">
              删除
            </Button>
          </Popconfirm>
        </Space>
      ),
    },
  ];

  return (
    <div style={{ padding: '24px' }}>
      <Space direction="vertical" size="large" style={{ width: '100%' }}>
        {/* 头部 */}
        <Card>
          <Row justify="space-between" align="middle">
            <Col>
              <Title level={2}>岗位管理</Title>
              <Text type="secondary">管理岗位数据</Text>
            </Col>
            <Col>
              <Space>
                <Button icon={<ReloadOutlined />} onClick={() => loadJobs()}>
                  刷新
                </Button>
                <Button type="primary" icon={<PlusOutlined />} onClick={handleCreate}>
                  新建岗位
                </Button>
              </Space>
            </Col>
          </Row>
        </Card>

        {/* 搜索 */}
        <Card>
          <Form form={searchForm} onFinish={handleSearch} layout="inline">
            <Form.Item name="keyword">
              <Input placeholder="关键词搜索" style={{ width: 200 }} />
            </Form.Item>
            <Form.Item name="industry">
              <Select placeholder="行业" allowClear style={{ width: 120 }}>
                <Option value="互联网">互联网</Option>
                <Option value="金融">金融</Option>
                <Option value="教育">教育</Option>
              </Select>
            </Form.Item>
            <Form.Item name="location">
              <Input placeholder="地点" style={{ width: 120 }} />
            </Form.Item>
            <Form.Item name="status">
              <Select placeholder="状态" allowClear style={{ width: 120 }}>
                <Option value="active">激活</Option>
                <Option value="inactive">未激活</Option>
                <Option value="expired">已过期</Option>
              </Select>
            </Form.Item>
            <Form.Item>
              <Button type="primary" htmlType="submit" icon={<SearchOutlined />}>
                搜索
              </Button>
            </Form.Item>
          </Form>
        </Card>

        {/* 表格 */}
        <Card>
          <Table
            columns={columns}
            dataSource={jobs}
            rowKey="id"
            loading={loading}
            scroll={{ x: 1200 }}
            pagination={{
              current: page,
              pageSize: pageSize,
              total: total,
              showSizeChanger: true,
              showTotal: (total) => `共 ${total} 条`,
              onChange: (page, pageSize) => {
                setPage(page);
                setPageSize(pageSize);
              },
            }}
          />
        </Card>
      </Space>

      {/* 编辑/新建 Modal */}
      <Modal
        title={editingJob ? '编辑岗位' : '新建岗位'}
        open={modalVisible}
        onOk={handleSubmit}
        onCancel={() => setModalVisible(false)}
        width={800}
        destroyOnClose
      >
        <Form form={form} layout="vertical">
          <Row gutter={16}>
            <Col span={12}>
              <Form.Item name="title" label="岗位名称" rules={[{ required: true }]}>
                <Input />
              </Form.Item>
            </Col>
            <Col span={12}>
              <Form.Item name="company" label="公司" rules={[{ required: true }]}>
                <Input />
              </Form.Item>
            </Col>
          </Row>
          <Row gutter={16}>
            <Col span={8}>
              <Form.Item name="industry" label="行业">
                <Input />
              </Form.Item>
            </Col>
            <Col span={8}>
              <Form.Item name="location" label="地点">
                <Input />
              </Form.Item>
            </Col>
            <Col span={8}>
              <Form.Item name="salary_range" label="薪资范围">
                <Input placeholder="如：10-20K" />
              </Form.Item>
            </Col>
          </Row>
          <Row gutter={16}>
            <Col span={8}>
              <Form.Item name="experience_required" label="经验要求">
                <Input placeholder="如：3-5年" />
              </Form.Item>
            </Col>
            <Col span={8}>
              <Form.Item name="education_required" label="学历要求">
                <Select>
                  <Option value="不限">不限</Option>
                  <Option value="大专">大专</Option>
                  <Option value="本科">本科</Option>
                  <Option value="硕士">硕士</Option>
                  <Option value="博士">博士</Option>
                </Select>
              </Form.Item>
            </Col>
            <Col span={8}>
              <Form.Item name="status" label="状态">
                <Select>
                  <Option value="active">激活</Option>
                  <Option value="inactive">未激活</Option>
                </Select>
              </Form.Item>
            </Col>
          </Row>
          <Form.Item name="description" label="岗位描述">
            <TextArea rows={4} />
          </Form.Item>
          <Form.Item name="requirements" label="任职要求">
            <TextArea rows={4} />
          </Form.Item>
        </Form>
      </Modal>
    </div>
  );
};

export default JobAdmin;
