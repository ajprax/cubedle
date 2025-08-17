import axios from 'axios';
import { Card, Kernel, CandidateCard } from './types';

const API_BASE_URL = 'http://localhost:8002/api';

const api = axios.create({
  baseURL: API_BASE_URL,
  headers: {
    'Content-Type': 'application/json',
  },
});

export const cardAPI = {
  getAll: () => api.get<Card[]>('/cards/'),
  get: (id: number) => api.get<Card>(`/cards/${id}/`),
  create: (card: Partial<Card>) => api.post<Card>('/cards/', card),
  update: (id: number, card: Partial<Card>) => api.put<Card>(`/cards/${id}/`, card),
  delete: (id: number) => api.delete(`/cards/${id}/`),
};

export const kernelAPI = {
  getAll: () => api.get<Kernel[]>('/kernels/'),
  get: (id: number) => api.get<Kernel>(`/kernels/${id}/`),
  create: (kernel: Partial<Kernel>) => api.post<Kernel>('/kernels/', kernel),
  update: (id: number, kernel: Partial<Kernel>) => api.put<Kernel>(`/kernels/${id}/`, kernel),
  delete: (id: number) => api.delete(`/kernels/${id}/`),
  addCard: (kernelId: number, cardId: number) => 
    api.post(`/kernels/${kernelId}/add_card/`, { card_id: cardId }),
  removeCard: (kernelId: number, cardId: number) => 
    api.post(`/kernels/${kernelId}/remove_card/`, { card_id: cardId }),
  reorder: (kernelIds: number[]) => 
    api.post('/kernels/reorder/', { kernel_ids: kernelIds }),
};

export const candidateAPI = {
  getAll: () => api.get<CandidateCard[]>('/candidates/'),
  moveToKernel: (cardId: number, kernelId: number) => 
    api.post('/candidates/move_to_kernel/', { card_id: cardId, kernel_id: kernelId }),
};

export default api;