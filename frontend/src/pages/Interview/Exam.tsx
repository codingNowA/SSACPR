/**
 * 考试形式的模拟面试页面
 * 每次显示1道题，共10题，最后给出综合评分和建议
 * 第一题固定为自我介绍，其余根据简历技能匹配抽取
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
import { useAppStore } from '../../store';
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
  const { user } = useAppStore();
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
  }, [currentQuestion, examStarted, examFinished]);

  const loadQuestions = async () => {
    setLoading(true);
    try {
      const token = localStorage.getItem('token');
      const headers: any = {};
      if (token) headers.Authorization = `Bearer ${token}`;

      // 1. 获取用户简历技能
      let userSkills: string[] = [];
      try {
        const resumeRes = await axios.get('/api/v1/resume/list', {
          params: { user_id: user?.userId, page: 1, page_size: 1 },
          headers,
        });
        const resumeData = resumeRes.data?.data || resumeRes.data;
        const resumes = resumeData?.items || resumeData?.resumes || [];
        if (resumes.length > 0 && resumes[0].parsed_data) {
          const parsed = resumes[0].parsed_data;
          userSkills = parsed.skills || parsed.技能 || parsed.skill_list || [];
        }
      } catch {
        // 简历获取失败不阻塞
      }

      // 2. 获取面试题库（多取一些，后面筛选）
      const response = await axios.get('/api/v1/interview-exam/questions', {
        params: { count: 50 },
      });
      const allQuestions = response.data?.data || [];

      if (allQuestions.length === 0) {
        message.error('题库为空，请先添加面试题目');
        setLoading(false);
        return;
      }

      // 3. 第一题固定为自我介绍（id=1）
      let selfIntro = allQuestions.find((q: any) => q.id === 1);
      if (!selfIntro) {
        // 如果id=1不存在，构造一个
        selfIntro = {
          id: 0,
          question_text: '请做一个简短的自我介绍',
          category: '通用',
          difficulty: 'easy',
        };
      }

      // 4. 根据技能匹配筛选题目（优先匹配related_skills）
      let matchedQuestions = allQuestions.filter((q: any) => q.id !== (selfIntro as any).id);
      
      if (userSkills.length > 0) {
        // 优先选取related_skills与用户技能匹配的题
        const skillLower = userSkills.map(s => s.toLowerCase());
        const skillMatched = matchedQuestions.filter((q: any) => {
          const related = q.related_skills || [];
          const qSkills = Array.isArray(related) 
            ? related.map((s: string) => s.toLowerCase())
            : [];
          return qSkills.some(s => skillLower.some(us => s.includes(us) || us.includes(s)));
        });
        const nonMatched = matchedQuestions.filter((q: any) => !skillMatched.includes(q));
        
        // 匹配的排前面，不匹配的排后面
        matchedQuestions = [...skillMatched, ...nonMatched];
      }

      // 5. 取需要的数量（第一题 + 后续题）
      const remainingCount = TOTAL_QUESTIONS - 1;
      const selected = matchedQuestions.slice(0, remainingCount);

      // 6. 组装最终题目列表
      const mapped = [
        {
          id: selfIntro.id,
          content: selfIntro.question_text || selfIntro.question || '请做一个简短的自我介绍',
          difficulty: selfIntro.difficulty || 'easy',
          category: selfIntro.category || '通用',
        },
        ...selected.map((q: any) => ({
          id: q.id,
          content: q.question_text || q.question || '',
          difficulty: q.difficulty || 'medium',
          category: q.category || '未分类',
        })),
      ];

      if (mapped.length < TOTAL_QUESTIONS) {
        message.warning(`题库题目不足，本次面试共 ${mapped.length} 道题`);
      }

      setQuestions(mapped);
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

      // 逐题评估
      const evaluatedAnswers = [];
      let totalScore = 0;

      for (const ans of finalAnswers) {
        try {
          const evalRes = await axios.post('/api/v1/interview-mock/evaluate', {
            question: ans.question,
            answer: ans.answer,
          });
          const evalData = evalRes.data?.data || evalRes.data;
          const feedback = evalData?.feedback || {};

          evaluatedAnswers.push({
            question: ans.question,
            user_answer: ans.answer,
            reference_answer: feedback?.sample_answer || '',
            score: feedback?.score || 0,
            feedback: feedback?.overall_assessment || '',
          });
          totalScore += feedback?.score || 0;
        } catch (error) {
          console.error('评估失败:', error);
          // 评估失败时，根据答案质量给予合理分数
          const answerLength = ans.answer.trim().length;
          const answerWords = ans.answer.trim().split(/\s+/).length;

          let baseScore = 0;
          if (answerLength < 20) {
            baseScore = 20; // 答案太短
          } else if (answerLength < 50) {
            baseScore = 35; // 答案较短
          } else if (answerLength < 100) {
            baseScore = 45; // 答案一般
          } else if (answerLength < 200) {
            baseScore = 55; // 答案较完整
          } else {
            baseScore = 60; // 答案完整
          }

          evaluatedAnswers.push({
            question: ans.question,
            user_answer: ans.answer,
            reference_answer: '',
            score: baseScore,
            feedback: `AI 评估服务暂时不可用。初步评分：${baseScore}分（基于答案长度：${answerLength}字，约${answerWords}词）。建议：答案应详细且结构化，使用 STAR 法则组织内容。`,
          });
          totalScore += baseScore;
        }
      }

      const avgScore = Math.round(totalScore / evaluatedAnswers.length);
      const avgTime = Math.round(totalTime / evaluatedAnswers.length);

      setResult({
        total_score: avgScore,
        time_score: Math.max(0, 100 - avgTime),
        content_score: avgScore,
        avg_time: avgTime,
        total_time: totalTime,
        summary: avgScore >= 80 ? '表现优秀' : avgScore >= 60 ? '表现良好' : '需要提升',
        suggestions: [
          avgScore < 60 ? '建议加强基础知识的学习' : '',
          avgTime > 120 ? '回答时间偏长，建议提高表达效率' : '',
          '多练习自我介绍，突出重点经历和技能',
          '回答时注意结构化表达：观点-论据-总结',
        ].filter(Boolean),
        answers: evaluatedAnswers,
      });

      setExamFinished(true);
    } catch (error: any) {
      console.error('提交评分失败:', error);
      message.error('评分失败，请重试');
    } finally {
      setEvaluating(false);
    }
  };

  const getDifficultyTag = (difficulty: string) => {
    const map: Record<string, { color: string; label: string }> = {
      easy: { color: 'green', label: '简单' },
      medium: { color: 'orange', label: '中等' },
      hard: { color: 'red', label: '困难' },
    };
    const item = map[difficulty] || { color: 'default', label: difficulty };
    return <Tag color={item.color}>{item.label}</Tag>;
  };

  // ===== 开始界面 =====
  if (!examStarted) {
    return (
      <div style={{ maxWidth: '800px', margin: '0 auto' }}>
        <Space direction="vertical" size="large" style={{ width: '100%' }}>
          <Title level={3}>🎯 模拟面试</Title>
          <Paragraph>
            系统将为您生成 <Text strong>{TOTAL_QUESTIONS} 道</Text>面试题，
            第一题为自我介绍，其余根据您的简历技能智能匹配。
            请认真作答，系统将自动评分并给出建议。
          </Paragraph>
          <Alert
            message="面试提示"
            description="请在一个安静的环境中进行，每道题尽量在2分钟内完成。回答时注意结构化表达。"
            type="info"
            showIcon
          />
          <Button
            type="primary"
            size="large"
            onClick={loadQuestions}
            loading={loading}
            block
          >
            开始面试
          </Button>
        </Space>
      </div>
    );
  }

  // ===== 答题界面 =====
  if (!examFinished) {
    const progress = ((currentQuestion + 1) / questions.length) * 100;
    return (
      <div style={{ maxWidth: '800px', margin: '0 auto' }}>
        <Space direction="vertical" size="middle" style={{ width: '100%' }}>
            <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
              <Space>
                <Tag color="blue">第 {currentQuestion + 1} / {questions.length} 题</Tag>
                {getDifficultyTag(questions[currentQuestion]?.difficulty)}
                {questions[currentQuestion]?.category && (
                  <Tag>{questions[currentQuestion].category}</Tag>
                )}
              </Space>
              <Button type="link" onClick={() => { setExamStarted(false); setQuestions([]); setAnswers([]); }}>
                退出面试
              </Button>
            </div>

            <Progress percent={Math.round(progress)} status="active" />

            <Card
              style={{ backgroundColor: '#f6f8fa', border: 'none' }}
            >
              <Title level={4}>
                {currentQuestion === 0 ? '🗣️ ' : '💡 '}
                {questions[currentQuestion]?.content}
              </Title>
            </Card>

            <TextArea
              value={currentAnswer}
              onChange={(e) => setCurrentAnswer(e.target.value)}
              placeholder={
                currentQuestion === 0
                  ? '请输入您的自我介绍（建议包含：姓名/专业、教育背景、核心技能、项目经历、求职意向）'
                  : '请输入您的回答（建议使用 STAR 法则：Situation 情境、Task 任务、Action 行动、Result 结果）'
              }
              rows={6}
              showCount
              maxLength={2000}
            />

            <div style={{ display: 'flex', justifyContent: 'flex-end' }}>
              <Button
                type="primary"
                icon={<ArrowRightOutlined />}
                onClick={handleNextQuestion}
                disabled={!currentAnswer.trim()}
              >
                {currentQuestion < questions.length - 1 ? '下一题' : '提交面试'}
          </Button>
        </div>
      </Space>
      </div>
    );
  }

  // ===== 结果界面 =====
  if (result) {
    const scoreColor = result.total_score >= 80 ? '#52c41a' : result.total_score >= 60 ? '#faad14' : '#f5222d';
    return (
      <div style={{ maxWidth: '900px', margin: '0 auto' }}>
        <Space direction="vertical" size="large" style={{ width: '100%' }}>
          <Card>
            <Row gutter={16}>
              <Col span={6}>
                <Statistic
                  title="综合评分"
                  value={result.total_score}
                  suffix="分"
                  valueStyle={{ color: scoreColor }}
                  prefix={<TrophyOutlined />}
                />
              </Col>
              <Col span={6}>
                <Statistic
                  title="总用时"
                  value={result.total_time}
                  suffix="秒"
                  prefix={<ClockCircleOutlined />}
                />
              </Col>
              <Col span={6}>
                <Statistic
                  title="平均用时"
                  value={result.avg_time}
                  suffix="秒/题"
                />
              </Col>
              <Col span={6}>
                <Statistic
                  title="题目数"
                  value={result.answers.length}
                  suffix="题"
                  prefix={<CheckCircleOutlined />}
                />
              </Col>
            </Row>
          </Card>

          <Card title={<><BulbOutlined /> 综合评价</>}>
            <Alert
              message={result.summary}
              type={result.total_score >= 60 ? 'success' : 'warning'}
              showIcon
            />
            {result.suggestions.length > 0 && (
              <div style={{ marginTop: 16 }}>
                <Text strong>改进建议：</Text>
                <List
                  size="small"
                  dataSource={result.suggestions}
                  renderItem={(item) => (
                    <List.Item>
                      <Text>• {item}</Text>
                    </List.Item>
                  )}
                />
              </div>
            )}
          </Card>

          <Card title="逐题反馈">
            <List
              dataSource={result.answers}
              renderItem={(item, index) => (
                <List.Item>
                  <List.Item.Meta
                    title={
                      <Space>
                        <span>第 {index + 1} 题</span>
                        <Tag color={item.score >= 80 ? 'green' : item.score >= 60 ? 'orange' : 'red'}>
                          {item.score}分
                        </Tag>
                      </Space>
                    }
                    description={
                      <div>
                        <Paragraph><Text strong>题目：</Text>{item.question}</Paragraph>
                        <Paragraph><Text strong>你的回答：</Text>{item.user_answer}</Paragraph>
                        {item.reference_answer && (
                          <Paragraph><Text strong>参考答案：</Text>{item.reference_answer}</Paragraph>
                        )}
                        {item.feedback && (
                          <Paragraph><Text strong>反馈：</Text>{item.feedback}</Paragraph>
                        )}
                      </div>
                    }
                  />
                </List.Item>
              )}
            />
          </Card>

          <div style={{ textAlign: 'center' }}>
            <Button type="primary" onClick={() => {
              setExamStarted(false);
              setExamFinished(false);
              setQuestions([]);
              setAnswers([]);
              setCurrentAnswer('');
              setCurrentQuestion(0);
              setResult(null);
            }}>
              再来一次
            </Button>
          </div>
        </Space>
      </div>
    );
  }

  return null;
};

export default InterviewExam;
