/**
 * 数据分析页面
 */
import React, { useState, useEffect } from 'react';
import {
  Card,
  Row,
  Col,
  Typography,
  Space,
  Spin,
  message,
  Tag,
  Select,
  Button,
  Empty,
  Statistic,
  Progress,
} from 'antd';
import {
  BarChartOutlined,
  LineChartOutlined,
  PieChartOutlined,
  TrophyOutlined,
  RiseOutlined,
  ReloadOutlined,
} from '@ant-design/icons';
import {
  getHotwords,
  getSkillRank,
  getSalaryDistribution,
  getComparison,
} from '../../services/analytics';

const { Title, Text } = Typography;
const { Option } = Select;

const Analytics: React.FC = () => {
  const [loading, setLoading] = useState(false);
  const [hotwords, setHotwords] = useState<any[]>([]);
  const [skillRank, setSkillRank] = useState<any[]>([]);
  const [salaryData, setSalaryData] = useState<any[]>([]);
  const [comparisonData, setComparisonData] = useState<any[]>([]);
  const [dimension, setDimension] = useState('city');
  const [metric, setMetric] = useState('count');

  useEffect(() => {
    loadAllData();
  }, []);

  useEffect(() => {
    // 当 dimension 或 metric 改变时，自动刷新对比数据
    if (dimension && metric) {
      handleComparisonChange();
    }
  }, [dimension, metric]);

  const loadAllData = async () => {
    setLoading(true);
    try {
      const [hotwordsRes, skillRankRes, salaryRes, comparisonRes] = await Promise.all([
        getHotwords({ limit: 20 }),
        getSkillRank({ limit: 20 }),
        getSalaryDistribution({ dimension: 'city', limit: 10 }),
        getComparison({ dimension, metric, limit: 10 }),
      ]);

      setHotwords(hotwordsRes?.data?.hotwords || hotwordsRes?.hotwords || []);
      setSkillRank(skillRankRes?.data?.skills || skillRankRes?.skills || []);
      setSalaryData(salaryRes?.data?.distributions || salaryRes?.distributions || []);
      setComparisonData(comparisonRes?.data?.items || comparisonRes?.items || []);
    } catch (error: any) {
      message.error(error || '加载数据失败');
    } finally {
      setLoading(false);
    }
  };

  const handleComparisonChange = async () => {
    try {
      const res = await getComparison({ dimension, metric, limit: 10 });
      setComparisonData(res?.data?.items || res?.items || []);
    } catch (error: any) {
      message.error(error || '加载对比数据失败');
    }
  };

  return (
    <div style={{ padding: '24px', maxWidth: '1400px', margin: '0 auto' }}>
      <Space direction="vertical" size="large" style={{ width: '100%' }}>
        {/* 头部 */}
        <Card>
          <Row justify="space-between" align="middle">
            <Col>
              <Title level={2}>
                <BarChartOutlined /> 数据分析
              </Title>
              <Text type="secondary">就业数据可视化分析与趋势洞察</Text>
            </Col>
            <Col>
              <Button
                type="primary"
                icon={<ReloadOutlined />}
                onClick={loadAllData}
                loading={loading}
              >
                刷新数据
              </Button>
            </Col>
          </Row>
        </Card>

        {loading ? (
          <div style={{ textAlign: 'center', padding: '100px 0' }}>
            <Spin size="large" tip="加载中..." />
          </div>
        ) : (
          <>
            {/* 岗位热词 */}
            <Card
              title={
                <Space>
                  <TrophyOutlined />
                  <span>岗位热词 Top 20</span>
                </Space>
              }
            >
              {hotwords.length > 0 ? (
                <Space size={[8, 16]} wrap>
                  {hotwords.map((item: any, index: number) => (
                    <Tag
                      key={index}
                      color={index < 5 ? 'red' : index < 10 ? 'orange' : 'blue'}
                      style={{ fontSize: '14px', padding: '4px 12px' }}
                    >
                      {item.word || item.skill} ({item.count || item.frequency})
                    </Tag>
                  ))}
                </Space>
              ) : (
                <Empty description="暂无数据" />
              )}
            </Card>

            {/* 技能排行榜 */}
            <Card
              title={
                <Space>
                  <RiseOutlined />
                  <span>技能排行榜 Top 20</span>
                </Space>
              }
            >
              {skillRank.length > 0 ? (
                <Row gutter={[16, 16]}>
                  {skillRank.slice(0, 10).map((item: any, index: number) => (
                    <Col xs={24} sm={12} md={12} lg={8} key={index}>
                      <Card size="small" style={{ background: index < 3 ? '#fff7e6' : '#f9f9f9' }}>
                        <Space direction="vertical" style={{ width: '100%' }}>
                          <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
                            <Space>
                              <Tag color={index === 0 ? 'gold' : index === 1 ? 'silver' : index === 2 ? 'orange' : 'blue'}>
                                #{index + 1}
                              </Tag>
                              <Text strong>{item.skill || item.name}</Text>
                            </Space>
                            <Text type="secondary">{item.count || item.demand}</Text>
                          </div>
                          <Progress
                            percent={Math.min(100, ((item.count || item.demand) / (skillRank[0]?.count || skillRank[0]?.demand || 1)) * 100)}
                            strokeColor={index < 3 ? '#faad14' : '#1890ff'}
                            showInfo={false}
                          />
                        </Space>
                      </Card>
                    </Col>
                  ))}
                </Row>
              ) : (
                <Empty description="暂无数据" />
              )}
            </Card>

            {/* 薪资分布 */}
            <Card
              title={
                <Space>
                  <PieChartOutlined />
                  <span>薪资分布（按城市）</span>
                </Space>
              }
            >
              {salaryData.length > 0 ? (
                <Row gutter={[16, 16]}>
                  {salaryData.map((item: any, index: number) => (
                    <Col xs={24} sm={12} md={8} lg={6} key={index}>
                      <Card size="small" hoverable>
                        <Statistic
                          title={item.range}
                          value={item.count}
                          suffix="个岗位"
                          valueStyle={{ color: '#3f8600', fontSize: '18px' }}
                        />
                        <Text type="secondary" style={{ fontSize: '12px' }}>
                          占比: {item.percentage}%
                        </Text>
                      </Card>
                    </Col>
                  ))}
                </Row>
              ) : (
                <Empty description="暂无数据" />
              )}
            </Card>

            {/* 维度对比 */}
            <Card
              title={
                <Space>
                  <LineChartOutlined />
                  <span>维度对比分析</span>
                </Space>
              }
              extra={
                <Space>
                  <Select value={dimension} onChange={setDimension} style={{ width: 120 }}>
                    <Option value="city">城市</Option>
                    <Option value="industry">行业</Option>
                    <Option value="education">学历</Option>
                  </Select>
                  <Select value={metric} onChange={setMetric} style={{ width: 120 }}>
                    <Option value="count">岗位数量</Option>
                    <Option value="avg_salary">平均薪资</Option>
                  </Select>
                </Space>
              }
            >
              {comparisonData.length > 0 ? (
                <Space direction="vertical" style={{ width: '90%' }} size="middle">
                  {(() => {
                    const maxValue = Math.max(...comparisonData.map((item: any) =>
                      metric === 'count' ? (item.count || item.value || 0) : (item.avg_salary || item.value || 0)
                    ));
                    return comparisonData.map((item: any, index: number) => {
                      const currentValue = metric === 'count' ? (item.count || item.value || 0) : (item.avg_salary || item.value || 0);
                      const percent = maxValue > 0 ? Math.min(90, (currentValue / maxValue) * 90) : 0;
                      return (
                        <div key={index}>
                          <div style={{ display: 'flex', justifyContent: 'space-between', marginBottom: 8 }}>
                            <Text strong>{item.dimension_value || item.name}</Text>
                            <Text>
                              {metric === 'count' ? currentValue : `${currentValue}K`}
                            </Text>
                          </div>
                          <Progress
                            percent={percent}
                            strokeColor="#1890ff"
                            showInfo={false}
                          />
                        </div>
                      );
                    });
                  })()}
                </Space>
              ) : (
                <Empty description="暂无数据" />
              )}
            </Card>
          </>
        )}
      </Space>
    </div>
  );
};

export default Analytics;
