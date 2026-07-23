/**
 * 面试题库页面 - 浏览/搜索所有面试题
 */
import React, { useState, useEffect } from 'react';
import { Table, Input, Select, Tag, Card, Space, Typography, message, Button } from 'antd';
import { ReloadOutlined, SearchOutlined } from '@ant-design/icons';
import { listQuestions, Question } from '../../services/interview';

const { Title } = Typography;

const difficultyMap: Record<string, { label: string; color: string }> = {
  easy: { label: '简单', color: 'green' },
  medium: { label: '中等', color: 'orange' },
  hard: { label: '困难', color: 'red' },
};

const QuestionBank: React.FC = () => {
  const [questions, setQuestions] = useState<Question[]>([]);
  const [loading, setLoading] = useState(false);
  const [category, setCategory] = useState<string | undefined>(undefined);
  const [difficulty, setDifficulty] = useState<string | undefined>(undefined);
  const [keyword, setKeyword] = useState('');
  const [pagination, setPagination] = useState({
    current: 1,
    pageSize: 20,
    total: 0,
  });

  useEffect(() => {
    loadQuestions();
  }, [category, difficulty, pagination.current, pagination.pageSize]);

  const loadQuestions = async () => {
    setLoading(true);
    try {
      const params: any = {
        page: pagination.current,
        page_size: pagination.pageSize,
      };
      if (category) params.category = category;
      if (difficulty) params.difficulty = difficulty;
      if (keyword) params.keyword = keyword;

      const response = await listQuestions(params);
      const data = response.data || [];
      setQuestions(data);
      setPagination(prev => ({
        ...prev,
        total: response.total || 0,
      }));
    } catch (error: any) {
      console.error('加载题目失败:', error);
      message.error('加载题库失败');
      setQuestions([]);
    } finally {
      setLoading(false);
    }
  };

  const handleSearch = () => {
    setPagination(prev => ({ ...prev, current: 1 }));
    loadQuestions();
  };

  const handleTableChange = (pag: any) => {
    setPagination({
      current: pag.current || 1,
      pageSize: pag.pageSize || 20,
      total: pagination.total,
    });
  };

  const columns = [
    { title: 'ID', dataIndex: 'id', key: 'id', width: 60 },
    {
      title: '题目内容',
      dataIndex: 'question_text',
      key: 'question_text',
      ellipsis: true,
    },
    {
      title: '分类',
      dataIndex: 'category',
      key: 'category',
      width: 120,
      render: (c: string) => (c && c !== '未分类' ? <Tag>{c}</Tag> : <Tag>未分类</Tag>),
    },
    {
      title: '难度',
      dataIndex: 'difficulty',
      key: 'difficulty',
      width: 80,
      render: (d: string) => {
        const info = difficultyMap[d] || { label: d || '未知', color: 'default' };
        return <Tag color={info.color}>{info.label}</Tag>;
      },
    },
    {
      title: '参考答案',
      dataIndex: 'reference_answer',
      key: 'reference_answer',
      ellipsis: true,
      render: (t: string) => t || '-',
    },
  ];

  return (
    <div style={{ padding: 24 }}>
      <Card>
        <Title level={3}>面试题库</Title>
        <Space style={{ marginBottom: 16 }} wrap>
          <Select
            placeholder="分类筛选"
            allowClear
            onChange={(v) => {
              setCategory(v);
              setPagination(prev => ({ ...prev, current: 1 }));
            }}
            style={{ width: 150 }}
            options={[
              { value: '综合', label: '综合' },
              { value: '技术', label: '技术' },
              { value: '行为', label: '行为' },
              { value: '项目', label: '项目' },
            ]}
          />
          <Select
            placeholder="难度筛选"
            allowClear
            onChange={(v) => {
              setDifficulty(v);
              setPagination(prev => ({ ...prev, current: 1 }));
            }}
            style={{ width: 150 }}
            options={[
              { value: 'easy', label: '简单' },
              { value: 'medium', label: '中等' },
              { value: 'hard', label: '困难' },
            ]}
          />
          <Input.Search
            placeholder="搜索题目"
            allowClear
            value={keyword}
            onChange={(e) => setKeyword(e.target.value)}
            onSearch={handleSearch}
            style={{ width: 250 }}
            enterButton={<SearchOutlined />}
          />
          <Button icon={<ReloadOutlined />} onClick={loadQuestions}>
            刷新
          </Button>
        </Space>

        <Table
          columns={columns}
          dataSource={questions}
          rowKey="id"
          loading={loading}
          pagination={{
            current: pagination.current,
            pageSize: pagination.pageSize,
            total: pagination.total,
            showSizeChanger: true,
            showTotal: (total) => `共 ${total} 道题`,
          }}
          onChange={handleTableChange}
        />
      </Card>
    </div>
  );
};

export default QuestionBank;
