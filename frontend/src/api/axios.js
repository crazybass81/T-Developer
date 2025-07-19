import axios from 'axios';
import apiClient from './config';

// axios 인스턴스 생성
const instance = axios.create({
  baseURL: apiClient.baseURL,
  headers: apiClient.headers,
  timeout: 10000, // 10초 타임아웃
});

// 요청 인터셉터
instance.interceptors.request.use(
  (config) => {
    // 요청 전에 수행할 작업
    return config;
  },
  (error) => {
    return Promise.reject(error);
  }
);

// 응답 인터셉터
instance.interceptors.response.use(
  (response) => {
    // 응답 데이터 가공
    return response;
  },
  (error) => {
    // 오류 응답 처리
    return Promise.reject(error);
  }
);

export default instance;