/**
 * 岗位列表页面
 */
import React, { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import {
  Card,
  Table,
  Tag,
  Button,
  Space,
  Input,
  Select,
  message,
  Typography,
} from 'antd';
import {
  SearchOutlined,
  EnvironmentOutlined,
  DollarOutlined,
  FileSearchOutlined,
} from '@ant-design/icons';
import apiClient from '../../services/api';

const { Title } = Typography;
const { Search } = Input;
const { Option } = Select;

interface Job {
  id: number;
  title: string;
  company: string;
  industry?: string;
  location: string;
  salary_range: string;
  experience_required?: string;
  education_required?: string;
  status: string;
  created_at: string;
}

const JobList: React.FC = () => {
  const navigate = useNavigate();
  const [loading, setLoading] = useState(false);
  const [jobs, setJobs] = useState<Job[]>([]);
  const [total, setTotal] = useState(0);
  const [currentPage, setCurrentPage] = useState(1);
  const [pageSize, setPageSize] = useState(10);

  // 筛选条件
  const [keyword, setKeyword] = useState('');
  const [industry, setIndustry] = useState<string | undefined>(undefined);
  const [location, setLocation] = useState<string | undefined>(undefined);

  useEffect(() => {
    loadJobs();
  }, [currentPage, pageSize]);

  const loadJobs = async () => {
    setLoading(true);
    try {
      const params: any = {
        page: currentPage,
        page_size: pageSize,
        status: 'active', // 只显示活跃岗位
      };

      if (keyword) params.keyword = keyword;
      if (industry) params.industry = industry;
      if (location) params.location = location;

      const response = await apiClient.get('/api/v1/job/list', { params });

      // API 客户端的响应拦截器已经解包了 {code, data}，直接使用响应数据
      if (response && typeof response === 'object') {
        setJobs(response.items || []);
        setTotal(response.total || 0);
      } else {
        message.error('加载岗位列表失败');
      }
    } catch (error: any) {
      message.error(error?.message || '加载岗位列表失败');
    } finally {
      setLoading(false);
    }
  };

  const handleSearch = () => {
    setCurrentPage(1);
    loadJobs();
  };

  const handleReset = () => {
    setKeyword('');
    setIndustry(undefined);
    setLocation(undefined);
    setCurrentPage(1);
    loadJobs();
  };

  const columns = [
    {
      title: '岗位名称',
      dataIndex: 'title',
      key: 'title',
      width: 200,
      render: (text: string, record: Job) => (
        <a onClick={() => navigate(`/job/interpret/${record.id}`)}>
          {text}
        </a>
      ),
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
      width: 120,
      render: (text: string) => text || '-',
    },
    {
      title: '地点',
      dataIndex: 'location',
      key: 'location',
      width: 120,
      render: (text: string) => (
        <span>
          <EnvironmentOutlined /> {text}
        </span>
      ),
    },
    {
      title: '薪资',
      dataIndex: 'salary_range',
      key: 'salary_range',
      width: 120,
      render: (text: string) => (
        <Tag color="green" icon={<DollarOutlined />}>
          {text}
        </Tag>
      ),
    },
    {
      title: '经验',
      dataIndex: 'experience_required',
      key: 'experience_required',
      width: 100,
      render: (text: string) => text || '-',
    },
    {
      title: '学历',
      dataIndex: 'education_required',
      key: 'education_required',
      width: 100,
      render: (text: string) => text || '-',
    },
    {
      title: '操作',
      key: 'action',
      width: 120,
      fixed: 'right' as const,
      render: (_: any, record: Job) => (
        <Space size="small">
          <Button
            type="link"
            size="small"
            icon={<FileSearchOutlined />}
            onClick={() => navigate(`/job/interpret/${record.id}`)}
          >
            查看详情
          </Button>
        </Space>
      ),
    },
  ];

  return (
    <div style={{ padding: '24px' }}>
      <Card>
        <Space direction="vertical" size="large" style={{ width: '100%' }}>
          <Title level={2}>岗位中心</Title>

          {/* 筛选条件 */}
          <Space size="middle" wrap>
            <Search
              placeholder="搜索岗位名称、公司或关键词"
              value={keyword}
              onChange={(e) => setKeyword(e.target.value)}
              onSearch={handleSearch}
              style={{ width: 300 }}
              enterButton={<SearchOutlined />}
            />

            <Select
              placeholder="选择行业"
              value={industry}
              onChange={setIndustry}
              style={{ width: 150 }}
              allowClear
            >
              <Option value="互联网">互联网</Option>
              <Option value="金融">金融</Option>
              <Option value="教育">教育</Option>
              <Option value="医疗">医疗</Option>
              <Option value="制造业">制造业</Option>
              <Option value="其他">其他</Option>
            </Select>

            <Select
              placeholder="选择地点"
              value={location}
              onChange={setLocation}
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

            <Button onClick={handleSearch} type="primary">
              搜索
            </Button>
            <Button onClick={handleReset}>
              重置
            </Button>
          </Space>

          {/* 岗位列表 */}
          <Table
            columns={columns}
            dataSource={jobs}
            rowKey="id"
            loading={loading}
            scroll={{ x: 1200 }}
            pagination={{
              current: currentPage,
              pageSize: pageSize,
              total: total,
              showSizeChanger: true,
              showQuickJumper: true,
              showTotal: (total) => `共 ${total} 个岗位`,
              onChange: (page, size) => {
                setCurrentPage(page);
                setPageSize(size);
              },
            }}
          />
        </Space>
      </Card>
    </div>
  );
};

export default JobList;
