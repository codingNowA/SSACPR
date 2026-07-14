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
  Divider,
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
  SaveOutlined,
  ThunderboltOutlined,
  HistoryOutlined,
} from '@ant-design/icons';
import { getResumeData, diagnoseResume, createResumeVersion, optimizeResume } from '../../services/resume';
import { useAppStore } from '../../store';
import { getScoreColor, getScoreLevel, getSeverityTag, formatDate } from '../../utils';
import type { DiagnosisResult, ResumeData } from '../../types';

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
    if (resumeId && !diagnosisResult) {
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
      setResumeData(resumeDataRes);
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
    if (!resumeId || !versionName.trim()) {
      message.warning('请输入版本名称');
      return;
    }

    try {
      await createResumeVersion(parseInt(resumeId), versionName);
      message.success('版本保存成功！');
      setSaveModalVisible(false);
      setVersionName('');
    } catch (error: any) {
      message.error(error || '保存失败');
    }
  };

  const handleGotoMatch = () => {
    navigate(`/resume/${resumeId}/match`);
  };

  const handleViewVersions = () => {
    navigate(`/resume/${resumeId}/versions`);
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

  const optimized_sections = diagnosisResult?.optimized_sections || [];

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
            {suggestions.map((item, index) => (
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

        {/* 优化后的内容 */}
        {optimized_sections && Object.keys(optimized_sections).length > 0 && (
          <Card title={<><RocketOutlined /> 优化后的内容</>}>
            <Collapse>
              {Object.entries(optimized_sections).map(([key, value]) => (
                <Panel header={key} key={key}>
                  <Paragraph style={{ whiteSpace: 'pre-wrap' }}>{value}</Paragraph>
                </Panel>
              ))}
            </Collapse>
          </Card>
        )}

        {/* 简历详细信息 */}
        {resumeData && (
          <Card title="简历详细信息">
            <Collapse>
              {resumeData.basic_info && (
                <Panel header="基本信息" key="basic">
                  <Descriptions column={2}>
                    <Descriptions.Item label="姓名">
                      {resumeData.basic_info.name}
                    </Descriptions.Item>
                    <Descriptions.Item label="电话">
                      {resumeData.basic_info.phone}
                    </Descriptions.Item>
                    <Descriptions.Item label="邮箱">
                      {resumeData.basic_info.email}
                    </Descriptions.Item>
                    <Descriptions.Item label="求职意向">
                      {resumeData.basic_info.job_intention}
                    </Descriptions.Item>
                  </Descriptions>
                </Panel>
              )}

              {resumeData.education && resumeData.education.length > 0 && (
                <Panel header={`教育经历 (${resumeData.education.length})`} key="education">
                  <Space direction="vertical" size="middle" style={{ width: '100%' }}>
                    {resumeData.education.map((edu, idx) => (
                      <Card key={idx} size="small" type="inner">
                        <Descriptions column={2}>
                          <Descriptions.Item label="学校">{edu.school}</Descriptions.Item>
                          <Descriptions.Item label="专业">{edu.major}</Descriptions.Item>
                          <Descriptions.Item label="学历">{edu.degree}</Descriptions.Item>
                          <Descriptions.Item label="时间">
                            {edu.start_date} - {edu.end_date}
                          </Descriptions.Item>
                        </Descriptions>
                      </Card>
                    ))}
                  </Space>
                </Panel>
              )}

              {resumeData.skills && resumeData.skills.length > 0 && (
                <Panel header={`技能标签 (${resumeData.skills.length})`} key="skills">
                  <Space wrap>
                    {resumeData.skills.map((skill, idx) => (
                      <Tag key={idx} color="blue">
                        {typeof skill === 'string' ? skill : skill.name}
                      </Tag>
                    ))}
                  </Space>
                </Panel>
              )}
            </Collapse>
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
          <Text>为当前简历创建一个版本快照，便于后续投递使用</Text>
          <Input
            placeholder="请输入版本名称（如：字节跳动-后端开发）"
            value={versionName}
            onChange={(e) => setVersionName(e.target.value)}
          />
        </Space>
      </Modal>
    </div>
  );
};

export default ResumeDiagnosis;
