import API from './api';

export const uploadDocument = async (formData) => {
  return API.post('/upload', formData, {
    headers: { 'Content-Type': 'multipart/form-data' },
  });
};

export const getDocuments = async () => {
  return API.get('/documents');
};
