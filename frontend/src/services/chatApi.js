import API from './api';

export const askQuestion = async (documentId, question) => {
  return API.post('/ask', { documentId, question });
};

export const getHistory = async (documentId) => {
  return API.get(`/history?documentId=${documentId}`);
};
