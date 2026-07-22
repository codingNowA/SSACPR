/**
 * 简历诊断结果页面
 */
import React, { useEffect, useState } from 'react';
import { useParams, useNavigate, useLocation } from 'react-router-dom';
import {
  Card,
  Row,
  Col,
  Progress,
  Tag,
  Typography,
  Space,
  Button,
  Alert,
  Spin,
  Collapse,
  Descriptions,
  message,
  Modal,
  Input,
} from 'antd';
import {
  TrophyOutlined,
  BulbOutlined,
  RocketOutlined,
  ThunderboltOutlined,
  ReloadOutlined,
  ArrowLeftOutlined,
  SaveOutlined,
  HistoryOutlined,
  EditOutlined,
  FileTextOutlined,
} from '@ant-design/icons';
import { getResumeData, diagnoseResume, optimizeResume, createResumeVersion } from '../../services/resume';
import apiClient from '../../services/api';
import { useAppStore } from '../../store';
import { getScoreColor, getScoreLevel, formatDate } from '../../utils';

const { Title, Text, Paragraph } = Typography;
const { Panel } = Collapse;

const ResumeDiagnosis: React.FC = () => {
  const { resumeId } = useParams<{ resumeId: string }>();
  const navigate = useNavigate();
  const location = useLocation(); // 添加 location 来监听路由变化
  const { diagnosisResult, setDiagnosisResult, resumeData, setResumeData } = useAppStore();

  const [loading, setLoading] = useState(false);
  const [optimizing, setOptimizing] = useState(false);
  const [saveModalVisible, setSaveModalVisible] = useState(false);
  const [versionName, setVersionName] = useState('');

  useEffect(() => {
    // 每次进入页面或路由变化时都加载数据并自动诊断
    if (resumeId) {
      loadAndDiagnose();
    }
  }, [resumeId, location.key]); // 使用 location.key 监听导航变化

  const loadAndDiagnose = async () => {
    if (!resumeId) return;

    setLoading(true);
    try {
      console.log('开始加载诊断数据，resumeId:', resumeId);

      // 先加载简历数据
      const resumeDataRes = await apiClient.get(`/api/v1/resume/${resumeId}/structured`);
      console.log('简历数据响应:', resumeDataRes);

      // 解析简历数据
      let parsedData = resumeDataRes;
      if (typeof parsedData === 'string') {
        parsedData = JSON.parse(parsedData);
      }
      console.log('解析后的简历数据:', parsedData);
      console.log('parsedData 类型:', typeof parsedData);
      console.log('parsedData.basic_info:', parsedData?.basic_info);

      setResumeData(parsedData);

      // 每次进入页面都自动触发诊断（覆盖旧的诊断结果）
      console.log('自动触发诊断');
      await handleDiagnose(false); // 不显示提示信息

    } catch (error: any) {
      console.error('加载失败:', error);
      const errorMsg = error?.message || error?.toString() || '加载失败';
      message.error(errorMsg);
    } finally {
      setLoading(false);
    }
  };

  const handleDiagnose = async (showMessage = true) => {
    if (!resumeId) return;

    const loadingKey = 'diagnose-' + Date.now();
    try {
      if (showMessage) {
        message.loading({ content: '正在诊断...', key: loadingKey, duration: 0 });
      }

      // 触发新的诊断
      const diagnosisRes = await diagnoseResume(parseInt(resumeId));
      setDiagnosisResult(diagnosisRes);

      if (showMessage) {
        message.success({ content: '诊断完成！', key: loadingKey });
      }
      return diagnosisRes;
    } catch (error: any) {
      const errorMsg = error?.message || error?.toString() || '诊断失败';
      if (showMessage) {
        message.error({ content: errorMsg, key: loadingKey });
      }
      throw error;
    }
  };

  const handleOptimize = async () => {
    if (!resumeId) return;

    setOptimizing(true);
    try {
      message.loading({ content: '正在优化简历...', key: 'optimize', duration: 0 });
      const result = await optimizeResume(
        parseInt(resumeId),
        resumeData?.basic_info?.job_intention
      );
      setDiagnosisResult(result);
      message.success({
        content: '优化完成！请及时保存版本，退出该页面后优化结果消失！',
        key: 'optimize',
        duration: 8  // 延长显示时间到8秒
      });
    } catch (error: any) {
      const errorMsg = error?.message || error?.toString() || '优化失败';
      message.error({ content: errorMsg, key: 'optimize' });
    } finally {
      setOptimizing(false);
    }
  };

  const handleSaveVersion = async () => {
    if (!versionName.trim()) {
      message.warning('请输入版本名称');
      return;
    }

    if (!diagnosisResult) {
      message.warning('请先进行简历诊断或优化');
      return;
    }

    console.log('保存版本 - diagnosisResult:', diagnosisResult);
    console.log('保存版本 - scores:', diagnosisResult.scores);
    console.log('保存版本 - optimization:', diagnosisResult.optimization);

    try {
      message.loading({ content: '正在保存版本...', key: 'save', duration: 0 });

      // 准备保存的数据：包含评分、优化建议和当前简历内容
      const versionData = {
        scores: diagnosisResult.scores,
        optimization: diagnosisResult.optimization,
        summary: diagnosisResult.summary,
      };

      await createResumeVersion(
        parseInt(resumeId!),
        versionName,
        versionData,  // 保存完整的诊断结果（包含scores、optimization、summary）
        resumeData     // 保存当前的简历数据
      );
      message.success({ content: '版本保存成功！', key: 'save' });
      setSaveModalVisible(false);
      setVersionName('');
    } catch (error: any) {
      const errorMsg = error?.message || error?.toString() || '保存版本失败';
      message.error({ content: errorMsg, key: 'save' });
    }
  };

  const handleGotoMatch = () => {
    navigate(`/resume/${resumeId}/match`);
  };

  const handleViewVersions = () => {
    navigate(`/resume/versions/${resumeId}`);
  };

  if (loading) {
    return (
      <div style={{ textAlign: 'center', padding: '100px 0' }}>
        <Spin size="large" tip="加载中..." />
      </div>
    );
  }

  if (!diagnosisResult) {
    return (
      <div style={{ padding: '24px', maxWidth: '1200px', margin: '0 auto' }}>
        <Space direction="vertical" size="large" style={{ width: '100%' }}>
          <Card>
            <Row justify="space-between" align="middle">
              <Col>
                <Title level={2}>
                  <TrophyOutlined /> 简历诊断
                </Title>
                <Text type="secondary">
                  简历 #{resumeData?._user_resume_number || resumeId}
                </Text>
              </Col>
              <Col>
                <Space>
                  <Button icon={<HistoryOutlined />} onClick={handleViewVersions}>
                    版本历史
                  </Button>
                  <Button icon={<ArrowLeftOutlined />} onClick={() => navigate('/resume/upload')}>
                    返回上传
                  </Button>
                  <Button
                    icon={<EditOutlined />}
                    onClick={() => navigate(`/resume/edit/${resumeId}`)}
                  >
                    编辑简历
                  </Button>
                </Space>
              </Col>
            </Row>
          </Card>

          <Card>
            <div style={{ textAlign: 'center', padding: '60px 0' }}>
              <Alert
                message="尚未诊断"
                description="点击下方按钮对简历进行智能诊断分析"
                type="info"
                showIcon
                style={{ marginBottom: 24 }}
              />
              <Button
                type="primary"
                size="large"
                icon={<ThunderboltOutlined />}
                onClick={handleDiagnose}
                loading={loading}
              >
                开始诊断
              </Button>
            </div>
          </Card>
        </Space>
      </div>
    );
  }

  // 后端返回的数据结构：{ resume_id, scores: {...} }
  console.log('diagnosisResult:', diagnosisResult);
  const scores = diagnosisResult?.scores || {};
  console.log('scores:', scores);

  // 从 dimensions 中提取建议
  const suggestions = Array.isArray(scores?.dimensions)
    ? scores.dimensions.map((dim: any) => ({
        type: dim.score >= 80 ? 'success' : dim.score >= 60 ? 'warning' : 'error',
        importance: dim.score < 60 ? '重要' : dim.score < 80 ? '中等' : '建议',
        content: dim.feedback,
        dimension: dim.name,
      }))
    : [];
  console.log('suggestions:', suggestions);

  // 提取优化内容
  const optimization = diagnosisResult?.optimization;
  const general_suggestions = optimization?.general_suggestions || [];
  const priority_actions = optimization?.priority_actions || [];
  const overall_summary = optimization?.overall_summary || '';
  const has_optimization = general_suggestions.length > 0 || priority_actions.length > 0;

  return (
    <div style={{ padding: '24px', maxWidth: '1200px', margin: '0 auto' }}>
      <Space direction="vertical" size="large" style={{ width: '100%' }}>
        {/* 头部 */}
        <Card>
          <Row justify="space-between" align="middle">
            <Col>
              <Title level={2}>
                <TrophyOutlined /> 简历诊断报告
              </Title>
              <Text type="secondary">
                简历 #{resumeData?._user_resume_number || resumeId}
                {diagnosisResult?.created_at && ` | 诊断时间: ${formatDate(diagnosisResult.created_at)}`}
              </Text>
            </Col>
            <Col>
              <Space>
                <Button icon={<HistoryOutlined />} onClick={handleViewVersions}>
                  版本历史
                </Button>
                <Button icon={<SaveOutlined />} onClick={() => setSaveModalVisible(true)}>
                  保存版本
                </Button>
                <Button
                  type="primary"
                  icon={<ThunderboltOutlined />}
                  onClick={handleDiagnose}
                  loading={loading}
                >
                  重新诊断
                </Button>
                <Button icon={<ArrowLeftOutlined />} onClick={() => navigate('/resume/upload')}>
                  返回上传
                </Button>
                <Button
                  icon={<EditOutlined />}
                  onClick={() => navigate(`/resume/edit/${resumeId}`)}
                >
                  编辑简历
                </Button>
                <Button
                  type="primary"
                  icon={<RocketOutlined />}
                  onClick={handleGotoMatch}
                >
                  岗位匹配
                </Button>
              </Space>
            </Col>
          </Row>
        </Card>

        {/* 诊断前快照提示 */}
        {diagnosisResult?.snapshot_id && diagnosisResult?.snapshot_name && (
          <Alert
            message="诊断前快照已自动保存"
            description={
              <Space>
                <Text>
                  系统已自动保存诊断前的简历版本：<Text strong>{diagnosisResult.snapshot_name}</Text>
                </Text>
                <Button
                  type="link"
                  size="small"
                  icon={<HistoryOutlined />}
                  onClick={handleViewVersions}
                >
                  查看版本历史
                </Button>
              </Space>
            }
            type="info"
            showIcon
            closable
          />
        )}

        {/* 简历内容展示 */}
        {resumeData && (
          <Card title={<Text strong><FileTextOutlined /> 简历内容</Text>}>
            <Collapse defaultActiveKey={['basic']}>
              {/* 基本信息 */}
              {resumeData.basic_info && (
                <Panel header="📋 基本信息" key="basic">
                  <Descriptions column={2} size="small">
                    {resumeData.basic_info.name && (
                      <Descriptions.Item label="姓名">{resumeData.basic_info.name}</Descriptions.Item>
                    )}
                    {resumeData.basic_info.phone && (
                      <Descriptions.Item label="电话">{resumeData.basic_info.phone}</Descriptions.Item>
                    )}
                    {resumeData.basic_info.email && (
                      <Descriptions.Item label="邮箱">{resumeData.basic_info.email}</Descriptions.Item>
                    )}
                    {resumeData.basic_info.job_intention && (
                      <Descriptions.Item label="求职意向">{resumeData.basic_info.job_intention}</Descriptions.Item>
                    )}
                    {resumeData.basic_info.age && (
                      <Descriptions.Item label="年龄">{resumeData.basic_info.age}</Descriptions.Item>
                    )}
                    {resumeData.basic_info.gender && (
                      <Descriptions.Item label="性别">{resumeData.basic_info.gender}</Descriptions.Item>
                    )}
                    {resumeData.basic_info.location && (
                      <Descriptions.Item label="所在地">{resumeData.basic_info.location}</Descriptions.Item>
                    )}
                  </Descriptions>
                </Panel>
              )}

              {/* 技能 */}
              {resumeData.skills && resumeData.skills.length > 0 && (
                <Panel header={`🛠 技能 (${resumeData.skills.length})`} key="skills">
                  <Space wrap>
                    {resumeData.skills.map((skill: any, idx: number) => (
                      <Tag key={idx} color="blue">
                        {typeof skill === 'string' ? skill : skill.name}
                        {skill.level && <Text type="secondary" style={{ marginLeft: 4 }}>({skill.level})</Text>}
                      </Tag>
                    ))}
                  </Space>
                </Panel>
              )}

              {/* 教育经历 */}
              {resumeData.education && resumeData.education.length > 0 && (
                <Panel header={`🎓 教育经历 (${resumeData.education.length})`} key="education">
                  <Space direction="vertical" size="middle" style={{ width: '100%' }}>
                    {resumeData.education.map((edu: any, idx: number) => (
                      <Card key={idx} size="small" type="inner">
                        <Descriptions column={2} size="small">
                          {edu.school && (
                            <Descriptions.Item label="学校">{edu.school}</Descriptions.Item>
                          )}
                          {edu.major && (
                            <Descriptions.Item label="专业">{edu.major}</Descriptions.Item>
                          )}
                          {edu.degree && (
                            <Descriptions.Item label="学历">{edu.degree}</Descriptions.Item>
                          )}
                          {(edu.start_date || edu.end_date) && (
                            <Descriptions.Item label="时间">
                              {edu.start_date || '?'} - {edu.end_date || '至今'}
                            </Descriptions.Item>
                          )}
                          {edu.gpa && (
                            <Descriptions.Item label="GPA">{edu.gpa}</Descriptions.Item>
                          )}
                          {edu.description && (
                            <Descriptions.Item label="描述" span={2}>{edu.description}</Descriptions.Item>
                          )}
                        </Descriptions>
                      </Card>
                    ))}
                  </Space>
                </Panel>
              )}

              {/* 工作经历 */}
              {resumeData.work_experience && resumeData.work_experience.length > 0 && (
                <Panel header={`🏢 工作经历 (${resumeData.work_experience.length})`} key="work">
                  <Space direction="vertical" size="middle" style={{ width: '100%' }}>
                    {resumeData.work_experience.map((work: any, idx: number) => (
                      <Card key={idx} size="small" type="inner">
                        <Descriptions column={2} size="small">
                          {work.company && (
                            <Descriptions.Item label="公司">{work.company}</Descriptions.Item>
                          )}
                          {work.position && (
                            <Descriptions.Item label="职位">{work.position}</Descriptions.Item>
                          )}
                          {(work.start_date || work.end_date) && (
                            <Descriptions.Item label="时间" span={2}>
                              {work.start_date || '?'} - {work.end_date || '至今'}
                            </Descriptions.Item>
                          )}
                          {work.description && (
                            <Descriptions.Item label="工作内容" span={2}>
                              {work.description}
                            </Descriptions.Item>
                          )}
                        </Descriptions>
                        {work.achievements && work.achievements.length > 0 && (
                          <div style={{ marginTop: 12 }}>
                            <Text strong>工作成果：</Text>
                            <ul style={{ margin: '8px 0 0 0', paddingLeft: 20 }}>
                              {work.achievements.map((achievement: string, aIdx: number) => (
                                <li key={aIdx}>{achievement}</li>
                              ))}
                            </ul>
                          </div>
                        )}
                      </Card>
                    ))}
                  </Space>
                </Panel>
              )}

              {/* 项目经历 */}
              {resumeData.project_experience && resumeData.project_experience.length > 0 && (
                <Panel header={`📦 项目经历 (${resumeData.project_experience.length})`} key="project">
                  <Space direction="vertical" size="middle" style={{ width: '100%' }}>
                    {resumeData.project_experience.map((project: any, idx: number) => (
                      <Card key={idx} size="small" type="inner">
                        <Descriptions column={2} size="small">
                          {project.name && (
                            <Descriptions.Item label="项目名称">{project.name}</Descriptions.Item>
                          )}
                          {project.role && (
                            <Descriptions.Item label="项目角色">{project.role}</Descriptions.Item>
                          )}
                          {(project.start_date || project.end_date) && (
                            <Descriptions.Item label="时间" span={2}>
                              {project.start_date || '?'} - {project.end_date || '至今'}
                            </Descriptions.Item>
                          )}
                          {project.description && (
                            <Descriptions.Item label="项目描述" span={2}>
                              {project.description}
                            </Descriptions.Item>
                          )}
                        </Descriptions>
                        {project.tech_stack && project.tech_stack.length > 0 && (
                          <div style={{ marginTop: 12 }}>
                            <Text strong>技术栈：</Text>
                            <div style={{ marginTop: 8 }}>
                              <Space wrap>
                                {project.tech_stack.map((tech: string, tIdx: number) => (
                                  <Tag key={tIdx} color="geekblue">{tech}</Tag>
                                ))}
                              </Space>
                            </div>
                          </div>
                        )}
                        {project.achievements && project.achievements.length > 0 && (
                          <div style={{ marginTop: 12 }}>
                            <Text strong>项目成果：</Text>
                            <ul style={{ margin: '8px 0 0 0', paddingLeft: 20 }}>
                              {project.achievements.map((achievement: string, aIdx: number) => (
                                <li key={aIdx}>{achievement}</li>
                              ))}
                            </ul>
                          </div>
                        )}
                      </Card>
                    ))}
                  </Space>
                </Panel>
              )}
            </Collapse>
          </Card>
        )}

        {/* 评分概览 */}
        <Card title={<><TrophyOutlined /> 综合评分</>}>
          <Row gutter={[24, 24]}>
            <Col xs={24} sm={12} md={8}>
              <div style={{ textAlign: 'center' }}>
                <Progress
                  type="circle"
                  percent={scores.total_score || 0}
                  strokeColor={getScoreColor(scores.total_score || 0)}
                  format={(percent) => (
                    <div>
                      <div style={{ fontSize: '24px', fontWeight: 'bold' }}>{percent}</div>
                      <div style={{ fontSize: '14px', color: '#666' }}>
                        {getScoreLevel(percent || 0)}
                      </div>
                    </div>
                  )}
                />
                <div style={{ marginTop: '16px' }}>
                  <Text strong>综合得分</Text>
                </div>
              </div>
            </Col>
            <Col xs={24} sm={12} md={16}>
              <Space direction="vertical" size="middle" style={{ width: '100%' }}>
                <div>
                  <Text>完整性</Text>
                  <Progress
                    percent={scores.completeness?.total_score || 0}
                    strokeColor={getScoreColor(scores.completeness?.total_score || 0)}
                  />
                </div>
                <div>
                  <Text>专业性</Text>
                  <Progress
                    percent={scores.professionalism?.total_score || 0}
                    strokeColor={getScoreColor(scores.professionalism?.total_score || 0)}
                  />
                </div>
                <div>
                  <Text>量化程度</Text>
                  <Progress
                    percent={scores.quantification?.total_score || 0}
                    strokeColor={getScoreColor(scores.quantification?.total_score || 0)}
                  />
                </div>
                <div>
                  <Text>项目深度</Text>
                  <Progress
                    percent={scores.project_depth?.total_score || 0}
                    strokeColor={getScoreColor(scores.project_depth?.total_score || 0)}
                  />
                </div>
              </Space>
            </Col>
          </Row>
        </Card>

        {/* 优化建议 */}
        <Card
          title={<><BulbOutlined /> 优化建议 ({suggestions.length})</>}
          extra={
            <Button
              type="primary"
              icon={<ThunderboltOutlined />}
              onClick={handleOptimize}
              loading={optimizing}
            >
              一键优化
            </Button>
          }
        >
          <Space direction="vertical" size="middle" style={{ width: '100%' }}>
            {suggestions.map((item: any, index: number) => (
              <Card key={index} size="small" type="inner">
                <Space direction="vertical" style={{ width: '100%' }}>
                  <div>
                    <Tag color={item.type === 'success' ? 'green' : item.type === 'warning' ? 'orange' : 'red'}>
                      {item.importance}
                    </Tag>
                    <Text strong>{item.dimension}</Text>
                  </div>
                  <Alert
                    message={item.content}
                    type={item.type}
                    showIcon
                  />
                </Space>
              </Card>
            ))}
          </Space>
        </Card>

        {/* 优化建议详情 */}
        {has_optimization && (
          <Card title={<><RocketOutlined /> 优化建议详情</>}>
            <Space direction="vertical" size="large" style={{ width: '100%' }}>
              {/* 总体摘要 */}
              {overall_summary && (
                <Alert
                  message="优化总结"
                  description={overall_summary}
                  type="info"
                  showIcon
                />
              )}

              {/* 优先行动 */}
              {priority_actions.length > 0 && (
                <div>
                  <Title level={4}>优先改进项</Title>
                  <Space direction="vertical" size="middle" style={{ width: '100%' }}>
                    {priority_actions.map((action: any, index: number) => (
                      <Card key={index} size="small" type="inner">
                        <Space direction="vertical" style={{ width: '100%' }}>
                          <div>
                            <Tag color="red">高优先级</Tag>
                          </div>
                          <Alert
                            message={typeof action === 'string' ? action : action.description}
                            type="error"
                            showIcon
                          />
                        </Space>
                      </Card>
                    ))}
                  </Space>
                </div>
              )}

              {/* 详细建议 */}
              {general_suggestions.length > 0 && (
                <div>
                  <Title level={4}>详细优化建议</Title>
                  <Collapse>
                    {general_suggestions.map((suggestion: any, index: number) => {
                      // 优先级映射：支持中英文
                      const getPriorityConfig = (priority: string) => {
                        const p = priority?.toLowerCase() || '';
                        if (p === 'high' || p === '高') return { color: 'red', text: '高' };
                        if (p === 'medium' || p === '中') return { color: 'orange', text: '中' };
                        return { color: 'blue', text: '低' };
                      };
                      const priorityConfig = getPriorityConfig(suggestion.priority);

                      return (
                        <Panel
                          header={
                            <Space>
                              <Tag color={priorityConfig.color}>
                                {priorityConfig.text}
                              </Tag>
                              <Text strong>{suggestion.title}</Text>
                            </Space>
                          }
                          key={index}
                        >
                        <Space direction="vertical" style={{ width: '100%' }}>
                          <Descriptions column={1} size="small">
                            <Descriptions.Item label="类别">{suggestion.category}</Descriptions.Item>
                            <Descriptions.Item label="说明">{suggestion.description}</Descriptions.Item>
                            {suggestion.reason && (
                              <Descriptions.Item label="原因">{suggestion.reason}</Descriptions.Item>
                            )}
                          </Descriptions>

                          {suggestion.current_content && (
                            <div>
                              <Text type="secondary">当前内容：</Text>
                              <Card size="small" style={{ backgroundColor: '#fff1f0' }}>
                                <Paragraph style={{ margin: 0 }}>{suggestion.current_content}</Paragraph>
                              </Card>
                            </div>
                          )}

                          {suggestion.suggested_content && (
                            <div>
                              <Text type="secondary">建议修改为：</Text>
                              <Card size="small" style={{ backgroundColor: '#f6ffed' }}>
                                <Paragraph style={{ margin: 0 }}>{suggestion.suggested_content}</Paragraph>
                              </Card>
                            </div>
                          )}

                          {suggestion.examples && suggestion.examples.length > 0 && (
                            <div>
                              <Text type="secondary">示例：</Text>
                              {suggestion.examples.map((example: string, idx: number) => (
                                <Card key={idx} size="small" style={{ marginTop: '8px' }}>
                                  <Paragraph style={{ margin: 0 }}>{example}</Paragraph>
                                </Card>
                              ))}
                            </div>
                          )}
                        </Space>
                      </Panel>
                      );
                    })}
                  </Collapse>
                </div>
              )}
            </Space>
          </Card>
        )}

      </Space>

      {/* 保存版本弹窗 */}
      <Modal
        title="保存简历版本"
        open={saveModalVisible}
        onOk={handleSaveVersion}
        onCancel={() => setSaveModalVisible(false)}
      >
        <Space direction="vertical" style={{ width: '100%' }}>
          <Text>为当前简历状态创建一个版本快照（包含诊断评分和优化建议）</Text>
          <Input
            placeholder="请输入版本名称（如：字节跳动-后端开发 v1.0）"
            value={versionName}
            onChange={(e) => setVersionName(e.target.value)}
            onPressEnter={handleSaveVersion}
          />
        </Space>
      </Modal>
    </div>
  );
};

export default ResumeDiagnosis;
