/**
 * 面试准备页面
 */
import React, { useState, useEffect } from 'react';
import { useSearchParams, useNavigate } from 'react-router-dom';
import {
  Card,
  Row,
  Col,
  Typography,
  Space,
  Tag,
  Divider,
  Button,
  Spin,
  message,
  Alert,
  Collapse,
  Timeline,
  List,
  Descriptions,
} from 'antd';
import {
  CheckCircleOutlined,
  CloseCircleOutlined,
  BulbOutlined,
  TrophyOutlined,
  BookOutlined,
  TeamOutlined,
  RocketOutlined,
  ArrowLeftOutlined,
  StarOutlined,
} from '@ant-design/icons';
import { getInterviewPrep, InterviewPrepResponse } from '../../services/interview';

const { Title, Text, Paragraph } = Typography;
const { Panel } = Collapse;

const InterviewPrep: React.FC = () => {
  const [searchParams] = useSearchParams();
  const navigate = useNavigate();
  const jobId = searchParams.get('jobId');
  const resumeId = searchParams.get('resumeId');

  const [loading, setLoading] = useState(false);
  const [prepData, setPrepData] = useState<InterviewPrepResponse | null>(null);

  useEffect(() => {
    if (jobId && resumeId) {
      loadInterviewPrep();
    }
  }, [jobId, resumeId]);

  const loadInterviewPrep = async () => {
    if (!jobId || !resumeId) return;

    setLoading(true);
    try {
      const data = await getInterviewPrep(parseInt(jobId), parseInt(resumeId));
      setPrepData(data);
    } catch (error: any) {
      message.error(error || '加载面试准备方案失败');
    } finally {
      setLoading(false);
    }
  };

  if (loading) {
    return (
      <div style={{ textAlign: 'center', padding: '100px' }}>
        <Spin size="large" tip="正在生成面试准备方案..." />
      </div>
    );
  }

  if (!prepData) {
    return (
      <div style={{ padding: '24px' }}>
        <Alert message="面试准备方案不存在" type="error" />
      </div>
    );
  }

  const getDifficultyColor = (difficulty: string) => {
    const colors: Record<string, string> = {
      easy: 'green',
      medium: 'orange',
      hard: 'red',
    };
    return colors[difficulty] || 'blue';
  };

  return (
    <div style={{ padding: '24px', maxWidth: '1200px', margin: '0 auto' }}>
      <Space direction="vertical" size="large" style={{ width: '100%' }}>
        {/* 返回按钮 */}
        <Button icon={<ArrowLeftOutlined />} onClick={() => navigate(-1)}>
          返回
        </Button>

        {/* 头部信息 */}
        <Card>
          <Space direction="vertical" style={{ width: '100%' }}>
            <Title level={2}>
              <BookOutlined /> 面试准备方案
            </Title>
            <Space size="large" wrap>
              <Text strong>岗位：{prepData.job_title}</Text>
              <Text>公司：{prepData.company}</Text>
              <Text type="secondary">应聘者：{prepData.candidate_name}</Text>
            </Space>
          </Space>
        </Card>

        {/* 核心建议 */}
        <Card title={<><BulbOutlined /> 核心建议</>}>
          <List
            dataSource={prepData.recommendations}
            renderItem={(item) => (
              <List.Item>
                <CheckCircleOutlined style={{ color: '#52c41a', marginRight: 8 }} />
                <Text>{item}</Text>
              </List.Item>
            )}
          />
        </Card>

        {/* 技术准备 */}
        <Card title={<><TrophyOutlined /> 技术准备</>}>
          <Space direction="vertical" size="middle" style={{ width: '100%' }}>
            {/* 已掌握的必需技能 */}
            {prepData.technical_prep.mastered_required.length > 0 && (
              <div>
                <Text strong style={{ fontSize: 15 }}>
                  <CheckCircleOutlined style={{ color: '#52c41a', marginRight: 8 }} />
                  已掌握的核心技能：
                </Text>
                <div style={{ marginTop: 8 }}>
                  <Space size={[0, 8]} wrap>
                    {prepData.technical_prep.mastered_required.map((skill, idx) => (
                      <Tag key={idx} color="green" icon={<CheckCircleOutlined />}>
                        {skill}
                      </Tag>
                    ))}
                  </Space>
                </div>
              </div>
            )}

            {/* 缺失的必需技能 */}
            {prepData.technical_prep.missing_required.length > 0 && (
              <div>
                <Text strong style={{ fontSize: 15 }}>
                  <CloseCircleOutlined style={{ color: '#ff4d4f', marginRight: 8 }} />
                  需要补充的技能：
                </Text>
                <div style={{ marginTop: 8 }}>
                  <Space size={[0, 8]} wrap>
                    {prepData.technical_prep.missing_required.map((skill, idx) => (
                      <Tag key={idx} color="red" icon={<CloseCircleOutlined />}>
                        {skill}
                      </Tag>
                    ))}
                  </Space>
                </div>
              </div>
            )}

            {/* 已掌握的加分技能 */}
            {prepData.technical_prep.mastered_bonus.length > 0 && (
              <div>
                <Text strong style={{ fontSize: 15 }}>
                  <StarOutlined style={{ color: '#faad14', marginRight: 8 }} />
                  加分技能：
                </Text>
                <div style={{ marginTop: 8 }}>
                  <Space size={[0, 8]} wrap>
                    {prepData.technical_prep.mastered_bonus.map((skill, idx) => (
                      <Tag key={idx} color="gold" icon={<StarOutlined />}>
                        {skill}
                      </Tag>
                    ))}
                  </Space>
                </div>
              </div>
            )}

            <Divider />

            {/* 重点准备领域 */}
            <div>
              <Text strong style={{ fontSize: 15 }}>重点准备领域：</Text>
              <div style={{ marginTop: 8 }}>
                <Space size={[0, 8]} wrap>
                  {prepData.technical_prep.focus_areas.map((area, idx) => (
                    <Tag key={idx} color="blue" style={{ fontSize: 14 }}>
                      {area}
                    </Tag>
                  ))}
                </Space>
              </div>
            </div>

            {/* 准备建议 */}
            {prepData.technical_prep.preparation_tips.length > 0 && (
              <Alert
                message="准备建议"
                description={
                  <ul style={{ margin: 0, paddingLeft: 20 }}>
                    {prepData.technical_prep.preparation_tips.map((tip, idx) => (
                      <li key={idx}>{tip}</li>
                    ))}
                  </ul>
                }
                type="info"
                showIcon
              />
            )}
          </Space>
        </Card>

        {/* 项目准备 */}
        <Card title={<><RocketOutlined /> 项目经验准备</>}>
          <Space direction="vertical" size="middle" style={{ width: '100%' }}>
            {/* 关键项目 */}
            {prepData.project_prep.key_projects.length > 0 && (
              <div>
                <Text strong style={{ fontSize: 15 }}>关键项目经验：</Text>
                <Timeline style={{ marginTop: 16 }}>
                  {prepData.project_prep.key_projects.map((project, idx) => (
                    <Timeline.Item key={idx}>
                      <Text strong>{project.position}</Text> @ {project.company}
                      <br />
                      <Text type="secondary">{project.duration}</Text>
                      {project.highlights.length > 0 && (
                        <ul style={{ marginTop: 8 }}>
                          {project.highlights.map((highlight, hIdx) => (
                            <li key={hIdx}>
                              <Text>{highlight}</Text>
                            </li>
                          ))}
                        </ul>
                      )}
                    </Timeline.Item>
                  ))}
                </Timeline>
              </div>
            )}

            <Divider />

            {/* 准备建议 */}
            <Alert
              message="项目准备建议"
              description={
                <ul style={{ margin: 0, paddingLeft: 20 }}>
                  {prepData.project_prep.preparation_tips.map((tip, idx) => (
                    <li key={idx}>{tip}</li>
                  ))}
                </ul>
              }
              type="success"
              showIcon
            />
          </Space>
        </Card>

        {/* 面试题库 */}
        <Card title={<><BookOutlined /> 面试题库</>}>
          <Collapse defaultActiveKey={['common']}>
            {/* 常见问题 */}
            <Panel header={`常见问题 (${prepData.common_questions.length})`} key="common">
              <List
                dataSource={prepData.common_questions}
                renderItem={(item, idx) => (
                  <List.Item>
                    <Space direction="vertical" style={{ width: '100%' }}>
                      <Text strong>{idx + 1}. {item.question}</Text>
                      <Alert message={item.tips} type="info" showIcon />
                    </Space>
                  </List.Item>
                )}
              />
            </Panel>

            {/* 技术问题 */}
            {prepData.technical_questions.length > 0 && (
              <Panel header={`技术问题 (${prepData.technical_questions.length})`} key="technical">
                <List
                  dataSource={prepData.technical_questions}
                  renderItem={(item, idx) => (
                    <List.Item>
                      <Space direction="vertical" style={{ width: '100%' }}>
                        <div>
                          <Text strong>{idx + 1}. {item.question}</Text>
                          <Tag
                            color={getDifficultyColor(item.difficulty)}
                            style={{ marginLeft: 8 }}
                          >
                            {item.difficulty}
                          </Tag>
                          {item.tags.map((tag, tagIdx) => (
                            <Tag key={tagIdx} color="blue">
                              {tag}
                            </Tag>
                          ))}
                        </div>
                        <Alert
                          message="答题提示"
                          description={item.answer_hint}
                          type="warning"
                          showIcon
                        />
                      </Space>
                    </List.Item>
                  )}
                />
              </Panel>
            )}

            {/* 行为问题 */}
            <Panel header={`行为面试问题 (${prepData.behavioral_questions.length})`} key="behavioral">
              <List
                dataSource={prepData.behavioral_questions}
                renderItem={(item, idx) => (
                  <List.Item>
                    <Space direction="vertical" style={{ width: '100%' }}>
                      <Text strong>{idx + 1}. {item.question}</Text>
                      <Alert message={item.tips} type="success" showIcon />
                    </Space>
                  </List.Item>
                )}
              />
            </Panel>
          </Collapse>
        </Card>

        {/* SWOT分析 */}
        <Card title={<><TeamOutlined /> SWOT分析</>}>
          <Row gutter={[16, 16]}>
            <Col span={12}>
              <Card
                size="small"
                title={<Text strong style={{ color: '#52c41a' }}>优势 (Strengths)</Text>}
                style={{ height: '100%' }}
              >
                <ul style={{ margin: 0, paddingLeft: 20 }}>
                  {prepData.swot_analysis.strengths.map((item, idx) => (
                    <li key={idx}>{item}</li>
                  ))}
                </ul>
              </Card>
            </Col>
            <Col span={12}>
              <Card
                size="small"
                title={<Text strong style={{ color: '#faad14' }}>劣势 (Weaknesses)</Text>}
                style={{ height: '100%' }}
              >
                <ul style={{ margin: 0, paddingLeft: 20 }}>
                  {prepData.swot_analysis.weaknesses.map((item, idx) => (
                    <li key={idx}>{item}</li>
                  ))}
                </ul>
              </Card>
            </Col>
            <Col span={12}>
              <Card
                size="small"
                title={<Text strong style={{ color: '#1890ff' }}>机会 (Opportunities)</Text>}
                style={{ height: '100%' }}
              >
                <ul style={{ margin: 0, paddingLeft: 20 }}>
                  {prepData.swot_analysis.opportunities.map((item, idx) => (
                    <li key={idx}>{item}</li>
                  ))}
                </ul>
              </Card>
            </Col>
            <Col span={12}>
              <Card
                size="small"
                title={<Text strong style={{ color: '#ff4d4f' }}>威胁 (Threats)</Text>}
                style={{ height: '100%' }}
              >
                <ul style={{ margin: 0, paddingLeft: 20 }}>
                  {prepData.swot_analysis.threats.map((item, idx) => (
                    <li key={idx}>{item}</li>
                  ))}
                </ul>
              </Card>
            </Col>
          </Row>
        </Card>
      </Space>
    </div>
  );
};

export default InterviewPrep;
