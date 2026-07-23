/**
 * 首页
 */
import React from 'react';
import { useNavigate } from 'react-router-dom';
import { Card, Row, Col, Button, Typography, Space, Divider } from 'antd';
import {
  FileTextOutlined,
  ThunderboltOutlined,
  TrophyOutlined,
  RocketOutlined,
  CheckCircleOutlined,
  StarOutlined,
} from '@ant-design/icons';

const { Title, Paragraph, Text } = Typography;

const Home: React.FC = () => {
  const navigate = useNavigate();

  const features = [
    {
      icon: <FileTextOutlined style={{ fontSize: '48px', color: '#1890ff' }} />,
      title: '简历智能解析',
      description: '支持 PDF、Word、图片等多种格式，自动提取基本信息、教育经历、工作经验、项目经验和技能标签',
    },
    {
      icon: <TrophyOutlined style={{ fontSize: '48px', color: '#52c41a' }} />,
      title: '全面诊断评分',
      description: '从完整性、专业性、量化程度、项目深度、岗位匹配等多维度评估简历质量',
    },
    {
      icon: <RocketOutlined style={{ fontSize: '48px', color: '#faad14' }} />,
      title: '智能优化建议',
      description: '提供可执行的修改建议和优化文案，帮助您打造更具竞争力的简历',
    },
    {
      icon: <ThunderboltOutlined style={{ fontSize: '48px', color: '#f5222d' }} />,
      title: '岗位精准匹配',
      description: '智能分析简历与岗位的匹配度，输出命中技能、缺失技能和推荐理由',
    },
    {
      icon: <CheckCircleOutlined style={{ fontSize: '48px', color: '#722ed1' }} />,
      title: '偏好筛选',
      description: '支持按行业、城市、薪资、公司性质等条件筛选，找到最适合的岗位',
    },
    {
      icon: <StarOutlined style={{ fontSize: '48px', color: '#13c2c2' }} />,
      title: '版本管理',
      description: '保存多个简历版本，针对不同岗位快速切换，提高投递效率',
    },
  ];

  return (
    <div style={{ background: '#f0f2f5' }}>
      {/* Hero Section */}
      <div style={{
        background: 'linear-gradient(135deg, #667eea 0%, #764ba2 100%)',
        padding: '80px 50px',
        textAlign: 'center',
        color: 'white'
      }}>
        <Title level={1} style={{ color: 'white', fontSize: '48px', marginBottom: '24px' }}>
          职业规划智能体系统
        </Title>
        <Paragraph style={{ color: 'white', fontSize: '20px', marginBottom: '40px' }}>
          基于大语言模型的简历智能诊断与岗位精准匹配
        </Paragraph>
        <Space size="large">
          <Button
            type="primary"
            size="large"
            icon={<FileTextOutlined />}
            onClick={() => navigate('/resume/upload')}
            style={{ height: '50px', fontSize: '18px', padding: '0 40px' }}
          >
            开始使用
          </Button>
          <Button
            size="large"
            style={{ height: '50px', fontSize: '18px', padding: '0 40px', background: 'rgba(255,255,255,0.2)', color: 'white', border: 'none' }}
          >
            了解更多
          </Button>
        </Space>
      </div>

      {/* Features Section */}
      <div style={{ padding: '80px 50px', maxWidth: '1400px', margin: '0 auto' }}>
        <div style={{ textAlign: 'center', marginBottom: '60px' }}>
          <Title level={2}>核心功能</Title>
          <Paragraph type="secondary" style={{ fontSize: '16px' }}>
            全方位提升简历质量，精准匹配理想岗位
          </Paragraph>
        </div>

        <Row gutter={[32, 32]}>
          {features.map((feature, index) => (
            <Col xs={24} sm={12} lg={8} key={index}>
              <Card
                hoverable
                style={{ height: '100%', textAlign: 'center' }}
              >
                <Space direction="vertical" size="large" style={{ width: '100%' }}>
                  <div>{feature.icon}</div>
                  <Title level={4}>{feature.title}</Title>
                  <Paragraph type="secondary">
                    {feature.description}
                  </Paragraph>
                </Space>
              </Card>
            </Col>
          ))}
        </Row>
      </div>

      {/* CTA Section */}
      <div style={{
        background: 'white',
        padding: '60px 50px',
        textAlign: 'center'
      }}>
        <Title level={2}>准备好优化您的简历了吗？</Title>
        <Paragraph type="secondary" style={{ fontSize: '16px', marginBottom: '32px' }}>
          立即上传简历，获取专业的诊断与建议
        </Paragraph>
        <Button
          type="primary"
          size="large"
          icon={<FileTextOutlined />}
          onClick={() => navigate('/resume/upload')}
          style={{ height: '50px', fontSize: '18px', padding: '0 40px' }}
        >
          立即开始
        </Button>
      </div>

      {/* Stats Section */}
      <div style={{ padding: '60px 50px', background: '#f0f2f5' }}>
        <Row gutter={[32, 32]} style={{ maxWidth: '1200px', margin: '0 auto' }}>
          <Col xs={24} sm={8} style={{ textAlign: 'center' }}>
            <Title level={1} style={{ color: '#1890ff', marginBottom: '8px' }}>95%</Title>
            <Text type="secondary" style={{ fontSize: '16px' }}>诊断准确率</Text>
          </Col>
          <Col xs={24} sm={8} style={{ textAlign: 'center' }}>
            <Title level={1} style={{ color: '#52c41a', marginBottom: '8px' }}>5+</Title>
            <Text type="secondary" style={{ fontSize: '16px' }}>评分维度</Text>
          </Col>
          <Col xs={24} sm={8} style={{ textAlign: 'center' }}>
            <Title level={1} style={{ color: '#faad14', marginBottom: '8px' }}>20+</Title>
            <Text type="secondary" style={{ fontSize: '16px' }}>岗位推荐</Text>
          </Col>
        </Row>
      </div>
    </div>
  );
};

export default Home;
