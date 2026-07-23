/**
 * 简历上传页面
 */
import React, { useState } from 'react';
import { useNavigate } from 'react-router-dom';
import {
  Upload,
  Button,
  Card,
  Typography,
  Space,
  message,
  Steps,
  Alert,
} from 'antd';
import { InboxOutlined, FileTextOutlined, CheckCircleOutlined } from '@ant-design/icons';
import type { UploadFile } from 'antd/es/upload/interface';
import { uploadResume, parseResume, diagnoseResume } from '../../services/resume';
import { useAppStore } from '../../store';
import { isValidResumeFile, formatFileSize } from '../../utils';

const { Title, Paragraph, Text } = Typography;
const { Dragger } = Upload;

const ResumeUpload: React.FC = () => {
  const navigate = useNavigate();
  const { user, setCurrentResumeId, setResumeData, setDiagnosisResult } = useAppStore();
  const userId = user?.userId;

  const [fileList, setFileList] = useState<UploadFile[]>([]);
  const [uploading, setUploading] = useState(false);
  const [currentStep, setCurrentStep] = useState(0);

  const handleUpload = async () => {
    console.log('开始上传，fileList:', fileList);

    if (fileList.length === 0) {
      message.warning('请先选择文件');
      return;
    }

    console.log('fileList[0]:', fileList[0]);
    const file = fileList[0].originFileObj;
    console.log('originFileObj:', file);

    if (!file) {
      console.error('文件读取失败: originFileObj 为空');
      message.error('文件读取失败，请重新选择');
      return;
    }

    console.log('文件信息:', { name: file.name, type: file.type, size: file.size });

    if (!isValidResumeFile(file)) {
      console.error('文件类型不支持:', file.type);
      message.error('不支持的文件格式，请上传 PDF、Word 或图片文件');
      return;
    }

    console.log('文件验证通过，开始上传');

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

      const resumeId = uploadResult.resume_id;

      // 检查是否成功获取 resume_id
      if (!resumeId) {
        message.error({
          content: '简历上传成功，但自动解析失败。请稍后重试或联系管理员。',
          duration: 5,
        });
        setCurrentStep(0);
        setUploading(false);
        return;
      }

      setCurrentResumeId(resumeId);

      // 步骤 2: 解析简历
      message.loading({ content: '正在解析简历内容...', key: 'parse', duration: 0 });
      const resumeData = await parseResume(resumeId);
      setResumeData(resumeData);
      message.success({ content: '解析完成！', key: 'parse' });
      setCurrentStep(2);

      // 步骤 3: 智能诊断
      message.loading({ content: '正在进行智能诊断...', key: 'diagnose', duration: 0 });
      const diagnosisResult = await diagnoseResume(resumeId);
      setDiagnosisResult(diagnosisResult);
      message.success({ content: '诊断完成！', key: 'diagnose' });
      setCurrentStep(3);

      // 跳转到诊断结果页面
      setTimeout(() => {
        navigate(`/resume/diagnosis/${resumeId}`);
      }, 1000);

    } catch (error: any) {
      message.error(error || '处理失败，请重试');
      setCurrentStep(0);
    } finally {
      setUploading(false);
    }
  };

  const steps = [
    { title: '上传文件', icon: <InboxOutlined /> },
    { title: '解析内容', icon: <FileTextOutlined /> },
    { title: '智能诊断', icon: <CheckCircleOutlined /> },
  ];

  return (
    <div style={{ padding: '24px', maxWidth: '900px', margin: '0 auto' }}>
      <Card>
        <Space direction="vertical" size="large" style={{ width: '100%' }}>
          <div style={{ textAlign: 'center' }}>
            <Title level={2}>简历智能诊断</Title>
            <Paragraph type="secondary">
              上传您的简历，我们将为您提供专业的诊断与优化建议
            </Paragraph>
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

          {fileList.length > 0 && (
            <Card size="small">
              <Space direction="vertical" style={{ width: '100%' }}>
                <Text strong>已选择文件:</Text>
                <Text>{fileList[0].name}</Text>
                <Text type="secondary">
                  大小: {formatFileSize(fileList[0].size || fileList[0].originFileObj?.size || 0)}
                </Text>
              </Space>
            </Card>
          )}

          <Button
            type="primary"
            size="large"
            block
            onClick={handleUpload}
            loading={uploading}
            disabled={fileList.length === 0}
          >
            {uploading ? '处理中...' : '开始分析'}
          </Button>

          <div style={{ textAlign: 'center' }}>
            <Space direction="vertical" size="small">
              <Text type="secondary">分析内容包括：</Text>
              <Text type="secondary">✓ 完整性评分 ✓ 专业性评分 ✓ 量化程度</Text>
              <Text type="secondary">✓ 项目深度 ✓ 岗位匹配度 ✓ 优化建议</Text>
            </Space>
          </div>
        </Space>
      </Card>
    </div>
  );
};

export default ResumeUpload;
