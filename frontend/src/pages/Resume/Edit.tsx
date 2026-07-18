/**
 * 简历编辑/重新上传页面
 */
import React, { useState, useEffect } from 'react';
import { useParams, useNavigate } from 'react-router-dom';
import {
  Card,
  Upload,
  Button,
  Form,
  Input,
  Space,
  Typography,
  message,
  Spin,
  Alert,
  Steps,
} from 'antd';
import {
  UploadOutlined,
  ArrowLeftOutlined,
  SaveOutlined,
  InboxOutlined,
} from '@ant-design/icons';
import type { UploadFile } from 'antd/es/upload/interface';
import { uploadResume, parseResume, diagnoseResume } from '../../services/resume';
import { useAppStore } from '../../store';
import { isValidResumeFile, formatFileSize } from '../../utils';

const { Title, Text, Paragraph } = Typography;
const { Dragger } = Upload;
const { TextArea } = Input;

const ResumeEdit: React.FC = () => {
  const { resumeId } = useParams<{ resumeId: string }>();
  const navigate = useNavigate();
  const { userId, setCurrentResumeId, setResumeData, setDiagnosisResult } = useAppStore();

  const [form] = Form.useForm();
  const [fileList, setFileList] = useState<UploadFile[]>([]);
  const [uploading, setUploading] = useState(false);
  const [currentStep, setCurrentStep] = useState(0);
  const [loading, setLoading] = useState(false);

  const handleReupload = async () => {
    if (fileList.length === 0) {
      message.warning('请先选择文件');
      return;
    }

    const file = fileList[0].originFileObj;
    if (!file) {
      message.error('文件读取失败，请重新选择');
      return;
    }

    if (!isValidResumeFile(file)) {
      message.error('不支持的文件格式，请上传 PDF、Word 或图片文件');
      return;
    }

    setUploading(true);
    setCurrentStep(0);

    try {
      // 步骤 1: 上传文件
      message.loading({ content: '正在上传简历...', key: 'upload', duration: 0 });
      if (!userId) {
        message.error('请先登录');
        setUploading(false);
        return;
      }

      const uploadResult = await uploadResume(file, userId);
      message.success({ content: '上传成功！', key: 'upload' });
      setCurrentStep(1);

      const newResumeId = uploadResult.resume_id;

      if (!newResumeId) {
        message.error('简历上传成功，但自动解析失败。请稍后重试或联系管理员。');
        setCurrentStep(0);
        setUploading(false);
        return;
      }

      setCurrentResumeId(newResumeId);

      // 步骤 2: 解析简历
      message.loading({ content: '正在解析简历内容...', key: 'parse', duration: 0 });
      const resumeData = await parseResume(newResumeId);
      setResumeData(resumeData);
      message.success({ content: '解析完成！', key: 'parse' });
      setCurrentStep(2);

      // 步骤 3: 智能诊断
      message.loading({ content: '正在进行智能诊断...', key: 'diagnose', duration: 0 });
      const diagnosisResult = await diagnoseResume(newResumeId);
      setDiagnosisResult(diagnosisResult);
      message.success({ content: '诊断完成！', key: 'diagnose' });
      setCurrentStep(3);

      // 跳转到诊断结果页面
      setTimeout(() => {
        navigate(`/resume/${newResumeId}/diagnosis`);
      }, 1000);

    } catch (error: any) {
      message.error(error || '处理失败，请重试');
      setCurrentStep(0);
    } finally {
      setUploading(false);
    }
  };

  const steps = [
    { title: '上传文件', icon: <UploadOutlined /> },
    { title: '解析内容', icon: <SaveOutlined /> },
    { title: '智能诊断', icon: <SaveOutlined /> },
  ];

  return (
    <div style={{ padding: '24px', maxWidth: '900px', margin: '0 auto' }}>
      <Card>
        <Space direction="vertical" size="large" style={{ width: '100%' }}>
          <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
            <div>
              <Title level={2}>编辑简历</Title>
              <Paragraph type="secondary">
                重新上传简历文件，系统将自动保存为新版本
              </Paragraph>
            </div>
            <Button
              icon={<ArrowLeftOutlined />}
              onClick={() => navigate(`/resume/${resumeId}/versions`)}
            >
              返回版本列表
            </Button>
          </div>

          {uploading && (
            <Steps current={currentStep} items={steps} />
          )}

          <Alert
            message="支持的文件格式"
            description="PDF、Word (doc/docx)、图片 (png/jpg/jpeg)"
            type="info"
            showIcon
          />

          <Form form={form} layout="vertical">
            <Form.Item
              label="上传新简历"
              name="file"
              rules={[{ required: true, message: '请上传简历文件' }]}
            >
              <Dragger
                name="file"
                multiple={false}
                fileList={fileList}
                beforeUpload={(file) => {
                  setFileList([{
                    uid: '-1',
                    name: file.name,
                    status: 'done',
                    size: file.size,
                    originFileObj: file,
                  } as any]);
                  return false;
                }}
                onRemove={() => {
                  setFileList([]);
                }}
                disabled={uploading}
                maxCount={1}
              >
                <p className="ant-upload-drag-icon">
                  <InboxOutlined style={{ fontSize: '48px', color: '#1890ff' }} />
                </p>
                <p className="ant-upload-text">点击或拖拽文件到此区域上传</p>
                <p className="ant-upload-hint">
                  支持单个文件上传，文件大小不超过 10MB
                </p>
              </Dragger>
            </Form.Item>

            {fileList.length > 0 && (
              <Card size="small" style={{ marginBottom: 16 }}>
                <Space direction="vertical" style={{ width: '100%' }}>
                  <Text strong>已选择文件:</Text>
                  <Text>{fileList[0].name}</Text>
                  <Text type="secondary">
                    大小: {formatFileSize(fileList[0].size || fileList[0].originFileObj?.size || 0)}
                  </Text>
                </Space>
              </Card>
            )}

            <Form.Item>
              <Space>
                <Button
                  type="primary"
                  icon={<SaveOutlined />}
                  onClick={handleReupload}
                  loading={uploading}
                  disabled={fileList.length === 0}
                  size="large"
                >
                  {uploading ? '处理中...' : '上传并保存为新版本'}
                </Button>
                <Button
                  onClick={() => navigate(`/resume/${resumeId}/versions`)}
                  disabled={uploading}
                  size="large"
                >
                  取消
                </Button>
              </Space>
            </Form.Item>
          </Form>

          <div style={{ textAlign: 'center' }}>
            <Space direction="vertical" size="small">
              <Text type="secondary">上传后将自动：</Text>
              <Text type="secondary">✓ 解析简历内容 ✓ 智能诊断 ✓ 保存新版本</Text>
            </Space>
          </div>
        </Space>
      </Card>
    </div>
  );
};

export default ResumeEdit;
