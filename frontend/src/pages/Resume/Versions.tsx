/**
 * 简历版本管理页面
 */
import React, { useState, useEffect } from 'react';
import { useParams, useNavigate } from 'react-router-dom';
import {
  Card,
  Table,
  Button,
  Space,
  Typography,
  Tag,
  Modal,
  message,
  Popconfirm,
  Empty,
  Progress,
  Descriptions,
  Divider,
  Row,
  Col,
  Collapse,
} from 'antd';
import {
  HistoryOutlined,
  EyeOutlined,
  DeleteOutlined,
  ArrowLeftOutlined,
  UserOutlined,
  TrophyOutlined,
  BulbOutlined,
  FileTextOutlined,
} from '@ant-design/icons';
import { getResumeVersions, getVersionDetail, deleteVersion } from '../../services/resume';
import { formatDate, getScoreColor, getScoreLevel } from '../../utils';
import type { ResumeVersion } from '../../types';
import type { ColumnsType } from 'antd/es/table';

const { Title, Text, Paragraph } = Typography;

/** 评分项配置 */
const SCORE_ITEMS = [
  { key: 'completeness', label: '完整性', icon: '📋' },
  { key: 'professionalism', label: '专业性', icon: '💼' },
  { key: 'quantification', label: '量化程度', icon: '📊' },
  { key: 'project_depth', label: '项目深度', icon: '🔬' },
  { key: 'job_match', label: '岗位匹配', icon: '🎯' },
];

/** 从 scores 对象中提取分数值（兼容嵌套对象和扁平数值） */
const getScoreValue = (scores: any, key: string): number | null => {
  const val = scores[key];
  if (val === undefined || val === null) return null;
  if (typeof val === 'number') return val;
  if (typeof val === 'object' && val !== null) {
    return typeof val.total_score === 'number' ? val.total_score : null;
  }
  const parsed = parseFloat(val);
  return isNaN(parsed) ? null : parsed;
};

/** 渲染评分区域 */
const ScoreSection: React.FC<{ scores: any }> = ({ scores }) => {
  if (!scores) return <Text type="secondary">暂无评分数据</Text>;

  const totalScore = getScoreValue(scores, 'total_score');

  return (
    <>
      {/* 总分 */}
      {totalScore !== null && (
        <div style={{ textAlign: 'center', marginBottom: 16 }}>
          <Progress
            type="dashboard"
            percent={totalScore}
            size={100}
            strokeColor={getScoreColor(totalScore)}
            format={(p) => <span style={{ fontSize: 24 }}>{p}</span>}
          />
          <div style={{ marginTop: 4 }}>
            <Tag color={getScoreColor(totalScore) === '#52c41a' ? 'success' : getScoreColor(totalScore) === '#faad14' ? 'warning' : 'error'}>
              ⭐ 综合评分 · {getScoreLevel(totalScore)}
            </Tag>
          </div>
        </div>
      )}

      {/* 各维度评分 */}
      <Row gutter={[16, 16]}>
        {SCORE_ITEMS.map(({ key, label, icon }) => {
          const score = getScoreValue(scores, key);
          if (score === null) return null;
          return (
            <Col span={8} key={key}>
              <Card size="small" style={{ textAlign: 'center' }}>
                <div style={{ fontSize: 20 }}>{icon}</div>
                <div style={{ margin: '8px 0 4px' }}>
                  <Text type="secondary" style={{ fontSize: 12 }}>{label}</Text>
                </div>
                <Progress
                  type="dashboard"
                  percent={score}
                  size={80}
                  strokeColor={getScoreColor(score)}
                  format={(p) => `${p}`}
                />
                <div style={{ marginTop: 4 }}>
                  <Tag color={getScoreColor(score) === '#52c41a' ? 'success' : getScoreColor(score) === '#faad14' ? 'warning' : 'error'}>
                    {getScoreLevel(score)}
                  </Tag>
                </div>
              </Card>
            </Col>
          );
        })}
      </Row>
    </>
  );
};

/** 渲染简历内容摘要 */
const ResumeSummary: React.FC<{ data: any }> = ({ data }) => {
  if (!data) return <Text type="secondary">暂无简历数据</Text>;

  let parsed = typeof data === 'string' ? JSON.parse(data) : data;
  // 兼容：如果 parsed_data 里嵌套了 parsed_data 字段，取内层
  if (parsed?.parsed_data && typeof parsed.parsed_data === 'object') {
    parsed = parsed.parsed_data;
  }
  const basic = parsed?.basic_info || {};
  const skills = parsed?.skills || [];
  const education = parsed?.education || [];
  const work = parsed?.work_experience || [];

  return (
    <Space direction="vertical" size="middle" style={{ width: '100%' }}>
      {/* 基本信息 */}
      {basic.name && (
        <Descriptions column={2} size="small" title={<Space><UserOutlined /> 基本信息</Space>}>
          {basic.name && <Descriptions.Item label="姓名">{basic.name}</Descriptions.Item>}
          {basic.phone && <Descriptions.Item label="电话">{basic.phone}</Descriptions.Item>}
          {basic.email && <Descriptions.Item label="邮箱">{basic.email}</Descriptions.Item>}
          {basic.job_intention && <Descriptions.Item label="求职意向">{basic.job_intention}</Descriptions.Item>}
          {basic.current_location && <Descriptions.Item label="所在地">{basic.current_location}</Descriptions.Item>}
          {basic.years_of_experience && <Descriptions.Item label="工作年限">{basic.years_of_experience}</Descriptions.Item>}
        </Descriptions>
      )}

      {/* 技能标签 */}
      {skills.length > 0 && (
        <div>
          <Text strong style={{ marginBottom: 8, display: 'block' }}>🛠 技能标签</Text>
          <Space wrap>
            {skills.map((s: any, i: number) => (
              <Tag color="blue" key={i}>{typeof s === 'string' ? s : s.name}</Tag>
            ))}
          </Space>
        </div>
      )}

      {/* 教育经历 */}
      {education.length > 0 && (
        <div>
          <Text strong style={{ marginBottom: 8, display: 'block' }}>🎓 教育经历</Text>
          {education.map((edu: any, i: number) => (
            <div key={i} style={{ marginBottom: 4 }}>
              <Text strong>{edu.school}</Text>
              {edu.major && <Text type="secondary"> · {edu.major}</Text>}
              {edu.degree && <Tag style={{ marginLeft: 8 }}>{edu.degree}</Tag>}
            </div>
          ))}
        </div>
      )}

      {/* 工作经历 */}
      {work.length > 0 && (
        <div>
          <Text strong style={{ marginBottom: 8, display: 'block' }}>🏢 工作经历</Text>
          {work.map((w: any, i: number) => (
            <div key={i} style={{ marginBottom: 4 }}>
              <Text strong>{w.company}</Text>
              {w.position && <Text type="secondary"> · {w.position}</Text>}
              {w.start_date && (
                <Text type="secondary" style={{ marginLeft: 8 }}>
                  {w.start_date} ~ {w.end_date || '至今'}
                </Text>
              )}
            </div>
          ))}
        </div>
      )}
    </Space>
  );
};

/** 渲染优化建议 - 兼容后端 general_suggestions/priority_actions/overall_summary 格式 */
const OptimizationSection: React.FC<{ optimization: any }> = ({ optimization }) => {
  if (!optimization) return <Text type="secondary">暂无优化建议</Text>;

  // 兼容多种格式
  const generalSuggestions = optimization?.general_suggestions || [];
  const priorityActions = optimization?.priority_actions || [];
  const overallSummary = optimization?.overall_summary || '';
  const suggestions = optimization?.suggestions || [];
  const hasBackendFormat = generalSuggestions.length > 0 || priorityActions.length > 0 || overallSummary;

  if (!hasBackendFormat && suggestions.length === 0 && !Array.isArray(optimization)) {
    return <Text type="secondary">暂无优化建议</Text>;
  }

  return (
    <Space direction="vertical" size="middle" style={{ width: '100%' }}>
      {/* 总体摘要 */}
      {overallSummary && (
        <Card size="small" style={{ background: '#f0f5ff', borderColor: '#adc6ff' }}>
          <Space><BulbOutlined /><Text strong>优化总结</Text></Space>
          <Paragraph style={{ margin: '8px 0 0' }}>{overallSummary}</Paragraph>
        </Card>
      )}

      {/* 优先行动 */}
      {priorityActions.length > 0 && (
        <div>
          <Text strong style={{ marginBottom: 8, display: 'block' }}>🔴 优先改进项</Text>
          <Space direction="vertical" size="small" style={{ width: '100%' }}>
            {priorityActions.map((action: any, i: number) => (
              <Tag key={i} color="error" style={{ width: '100%', textAlign: 'left', whiteSpace: 'pre-wrap', height: 'auto', padding: '4px 8px' }}>
                {typeof action === 'string' ? action : action.description || action.title}
              </Tag>
            ))}
          </Space>
        </div>
      )}

      {/* 详细建议 - general_suggestions 格式 */}
      {generalSuggestions.length > 0 && (
        <div>
          <Text strong style={{ marginBottom: 8, display: 'block' }}>💡 详细优化建议</Text>
          <Collapse
            items={generalSuggestions.map((s: any, i: number) => ({
              key: i,
              label: (
                <Space>
                  <Tag color={s.priority === 'high' || s.priority === '高' ? 'error' : s.priority === 'medium' || s.priority === '中' ? 'warning' : 'info'}>
                    {s.priority === 'high' || s.priority === '高' ? '高' : s.priority === 'medium' || s.priority === '中' ? '中' : '低'}
                  </Tag>
                  <Text>{s.title || s.category}</Text>
                </Space>
              ),
              children: (
                <Space direction="vertical" style={{ width: '100%' }}>
                  {s.description && <Paragraph>{s.description}</Paragraph>}
                  {s.reason && <Text type="secondary">原因：{s.reason}</Text>}
                  {s.current_content && (
                    <div style={{ background: '#fff1f0', padding: 8, borderRadius: 4 }}>
                      <Text type="secondary" style={{ fontSize: 12 }}>当前内容：</Text>
                      <Paragraph style={{ margin: '4px 0 0' }}>{s.current_content}</Paragraph>
                    </div>
                  )}
                  {s.suggested_content && (
                    <div style={{ background: '#f6ffed', padding: 8, borderRadius: 4 }}>
                      <Text type="secondary" style={{ fontSize: 12 }}>建议修改：</Text>
                      <Paragraph style={{ margin: '4px 0 0' }}>{s.suggested_content}</Paragraph>
                    </div>
                  )}
                </Space>
              ),
            }))}
          />
        </div>
      )}

      {/* suggestions 格式（兜底） */}
      {suggestions.length > 0 && !hasBackendFormat && (
        <Collapse
          items={suggestions.map((s: any, i: number) => ({
            key: i,
            label: (
              <Space>
                <Tag color={s.severity === 'high' ? 'error' : s.severity === 'medium' ? 'warning' : 'info'}>
                  {s.severity === 'high' ? '重要' : s.severity === 'medium' ? '中等' : '建议'}
                </Tag>
                <Text>{s.issue || s.category}</Text>
              </Space>
            ),
            children: (
              <Space direction="vertical" style={{ width: '100%' }}>
                <Paragraph>{s.suggestion}</Paragraph>
                {s.example && (
                  <div style={{ background: '#f6f8fa', padding: 12, borderRadius: 6 }}>
                    <Text type="secondary" style={{ fontSize: 12 }}>参考示例：</Text>
                    <Paragraph style={{ margin: '4px 0 0', whiteSpace: 'pre-wrap' }}>{s.example}</Paragraph>
                  </div>
                )}
              </Space>
            ),
          }))}
        />
      )}
    </Space>
  );
};

const ResumeVersions: React.FC = () => {
  const { resumeId } = useParams<{ resumeId: string }>();
  const navigate = useNavigate();

  const [versions, setVersions] = useState<any[]>([]);
  const [loading, setLoading] = useState(false);
  const [total, setTotal] = useState(0);
  const [page, setPage] = useState(1);
  const [pageSize, setPageSize] = useState(10);
  const [detailModalVisible, setDetailModalVisible] = useState(false);
  const [selectedVersion, setSelectedVersion] = useState<any>(null);
  const [detailLoading, setDetailLoading] = useState(false);

  useEffect(() => {
    if (resumeId) {
      loadVersions();
    }
  }, [resumeId, page, pageSize]);

  const loadVersions = async () => {
    if (!resumeId) return;

    setLoading(true);
    try {
      const response = await getResumeVersions(parseInt(resumeId), page, pageSize);
      const data = response?.data || response;
      const versionList = data?.versions || data?.items || [];
      const totalCount = data?.total || 0;
      setVersions(Array.isArray(versionList) ? versionList : []);
      setTotal(totalCount);
    } catch (error: any) {
      console.error('加载版本列表失败:', error);
      setVersions([]);
      setTotal(0);
      message.error(error || '加载版本列表失败');
    } finally {
      setLoading(false);
    }
  };

  const handleViewDetail = async (versionId: number) => {
    try {
      setDetailModalVisible(true);
      setDetailLoading(true);
      const detail = await getVersionDetail(versionId);
      const data = detail?.data || detail;
      setSelectedVersion(data);
    } catch (error: any) {
      setDetailModalVisible(false);
      message.error(error || '加载版本详情失败');
    } finally {
      setDetailLoading(false);
    }
  };

  const handleDelete = async (versionId: number) => {
    try {
      await deleteVersion(versionId);
      message.success('版本删除成功！');
      loadVersions();
    } catch (error: any) {
      message.error(error || '删除失败');
    }
  };

  const columns: ColumnsType<any> = [
    {
      title: '版本名称',
      dataIndex: 'version_name',
      key: 'version_name',
      render: (text) => <strong>{text}</strong>,
    },
    {
      title: '版本ID',
      dataIndex: 'id',
      key: 'id',
      width: 100,
      render: (text) => <Tag color="blue">#{text}</Tag>,
    },
    {
      title: '创建时间',
      dataIndex: 'created_at',
      key: 'created_at',
      width: 180,
      render: (text) => formatDate(text),
      sorter: (a, b) => new Date(b.created_at).getTime() - new Date(a.created_at).getTime(),
    },
    {
      title: '操作',
      key: 'action',
      width: 160,
      render: (_, record) => (
        <Space>
          <Button
            type="link"
            icon={<EyeOutlined />}
            onClick={() => handleViewDetail(record.id)}
          >
            查看
          </Button>
          <Popconfirm
            title="确认删除此版本？"
            description="删除后无法恢复"
            onConfirm={() => handleDelete(record.id)}
            okText="确认"
            cancelText="取消"
          >
            <Button type="link" danger icon={<DeleteOutlined />}>删除</Button>
          </Popconfirm>
        </Space>
      ),
    },
  ];

  return (
    <div style={{ padding: '24px', maxWidth: '1200px', margin: '0 auto' }}>
      <Space direction="vertical" size="large" style={{ width: '100%' }}>
        <Card>
          <Space direction="vertical" style={{ width: '100%' }}>
            <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
              <div>
                <Title level={2}>
                  <HistoryOutlined /> 版本历史
                </Title>
                <div style={{ color: 'rgba(0, 0, 0, 0.45)' }}>
                  简历ID: {resumeId} | 共 {total} 个版本
                </div>
              </div>
              <Button
                icon={<ArrowLeftOutlined />}
                onClick={() => navigate(`/resume/${resumeId}/diagnosis`)}
              >
                返回诊断
              </Button>
            </div>
          </Space>
        </Card>

        <Card>
          {total === 0 && !loading ? (
            <Empty
              description="暂无版本记录，请在诊断页面点击「保存版本」按钮手动保存"
              style={{ padding: '40px 0' }}
            />
          ) : (
            <Table
              columns={columns}
              dataSource={versions}
              rowKey="id"
              loading={loading}
              pagination={{
                current: page,
                pageSize: pageSize,
                total: total,
                showSizeChanger: true,
                showTotal: (total) => `共 ${total} 个版本`,
                onChange: (page, pageSize) => {
                  setPage(page);
                  setPageSize(pageSize);
                },
              }}
            />
          )}
        </Card>
      </Space>

      {/* 版本详情 Modal */}
      <Modal
        title={
          selectedVersion ? (
            <Space>
              <FileTextOutlined />
              <span>{selectedVersion.version_name || '版本详情'}</span>
              <Tag color="blue">#{selectedVersion.id}</Tag>
            </Space>
          ) : '版本详情'
        }
        open={detailModalVisible}
        onCancel={() => {
          setDetailModalVisible(false);
          setSelectedVersion(null);
        }}
        footer={[
          <Button key="close" onClick={() => {
            setDetailModalVisible(false);
            setSelectedVersion(null);
          }}>
            关闭
          </Button>,
        ]}
        width={800}
        destroyOnClose
      >
        {detailLoading ? (
          <div style={{ textAlign: 'center', padding: '40px 0' }}>
            <Text type="secondary">加载中...</Text>
          </div>
        ) : selectedVersion ? (
          <Space direction="vertical" size="middle" style={{ width: '100%' }}>
            {/* 基本信息 */}
            <Descriptions column={2} size="small" bordered>
              <Descriptions.Item label="版本名称">{selectedVersion.version_name || '未命名'}</Descriptions.Item>
              <Descriptions.Item label="创建时间">
                {selectedVersion.created_at ? formatDate(selectedVersion.created_at) : '未知'}
              </Descriptions.Item>
            </Descriptions>

            {/* 评分区域 */}
            {selectedVersion.scores && (
              <>
                <Divider orientation="left"><TrophyOutlined /> 诊断评分</Divider>
                <ScoreSection scores={selectedVersion.scores} />
              </>
            )}

            {/* 简历内容摘要 */}
            {selectedVersion.parsed_data && (
              <>
                <Divider orientation="left"><UserOutlined /> 简历摘要</Divider>
                <ResumeSummary data={selectedVersion.parsed_data} />
              </>
            )}

            {/* 优化建议 */}
            {selectedVersion.optimization && (
              <>
                <Divider orientation="left"><BulbOutlined /> 优化建议</Divider>
                <OptimizationSection optimization={selectedVersion.optimization} />
              </>
            )}
          </Space>
        ) : null}
      </Modal>
    </div>
  );
};

export default ResumeVersions;
