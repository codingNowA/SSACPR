/**
 * 面试题库页面 - 浏览/搜索所有面试题
 */
import React, { useState, useEffect } from 'react';
import { Table, Input, Select, Tag, Card, Space, Typography } from 'antd';
import { SearchOutlined } from '@ant-design/icons';
import axios from 'axios';

const { Title } = Typography;
const { Search } = Input;

interface Question {
  id: number;
  content: string;
  category: string;
  difficulty: string;
  answer_points?: string;
}

const difficultyMap: Record<string, { label: string; color: string }> = {
  easy: { label: '简单', color: 'green' },
  medium: { label: '中等', color: 'orange' },
  hard: { label: '困难', color: 'red' },
};

const QuestionBank: React.FC = () => {
  const [questions, setQuestions] = useState<Question[]>([]);
  const [loading, setLoading] = useState(false);
  const [total, setTotal] = useState(0);
  const [page, setPage] = useState(1);
  const [pageSize, setPageSize] = useState(20);
  const [keyword, setKeyword] = useState('');
  const [category, setCategory] = useState<string | undefined>(undefined);
  const [difficulty, setDifficulty] = useState<string | undefined>(undefined);

  useEffect(() => {
    loadQuestions();
  }, [page, pageSize, category, difficulty]);

  const loadQuestions = async () => {
    setLoading(true);
    try {
      const response = await axios.get('/api/v1/admin/questions', {
        params: { page, page_size: pageSize, category, difficulty, keyword },
      });
      const data = response.data?.data || response.data;
      setQuestions(data?.items || data?.questions || []);
      setTotal(data?.total || 0);
    } catch (error) {
      console.error('加载题目失败:', error);
    } finally {
      setLoading(false);
    }
  };

  const columns = [
    { title: 'ID', dataIndex: 'id', key: 'id', width: 60 },
    {
      title: '题目内容',
      dataIndex: 'content',
      key: 'content',
      ellipsis: true,
    },
    {
      title: '分类',
      dataIndex: 'category',
      key: 'category',
      width: 120,
      render: (c: string) => (c ? <Tag>{c}</Tag> : '-'),
    },
    {
      title: '难度',
      dataIndex: 'difficulty',
      key: 'difficulty',
      width: 80,
      render: (d: string) => {
        const info = difficultyMap[d] || { label: d, color: 'default' };
        return <Tag color={info.color}>{info.label}</Tag>;
      },
    },
    {
      title: '参考要点',
      dataIndex: 'answer_points',
      key: 'answer_points',
      ellipsis: true,
      render: (t: string) => t || '-',
    },
  ];

  return (
    <div style={{ padding: 24 }}>
      <Card>
        <Title level={3}>面试题库</Title>
        <Space style={{ marginBottom: 16 }} wrap>
          <Search
            placeholder="搜索题目"
            allowClear
            onSearch={(v) => {
              setKeyword(v);
              setPage(1);
              loadQuestions();
            }}
            style={{ width: 300 }}
          />
          <Select
            placeholder="分类筛选"
            allowClear
            onChange={(v) => {
              setCategory(v);
              setPage(1);
            }}
            style={{ width: 150 }}
            options={[
              { value: '综合', label: '综合' },
              { value: '技术', label: '技术' },
              { value: '项目', label: '项目' },
              { value: '行为', label: '行为' },
            ]}
          />
          <Select
            placeholder="难度筛选"
            allowClear
            onChange={(v) => {
              setDifficulty(v);
              setPage(1);
            }}
            style={{ width: 120 }}
            options={[
              { value: 'easy', label: '简单' },
              { value: 'medium', label: '中等' },
              { value: 'hard', label: '困难' },
            ]}
          />
        </Space>
        <Table
          columns={columns}
          dataSource={questions}
          rowKey="id"
          loading={loading}
          pagination={{
            current: page,
            pageSize,
            total,
            onChange: (p, ps) => {
              setPage(p);
              setPageSize(ps);
            },
            showTotal: (t) => `共 ${t} 题`,
          }}
        />
      </Card>
    </div>
  );
};

export default QuestionBank;
