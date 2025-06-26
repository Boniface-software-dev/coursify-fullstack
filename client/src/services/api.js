import axios from 'axios';

const api = axios.create({
  baseURL: process.env.REACT_APP_API_BASE_URL || 'http://localhost:3001/api',
  headers: {
    'Content-Type': 'application/json',
  }
});

// Add request interceptor for auth tokens
api.interceptors.request.use(config => {
  const token = localStorage.getItem('token');
  if (token) {
    config.headers.Authorization = `Bearer ${token}`;
  }
  return config;
});

export default {
  // Course endpoints
  getCourses: () => api.get('/courses'),
  getCourse: (id) => api.get(`/courses/${id}`),
  createCourse: (data) => api.post('/courses', data),
  updateCourse: (id, data) => api.put(`/courses/${id}`, data),
  deleteCourse: (id) => api.delete(`/courses/${id}`),
  
  // User endpoints
  login: (credentials) => api.post('/login', credentials),
  register: (userData) => api.post('/users', userData),
  getCurrentUser: () => api.get('/me'),
  
  // Enrollment endpoints
  enrollCourse: (courseId) => api.post(`/courses/${courseId}/enrollments`),
  getUserCourses: () => api.get('/me/courses'),
};