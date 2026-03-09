# node-api-demo

一个使用 Express 实现的 Node.js 用户认证 API，包含：

- 用户注册：`POST /api/auth/register`
- 用户登录：`POST /api/auth/login`

## 启动

```bash
npm install
npm start
```

默认端口：`3000`

## 接口示例

### 1) 注册

```bash
curl -X POST http://localhost:3000/api/auth/register \
  -H "Content-Type: application/json" \
  -d '{
    "username": "alice",
    "email": "alice@example.com",
    "password": "mypassword"
  }'
```

### 2) 登录

```bash
curl -X POST http://localhost:3000/api/auth/login \
  -H "Content-Type: application/json" \
  -d '{
    "email": "alice@example.com",
    "password": "mypassword"
  }'
```

## 环境变量

- `PORT`：服务端口（可选，默认 `3000`）
- `JWT_SECRET`：JWT 密钥（可选，建议生产环境配置）

## 测试

```bash
npm test
```
