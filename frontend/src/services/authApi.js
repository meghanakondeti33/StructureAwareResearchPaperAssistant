import API from './api';

export const loginUser = async (email, password) => {
  return API.post('/login', { email, password });
};

export const registerUser = async (name, email, password) => {
  return API.post('/register', { name, email, password });
};
