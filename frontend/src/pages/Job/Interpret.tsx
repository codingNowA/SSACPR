/**
 * 岗位解读页面
 */
import React, { useState, useEffect } from 'react';
import { useParams, useNavigate, useSearchParams } from 'react-router-dom';
import {
  Card,
  Row,
  Col,
  Typography,
  Space,
  Tag,
  Divider,
  Timeline,
  Descriptions,
  Button,
  Spin,
  message,
  Alert,
} from 'antd';
import {
  FileSearchOutlined,
  EnvironmentOutlined,
  DollarOutlined,
  TrophyOutlined,
  RocketOutlined,
  TeamOutlined,
  ArrowLeftOutlined,
  ThunderboltOutlined,
  WarningOutlined,
} from '@ant-design/icons';
import apiClient from '../../services/api';

const { Title, Text, Paragraph } = Typography;

interface JobAnalysis {
  job_id: number;
  job_title: string;
  company: string;
  location: string;
  salary_range: string;
  core_info: {
    responsibilities: string[];
    required_skills: string[];
    bonus_skills: string[];
    requirements: string[];
  };
  market_analysis: {
    salary_competitiveness: string;
    skill_hotness: Record<string, string>;
  };
  career_path: Array<{
    stage: string;
    duration: string;
    focus: string;
  }>;
  suitable_candidates: {
    education: string;
    experience: string;
    skills: string[];
    personality: string;
  };
  difficulty_assessment?: {
    overall_difficulty: string;
    difficulty_score: number;
    factors: Record<string, { score: number; description: string }>;
    competitive_pressure: string;
    preparation_time: string;
  };
}

const JobInterpret: React.FC = () => {
  const { jobId } = useParams<{ jobId: string }>();
  const navigate = useNavigate();
  const [searchParams] = useSearchParams();
  const resumeId = searchParams.get('resumeId');
  const [loading, setLoading] = useState(false);
  const [analysis, setAnalysis] = useState<JobAnalysis | null>(null);

  useEffect(() => {
    if (jobId) {
      loadJobAnalysis();
    }
  }, [jobId]);

  const loadJobAnalysis = async () => {
    if (!jobId) return;

    setLoading(true);
    try {
      const data = await apiClient.get(`/api/v1/job-analysis/interpret/${jobId}`);
      setAnalysis(data);
    } catch (error: any) {
      message.error(error || '加载岗位解读失败');
    } finally {
      setLoading(false);
    }
  };

  if (loading) {
    return (
      <div style={{ textAlign: 'center', padding: '100px' }}>
        <Spin size="large" tip="正在分析岗位..." />
      </div>
    );
  }

  if (!analysis) {
    return (
      <div style={{ padding: '24px' }}>
        <Alert message="岗位信息不存在" type="error" />
      </div>
    );
  }

  return (
    <div style={{ padding: '24px', maxWidth: '1200px', margin: '0 auto' }}>
      <Space direction="vertical" size="large" style={{ width: '100%' }}>
        {/* 返回按钮 */}
        <Space>
          <Button icon={<ArrowLeftOutlined />} onClick={() => navigate(-1)}>
            返回
          </Button>
          {resumeId && (
            <Button type="primary" onClick={() => navigate(`/interview/prep?jobId=${jobId}&resumeId=${resumeId}`)}>
              准备面试
            </Button>
          )}
        </Space>

        {/* 岗位基本信息 */}
        <Card>
          <Space direction="vertical" style={{ width: '100%' }}>
            <Title level={2}>
              <FileSearchOutlined /> {analysis.job_title}
            </Title>
            <Space size="large" wrap>
              <Text strong>{analysis.company}</Text>
              <Tag icon={<EnvironmentOutlined />}>{analysis.location}</Tag>
              <Tag icon={<DollarOutlined />} color="green">
                {analysis.salary_range}
              </Tag>
            </Space>
          </Space>
        </Card>

        {/* 核心信息 */}
        <Card title={<><TrophyOutlined /> 核心信息</>}>
          <Space direction="vertical" size="middle" style={{ width: '100%' }}>
            {/* 岗位职责 */}
            <div>
              <Text strong style={{ fontSize: 16 }}>岗位职责：</Text>
              <ul style={{ marginTop: 8 }}>
                {analysis.core_info.responsibilities.map((item, idx) => (
                  <li key={idx}>
                    <Paragraph style={{ marginBottom: 8 }}>{item}</Paragraph>
                  </li>
                ))}
              </ul>
            </div>

            <Divider />

            {/* 必需技能 */}
            <div>
              <Text strong style={{ fontSize: 16 }}>必需技能：</Text>
              <div style={{ marginTop: 8 }}>
                <Space size={[0, 8]} wrap>
                  {analysis.core_info.required_skills.map((skill, idx) => (
                    <Tag key={idx} color="blue" style={{ fontSize: 14 }}>
                      {skill}
                    </Tag>
                  ))}
                </Space>
              </div>
            </div>

            {/* 加分技能 */}
            {analysis.core_info.bonus_skills.length > 0 && (
              <div>
                <Text strong style={{ fontSize: 16 }}>加分技能：</Text>
                <div style={{ marginTop: 8 }}>
                  <Space size={[0, 8]} wrap>
                    {analysis.core_info.bonus_skills.map((skill, idx) => (
                      <Tag key={idx} color="cyan" style={{ fontSize: 14 }}>
                        {skill}
                      </Tag>
                    ))}
                  </Space>
                </div>
              </div>
            )}

            {/* 其他要求 */}
            {analysis.core_info.requirements.length > 0 && (
              <>
                <Divider />
                <div>
                  <Text strong style={{ fontSize: 16 }}>任职要求：</Text>
                  <ul style={{ marginTop: 8 }}>
                    {analysis.core_info.requirements.map((req, idx) => (
                      <li key={idx}>
                        <Text>{req}</Text>
                      </li>
                    ))}
                  </ul>
                </div>
              </>
            )}
          </Space>
        </Card>

        {/* 市场分析 */}
        <Card title="市场分析">
          <Row gutter={24}>
            <Col span={12}>
              <Alert
                message="薪资竞争力"
                description={analysis.market_analysis.salary_competitiveness}
                type="success"
                showIcon
              />
            </Col>
            <Col span={12}>
              <div>
                <Text strong>技能热度分析：</Text>
                <div style={{ marginTop: 12 }}>
                  {Object.entries(analysis.market_analysis.skill_hotness).map(([skill, hotness]) => (
                    <div key={skill} style={{ marginBottom: 8 }}>
                      <Tag color="blue">{skill}</Tag>
                      <Text type="secondary">{hotness}</Text>
                    </div>
                  ))}
                </div>
              </div>
            </Col>
          </Row>
        </Card>

        {/* 岗位难度评估 */}
        {analysis.difficulty_assessment && (
          <Card title={<><ThunderboltOutlined /> 岗位难度评估</>}>
            <Space direction="vertical" size="large" style={{ width: '100%' }}>
              {/* 总体评估 */}
              <Row gutter={24}>
                <Col span={8}>
                  <Card size="small" style={{ textAlign: 'center', backgroundColor: '#f0f5ff' }}>
                    <div style={{ fontSize: 16, color: '#666' }}>总体难度</div>
                    <div style={{ fontSize: 32, fontWeight: 'bold', color: '#1890ff', margin: '10px 0' }}>
                      {analysis.difficulty_assessment.overall_difficulty}
                    </div>
                    <div style={{ fontSize: 14, color: '#999' }}>
                      综合评分: {analysis.difficulty_assessment.difficulty_score}/100
                    </div>
                  </Card>
                </Col>
                <Col span={8}>
                  <Card size="small" style={{ textAlign: 'center', backgroundColor: '#fff7e6' }}>
                    <div style={{ fontSize: 16, color: '#666' }}>竞争压力</div>
                    <div style={{ fontSize: 28, fontWeight: 'bold', color: '#fa8c16', margin: '10px 0' }}>
                      {analysis.difficulty_assessment.competitive_pressure}
                    </div>
                    <WarningOutlined style={{ fontSize: 24, color: '#faad14' }} />
                  </Card>
                </Col>
                <Col span={8}>
                  <Card size="small" style={{ textAlign: 'center', backgroundColor: '#f6ffed' }}>
                    <div style={{ fontSize: 16, color: '#666' }}>准备时间</div>
                    <div style={{ fontSize: 20, fontWeight: 'bold', color: '#52c41a', margin: '10px 0' }}>
                      {analysis.difficulty_assessment.preparation_time}
                    </div>
                  </Card>
                </Col>
              </Row>

              <Divider />

              {/* 各维度评估 */}
              <div>
                <Text strong style={{ fontSize: 16 }}>难度分析：</Text>
                <div style={{ marginTop: 12 }}>
                  {Object.entries(analysis.difficulty_assessment.factors).map(([key, factor]) => {
                    const labels: Record<string, string> = {
                      skill_complexity: '技能复杂度',
                      experience_requirement: '经验要求',
                      education_requirement: '学历要求',
                      salary_level: '薪资水平',
                      company_prestige: '公司知名度',
                    };

                    let color = '#52c41a';
                    if (factor.score >= 70) color = '#ff4d4f';
                    else if (factor.score >= 50) color = '#faad14';

                    return (
                      <div key={key} style={{ marginBottom: 12 }}>
                        <div style={{ display: 'flex', alignItems: 'center', marginBottom: 4 }}>
                          <Text style={{ width: 120 }}>{labels[key]}:</Text>
                          <div style={{
                            flex: 1,
                            height: 20,
                            backgroundColor: '#f0f0f0',
                            borderRadius: 10,
                            overflow: 'hidden',
                            marginRight: 12
                          }}>
                            <div style={{
                              width: `${factor.score}%`,
                              height: '100%',
                              backgroundColor: color,
                              transition: 'width 0.3s ease'
                            }} />
                          </div>
                          <Text strong style={{ width: 50, textAlign: 'right' }}>{factor.score}</Text>
                        </div>
                        <Text type="secondary" style={{ fontSize: 12, marginLeft: 120 }}>
                          {factor.description}
                        </Text>
                      </div>
                    );
                  })}
                </div>
              </div>
            </Space>
          </Card>
        )}

        {/* 职业发展路径 */}
        <Card title={<><RocketOutlined /> 职业发展路径</>}>
          <Timeline
            items={analysis.career_path.map((item) => ({
              children: (
                <div>
                  <Text strong style={{ fontSize: 15 }}>{item.stage}</Text>
                  <br />
                  <Text type="secondary">时间：{item.duration}</Text>
                  <br />
                  <Text>重点：{item.focus}</Text>
                </div>
              ),
            }))}
          />
        </Card>

        {/* 适合人群画像 */}
        <Card title={<><TeamOutlined /> 适合人群画像</>}>
          <Descriptions column={1} bordered>
            <Descriptions.Item label="学历要求">
              {analysis.suitable_candidates.education}
            </Descriptions.Item>
            <Descriptions.Item label="经验要求">
              {analysis.suitable_candidates.experience}
            </Descriptions.Item>
            <Descriptions.Item label="核心技能">
              <Space size={[0, 8]} wrap>
                {analysis.suitable_candidates.skills.map((skill, idx) => (
                  <Tag key={idx} color="blue">{skill}</Tag>
                ))}
              </Space>
            </Descriptions.Item>
            <Descriptions.Item label="性格特质">
              {analysis.suitable_candidates.personality}
            </Descriptions.Item>
          </Descriptions>
        </Card>
      </Space>
    </div>
  );
};

export default JobInterpret;
