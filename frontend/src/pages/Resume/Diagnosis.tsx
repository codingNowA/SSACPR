/**
 * 简历诊断结果页面
 */
import React, { useEffect, useState } from 'react';
import { useParams, useNavigate } from 'react-router-dom';
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
} from '@ant-design/icons';
import { getResumeData, diagnoseResume, optimizeResume, createResumeVersion } from '../../services/resume';
import { useAppStore } from '../../store';
import { getScoreColor, getScoreLevel, formatDate } from '../../utils';

const { Title, Text, Paragraph } = Typography;
const { Panel } = Collapse;

const ResumeDiagnosis: React.FC = () => {
  const { resumeId } = useParams<{ resumeId: string }>();
  const navigate = useNavigate();
  const { diagnosisResult, setDiagnosisResult, resumeData, setResumeData } = useAppStore();

  const [loading, setLoading] = useState(false);
  const [optimizing, setOptimizing] = useState(false);
  const [saveModalVisible, setSaveModalVisible] = useState(false);
  const [versionName, setVersionName] = useState('');

  useEffect(() => {
    // 仅当无结果或结果属于其他简历时才重新加载，避免切换 resumeId 后展示上一份简历的诊断（脏数据）
    if (resumeId && (!diagnosisResult || diagnosisResult.resume_id !== parseInt(resumeId))) {
      loadDiagnosisResult();
    }
  }, [resumeId]);

  const loadDiagnosisResult = async () => {
    if (!resumeId) return;

    setLoading(true);
    try {
      const [resumeDataRes, diagnosisRes] = await Promise.all([
        getResumeData(parseInt(resumeId)),
        diagnoseResume(parseInt(resumeId)),
      ]);

      // 如果parsed_data是字符串，解析它
      if (resumeDataRes.parsed_data && typeof resumeDataRes.parsed_data === 'string') {
        resumeDataRes.parsed_data = JSON.parse(resumeDataRes.parsed_data);
      }

      setResumeData(resumeDataRes.parsed_data || resumeDataRes);
      setDiagnosisResult(diagnosisRes);
    } catch (error: any) {
      message.error(error || '加载失败');
    } finally {
      setLoading(false);
    }
  };

  const handleOptimize = async () => {
    if (!resumeId) return;

    setOptimizing(true);
    try {
      const result = await optimizeResume(
        parseInt(resumeId),
        resumeData?.basic_info?.job_intention
      );
      setDiagnosisResult(result);
      message.success('优化完成！');
    } catch (error: any) {
      message.error(error || '优化失败');
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
      await createResumeVersion(
        parseInt(resumeId!),
        versionName,
        diagnosisResult.scores,
        diagnosisResult.optimization
      );
      message.success('版本保存成功！');
      setSaveModalVisible(false);
      setVersionName('');
    } catch (error: any) {
      message.error(error || '保存版本失败');
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
      <div style={{ textAlign: 'center', padding: '100px 0' }}>
        <Alert message="未找到诊断结果" type="warning" />
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
                简历ID: {resumeId}
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
                  icon={<ReloadOutlined />}
                  onClick={loadDiagnosisResult}
                  loading={loading}
                >
                  刷新
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
                <div>
                  <Text>岗位匹配</Text>
                  <Progress
                    percent={scores.job_match || 0}
                    strokeColor={getScoreColor(scores.job_match || 0)}
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

        {/* 简历详细信息 */}
        {(() => {
          let d = resumeData;
          if (resumeData?.parsed_data && typeof resumeData.parsed_data === 'object') {
            d = resumeData.parsed_data;
          }
          return d && (
          <Card title="简历详细信息">
            <Collapse>
              {d.basic_info && (
                <Panel header="基本信息" key="basic">
                  <Descriptions column={2}>
                    <Descriptions.Item label="姓名">{d.basic_info.name}</Descriptions.Item>
                    <Descriptions.Item label="电话">{d.basic_info.phone}</Descriptions.Item>
                    <Descriptions.Item label="邮箱">{d.basic_info.email}</Descriptions.Item>
                    <Descriptions.Item label="求职意向">{d.basic_info.job_intention}</Descriptions.Item>
                  </Descriptions>
                </Panel>
              )}

              {d.education && d.education.length > 0 && (
                <Panel header={`教育经历 (${d.education.length})`} key="education">
                  <Space direction="vertical" size="middle" style={{ width: '100%' }}>
                    {d.education.map((edu, idx) => (
                      <Card key={idx} size="small" type="inner">
                        <Descriptions column={2}>
                          <Descriptions.Item label="学校">{edu.school}</Descriptions.Item>
                          <Descriptions.Item label="专业">{edu.major}</Descriptions.Item>
                          <Descriptions.Item label="学历">{edu.degree}</Descriptions.Item>
                          <Descriptions.Item label="时间">{edu.start_date} - {edu.end_date}</Descriptions.Item>
                        </Descriptions>
                      </Card>
                    ))}
                  </Space>
                </Panel>
              )}

              {d.work_experience && d.work_experience.length > 0 && (
                <Panel header={`工作经历 (${d.work_experience.length})`} key="work">
                  <Space direction="vertical" size="middle" style={{ width: '100%' }}>
                    {d.work_experience.map((w, idx) => (
                      <Card key={idx} size="small" type="inner">
                        <Descriptions column={2}>
                          <Descriptions.Item label="公司">{w.company}</Descriptions.Item>
                          <Descriptions.Item label="职位">{w.position}</Descriptions.Item>
                          <Descriptions.Item label="时间">{w.start_date} - {w.end_date || '至今'}</Descriptions.Item>
                        </Descriptions>
                      </Card>
                    ))}
                  </Space>
                </Panel>
              )}

              {d.skills && d.skills.length > 0 && (
                <Panel header={`技能标签 (${d.skills.length})`} key="skills">
                  <Space wrap>
                    {d.skills.map((skill, idx) => (
                      <Tag key={idx} color="blue">
                        {typeof skill === 'string' ? skill : skill.name}
                      </Tag>
                    ))}
                  </Space>
                </Panel>
              )}
            </Collapse>
          </Card>
          );
        })()}
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
