# ==================== 阶段1：构建静态文件 ====================
FROM node:22.14.0-alpine AS builder

# 设置 Alpine 镜像源为阿里云
RUN sed -i 's/dl-cdn.alpinelinux.org/mirrors.aliyun.com/g' /etc/apk/repositories

# 设置工作目录
WORKDIR /app

# 设置 npm 镜像源（国内加速）
RUN npm config set registry https://registry.npmmirror.com

# 复制 package.json 和 package-lock.json
COPY package*.json ./

# 安装依赖
RUN npm install

# 复制项目文件
COPY . .

# 构建生产版本（生成 dist/ 目录）
RUN npm run build

# ==================== 阶段2：使用 Nginx 提供静态文件 ====================
FROM nginx:1.25-alpine

# 从构建阶段复制静态文件到 Nginx 目录
COPY --from=builder /app/dist /usr/share/nginx/html

# 复制自定义 Nginx 配置（可选）
# COPY nginx.conf /etc/nginx/conf.d/default.conf

# 暴露端口
EXPOSE 80

# Nginx 会自动启动
CMD ["nginx", "-g", "daemon off;"]
