/**
 * 岗位中心页面 - 支持难度排序
 */
import React, { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import {
  Card,
  Table,
  Input,
  Select,
  Space,
  Button,
  Tag,
  Typography,
  message,
  Progress,
  Tooltip,
} from 'antd';
import {
  SearchOutlined,
  EnvironmentOutlined,
  DollarOutlined,
  TrophyOutlined,
} from '@ant-design/icons';
import axios from 'axios';
import type { ColumnsType } from 'antd/es/table';

const { Search } = Input;
const { Option } = Select;
const { Title, Text } = Typography;

interface Job {
  id: number;
  title: string;
  company: string;
  industry?: string;
  location?: string;
  salary_range?: string;
  experience_required?: string;
  education_required?: string;
  description?: string;
  requirements?: string;
  status: string;
  created_at: string;
  difficulty?: {
    total_score: number;
    level: string;
    dimensions: {
      skill_complexity: number;
      experience: number;
      education: number;
      salary: number;
      company: number;
    };
  };
}

const getDifficultyColor = (score: number): string => {
  if (score >= 80) return '#f5222d';
  if (score >= 65) return '#fa8c16';
  if (score >= 50) return '#faad14';
  if (score >= 35) return '#52c41a';
  return '#1890ff';
};

const JobCenter: React.FC = () => {
  const navigate = useNavigate();
  const [jobs, setJobs] = useState<Job[]>([]);
  const [loading, setLoading] = useState(false);
  const [total, setTotal] = useState(0);
  const [page, setPage] = useState(1);
  const [pageSize, setPageSize] = useState(20);
  const [keyword, setKeyword] = useState('');
  const [industry, setIndustry] = useState<string | undefined>(undefined);
  const [location, setLocation] = useState<string | undefined>(undefined);
  const [sortBy, setSortBy] = useState<string>('created_at');

  useEffect(() => {
    loadJobs();
  }, [page, pageSize, industry, location, sortBy]);

  const loadJobs = async () => {
    setLoading(true);
    try {
      const params: any = {
        page,
        page_size: pageSize,
      };
      if (keyword) params.keyword = keyword;
      if (industry) params.industry = industry;
      if (location) params.location = location;
      if (sortBy) params.sort_by = sortBy;

      const response = await axios.get('/api/v1/jobs/center', { params });

      const respData = response.data;
      setJobs(respData?.data || []);
      setTotal(respData?.total || 0);
    } catch (error: any) {
      console.error('加载岗位列表失败:', error);
      message.error('加载岗位列表失败');
      setJobs([]);
      setTotal(0);
    } finally {
      setLoading(false);
    }
  };

  const handleSearch = () => {
    setPage(1);
    loadJobs();
  };

  const columns: ColumnsType<Job> = [
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
      title: '地点',
      dataIndex: 'location',
      key: 'location',
      width: 100,
      render: (text) => text ? <Tag icon={<EnvironmentOutlined />}>{text}</Tag> : '-',
    },
    {
      title: '薪资',
      dataIndex: 'salary_range',
      key: 'salary_range',
      width: 120,
      render: (text) => text ? <Tag icon={<DollarOutlined />} color="green">{text}</Tag> : '-',
    },
    {
      title: '经验要求',
      dataIndex: 'experience_required',
      key: 'experience_required',
      width: 100,
      render: (text) => text || '-',
    },
    {
      title: '学历要求',
      dataIndex: 'education_required',
      key: 'education_required',
      width: 100,
      render: (text) => text || '-',
    },
    {
      title: '岗位难度',
      key: 'difficulty',
      width: 150,
      render: (_, record) => {
        if (!record.difficulty) return '-';
        const { total_score, level } = record.difficulty;
        return (
          <Tooltip
            title={
              <div>
                <div>技能复杂度: {record.difficulty.dimensions.skill_complexity}</div>
                <div>经验要求: {record.difficulty.dimensions.experience}</div>
                <div>学历要求: {record.difficulty.dimensions.education}</div>
                <div>薪资水平: {record.difficulty.dimensions.salary}</div>
                <div>公司知名度: {record.difficulty.dimensions.company}</div>
              </div>
            }
          >
            <Space direction="vertical" size="small" style={{ width: '100%' }}>
              <Progress
                percent={total_score}
                size="small"
                strokeColor={getDifficultyColor(total_score)}
                format={(p) => `${p}`}
              />
              <Tag color={getDifficultyColor(total_score)} icon={<TrophyOutlined />}>
                {level}
              </Tag>
            </Space>
          </Tooltip>
        );
      },
    },
    {
      title: '操作',
      key: 'action',
      width: 100,
      render: (_, record) => (
        <Button type="link" onClick={() => navigate(`/job/${record.id}`)}>
          查看详情
        </Button>
      ),
    },
  ];

  return (
    <div style={{ padding: '24px', maxWidth: '1400px', margin: '0 auto' }}>
      <Card>
        <Space direction="vertical" size="large" style={{ width: '100%' }}>
          <div>
            <Title level={2}>岗位中心</Title>
            <Text type="secondary">浏览和搜索职位信息，支持按难度排序</Text>
          </div>

          <Space size="middle" wrap>
            <Search
              placeholder="搜索岗位、公司或关键词"
              value={keyword}
              onChange={(e) => setKeyword(e.target.value)}
              onSearch={handleSearch}
              style={{ width: 300 }}
              enterButton={<SearchOutlined />}
            />
            <Select
              placeholder="选择行业"
              value={industry}
              onChange={(value) => {
                setIndustry(value);
                setPage(1);
              }}
              style={{ width: 150 }}
              allowClear
            >
              <Option value="互联网">互联网</Option>
              <Option value="金融">金融</Option>
              <Option value="教育">教育</Option>
              <Option value="医疗">医疗</Option>
              <Option value="制造业">制造业</Option>
            </Select>
            <Select
              placeholder="选择地点"
              value={location}
              onChange={(value) => {
                setLocation(value);
                setPage(1);
              }}
              style={{ width: 150 }}
              allowClear
            >
              <Option value="北京">北京</Option>
              <Option value="上海">上海</Option>
              <Option value="深圳">深圳</Option>
              <Option value="杭州">杭州</Option>
              <Option value="广州">广州</Option>
              <Option value="成都">成都</Option>
            </Select>
            <Select
              placeholder="排序方式"
              value={sortBy}
              onChange={(value) => {
                setSortBy(value);
                setPage(1);
              }}
              style={{ width: 180 }}
            >
              <Option value="created_at">发布时间</Option>
              <Option value="difficulty_asc">难度：简单到困难</Option>
              <Option value="difficulty_desc">难度：困难到简单</Option>
            </Select>
          </Space>

          <Table
            columns={columns}
            dataSource={jobs}
            rowKey="id"
            loading={loading}
            pagination={{
              current: page,
              pageSize: pageSize,
              total: total,
              showSizeChanger: true,
              showTotal: (total) => `共 ${total} 个岗位`,
              onChange: (page, pageSize) => {
                setPage(page);
                setPageSize(pageSize);
              },
            }}
          />
        </Space>
      </Card>
    </div>
  );
};

export default JobCenter;
