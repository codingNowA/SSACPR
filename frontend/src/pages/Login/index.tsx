/**
 * 登录页面
 */
import React, { useState } from 'react';
import { Form, Input, Button, Card, message, Tabs } from 'antd';
import { UserOutlined, LockOutlined, MailOutlined } from '@ant-design/icons';
import { useNavigate } from 'react-router-dom';
import { login, register } from '../../services/auth';
import { useStore } from '../../store';

const { TabPane } = Tabs;

const Login: React.FC = () => {
  const [loginForm] = Form.useForm();
  const [registerForm] = Form.useForm();
  const [loading, setLoading] = useState(false);
  const navigate = useNavigate();
  const { setUser } = useStore();

  const handleLogin = async (values: any) => {
    setLoading(true);
    try {
      const response = await login(values.username, values.password);
      message.success('登录成功！');

      // 清除旧用户的简历ID
      localStorage.removeItem('currentResumeId');

      // 保存用户信息到store和localStorage
      setUser({
        userId: response.user_id,
        username: response.username,
        role: response.role,
        realName: response.real_name || '',
        token: response.access_token,
      });

      localStorage.setItem('token', response.access_token);
      localStorage.setItem('user', JSON.stringify({
        userId: response.user_id,
        username: response.username,
        role: response.role,
        realName: response.real_name || '',
      }));

      // 跳转到首页
      navigate('/');
    } catch (error: any) {
      message.error(error || '登录失败');
    } finally {
      setLoading(false);
    }
  };

  const handleRegister = async (values: any) => {
    setLoading(true);
    try {
      const response = await register({
        username: values.username,
        password: values.password,
        email: values.email,
        real_name: values.realName || '',
      });
      message.success('注册成功！');

      // 注册成功后自动登录
      setUser({
        userId: response.user_id,
        username: response.username,
        role: response.role,
        realName: response.real_name || '',
        token: response.access_token,
      });

      localStorage.setItem('token', response.access_token);
      localStorage.setItem('user', JSON.stringify({
        userId: response.user_id,
        username: response.username,
        role: response.role,
        realName: response.real_name || '',
      }));

      // 跳转到首页
      navigate('/');
    } catch (error: any) {
      message.error(error || '注册失败');
    } finally {
      setLoading(false);
    }
  };

  return (
    <div style={{
      minHeight: '100vh',
      display: 'flex',
      alignItems: 'center',
      justifyContent: 'center',
      background: 'linear-gradient(135deg, #667eea 0%, #764ba2 100%)'
    }}>
      <Card
        style={{
          width: 400,
          boxShadow: '0 8px 16px rgba(0,0,0,0.1)',
          borderRadius: 8
        }}
      >
        <div style={{ textAlign: 'center', marginBottom: 24 }}>
          <h2 style={{ margin: 0 }}>职业规划智能体系统</h2>
        </div>

        <Tabs defaultActiveKey="login">
          <TabPane tab="登录" key="login">
            <Form
              form={loginForm}
              onFinish={handleLogin}
              autoComplete="off"
            >
              <Form.Item
                name="username"
                rules={[{ required: true, message: '请输入用户名' }]}
              >
                <Input
                  prefix={<UserOutlined />}
                  placeholder="用户名"
                  size="large"
                />
              </Form.Item>

              <Form.Item
                name="password"
                rules={[{ required: true, message: '请输入密码' }]}
              >
                <Input.Password
                  prefix={<LockOutlined />}
                  placeholder="密码"
                  size="large"
                />
              </Form.Item>

              <Form.Item>
                <Button
                  type="primary"
                  htmlType="submit"
                  block
                  size="large"
                  loading={loading}
                >
                  登录
                </Button>
              </Form.Item>

              <div style={{ textAlign: 'center', color: '#666', fontSize: 12 }}>
                <p>测试账号：admin / admin123（管理员）</p>
              </div>
            </Form>
          </TabPane>

          <TabPane tab="注册" key="register">
            <Form
              form={registerForm}
              onFinish={handleRegister}
              autoComplete="off"
            >
              <Form.Item
                name="username"
                rules={[
                  { required: true, message: '请输入用户名' },
                  { min: 3, message: '用户名至少3个字符' }
                ]}
              >
                <Input
                  prefix={<UserOutlined />}
                  placeholder="用户名"
                  size="large"
                />
              </Form.Item>

              <Form.Item
                name="email"
                rules={[
                  { required: true, message: '请输入邮箱' },
                  { type: 'email', message: '请输入有效的邮箱地址' }
                ]}
              >
                <Input
                  prefix={<MailOutlined />}
                  placeholder="邮箱"
                  size="large"
                />
              </Form.Item>

              <Form.Item
                name="realName"
              >
                <Input
                  prefix={<UserOutlined />}
                  placeholder="真实姓名（可选）"
                  size="large"
                />
              </Form.Item>

              <Form.Item
                name="password"
                rules={[
                  { required: true, message: '请输入密码' },
                  { min: 6, message: '密码至少6个字符' }
                ]}
              >
                <Input.Password
                  prefix={<LockOutlined />}
                  placeholder="密码"
                  size="large"
                />
              </Form.Item>

              <Form.Item
                name="confirmPassword"
                dependencies={['password']}
                rules={[
                  { required: true, message: '请确认密码' },
                  ({ getFieldValue }) => ({
                    validator(_, value) {
                      if (!value || getFieldValue('password') === value) {
                        return Promise.resolve();
                      }
                      return Promise.reject(new Error('两次输入的密码不一致'));
                    },
                  }),
                ]}
              >
                <Input.Password
                  prefix={<LockOutlined />}
                  placeholder="确认密码"
                  size="large"
                />
              </Form.Item>

              <Form.Item>
                <Button
                  type="primary"
                  htmlType="submit"
                  block
                  size="large"
                  loading={loading}
                >
                  注册
                </Button>
              </Form.Item>
            </Form>
          </TabPane>
        </Tabs>
      </Card>
    </div>
  );
};

export default Login;
