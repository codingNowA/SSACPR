/**
 * 题库管理页面
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
  UploadOutlined,
} from '@ant-design/icons';
import { getQuestions, createQuestion, updateQuestion, deleteQuestion } from '../../services/question';
import { Upload } from 'antd';
import type { ColumnsType } from 'antd/es/table';

const { Title, Text } = Typography;
const { Option } = Select;
const { TextArea } = Input;

const QuestionAdmin: React.FC = () => {
  const [form] = Form.useForm();
  const [searchForm] = Form.useForm();
  const [questions, setQuestions] = useState<any[]>([]);
  const [loading, setLoading] = useState(false);
  const [modalVisible, setModalVisible] = useState(false);
  const [editingQuestion, setEditingQuestion] = useState<any>(null);
  const [total, setTotal] = useState(0);
  const [page, setPage] = useState(1);
  const [pageSize, setPageSize] = useState(20);

  useEffect(() => {
    loadQuestions();
  }, [page, pageSize]);

  const loadQuestions = async (searchParams?: any) => {
    setLoading(true);
    try {
      const params = {
        page,
        page_size: pageSize,
        ...searchParams,
      };
      const response = await getQuestions(params);
      const data = response?.data || response;
      setQuestions(data?.items || []);
      setTotal(data?.total || 0);
    } catch (error: any) {
      message.error(error || '加载题目列表失败');
    } finally {
      setLoading(false);
    }
  };

  const handleSearch = (values: any) => {
    setPage(1);
    loadQuestions(values);
  };

  const handleBatchImportQuestions = async (file: any) => {
    const formData = new FormData();
    formData.append('file', file);
    try {
      const res = await fetch('/api/v1/questions/batch-import', {
        method: 'POST',
        headers: {
          Authorization: `Bearer ${localStorage.getItem('token')}`,
        },
        body: formData,
      });
      const data = await res.json();
      if (res.ok) {
        message.success(data?.message || '导入成功');
        loadQuestions();
      } else {
        message.error(data?.detail || '导入失败');
      }
    } catch (e: any) {
      message.error('导入失败: ' + (e.message || '网络错误'));
    }
    return false;
  };

  const handleCreate = () => {
    setEditingQuestion(null);
    form.resetFields();
    setModalVisible(true);
  };

  const handleEdit = (record: any) => {
    setEditingQuestion(record);
    // 映射字段名：后端 question/answer_points/related_skills -> 前端 content/answer/tags
    form.setFieldsValue({
      content: record.question,
      answer: record.answer_points,
      category: record.category,
      difficulty: record.difficulty,
      tags: record.related_skills ? record.related_skills.join(', ') : ''
    });
    setModalVisible(true);
  };

  const handleSubmit = async () => {
    try {
      const values = await form.validateFields();
      // 映射字段名：前端 content/answer/tags -> 后端 question/answer_points/related_skills
      const payload = {
        question: values.content,
        answer_points: values.answer,
        category: values.category,
        difficulty: values.difficulty,
        related_skills: values.tags ? values.tags.split(',').map((t: string) => t.trim()) : []
      };
      if (editingQuestion) {
        await updateQuestion(editingQuestion.id, payload);
        message.success('更新成功！');
      } else {
        await createQuestion(payload);
        message.success('创建成功！');
      }
      setModalVisible(false);
      loadQuestions();
    } catch (error: any) {
      message.error(error || '操作失败');
    }
  };

  const handleDelete = async (id: number) => {
    try {
      await deleteQuestion(id);
      message.success('删除成功！');
      loadQuestions();
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
      title: '题目内容',
      dataIndex: 'question',
      key: 'question',
      width: 300,
      ellipsis: true,
      render: (text) => <Text strong>{text}</Text>,
    },
    {
      title: '分类',
      dataIndex: 'category',
      key: 'category',
      width: 120,
    },
    {
      title: '难度',
      dataIndex: 'difficulty',
      key: 'difficulty',
      width: 100,
      render: (difficulty) => (
        <Tag color={difficulty === 'easy' ? 'green' : difficulty === 'medium' ? 'orange' : 'red'}>
          {difficulty === 'easy' ? '简单' : difficulty === 'medium' ? '中等' : '困难'}
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
              <Title level={2}>题库管理</Title>
              <Text type="secondary">管理面试题目</Text>
            </Col>
            <Col>
              <Space>
                <Button icon={<ReloadOutlined />} onClick={() => loadQuestions()}>
                  刷新
                </Button>
                <Button type="primary" icon={<PlusOutlined />} onClick={handleCreate}>
                  新建题目
                </Button>
                <Upload
                  accept=".xlsx,.xls"
                  showUploadList={false}
                  beforeUpload={handleBatchImportQuestions}
                >
                  <Button icon={<UploadOutlined />}>批量导入题库</Button>
                </Upload>
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
            <Form.Item name="category">
              <Input placeholder="分类" style={{ width: 120 }} />
            </Form.Item>
            <Form.Item name="difficulty">
              <Select placeholder="难度" allowClear style={{ width: 120 }}>
                <Option value="easy">简单</Option>
                <Option value="medium">中等</Option>
                <Option value="hard">困难</Option>
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
            dataSource={questions}
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

      {/* 编辑/新建 Modal */}
      <Modal
        title={editingQuestion ? '编辑题目' : '新建题目'}
        open={modalVisible}
        onOk={handleSubmit}
        onCancel={() => setModalVisible(false)}
        width={800}
        destroyOnClose
      >
        <Form form={form} layout="vertical">
          <Form.Item name="content" label="题目内容" rules={[{ required: true }]}>
            <TextArea rows={4} />
          </Form.Item>
          <Row gutter={16}>
            <Col span={12}>
              <Form.Item name="category" label="分类" rules={[{ required: true }]}>
                <Input placeholder="如：技术、行为、综合" />
              </Form.Item>
            </Col>
            <Col span={12}>
              <Form.Item name="difficulty" label="难度" rules={[{ required: true }]}>
                <Select>
                  <Option value="easy">简单</Option>
                  <Option value="medium">中等</Option>
                  <Option value="hard">困难</Option>
                </Select>
              </Form.Item>
            </Col>
          </Row>
          <Form.Item name="answer" label="参考答案">
            <TextArea rows={6} />
          </Form.Item>
          <Form.Item name="tags" label="标签（逗号分隔）">
            <Input placeholder="如：Python,算法,数据结构" />
          </Form.Item>
        </Form>
      </Modal>
    </div>
  );
};

export default QuestionAdmin;
