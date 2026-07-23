/**
 * 日志查询页面
 */
import React, { useState, useEffect } from 'react';
import {
  Card,
  Table,
  Button,
  Space,
  Typography,
  Tag,
  Form,
  Input,
  Select,
  DatePicker,
  message,
  Row,
  Col,
  Descriptions,
  Modal,
} from 'antd';
import {
  ReloadOutlined,
  SearchOutlined,
  EyeOutlined,
} from '@ant-design/icons';
import { getLogs } from '../../services/log';
import { formatDate } from '../../utils';
import type { ColumnsType } from 'antd/es/table';

const { Title, Text } = Typography;
const { Option } = Select;
const { RangePicker } = DatePicker;

const LogQuery: React.FC = () => {
  const [searchForm] = Form.useForm();
  const [logs, setLogs] = useState<any[]>([]);
  const [loading, setLoading] = useState(false);
  const [total, setTotal] = useState(0);
  const [page, setPage] = useState(1);
  const [pageSize, setPageSize] = useState(20);
  const [detailModalVisible, setDetailModalVisible] = useState(false);
  const [selectedLog, setSelectedLog] = useState<any>(null);

  useEffect(() => {
    loadLogs();
  }, [page, pageSize]);

  const loadLogs = async (searchParams?: any) => {
    setLoading(true);
    try {
      const params = {
        page,
        page_size: pageSize,
        ...searchParams,
      };
      const response = await getLogs(params);
      const data = response?.data || response;
      setLogs(data?.items || []);
      setTotal(data?.total || 0);
    } catch (error: any) {
      message.error(error || '加载日志列表失败');
    } finally {
      setLoading(false);
    }
  };

  const handleSearch = (values: any) => {
    const params: any = { ...values };
    if (values.dateRange) {
      params.start_date = values.dateRange[0].format('YYYY-MM-DD');
      params.end_date = values.dateRange[1].format('YYYY-MM-DD');
      delete params.dateRange;
    }
    setPage(1);
    loadLogs(params);
  };

  const handleViewDetail = async (record: any) => {
    setSelectedLog(record);
    setDetailModalVisible(true);
  };

  const columns: ColumnsType<any> = [
    {
      title: 'ID',
      dataIndex: 'id',
      key: 'id',
      width: 80,
    },
    {
      title: '用户ID',
      dataIndex: 'user_id',
      key: 'user_id',
      width: 100,
    },
    {
      title: '操作',
      dataIndex: 'action',
      key: 'action',
      width: 120,
      render: (action) => {
        const colorMap: any = {
          CREATE: 'green',
          UPDATE: 'blue',
          DELETE: 'red',
          LOGIN: 'cyan',
          LOGOUT: 'default',
        };
        return <Tag color={colorMap[action] || 'default'}>{action}</Tag>;
      },
    },
    {
      title: '模块',
      dataIndex: 'module',
      key: 'module',
      width: 120,
    },
    {
      title: 'IP地址',
      dataIndex: 'ip_address',
      key: 'ip_address',
      width: 150,
    },
    {
      title: '时间',
      dataIndex: 'created_at',
      key: 'created_at',
      width: 180,
      render: (text) => formatDate(text),
    },
    {
      title: '操作',
      key: 'operation',
      width: 100,
      fixed: 'right',
      render: (_, record) => (
        <Button
          type="link"
          icon={<EyeOutlined />}
          onClick={() => handleViewDetail(record)}
          size="small"
        >
          查看
        </Button>
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
              <Title level={2}>日志查询</Title>
              <Text type="secondary">查看系统操作日志</Text>
            </Col>
            <Col>
              <Button icon={<ReloadOutlined />} onClick={() => loadLogs()}>
                刷新
              </Button>
            </Col>
          </Row>
        </Card>

        {/* 搜索 */}
        <Card>
          <Form form={searchForm} onFinish={handleSearch} layout="inline">
            <Form.Item name="keyword">
              <Input placeholder="关键词搜索" style={{ width: 200 }} />
            </Form.Item>
            <Form.Item name="user_id">
              <Input placeholder="用户ID" style={{ width: 120 }} />
            </Form.Item>
            <Form.Item name="action">
              <Select placeholder="操作类型" allowClear style={{ width: 120 }}>
                <Option value="CREATE">CREATE</Option>
                <Option value="UPDATE">UPDATE</Option>
                <Option value="DELETE">DELETE</Option>
                <Option value="LOGIN">LOGIN</Option>
                <Option value="LOGOUT">LOGOUT</Option>
              </Select>
            </Form.Item>
            <Form.Item name="module">
              <Select placeholder="模块" allowClear style={{ width: 120 }}>
                <Option value="job">job</Option>
                <Option value="question">question</Option>
                <Option value="user">user</Option>
                <Option value="analytics">analytics</Option>
              </Select>
            </Form.Item>
            <Form.Item name="dateRange">
              <RangePicker />
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
            dataSource={logs}
            rowKey="id"
            loading={loading}
            scroll={{ x: 1000 }}
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

      {/* 详情 Modal */}
      <Modal
        title="日志详情"
        open={detailModalVisible}
        onCancel={() => setDetailModalVisible(false)}
        footer={[
          <Button key="close" onClick={() => setDetailModalVisible(false)}>
            关闭
          </Button>,
        ]}
        width={700}
      >
        {selectedLog && (
          <Descriptions column={2} bordered>
            <Descriptions.Item label="ID">{selectedLog.id}</Descriptions.Item>
            <Descriptions.Item label="用户ID">{selectedLog.user_id}</Descriptions.Item>
            <Descriptions.Item label="操作类型">
              <Tag>{selectedLog.action}</Tag>
            </Descriptions.Item>
            <Descriptions.Item label="模块">{selectedLog.module}</Descriptions.Item>
            <Descriptions.Item label="IP地址">{selectedLog.ip_address}</Descriptions.Item>
            <Descriptions.Item label="时间">{formatDate(selectedLog.created_at)}</Descriptions.Item>
            <Descriptions.Item label="详情" span={2}>
              <pre style={{ margin: 0, whiteSpace: 'pre-wrap' }}>
                {JSON.stringify(selectedLog.details, null, 2)}
              </pre>
            </Descriptions.Item>
          </Descriptions>
        )}
      </Modal>
    </div>
  );
};

export default LogQuery;
