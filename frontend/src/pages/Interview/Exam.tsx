/**
 * 考试形式的模拟面试页面
 * 每次显示1道题，共10题，最后给出综合评分和建议
 */
import React, { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import {
  Card,
  Button,
  Input,
  Space,
  Typography,
  Progress,
  Alert,
  Spin,
  message,
  Divider,
  Tag,
  Row,
  Col,
  Statistic,
  List,
} from 'antd';
import {
  CheckCircleOutlined,
  ClockCircleOutlined,
  TrophyOutlined,
  BulbOutlined,
  ArrowRightOutlined,
  HomeOutlined,
} from '@ant-design/icons';
import axios from 'axios';

const { Title, Text, Paragraph } = Typography;
const { TextArea } = Input;

interface Question {
  id: number;
  content: string;
  difficulty: string;
  category: string;
}

interface Answer {
  question_id: number;
  question: string;
  answer: string;
  time_spent: number;
}

interface ExamResult {
  total_score: number;
  time_score: number;
  content_score: number;
  avg_time: number;
  total_time: number;
  summary: string;
  suggestions: string[];
  answers: Array<{
    question: string;
    user_answer: string;
    reference_answer: string;
    score: number;
    feedback: string;
  }>;
}

const InterviewExam: React.FC = () => {
  const navigate = useNavigate();
  const [currentQuestion, setCurrentQuestion] = useState(0);
  const [questions, setQuestions] = useState<Question[]>([]);
  const [answers, setAnswers] = useState<Answer[]>([]);
  const [currentAnswer, setCurrentAnswer] = useState('');
  const [loading, setLoading] = useState(false);
  const [examStarted, setExamStarted] = useState(false);
  const [examFinished, setExamFinished] = useState(false);
  const [startTime, setStartTime] = useState<number>(0);
  const [questionStartTime, setQuestionStartTime] = useState<number>(0);
  const [result, setResult] = useState<ExamResult | null>(null);
  const [evaluating, setEvaluating] = useState(false);

  const TOTAL_QUESTIONS = 10;

  useEffect(() => {
    if (examStarted && !examFinished) {
      setQuestionStartTime(Date.now());
    }
  }, [currentQuestion, examStarted]);

  const loadQuestions = async () => {
    setLoading(true);
    try {
      // 随机获取10道题
      const response = await axios.get('/api/v1/admin/questions', {
        params: {
          page: 1,
          page_size: 50,
        },
      });

      const allQuestions = response.data?.data?.items || response.data?.items || [];

      if (allQuestions.length < TOTAL_QUESTIONS) {
        message.warning(`题库题目不足，当前只有 ${allQuestions.length} 道题`);
      }

      // 随机选择10道题
      const shuffled = allQuestions.sort(() => 0.5 - Math.random());
      const selected = shuffled.slice(0, Math.min(TOTAL_QUESTIONS, allQuestions.length));

      setQuestions(selected);
      setExamStarted(true);
      setStartTime(Date.now());
      setQuestionStartTime(Date.now());
    } catch (error: any) {
      console.error('加载题目失败:', error);
      message.error('加载题目失败，请重试');
    } finally {
      setLoading(false);
    }
  };

  const handleNextQuestion = () => {
    if (!currentAnswer.trim()) {
      message.warning('请回答当前问题后再继续');
      return;
    }

    const timeSpent = Math.floor((Date.now() - questionStartTime) / 1000);
    const newAnswer: Answer = {
      question_id: questions[currentQuestion].id,
      question: questions[currentQuestion].content,
      answer: currentAnswer,
      time_spent: timeSpent,
    };

    setAnswers([...answers, newAnswer]);
    setCurrentAnswer('');

    if (currentQuestion < questions.length - 1) {
      setCurrentQuestion(currentQuestion + 1);
    } else {
      // 最后一题，提交评分
      submitExam([...answers, newAnswer]);
    }
  };

  const submitExam = async (finalAnswers: Answer[]) => {
    setEvaluating(true);
    try {
      const totalTime = Math.floor((Date.now() - startTime) / 1000);

      const response = await axios.post('/api/v1/interview/exam/evaluate', {
        answers: finalAnswers,
        total_time: totalTime,
      });

      const examResult = response.data?.data || response.data;
      setResult(examResult);
      setExamFinished(true);
    } catch (error: any) {
      console.error('评分失败:', error);
      message.error('评分失败，请重试');
    } finally {
      setEvaluating(false);
    }
  };

  const getScoreColor = (score: number): string => {
    if (score >= 90) return '#52c41a';
    if (score >= 75) return '#1890ff';
    if (score >= 60) return '#faad14';
    return '#f5222d';
  };

  // 未开始
  if (!examStarted) {
    return (
      <div style={{ padding: '24px', maxWidth: '900px', margin: '0 auto' }}>
        <Card>
          <Space direction="vertical" size="large" style={{ width: '100%', textAlign: 'center' }}>
            <Title level={2}>
              <TrophyOutlined /> 模拟面试考试
            </Title>
            <Paragraph type="secondary">
              本次考试共 {TOTAL_QUESTIONS} 道题，每次显示 1 道题。<br />
              请认真作答，系统将根据答题时间和内容质量综合评分。
            </Paragraph>
            <Alert
              message="考试说明"
              description={
                <ul style={{ textAlign: 'left', paddingLeft: 20 }}>
                  <li>每道题需完成作答后才能进入下一题</li>
                  <li>答题时间会被记录，作为评分参考</li>
                  <li>完成所有题目后，系统将给出综合评分和建议</li>
                  <li>每道题会提供参考答案和详细反馈</li>
                </ul>
              }
              type="info"
              showIcon
            />
            <Button
              type="primary"
              size="large"
              icon={<CheckCircleOutlined />}
              onClick={loadQuestions}
              loading={loading}
            >
              开始考试
            </Button>
          </Space>
        </Card>
      </div>
    );
  }

  // 评分中
  if (evaluating) {
    return (
      <div style={{ padding: '24px', maxWidth: '900px', margin: '0 auto' }}>
        <Card>
          <div style={{ textAlign: 'center', padding: '60px 0' }}>
            <Spin size="large" />
            <Title level={3} style={{ marginTop: 24 }}>评分中...</Title>
            <Paragraph type="secondary">AI 正在分析您的答案，请稍候</Paragraph>
          </div>
        </Card>
      </div>
    );
  }

  // 考试完成，显示结果
  if (examFinished && result) {
    return (
      <div style={{ padding: '24px', maxWidth: '1200px', margin: '0 auto' }}>
        <Card>
          <Space direction="vertical" size="large" style={{ width: '100%' }}>
            <div style={{ textAlign: 'center' }}>
              <Title level={2}>
                <TrophyOutlined /> 考试完成
              </Title>
            </div>

            {/* 总分展示 */}
            <Row gutter={16}>
              <Col span={8}>
                <Card>
                  <Statistic
                    title="综合得分"
                    value={result.total_score}
                    suffix="/ 100"
                    valueStyle={{ color: getScoreColor(result.total_score) }}
                  />
                  <Progress
                    percent={result.total_score}
                    strokeColor={getScoreColor(result.total_score)}
                    style={{ marginTop: 8 }}
                  />
                </Card>
              </Col>
              <Col span={8}>
                <Card>
                  <Statistic
                    title="内容得分"
                    value={result.content_score}
                    suffix="/ 100"
                    valueStyle={{ color: getScoreColor(result.content_score) }}
                  />
                </Card>
              </Col>
              <Col span={8}>
                <Card>
                  <Statistic
                    title="时间得分"
                    value={result.time_score}
                    suffix="/ 100"
                    valueStyle={{ color: getScoreColor(result.time_score) }}
                  />
                </Card>
              </Col>
            </Row>

            {/* 统计信息 */}
            <Card title="答题统计" size="small">
              <Row gutter={16}>
                <Col span={8}>
                  <Text type="secondary">总用时：</Text>
                  <Text strong>{Math.floor(result.total_time / 60)}分{result.total_time % 60}秒</Text>
                </Col>
                <Col span={8}>
                  <Text type="secondary">平均每题：</Text>
                  <Text strong>{Math.floor(result.avg_time / 60)}分{Math.floor(result.avg_time % 60)}秒</Text>
                </Col>
                <Col span={8}>
                  <Text type="secondary">题目数量：</Text>
                  <Text strong>{answers.length} 道</Text>
                </Col>
              </Row>
            </Card>

            {/* 总体评价 */}
            {result.summary && (
              <Card title={<><BulbOutlined /> 总体评价</>} size="small">
                <Paragraph>{result.summary}</Paragraph>
              </Card>
            )}

            {/* 改进建议 */}
            {result.suggestions && result.suggestions.length > 0 && (
              <Card title="改进建议" size="small">
                <List
                  dataSource={result.suggestions}
                  renderItem={(item, index) => (
                    <List.Item>
                      <Text>
                        {index + 1}. {item}
                      </Text>
                    </List.Item>
                  )}
                />
              </Card>
            )}

            {/* 每道题的详细反馈 */}
            <Card title="详细反馈">
              {result.answers.map((item, index) => (
                <Card
                  key={index}
                  type="inner"
                  title={`第 ${index + 1} 题`}
                  extra={<Tag color={getScoreColor(item.score)}>得分: {item.score}</Tag>}
                  style={{ marginBottom: 16 }}
                >
                  <Space direction="vertical" size="middle" style={{ width: '100%' }}>
                    <div>
                      <Text strong>问题：</Text>
                      <Paragraph>{item.question}</Paragraph>
                    </div>
                    <div>
                      <Text strong>您的回答：</Text>
                      <Paragraph style={{ background: '#f5f5f5', padding: 12, borderRadius: 4 }}>
                        {item.user_answer}
                      </Paragraph>
                    </div>
                    <div>
                      <Text strong>参考答案：</Text>
                      <Paragraph style={{ background: '#f6ffed', padding: 12, borderRadius: 4 }}>
                        {item.reference_answer}
                      </Paragraph>
                    </div>
                    {item.feedback && (
                      <div>
                        <Text strong>反馈：</Text>
                        <Paragraph type="secondary">{item.feedback}</Paragraph>
                      </div>
                    )}
                  </Space>
                </Card>
              ))}
            </Card>

            <div style={{ textAlign: 'center' }}>
              <Space>
                <Button
                  type="primary"
                  icon={<HomeOutlined />}
                  onClick={() => navigate('/')}
                >
                  返回首页
                </Button>
                <Button
                  onClick={() => {
                    setExamStarted(false);
                    setExamFinished(false);
                    setCurrentQuestion(0);
                    setAnswers([]);
                    setCurrentAnswer('');
                    setResult(null);
                  }}
                >
                  再来一次
                </Button>
              </Space>
            </div>
          </Space>
        </Card>
      </div>
    );
  }

  // 答题中
  return (
    <div style={{ padding: '24px', maxWidth: '900px', margin: '0 auto' }}>
      <Card>
        <Space direction="vertical" size="large" style={{ width: '100%' }}>
          {/* 进度条 */}
          <div>
            <div style={{ display: 'flex', justifyContent: 'space-between', marginBottom: 8 }}>
              <Text strong>
                <ClockCircleOutlined /> 第 {currentQuestion + 1} / {questions.length} 题
              </Text>
              <Text type="secondary">已完成 {Math.round((currentQuestion / questions.length) * 100)}%</Text>
            </div>
            <Progress
              percent={Math.round(((currentQuestion + 1) / questions.length) * 100)}
              status="active"
            />
          </div>

          {/* 题目信息 */}
          <Card size="small">
            <Space>
              <Tag color="blue">{questions[currentQuestion]?.difficulty || '中等'}</Tag>
              <Tag>{questions[currentQuestion]?.category || '综合'}</Tag>
            </Space>
          </Card>

          {/* 题目内容 */}
          <div>
            <Title level={4}>题目：</Title>
            <Paragraph style={{ fontSize: 16, lineHeight: 1.8 }}>
              {questions[currentQuestion]?.content}
            </Paragraph>
          </div>

          {/* 答题区 */}
          <div>
            <Title level={5}>您的回答：</Title>
            <TextArea
              value={currentAnswer}
              onChange={(e) => setCurrentAnswer(e.target.value)}
              placeholder="请输入您的答案..."
              rows={8}
              maxLength={1000}
              showCount
            />
          </div>

          {/* 按钮 */}
          <div style={{ textAlign: 'right' }}>
            <Button
              type="primary"
              size="large"
              icon={currentQuestion < questions.length - 1 ? <ArrowRightOutlined /> : <CheckCircleOutlined />}
              onClick={handleNextQuestion}
              disabled={!currentAnswer.trim()}
            >
              {currentQuestion < questions.length - 1 ? '下一题' : '提交考试'}
            </Button>
          </div>
        </Space>
      </Card>
    </div>
  );
};

export default InterviewExam;
