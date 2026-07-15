/**
 * 岗位匹配页面
 */
import React, { useState, useEffect } from 'react';
import { useParams } from 'react-router-dom';
import {
  Card,
  Row,
  Col,
  Tag,
  Typography,
  Space,
  Button,
  Divider,
  Progress,
  Form,
  Select,
  InputNumber,
  Spin,
  Alert,
  message,
  Tabs,
  Empty,
} from 'antd';
import {
  HeartOutlined,
  ThunderboltOutlined,
  RocketOutlined,
  FilterOutlined,
  EnvironmentOutlined,
  DollarOutlined,
} from '@ant-design/icons';
import { calculateMatch } from '../../services/job';
import { getResumeData } from '../../services/resume';
import { useAppStore } from '../../store';
import { getScoreColor } from '../../utils';
import type { JobMatchResponse, JobMatchResult, MatchPreferences } from '../../types';

const { Title, Text } = Typography;
const { Option } = Select;

const JobMatch: React.FC = () => {
  const { resumeId } = useParams<{ resumeId: string }>();
  const { setResumeData } = useAppStore();

  const [form] = Form.useForm();
  const [loading, setLoading] = useState(false);
  const [matchResult, setMatchResult] = useState<JobMatchResponse | null>(null);
  const [showFilter, setShowFilter] = useState(false);

  useEffect(() => {
    if (resumeId) {
      loadResumeData();
    }
  }, [resumeId]);

  const loadResumeData = async () => {
    if (!resumeId) return;
    try {
      const data = await getResumeData(parseInt(resumeId));
      setResumeData(data);
    } catch (error: any) {
      message.error(error || '加载简历失败');
    }
  };

  const handleMatch = async (preferences?: MatchPreferences) => {
    if (!resumeId) return;

    setLoading(true);
    try {
      const result = await calculateMatch({
        resume_id: parseInt(resumeId),
        preferences,
        top_k: 20,
      });
      setMatchResult(result);
      message.success(`匹配完成！共找到 ${result.total} 个岗位`);
    } catch (error: any) {
      message.error(error || '匹配失败');
    } finally {
      setLoading(false);
    }
  };

  const handleFilterSubmit = (values: any) => {
    const preferences: MatchPreferences = {
      industries: values.industries,
      cities: values.cities,
      salary_min: values.salary_min,
      salary_max: values.salary_max,
      education: values.education,
      experience: values.experience,
      company_types: values.company_types,
    };
    handleMatch(preferences);
  };

  const renderJobCard = (job: JobMatchResult) => {
    const handleViewDetail = () => {
      window.open(`https://www.zhipin.com/job_detail/${job.job_id}.html`, '_blank');
    };

    return (
      <Card
        key={job.job_id}
        size="small"
        style={{ marginBottom: '16px' }}
        hoverable
      >
        <Row gutter={16}>
          <Col span={16}>
            <Space direction="vertical" style={{ width: '100%' }}>
              <div>
                <Text strong style={{ fontSize: '16px' }}>{job.job_title}</Text>
                <Divider type="vertical" />
                <Text type="secondary">{job.company}</Text>
              </div>
              <Space size="small" wrap>
                {job.location && (
                  <Tag icon={<EnvironmentOutlined />}>{job.location}</Tag>
                )}
                {job.salary_range && (
                  <Tag icon={<DollarOutlined />} color="green">{job.salary_range}</Tag>
                )}
              </Space>
              <div>
                <Text type="secondary">命中技能：</Text>
                <Space size={[0, 8]} wrap style={{ marginTop: '4px' }}>
                  {job.matched_skills.map((skill, idx) => (
                    <Tag key={idx} color="blue">{skill}</Tag>
                  ))}
                </Space>
              </div>
              {job.missing_skills.length > 0 && (
                <div>
                  <Text type="secondary">缺失技能：</Text>
                  <Space size={[0, 8]} wrap style={{ marginTop: '4px' }}>
                    {job.missing_skills.map((skill, idx) => (
                      <Tag key={idx} color="default">{skill}</Tag>
                    ))}
                  </Space>
                </div>
              )}
              <Alert
                message={job.match_reason}
                type="info"
                showIcon
                style={{ fontSize: '13px' }}
              />
            </Space>
          </Col>
          <Col span={8} style={{ textAlign: 'center' }}>
            <div style={{ display: 'flex', flexDirection: 'column', alignItems: 'center', justifyContent: 'center', height: '100%' }}>
              <Progress
                type="circle"
                percent={Math.round(job.match_score)}
                strokeColor={getScoreColor(job.match_score)}
                width={100}
                format={(percent) => (
                  <div>
                    <div style={{ fontSize: '20px', fontWeight: 'bold' }}>{percent}</div>
                    <div style={{ fontSize: '12px', color: '#666' }}>匹配度</div>
                  </div>
                )}
              />
              <Button type="primary" size="small" style={{ marginTop: '16px' }} onClick={handleViewDetail}>
                查看详情
              </Button>
            </div>
          </Col>
        </Row>
      </Card>
    );
  };

  return (
    <div style={{ padding: '24px', maxWidth: '1400px', margin: '0 auto' }}>
      <Space direction="vertical" size="large" style={{ width: '100%' }}>
        {/* 头部 */}
        <Card>
          <Row justify="space-between" align="middle">
            <Col>
              <Title level={2}>
                <ThunderboltOutlined /> 岗位精准匹配
              </Title>
              <Text type="secondary">
                基于简历智能分析，为您推荐最匹配的岗位
              </Text>
            </Col>
            <Col>
              <Space>
                <Button
                  icon={<FilterOutlined />}
                  onClick={() => setShowFilter(!showFilter)}
                >
                  {showFilter ? '隐藏筛选' : '筛选条件'}
                </Button>
                <Button
                  type="primary"
                  icon={<ThunderboltOutlined />}
                  onClick={() => handleMatch()}
                  loading={loading}
                >
                  开始匹配
                </Button>
              </Space>
            </Col>
          </Row>
        </Card>

        {/* 筛选条件 */}
        {showFilter && (
          <Card title="筛选条件">
            <Form
              form={form}
              layout="vertical"
              onFinish={handleFilterSubmit}
            >
              <Row gutter={16}>
                <Col span={8}>
                  <Form.Item label="行业" name="industries">
                    <Select mode="multiple" placeholder="选择行业">
                      <Option value="互联网">互联网</Option>
                      <Option value="金融">金融</Option>
                      <Option value="教育">教育</Option>
                      <Option value="医疗">医疗</Option>
                      <Option value="制造业">制造业</Option>
                    </Select>
                  </Form.Item>
                </Col>
                <Col span={8}>
                  <Form.Item label="城市" name="cities">
                    <Select mode="multiple" placeholder="选择城市">
                      <Option value="北京">北京</Option>
                      <Option value="上海">上海</Option>
                      <Option value="深圳">深圳</Option>
                      <Option value="杭州">杭州</Option>
                      <Option value="成都">成都</Option>
                      <Option value="广州">广州</Option>
                    </Select>
                  </Form.Item>
                </Col>
                <Col span={8}>
                  <Form.Item label="学历要求" name="education">
                    <Select placeholder="选择学历">
                      <Option value="不限">不限</Option>
                      <Option value="大专">大专</Option>
                      <Option value="本科">本科</Option>
                      <Option value="硕士">硕士</Option>
                      <Option value="博士">博士</Option>
                    </Select>
                  </Form.Item>
                </Col>
              </Row>
              <Row gutter={16}>
                <Col span={8}>
                  <Form.Item label="经验要求" name="experience">
                    <Select placeholder="选择经验">
                      <Option value="不限">不限</Option>
                      <Option value="应届生">应届生</Option>
                      <Option value="1-3年">1-3年</Option>
                      <Option value="3-5年">3-5年</Option>
                      <Option value="5-10年">5-10年</Option>
                      <Option value="10年以上">10年以上</Option>
                    </Select>
                  </Form.Item>
                </Col>
                <Col span={8}>
                  <Form.Item label="薪资范围 (K)">
                    <Space>
                      <Form.Item name="salary_min" noStyle>
                        <InputNumber placeholder="最低" min={0} />
                      </Form.Item>
                      <Text>-</Text>
                      <Form.Item name="salary_max" noStyle>
                        <InputNumber placeholder="最高" min={0} />
                      </Form.Item>
                    </Space>
                  </Form.Item>
                </Col>
                <Col span={8}>
                  <Form.Item label="公司类型" name="company_types">
                    <Select mode="multiple" placeholder="选择公司类型">
                      <Option value="上市公司">上市公司</Option>
                      <Option value="外企">外企</Option>
                      <Option value="国企">国企</Option>
                      <Option value="创业公司">创业公司</Option>
                    </Select>
                  </Form.Item>
                </Col>
              </Row>
              <Form.Item>
                <Space>
                  <Button type="primary" htmlType="submit" loading={loading}>
                    应用筛选
                  </Button>
                  <Button onClick={() => form.resetFields()}>
                    重置
                  </Button>
                </Space>
              </Form.Item>
            </Form>
          </Card>
        )}

        {/* 匹配结果 */}
        {loading ? (
          <div style={{ textAlign: 'center', padding: '100px 0' }}>
            <Spin size="large" tip="正在智能匹配岗位..." />
          </div>
        ) : matchResult ? (
          <Card>
            <Tabs
              defaultActiveKey="highly"
              items={[
                {
                  key: 'highly',
                  label: (
                    <span>
                      <HeartOutlined />
                      高度匹配 ({matchResult.highly_matched.length})
                    </span>
                  ),
                  children: matchResult.highly_matched.length > 0 ? (
                    matchResult.highly_matched.map(renderJobCard)
                  ) : (
                    <Empty description="暂无高度匹配的岗位" />
                  ),
                },
                {
                  key: 'fairly',
                  label: (
                    <span>
                      <ThunderboltOutlined />
                      较为匹配 ({matchResult.fairly_matched.length})
                    </span>
                  ),
                  children: matchResult.fairly_matched.length > 0 ? (
                    matchResult.fairly_matched.map(renderJobCard)
                  ) : (
                    <Empty description="暂无较为匹配的岗位" />
                  ),
                },
                {
                  key: 'development',
                  label: (
                    <span>
                      <RocketOutlined />
                      发展方向 ({matchResult.development_direction.length})
                    </span>
                  ),
                  children: matchResult.development_direction.length > 0 ? (
                    matchResult.development_direction.map(renderJobCard)
                  ) : (
                    <Empty description="暂无发展方向岗位" />
                  ),
                },
              ]}
            />
          </Card>
        ) : (
          <Card>
            <Empty
              description='点击上方"开始匹配"按钮，为您智能推荐岗位'
              image={Empty.PRESENTED_IMAGE_SIMPLE}
            />
          </Card>
        )}
      </Space>
    </div>
  );
};

export default JobMatch;
