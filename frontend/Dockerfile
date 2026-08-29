# 学术说明：前端服务镜像构建脚本。
# 功能定位：完成静态站点构建并输出 Nginx 运行镜像。
# 方法论：以分阶段构建降低最终镜像体积。

FROM node:20-slim AS builder

WORKDIR /app

COPY package*.json ./

RUN npm ci --registry=https://registry.npmmirror.com

COPY . .

RUN npm run build


FROM nginx:alpine

COPY --from=builder /app/dist /usr/share/nginx/html

COPY nginx.conf /etc/nginx/conf.d/default.conf

EXPOSE 80

CMD ["nginx", "-g", "daemon off;"]
