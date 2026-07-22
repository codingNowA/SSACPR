/**
 * 题库刷题页面
 */
import React, { useState, useEffect } from 'react';
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
  ReloadOutlined,
} from '@ant-design/icons';
import apiClient from '../../services/api';
import axios from 'axios';

const { Title, Text, Paragraph } = Typography;
const { TextArea } = Input;
const { Option } = Select;

interface Question {
  id: number;
  category: string;
  difficulty: string;
  question?: string;
  question_text?: string;
  answer_points?: string;
}

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
  const [customQuestion, setCustomQuestion] = useState('');
  const [answer, setAnswer] = useState('');
  const [loading, setLoading] = useState(false);
  const [feedback, setFeedback] = useState<Feedback | null>(null);
  const [questions, setQuestions] = useState<Question[]>([]);
  const [loadingQuestions, setLoadingQuestions] = useState(false);
  const [selectedCategory, setSelectedCategory] = useState<string>('');
  const [showQuestionList, setShowQuestionList] = useState(true); // 控制是否显示题库列表

  // 加载题库
  useEffect(() => {
    loadQuestions();
  }, []);

  const loadQuestions = async () => {
    setLoadingQuestions(true);
    try {
      const response = await axios.get('/api/v1/interview-exam/questions', {
        params: { count: 100 },
      });
      const rawData = response.data?.data || [];

      // 映射字段名，与 Exam.tsx 保持一致
      const mappedData = rawData.map((q: any) => ({
        id: q.id,
        category: q.category,
        difficulty: q.difficulty,
        question: q.question_text || q.question || '', // 关键：统一使用 question 字段
        answer_points: q.answer_points,
        related_skills: q.related_skills,
      }));

      setQuestions(mappedData);
    } catch (error) {
      message.error('加载题库失败');
      console.error('加载题库失败:', error);
    } finally {
      setLoadingQuestions(false);
    }
  };

  // 筛选题目
  const filteredQuestions = questions.filter((q) => {
    if (selectedCategory && q.category !== selectedCategory) return false;
    return true;
  });

  // 获取所有分类
  const categories = Array.from(new Set(questions.map((q) => q.category)));

  const handleSelectQuestion = (q: string | undefined) => {
    if (q) {
      setQuestion(q);
      setCustomQuestion(''); // 清空自定义输入
    }
  };

  const handleReset = () => {
    setQuestion('');
    setCustomQuestion('');
    setAnswer('');
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

      // API 客户端的响应拦截器已经解包了 {code, data}，response 直接是 data 部分
      const data = response as any;
      if (data?.feedback) {
        setFeedback(data.feedback);
        message.success('评估完成');
      } else {
        message.error('评估失败，请重试');
      }
    } catch (error: any) {
      message.error(error?.message || error || '评估失败');
    } finally {
      setLoading(false);
    }
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
    <div>
      <Space direction="vertical" size="large" style={{ width: '100%' }}>
        <div>
          <Title level={2}>题库刷题</Title>
          <Paragraph type="secondary">
            从题库中选择面试问题进行练习，AI将为你提供详细的反馈和改进建议。
          </Paragraph>
        </div>

        <Alert
          message="使用提示"
          description={
            <ul style={{ margin: 0, paddingLeft: 20 }}>
              <li>从题库中选择面试问题进行练习</li>
              <li>可以按分类和难度筛选题目</li>
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
            {showQuestionList ? (
              <>
                {/* 筛选器 */}
                <Space wrap>
                  <Text strong>筛选条件：</Text>
                  <Select
                    placeholder="选择分类"
                    allowClear
                    style={{ width: 150 }}
                    value={selectedCategory || undefined}
                    onChange={setSelectedCategory}
                    loading={loadingQuestions}
                  >
                    {categories.map((cat) => (
                      <Option key={cat} value={cat}>
                        {cat}
                      </Option>
                    ))}
                  </Select>
                  <Button icon={<ReloadOutlined />} onClick={loadQuestions} loading={loadingQuestions}>
                    刷新题库
                  </Button>
                  <Text type="secondary">
                    共 {filteredQuestions.length} 道题目
                  </Text>
                </Space>

                <div>
                  <Text strong>从题库选择：</Text>
                  <div style={{ marginTop: 8, maxHeight: '400px', overflowY: 'auto' }}>
                    {loadingQuestions ? (
                      <Spin />
                    ) : filteredQuestions.length === 0 ? (
                      <Text type="secondary">暂无题目</Text>
                    ) : (
                      filteredQuestions.map((q) => (
                        <div
                          key={q.id}
                          onClick={() => {
                            if (q.question) {
                              setQuestion(q.question);
                              setCustomQuestion('');
                              setShowQuestionList(false); // 隐藏题库列表
                            }
                          }}
                          style={{
                            padding: '12px 16px',
                            marginBottom: 8,
                            border: '1px solid #d9d9d9',
                            borderRadius: 4,
                            cursor: 'pointer',
                            backgroundColor: '#fff',
                            transition: 'background-color 0.2s',
                          }}
                          onMouseEnter={(e) => {
                            e.currentTarget.style.backgroundColor = '#f5f5f5';
                          }}
                          onMouseLeave={(e) => {
                            e.currentTarget.style.backgroundColor = '#fff';
                          }}
                        >
                          <div style={{ marginBottom: 8 }}>
                            <Tag color="blue">{q.category}</Tag>
                            <Tag
                              color={
                                q.difficulty === 'easy' ? 'green' : q.difficulty === 'medium' ? 'orange' : 'red'
                              }
                            >
                              {q.difficulty === 'easy' ? '简单' : q.difficulty === 'medium' ? '中等' : '困难'}
                            </Tag>
                          </div>
                          <div style={{ color: '#262626', fontSize: 14, lineHeight: '1.6' }}>
                            {q.question}
                          </div>
                        </div>
                      ))
                    )}
                  </div>
                </div>
              </>
            ) : (
              <>
                {/* 显示选中的题目 */}
                <div>
                  <Text strong>当前题目：</Text>
                  <Card size="small" style={{ marginTop: 8, backgroundColor: '#f0f5ff', border: '1px solid #1890ff' }}>
                    <Paragraph style={{ fontSize: 16, marginBottom: 0 }}>
                      {question}
                    </Paragraph>
                  </Card>
                </div>
                <Button
                  onClick={() => {
                    setShowQuestionList(true);
                    setQuestion('');
                    setCustomQuestion('');
                    setAnswer('');
                    setFeedback(null);
                  }}
                >
                  重新选择题目
                </Button>
              </>
            )}
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
      </div>
    );
};

export default MockInterview;
