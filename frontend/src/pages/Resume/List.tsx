/**
 * 我的简历列表页面
 */
import React, { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import {
  Card,
  Table,
  Button,
  Space,
  Typography,
  Tag,
  message,
  Popconfirm,
  Empty,
  Tooltip,
  Row,
  Col,
} from 'antd';
import {
  FileTextOutlined,
  EyeOutlined,
  DeleteOutlined,
  HistoryOutlined,
  StarOutlined,
  StarFilled,
  PlusOutlined,
} from '@ant-design/icons';
import apiClient from '../../services/api';
import { useStore } from '../../store';
import { formatDate } from '../../utils';
import type { ColumnsType } from 'antd/es/table';

const { Title, Text } = Typography;

interface Resume {
  id: number;
  file_path: string;
  file_type: string;
  version: number;
  status: string;
  created_at: string;
  updated_at: string;
}

const ResumeList: React.FC = () => {
  const navigate = useNavigate();
  const { currentResumeId, setCurrentResumeId } = useStore();
  const [resumes, setResumes] = useState<Resume[]>([]);
  const [loading, setLoading] = useState(false);
  const [total, setTotal] = useState(0);
  const [page, setPage] = useState(1);
  const [pageSize, setPageSize] = useState(10);

  useEffect(() => {
    loadResumes();
  }, [page, pageSize]);

  const loadResumes = async () => {
    setLoading(true);
    try {
      const response = await apiClient.get('/api/v1/resume/list', {
        params: { page, page_size: pageSize },
      });

      if (response && typeof response === 'object') {
        const items = response.items || [];

        // 串行加载以避免数据库连接池耗尽
        const resumesWithData = [];
        for (const resume of items) {
          try {
            const detailData = await apiClient.get(`/api/v1/resume/${resume.id}/structured`);
            resumesWithData.push({ ...resume, parsed_data: detailData });
          } catch (error) {
            resumesWithData.push({ ...resume, parsed_data: null });
          }
        }

        setResumes(resumesWithData);
        setTotal(response.total || 0);
      }
    } catch (error: any) {
      message.error(error || '加载简历列表失败');
    } finally {
      setLoading(false);
    }
  };

  const handleSetCurrent = (resumeId: number) => {
    setCurrentResumeId(resumeId);
    message.success('已设置为当前简历');
  };

  const handleDelete = async (resumeId: number) => {
    try {
      await apiClient.delete(`/api/v1/resume/${resumeId}`);
      message.success('删除成功');
      if (currentResumeId === resumeId) {
        setCurrentResumeId(null);
      }
      loadResumes();
    } catch (error: any) {
      message.error(error || '删除失败');
    }
  };

  const getFileName = (filePath: string) => {
    return filePath.split('/').pop() || filePath;
  };

  return (
    <div style={{ padding: '24px', maxWidth: '1400px', margin: '0 auto' }}>
      <Space direction="vertical" size="large" style={{ width: '100%' }}>
        {/* 头部 */}
        <Card>
          <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
            <div>
              <Title level={2}>
                <FileTextOutlined /> 我的简历
              </Title>
              <Text type="secondary">
                管理你的所有简历，查看详细内容和版本历史
                {currentResumeId && (
                  <Tag color="gold" style={{ marginLeft: 8 }}>
                    <StarFilled /> 当前简历 ID: {currentResumeId}
                  </Tag>
                )}
              </Text>
            </div>
            <Button
              type="primary"
              icon={<PlusOutlined />}
              onClick={() => navigate('/resume/upload')}
            >
              上传新简历
            </Button>
          </div>
        </Card>

        {/* 简历列表（卡片式） */}
        {loading ? (
          <Card>
            <div style={{ textAlign: 'center', padding: '40px 0' }}>
              <Text type="secondary">加载中...</Text>
            </div>
          </Card>
        ) : resumes.length === 0 ? (
          <Card>
            <Empty
              description="还没有上传简历"
              image={Empty.PRESENTED_IMAGE_SIMPLE}
            >
              <Button type="primary" onClick={() => navigate('/resume/upload')}>
                立即上传
              </Button>
            </Empty>
          </Card>
        ) : (
          <>
            {resumes.map((resume: any) => {
              const parsedData = resume.parsed_data || {};
              const basicInfo = parsedData.basic_info || {};
              const skills = parsedData.skills || [];
              const education = parsedData.education || [];
              const workExperience = parsedData.work_experience || [];
              const projectExperience = parsedData.project_experience || [];

              return (
                <Card
                  key={resume.id}
                  title={
                    <Space>
                      {resume.id === currentResumeId && (
                        <StarFilled style={{ color: '#faad14' }} />
                      )}
                      <FileTextOutlined />
                      <Text strong>{getFileName(resume.file_path)}</Text>
                      <Tag color={resume.status === 'active' ? 'success' : 'default'}>
                        {resume.status === 'active' ? '活跃' : resume.status}
                      </Tag>
                      <Tag>{resume.file_type?.toUpperCase()}</Tag>
                    </Space>
                  }
                  extra={
                    <Space>
                      {resume.id !== currentResumeId && (
                        <Tooltip title="设置为当前简历">
                          <Button
                            type="link"
                            size="small"
                            icon={<StarOutlined />}
                            onClick={() => handleSetCurrent(resume.id)}
                          >
                            设为当前
                          </Button>
                        </Tooltip>
                      )}
                      <Button
                        type="link"
                        size="small"
                        icon={<EyeOutlined />}
                        onClick={() => navigate(`/resume/diagnosis/${resume.id}`)}
                      >
                        查看诊断
                      </Button>
                      <Button
                        type="link"
                        size="small"
                        icon={<HistoryOutlined />}
                        onClick={() => navigate(`/resume/versions/${resume.id}`)}
                      >
                        版本历史
                      </Button>
                      <Popconfirm
                        title="确定删除这份简历吗？"
                        description="删除后将无法恢复，包括所有版本记录"
                        onConfirm={() => handleDelete(resume.id)}
                        okText="确定"
                        cancelText="取消"
                      >
                        <Button type="link" size="small" danger icon={<DeleteOutlined />}>
                          删除
                        </Button>
                      </Popconfirm>
                    </Space>
                  }
                >
                  <Space direction="vertical" size="middle" style={{ width: '100%' }}>
                    {/* 基本信息 */}
                    {basicInfo.name && (
                      <div>
                        <Text strong style={{ fontSize: 16 }}>📋 基本信息</Text>
                        <div style={{ marginTop: 8, marginLeft: 16 }}>
                          <Row gutter={[16, 8]}>
                            {basicInfo.name && <Col span={8}><Text>姓名：{basicInfo.name}</Text></Col>}
                            {basicInfo.phone && <Col span={8}><Text>电话：{basicInfo.phone}</Text></Col>}
                            {basicInfo.email && <Col span={8}><Text>邮箱：{basicInfo.email}</Text></Col>}
                            {basicInfo.job_intention && <Col span={8}><Text>求职意向：{basicInfo.job_intention}</Text></Col>}
                            {basicInfo.current_location && <Col span={8}><Text>所在地：{basicInfo.current_location}</Text></Col>}
                            {basicInfo.years_of_experience && <Col span={8}><Text>工作年限：{basicInfo.years_of_experience}</Text></Col>}
                          </Row>
                        </div>
                      </div>
                    )}

                    {/* 技能 */}
                    {skills.length > 0 && (
                      <div>
                        <Text strong style={{ fontSize: 16 }}>🛠 技能</Text>
                        <div style={{ marginTop: 8, marginLeft: 16 }}>
                          <Space wrap>
                            {skills.map((skill: any, idx: number) => (
                              <Tag key={idx} color="blue">
                                {typeof skill === 'string' ? skill : skill.name}
                              </Tag>
                            ))}
                          </Space>
                        </div>
                      </div>
                    )}

                    {/* 教育经历 */}
                    {education.length > 0 && (
                      <div>
                        <Text strong style={{ fontSize: 16 }}>🎓 教育经历</Text>
                        <div style={{ marginTop: 8, marginLeft: 16 }}>
                          {education.map((edu: any, idx: number) => (
                            <div key={idx} style={{ marginBottom: 8 }}>
                              <Text strong>{edu.school}</Text>
                              {edu.major && <Text type="secondary"> · {edu.major}</Text>}
                              {edu.degree && <Tag style={{ marginLeft: 8 }}>{edu.degree}</Tag>}
                              {edu.start_date && (
                                <Text type="secondary" style={{ marginLeft: 8 }}>
                                  ({edu.start_date} ~ {edu.end_date || '至今'})
                                </Text>
                              )}
                            </div>
                          ))}
                        </div>
                      </div>
                    )}

                    {/* 工作经历 */}
                    {workExperience.length > 0 && (
                      <div>
                        <Text strong style={{ fontSize: 16 }}>🏢 工作经历</Text>
                        <div style={{ marginTop: 8, marginLeft: 16 }}>
                          {workExperience.map((work: any, idx: number) => (
                            <div key={idx} style={{ marginBottom: 12 }}>
                              <div>
                                <Text strong>{work.company}</Text>
                                {work.position && <Text type="secondary"> · {work.position}</Text>}
                                {work.start_date && (
                                  <Text type="secondary" style={{ marginLeft: 8 }}>
                                    ({work.start_date} ~ {work.end_date || '至今'})
                                  </Text>
                                )}
                              </div>
                              {work.description && (
                                <Text type="secondary" style={{ display: 'block', marginTop: 4 }}>
                                  {work.description}
                                </Text>
                              )}
                            </div>
                          ))}
                        </div>
                      </div>
                    )}

                    {/* 项目经历 */}
                    {projectExperience.length > 0 && (
                      <div>
                        <Text strong style={{ fontSize: 16 }}>📦 项目经历</Text>
                        <div style={{ marginTop: 8, marginLeft: 16 }}>
                          {projectExperience.map((project: any, idx: number) => (
                            <div key={idx} style={{ marginBottom: 12 }}>
                              <div>
                                <Text strong>{project.name}</Text>
                                {project.role && <Text type="secondary"> · {project.role}</Text>}
                                {project.start_date && (
                                  <Text type="secondary" style={{ marginLeft: 8 }}>
                                    ({project.start_date} ~ {project.end_date || '至今'})
                                  </Text>
                                )}
                              </div>
                              {project.description && (
                                <Text type="secondary" style={{ display: 'block', marginTop: 4 }}>
                                  {project.description}
                                </Text>
                              )}
                            </div>
                          ))}
                        </div>
                      </div>
                    )}

                    {/* 底部信息 */}
                    <div style={{ borderTop: '1px solid #f0f0f0', paddingTop: 12, marginTop: 8 }}>
                      <Space split={<span style={{ color: '#d9d9d9' }}>|</span>}>
                        <Text type="secondary">简历ID: {resume.id}</Text>
                        <Text type="secondary">版本数: {resume.version}</Text>
                        <Text type="secondary">上传时间: {formatDate(resume.created_at)}</Text>
                      </Space>
                    </div>
                  </Space>
                </Card>
              );
            })}

            {/* 分页 */}
            {total > pageSize && (
              <Card>
                <div style={{ textAlign: 'center' }}>
                  <Space>
                    <Button
                      disabled={page === 1}
                      onClick={() => setPage(page - 1)}
                    >
                      上一页
                    </Button>
                    <Text>第 {page} 页 / 共 {Math.ceil(total / pageSize)} 页</Text>
                    <Button
                      disabled={page >= Math.ceil(total / pageSize)}
                      onClick={() => setPage(page + 1)}
                    >
                      下一页
                    </Button>
                  </Space>
                </div>
              </Card>
            )}
          </>
        )}
      </Space>
    </div>
  );
};

export default ResumeList;
