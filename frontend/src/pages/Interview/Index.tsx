/**
 * 面试系统入口页面 - 包含模拟面试和题库刷题两个模块
 */
import React, { useState } from 'react';
import { Card, Tabs } from 'antd';
import { TrophyOutlined, BookOutlined } from '@ant-design/icons';
import InterviewExam from './Exam';
import MockInterview from './Mock';

const { TabPane } = Tabs;

const InterviewIndex: React.FC = () => {
  const [activeTab, setActiveTab] = useState('exam');

  return (
    <div style={{ padding: '24px' }}>
      <Card>
        <Tabs
          activeKey={activeTab}
          onChange={setActiveTab}
          size="large"
          items={[
            {
              key: 'exam',
              label: (
                <span>
                  <TrophyOutlined />
                  模拟面试
                </span>
              ),
              children: <InterviewExam />,
            },
            {
              key: 'mock',
              label: (
                <span>
                  <BookOutlined />
                  题库刷题
                </span>
              ),
              children: <MockInterview />,
            },
          ]}
        />
      </Card>
    </div>
  );
};

export default InterviewIndex;
