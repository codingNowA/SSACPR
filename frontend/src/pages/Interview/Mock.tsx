/**
 * 模拟面试页面
 */
import React, { useState } from 'react';
import {
  Card,
  Input,
  Button,
  Space,
  Typography,
  Alert,
  Spin,
  Tag,
  Divider,
  Progress,
  message,
  Select,
} from 'antd';
import {
  SendOutlined,
  BulbOutlined,
  CheckCircleOutlined,
  CloseCircleOutlined,
  TrophyOutlined,
} from '@ant-design/icons';
import apiClient from '../../services/api';

const { Title, Text, Paragraph } = Typography;
const { TextArea } = Input;
const { Option } = Select;

// 预设问题
const PRESET_QUESTIONS = [
  '请做一个简单的自我介绍',
  '为什么选择我们公司？',
  '你的职业规划是什么？',
  '请介绍一下你最近的项目经验',
  '描述一次你解决技术难题的经历',
  '你如何处理团队合作中的冲突？',
  '你的优势和劣势是什么？',
  '你期望的薪资是多少？为什么？',
];

interface Feedback {
  score: number;
  overall_assessment: string;
  strengths: string[];
  weaknesses: string[];
  suggestions: string[];
  sample_answer?: string;
}

const MockInterview: React.FC = () => {
  const [question, setQuestion] = useState('');
  const [answer, setAnswer] = useState('');
  const [loading, setLoading] = useState(false);
  const [feedback, setFeedback] = useState<Feedback | null>(null);

  const handleSelectQuestion = (q: string) => {
    setQuestion(q);
    setFeedback(null);
  };

  const handleSubmit = async () => {
    if (!question.trim()) {
      message.warning('请输入或选择面试问题');
      return;
    }

    if (!answer.trim()) {
      message.warning('请输入你的答案');
      return;
    }

    setLoading(true);
    setFeedback(null);

    try {
      const response = await apiClient.post('/api/v1/interview-mock/evaluate', {
        question: question.trim(),
        answer: answer.trim(),
      });

      if (response.data?.code === 200 && response.data?.data?.feedback) {
        setFeedback(response.data.data.feedback);
        message.success('评估完成');
      } else {
        message.error('评估失败，请重试');
      }
    } catch (error: any) {
      message.error(error?.message || '评估失败');
    } finally {
      setLoading(false);
    }
  };

  const handleReset = () => {
    setQuestion('');
    setAnswer('');
    setFeedback(null);
  };

  const getScoreColor = (score: number) => {
    if (score >= 80) return '#52c41a';
    if (score >= 60) return '#1890ff';
    if (score >= 40) return '#faad14';
    return '#ff4d4f';
  };

  const getScoreStatus = (score: number) => {
    if (score >= 80) return '优秀';
    if (score >= 60) return '良好';
    if (score >= 40) return '一般';
    return '需改进';
  };

  return (
    <div style={{ padding: '24px' }}>
      <Card>
        <Space direction="vertical" size="large" style={{ width: '100%' }}>
          <div>
            <Title level={2}>模拟面试</Title>
            <Paragraph type="secondary">
              选择或输入面试问题，输入你的答案，AI将为你提供详细的反馈和改进建议。
            </Paragraph>
          </div>

          <Alert
            message="使用提示"
            description={
              <ul style={{ margin: 0, paddingLeft: 20 }}>
                <li>选择预设问题或输入自定义问题</li>
                <li>认真输入你的答案，尽量详细和完整</li>
                <li>AI会从完整性、逻辑性、专业性等维度评估你的答案</li>
                <li>根据反馈建议改进后，可以重复练习</li>
              </ul>
            }
            type="info"
            showIcon
          />

          {/* 问题选择 */}
          <Card title="1. 选择或输入面试问题" size="small" style={{ backgroundColor: '#fafafa' }}>
            <Space direction="vertical" size="middle" style={{ width: '100%' }}>
              <div>
                <Text strong>预设问题：</Text>
                <div style={{ marginTop: 8 }}>
                  <Select
                    placeholder="选择一个预设问题"
                    style={{ width: '100%' }}
                    onChange={handleSelectQuestion}
                    value={question || undefined}
                  >
                    {PRESET_QUESTIONS.map((q, idx) => (
                      <Option key={idx} value={q}>
                        {q}
                      </Option>
                    ))}
                  </Select>
                </div>
              </div>

              <div>
                <Text strong>或输入自定义问题：</Text>
                <Input
                  placeholder="例如：请介绍一下你在Python方面的项目经验"
                  value={question}
                  onChange={(e) => setQuestion(e.target.value)}
                  style={{ marginTop: 8 }}
                />
              </div>
            </Space>
          </Card>

          {/* 答案输入 */}
          <Card title="2. 输入你的答案" size="small" style={{ backgroundColor: '#fafafa' }}>
            <TextArea
              placeholder="请输入你的答案，尽量详细和完整。建议使用STAR法则（Situation情境、Task任务、Action行动、Result结果）来组织答案。"
              value={answer}
              onChange={(e) => setAnswer(e.target.value)}
              rows={8}
              maxLength={2000}
              showCount
            />
          </Card>

          {/* 提交按钮 */}
          <Space>
            <Button
              type="primary"
              icon={<SendOutlined />}
              onClick={handleSubmit}
              loading={loading}
              size="large"
            >
              提交评估
            </Button>
            <Button onClick={handleReset} size="large">
              重置
            </Button>
          </Space>

          {/* 评估结果 */}
          {loading && (
            <div style={{ textAlign: 'center', padding: '40px' }}>
              <Spin size="large" tip="AI正在评估中..." />
            </div>
          )}

          {feedback && !loading && (
            <Card title={<><TrophyOutlined /> 评估结果</>} style={{ marginTop: 16 }}>
              <Space direction="vertical" size="large" style={{ width: '100%' }}>
                {/* 评分 */}
                <div style={{ textAlign: 'center' }}>
                  <Progress
                    type="circle"
                    percent={feedback.score}
                    strokeColor={getScoreColor(feedback.score)}
                    format={(percent) => (
                      <div>
                        <div style={{ fontSize: 32, fontWeight: 'bold' }}>{percent}</div>
                        <div style={{ fontSize: 14, color: '#999' }}>
                          {getScoreStatus(percent || 0)}
                        </div>
                      </div>
                    )}
                    width={150}
                  />
                  <div style={{ marginTop: 16, fontSize: 16 }}>
                    {feedback.overall_assessment}
                  </div>
                </div>

                <Divider />

                {/* 优点 */}
                <div>
                  <Title level={4} style={{ color: '#52c41a' }}>
                    <CheckCircleOutlined /> 优点
                  </Title>
                  <ul style={{ marginLeft: 20 }}>
                    {feedback.strengths.map((item, idx) => (
                      <li key={idx}>
                        <Tag color="success" style={{ marginBottom: 8 }}>✓</Tag>
                        {item}
                      </li>
                    ))}
                  </ul>
                </div>

                {/* 不足 */}
                <div>
                  <Title level={4} style={{ color: '#ff4d4f' }}>
                    <CloseCircleOutlined /> 不足
                  </Title>
                  <ul style={{ marginLeft: 20 }}>
                    {feedback.weaknesses.map((item, idx) => (
                      <li key={idx}>
                        <Tag color="error" style={{ marginBottom: 8 }}>✗</Tag>
                        {item}
                      </li>
                    ))}
                  </ul>
                </div>

                {/* 改进建议 */}
                <div>
                  <Title level={4} style={{ color: '#1890ff' }}>
                    <BulbOutlined /> 改进建议
                  </Title>
                  <ul style={{ marginLeft: 20 }}>
                    {feedback.suggestions.map((item, idx) => (
                      <li key={idx}>
                        <Tag color="processing" style={{ marginBottom: 8 }}>💡</Tag>
                        {item}
                      </li>
                    ))}
                  </ul>
                </div>

                {/* 参考答案 */}
                {feedback.sample_answer && (
                  <div>
                    <Title level={4}>📝 参考答案</Title>
                    <Card size="small" style={{ backgroundColor: '#f0f5ff' }}>
                      <Paragraph>{feedback.sample_answer}</Paragraph>
                    </Card>
                  </div>
                )}

                {/* 继续练习 */}
                <Alert
                  message="提示"
                  description="根据上述反馈改进你的答案，然后可以继续提交评估，反复练习直到满意为止。"
                  type="success"
                  showIcon
                />
              </Space>
            </Card>
          )}
        </Space>
      </Card>
    </div>
  );
};

export default MockInterview;
