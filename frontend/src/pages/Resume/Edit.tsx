/**
 * 简历编辑页面
 */
import React, { useState, useEffect } from 'react';
import { useParams, useNavigate } from 'react-router-dom';
import {
  Card,
  Form,
  Input,
  Button,
  Space,
  Typography,
  message,
  Spin,
  Divider,
  Row,
  Col,
  Tag,
  Select,
  Modal,
} from 'antd';
import {
  SaveOutlined,
  ArrowLeftOutlined,
  EyeOutlined,
  PlusOutlined,
  DeleteOutlined,
} from '@ant-design/icons';
import apiClient from '../../services/api';
import { createResumeVersion } from '../../services/resume';

const { Title, Text } = Typography;
const { TextArea } = Input;
const { Option } = Select;

const ResumeEdit: React.FC = () => {
  const { resumeId } = useParams<{ resumeId: string }>();
  const navigate = useNavigate();
  const [form] = Form.useForm();

  const [loading, setLoading] = useState(false);
  const [saving, setSaving] = useState(false);
  const [saveModalVisible, setSaveModalVisible] = useState(false);
  const [versionName, setVersionName] = useState('');
  const [resumeData, setResumeData] = useState<any>(null);

  useEffect(() => {
    if (resumeId) {
      loadResumeData();
    }
  }, [resumeId]);

  const loadResumeData = async () => {
    setLoading(true);
    try {
      const response = await apiClient.get(`/api/v1/resume/${resumeId}/structured`);
      const data = response?.data || response;

      setResumeData(data);

      // 兼容两种数据格式：扁平化 (data.name) 和嵌套 (data.basic_info.name)
      const basicInfo = data.basic_info || {};

      // 处理技能：兼容字符串数组和 SkillTag 对象数组
      let skillsStr = '';
      if (data.skills && Array.isArray(data.skills)) {
        skillsStr = data.skills.map((s: any) => {
          if (typeof s === 'string') return s;
          if (s && s.name) return s.name;
          return '';
        }).filter(Boolean).join(', ');
      }

      // 填充表单
      form.setFieldsValue({
        name: data.name || basicInfo.name,
        phone: data.phone || basicInfo.phone,
        email: data.email || basicInfo.email,
        education: data.education || [],
        work_experience: data.work_experience || [],
        project_experience: data.project_experience || [],
        skills: skillsStr,
        self_evaluation: data.self_evaluation,
      });
    } catch (error: any) {
      message.error(error || '加载简历数据失败');
      navigate('/resume/list');
    } finally {
      setLoading(false);
    }
  };

  const handleSave = async () => {
    try {
      const values = await form.validateFields();

      // 转换技能为数组
      const skills = values.skills ? values.skills.split(/[,，、]/).map((s: string) => s.trim()).filter(Boolean) : [];

      // 转换技能为 SkillTag 格式（后端 Pydantic 模型要求）
      const skillTags = skills.map((skill: string) => ({
        name: skill,
        category: null,
        level: null,
      }));

      // 构造标准的 parsed_data 格式（嵌套结构）
      const structuredData = {
        basic_info: {
          name: values.name,
          phone: values.phone,
          email: values.email,
        },
        education: values.education || [],
        work_experience: values.work_experience || [],
        project_experience: values.project_experience || [],
        skills: skillTags,
        self_evaluation: values.self_evaluation,
      };

      // 更新简历数据
      await apiClient.put(`/api/v1/resume/${resumeId}/structured`, structuredData);

      // 更新本地 resumeData 以保持一致
      setResumeData(structuredData);

      // 保存成功后弹出版本命名弹窗
      setSaveModalVisible(true);
    } catch (error: any) {
      if (error?.errorFields) {
        message.warning('请检查必填项');
      } else {
        message.error(error || '保存失败');
      }
    }
  };

  const handleSaveVersion = async () => {
    if (!versionName.trim()) {
      message.warning('请输入版本名称');
      return;
    }

    setSaving(true);
    try {
      const values = form.getFieldsValue();
      const skills = values.skills ? values.skills.split(/[,，、]/).map((s: string) => s.trim()).filter(Boolean) : [];

      // 转换技能为 SkillTag 格式
      const skillTags = skills.map((skill: string) => ({
        name: skill,
        category: null,
        level: null,
      }));

      // 基于原始 resumeData 构造完整的 parsed_data，确保不丢失任何字段
      const parsedData = {
        basic_info: {
          ...(resumeData?.basic_info || {}),
          name: values.name,
          phone: values.phone,
          email: values.email,
        },
        education: values.education || [],
        work_experience: values.work_experience || [],
        project_experience: values.project_experience || [],
        skills: skillTags,
        self_evaluation: values.self_evaluation,
      };

      // 保存为新版本
      await createResumeVersion(
        parseInt(resumeId!),
        versionName,
        null, // scores 为空
        parsedData // 传递结构化的 parsed_data
      );

      message.success('版本保存成功！');
      setSaveModalVisible(false);
      setVersionName('');

      // 跳转到版本历史
      navigate(`/resume/versions/${resumeId}`);
    } catch (error: any) {
      message.error(error || '保存版本失败');
    } finally {
      setSaving(false);
    }
  };

  if (loading) {
    return (
      <div style={{ textAlign: 'center', padding: '100px 0' }}>
        <Spin size="large" tip="加载简历数据中..." />
      </div>
    );
  }

  return (
    <div style={{ padding: '24px', maxWidth: '1200px', margin: '0 auto' }}>
      <Card>
        <Space direction="vertical" size="large" style={{ width: '100%' }}>
          {/* 头部 */}
          <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
            <Space>
              <Button icon={<ArrowLeftOutlined />} onClick={() => navigate(-1)}>
                返回
              </Button>
              <Title level={2} style={{ margin: 0 }}>编辑简历</Title>
              <Tag color="blue">
                简历 #{resumeData?._user_resume_number || resumeId}
              </Tag>
            </Space>
            <Space>
              <Button
                icon={<EyeOutlined />}
                onClick={() => navigate(`/resume/diagnosis/${resumeId}`)}
              >
                查看诊断
              </Button>
              <Button type="primary" icon={<SaveOutlined />} onClick={handleSave}>
                保存并创建版本
              </Button>
            </Space>
          </div>

          <Divider />

          {/* 编辑表单 */}
          <Form form={form} layout="vertical">
            {/* 基本信息 */}
            <Card title="基本信息" size="small" style={{ marginBottom: 16 }}>
              <Row gutter={16}>
                <Col span={8}>
                  <Form.Item label="姓名" name="name" rules={[{ required: true, message: '请输入姓名' }]}>
                    <Input placeholder="请输入姓名" />
                  </Form.Item>
                </Col>
                <Col span={8}>
                  <Form.Item label="手机号" name="phone" rules={[{ required: true, message: '请输入手机号' }]}>
                    <Input placeholder="请输入手机号" />
                  </Form.Item>
                </Col>
                <Col span={8}>
                  <Form.Item
                    label="邮箱"
                    name="email"
                    rules={[
                      { required: true, message: '请输入邮箱' },
                      { pattern: /^[^\s@]+@[^\s@]+\.[^\s@]+$/, message: '邮箱格式不正确' }
                    ]}
                  >
                    <Input placeholder="请输入邮箱" />
                  </Form.Item>
                </Col>
              </Row>
            </Card>

            {/* 教育经历 */}
            <Card title="教育经历" size="small" style={{ marginBottom: 16 }}>
              <Form.List name="education">
                {(fields, { add, remove }) => (
                  <>
                    {fields.map((field, index) => (
                      <Card key={field.key} size="small" style={{ marginBottom: 16, background: '#fafafa' }}>
                        <Space direction="vertical" style={{ width: '100%' }}>
                          <div style={{ display: 'flex', justifyContent: 'space-between' }}>
                            <Text strong>教育经历 {index + 1}</Text>
                            <Button type="link" danger icon={<DeleteOutlined />} onClick={() => remove(field.name)}>
                              删除
                            </Button>
                          </div>
                          <Row gutter={16}>
                            <Col span={12}>
                              <Form.Item {...field} name={[field.name, 'school']} label="学校" rules={[{ required: true }]}>
                                <Input placeholder="学校名称" />
                              </Form.Item>
                            </Col>
                            <Col span={12}>
                              <Form.Item {...field} name={[field.name, 'major']} label="专业" rules={[{ required: true }]}>
                                <Input placeholder="专业名称" />
                              </Form.Item>
                            </Col>
                          </Row>
                          <Row gutter={16}>
                            <Col span={8}>
                              <Form.Item {...field} name={[field.name, 'degree']} label="学历">
                                <Select placeholder="选择学历">
                                  <Option value="高中">高中</Option>
                                  <Option value="大专">大专</Option>
                                  <Option value="本科">本科</Option>
                                  <Option value="硕士">硕士</Option>
                                  <Option value="博士">博士</Option>
                                </Select>
                              </Form.Item>
                            </Col>
                            <Col span={8}>
                              <Form.Item {...field} name={[field.name, 'start_date']} label="开始时间">
                                <Input placeholder="2019-09" />
                              </Form.Item>
                            </Col>
                            <Col span={8}>
                              <Form.Item {...field} name={[field.name, 'end_date']} label="结束时间">
                                <Input placeholder="2023-06" />
                              </Form.Item>
                            </Col>
                          </Row>
                        </Space>
                      </Card>
                    ))}
                    <Button type="dashed" onClick={() => add()} block icon={<PlusOutlined />}>
                      添加教育经历
                    </Button>
                  </>
                )}
              </Form.List>
            </Card>

            {/* 工作经历 */}
            <Card title="工作经历" size="small" style={{ marginBottom: 16 }}>
              <Form.List name="work_experience">
                {(fields, { add, remove }) => (
                  <>
                    {fields.map((field, index) => (
                      <Card key={field.key} size="small" style={{ marginBottom: 16, background: '#fafafa' }}>
                        <Space direction="vertical" style={{ width: '100%' }}>
                          <div style={{ display: 'flex', justifyContent: 'space-between' }}>
                            <Text strong>工作经历 {index + 1}</Text>
                            <Button type="link" danger icon={<DeleteOutlined />} onClick={() => remove(field.name)}>
                              删除
                            </Button>
                          </div>
                          <Row gutter={16}>
                            <Col span={12}>
                              <Form.Item {...field} name={[field.name, 'company']} label="公司" rules={[{ required: true }]}>
                                <Input placeholder="公司名称" />
                              </Form.Item>
                            </Col>
                            <Col span={12}>
                              <Form.Item {...field} name={[field.name, 'position']} label="职位" rules={[{ required: true }]}>
                                <Input placeholder="职位名称" />
                              </Form.Item>
                            </Col>
                          </Row>
                          <Row gutter={16}>
                            <Col span={12}>
                              <Form.Item {...field} name={[field.name, 'start_date']} label="开始时间">
                                <Input placeholder="2020-07" />
                              </Form.Item>
                            </Col>
                            <Col span={12}>
                              <Form.Item {...field} name={[field.name, 'end_date']} label="结束时间">
                                <Input placeholder="2023-12 或 至今" />
                              </Form.Item>
                            </Col>
                          </Row>
                          <Form.Item {...field} name={[field.name, 'description']} label="工作描述">
                            <TextArea rows={4} placeholder="描述你的工作内容和成就..." />
                          </Form.Item>
                        </Space>
                      </Card>
                    ))}
                    <Button type="dashed" onClick={() => add()} block icon={<PlusOutlined />}>
                      添加工作经历
                    </Button>
                  </>
                )}
              </Form.List>
            </Card>

            {/* 项目经验 */}
            <Card title="项目经验" size="small" style={{ marginBottom: 16 }}>
              <Form.List name="project_experience">
                {(fields, { add, remove }) => (
                  <>
                    {fields.map((field, index) => (
                      <Card key={field.key} size="small" style={{ marginBottom: 16, background: '#fafafa' }}>
                        <Space direction="vertical" style={{ width: '100%' }}>
                          <div style={{ display: 'flex', justifyContent: 'space-between' }}>
                            <Text strong>项目经验 {index + 1}</Text>
                            <Button type="link" danger icon={<DeleteOutlined />} onClick={() => remove(field.name)}>
                              删除
                            </Button>
                          </div>
                          <Row gutter={16}>
                            <Col span={12}>
                              <Form.Item {...field} name={[field.name, 'name']} label="项目名称" rules={[{ required: true }]}>
                                <Input placeholder="项目名称" />
                              </Form.Item>
                            </Col>
                            <Col span={12}>
                              <Form.Item {...field} name={[field.name, 'role']} label="担任角色">
                                <Input placeholder="项目角色" />
                              </Form.Item>
                            </Col>
                          </Row>
                          <Row gutter={16}>
                            <Col span={12}>
                              <Form.Item {...field} name={[field.name, 'start_date']} label="开始时间">
                                <Input placeholder="2022-01" />
                              </Form.Item>
                            </Col>
                            <Col span={12}>
                              <Form.Item {...field} name={[field.name, 'end_date']} label="结束时间">
                                <Input placeholder="2022-06" />
                              </Form.Item>
                            </Col>
                          </Row>
                          <Form.Item {...field} name={[field.name, 'description']} label="项目描述">
                            <TextArea rows={4} placeholder="描述项目背景、你的职责和成果..." />
                          </Form.Item>
                        </Space>
                      </Card>
                    ))}
                    <Button type="dashed" onClick={() => add()} block icon={<PlusOutlined />}>
                      添加项目经验
                    </Button>
                  </>
                )}
              </Form.List>
            </Card>

            {/* 技能特长 */}
            <Card title="技能特长" size="small" style={{ marginBottom: 16 }}>
              <Form.Item
                label="技能列表"
                name="skills"
                extra="多个技能用逗号分隔，如：Java, Python, React"
              >
                <TextArea rows={3} placeholder="请输入技能，用逗号分隔" />
              </Form.Item>
            </Card>

            {/* 自我评价 */}
            <Card title="自我评价" size="small">
              <Form.Item label="自我评价" name="self_evaluation">
                <TextArea rows={6} placeholder="简要介绍你的优势、特点和职业目标..." />
              </Form.Item>
            </Card>
          </Form>
        </Space>
      </Card>

      {/* 保存版本弹窗 */}
      <Modal
        title="保存为新版本"
        open={saveModalVisible}
        onOk={handleSaveVersion}
        onCancel={() => setSaveModalVisible(false)}
        confirmLoading={saving}
        okText="确定"
        cancelText="取消"
      >
        <Space direction="vertical" style={{ width: '100%' }}>
          <Text>请为这个版本命名：</Text>
          <Input
            placeholder="例如：根据优化建议修改-v1"
            value={versionName}
            onChange={(e) => setVersionName(e.target.value)}
          />
        </Space>
      </Modal>
    </div>
  );
};

export default ResumeEdit;
