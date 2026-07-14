# JWT 认证使用指南

## 一、什么是 JWT 认证？

JWT（JSON Web Token）是一种**用户身份验证机制**，用来保护 API 接口，确保只有授权用户才能访问。

### 工作流程
```
1. 用户登录 → 输入用户名和密码
2. 后端验证 → 检查用户名密码是否正确
3. 生成 Token → 后端生成一个加密的 JWT token
4. 访问 API → 用户携带这个 token 访问其他接口
5. 验证 Token → 后端验证 token 是否有效
```

## 二、在 Swagger UI 中使用 JWT 认证

### 步骤 1：访问 Swagger UI
打开浏览器：http://localhost:8000/docs

### 步骤 2：登录获取 Token

1. 找到 **认证** 分类下的 `POST /api/v1/auth/login` 接口
2. 点击 **"Try it out"**
3. 输入测试账号：
   ```json
   {
     "username": "test_user",
     "password": "test123"
   }
   ```
4. 点击 **"Execute"**
5. 你会看到返回的 token：
   ```json
   {
     "access_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
     "token_type": "bearer",
     "user_id": 1,
     "username": "test_user"
   }
   ```
6. **复制** `access_token` 的值（那一长串字符串）

### 步骤 3：配置认证

1. 在 Swagger UI 页面**右上角**找到 **🔒 Authorize** 按钮
2. 点击它会弹出对话框
3. 在 `HTTPBearer (http, Bearer)` 输入框中输入：
   ```
   Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...
   ```
   **注意**：前面要加 `Bearer ` （Bearer后面有一个空格）
4. 点击 **"Authorize"**
5. 点击 **"Close"**

### 步骤 4：测试受保护的接口

现在你可以访问任何需要认证的接口了！

例如测试 `GET /api/v1/job/list`：
1. 找到这个接口
2. 点击 **"Try it out"**
3. 点击 **"Execute"**
4. 成功返回职位列表！（不再显示 401 错误）

## 三、测试账号

系统提供了两个测试账号：

| 用户名 | 密码 | 角色 |
|--------|------|------|
| test_user | test123 | 普通用户 |
| admin | admin123 | 管理员 |

## 四、使用 curl 测试

### 1. 登录获取 token
```bash
curl -X POST "http://localhost:8000/api/v1/auth/login" \
  -H "Content-Type: application/json" \
  -d '{"username":"test_user","password":"test123"}'
```

返回：
```json
{
  "access_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
  "token_type": "bearer",
  "user_id": 1,
  "username": "test_user"
}
```

### 2. 使用 token 访问接口
```bash
TOKEN="eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9..."

curl -X GET "http://localhost:8000/api/v1/job/list" \
  -H "Authorization: Bearer $TOKEN"
```

## 五、常见问题

### Q1: 为什么我访问接口时提示 401 未授权？
**A**: 你需要先登录获取 token，然后在 Swagger UI 右上角配置认证。

### Q2: Token 会过期吗？
**A**: 会的，当前配置是 **24 小时**（1440 分钟）。过期后需要重新登录。

### Q3: 如何退出登录？
**A**: 在 Swagger UI 右上角点击 **🔒 Authorize**，然后点击 **Logout**。

### Q4: 开发测试时觉得认证太麻烦，能禁用吗？
**A**: 可以。编辑 `backend/.env` 文件，注释掉这一行：
```bash
# JWT_SECRET_KEY=tHXCFfEAXBmBUFweppo0N5NuGxK5Glzme7sooI_1M9U
```
然后重启服务：
```bash
docker-compose restart backend
```
**注意**：禁用后所有接口都不需要认证，**生产环境绝对不能禁用**！

### Q5: Token 是什么格式？
**A**: JWT token 由三部分组成，用 `.` 分隔：
```
eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9    ← Header（头部）
.
eyJ1c2VyX2lkIjoxLCJ1c2VybmFtZSI6InRlc3RfdXNlciIsInJvbGUiOiJ1c2VyIiwiZXhwIjoxNzg0MTI4NDUwfQ    ← Payload（载荷：用户信息）
.
_qb7pY0O_GRJTIEK8cSFEfRNsixXApr_baf3kV6iJzw    ← Signature（签名：防篡改）
```

你可以在 https://jwt.io 解码查看 token 内容（仅用于学习，不要泄露真实 token）。

## 六、前端集成示例

### JavaScript / Fetch API
```javascript
// 1. 登录获取 token
const response = await fetch('http://localhost:8000/api/v1/auth/login', {
  method: 'POST',
  headers: { 'Content-Type': 'application/json' },
  body: JSON.stringify({
    username: 'test_user',
    password: 'test123'
  })
});

const { access_token } = await response.json();

// 2. 保存 token（例如存到 localStorage）
localStorage.setItem('token', access_token);

// 3. 使用 token 访问接口
const jobsResponse = await fetch('http://localhost:8000/api/v1/job/list', {
  headers: {
    'Authorization': `Bearer ${access_token}`
  }
});

const jobs = await jobsResponse.json();
```

### Axios
```javascript
import axios from 'axios';

// 1. 登录
const { data } = await axios.post('http://localhost:8000/api/v1/auth/login', {
  username: 'test_user',
  password: 'test123'
});

const token = data.access_token;

// 2. 配置默认 header
axios.defaults.headers.common['Authorization'] = `Bearer ${token}`;

// 3. 之后所有请求都会自动带上 token
const jobs = await axios.get('http://localhost:8000/api/v1/job/list');
```

## 七、安全建议

### 开发环境（现在）
✅ 可以使用测试账号  
✅ 可以临时禁用认证方便测试  
✅ Token 可以设置较长过期时间  

### 生产环境（部署时）
❌ 必须启用认证  
❌ 不能使用默认测试账号  
❌ 必须使用强密码（加密存储）  
❌ Token 过期时间建议 1-2 小时  
✅ 使用 HTTPS 传输（防止 token 被窃听）  
✅ 定期更换 JWT_SECRET_KEY  

---

**总结**：JWT 认证就像是**进入大楼的门禁卡**，你需要先在前台（登录接口）登记获得门禁卡（token），然后用这张卡才能进入各个房间（访问其他接口）。

**现在就去试试吧！** 打开 http://localhost:8000/docs 开始测试！
