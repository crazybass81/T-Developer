FROM node:18-alpine

WORKDIR /app

# 의존성 복사 및 설치
COPY frontend/package*.json ./
RUN npm ci

# 소스 코드 복사
COPY frontend/ .

# 빌드
RUN npm run build

EXPOSE 3000

CMD ["npm", "run", "preview"]