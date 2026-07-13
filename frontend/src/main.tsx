import React from 'react'
import ReactDOM from 'react-dom/client'
import { ConfigProvider } from 'antd'
import zhCN from 'antd/locale/zh_CN'
import 'dayjs/locale/zh-cn'
import './index.css'

ReactDOM.createRoot(document.getElementById('root')!).render(
  <React.StrictMode>
    <ConfigProvider locale={zhCN}>
      <div style={{ padding: '50px', textAlign: 'center' }}>
        <h1>职业规划智能体系统</h1>
        <p>前端开发中...</p>
      </div>
    </ConfigProvider>
  </React.StrictMode>,
)
