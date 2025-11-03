// import axios from 'axios';

// const API_BASE_URL = process.env.VITE_API_URL || 'http://localhost:7071/api';

// // Today API functions
// export const todayAPI = {
//   // Get all today entries
//   getAll: async () => {
//     const response = await axios.get(`${API_BASE_URL}/today`);
//     return response.data;
//   },

//   // Add new today entry
//   create: async (entry: { description: string; resolved: string; who: string; whom: string }) => {
//     const response = await axios.post(`${API_BASE_URL}/today`, entry);
//     return response.data;
//   },

//   // Update today entry
//   update: async (sr_no: number, entry: any) => {
//     const response = await axios.put(`${API_BASE_URL}/today/${sr_no}`, entry);
//     return response.data;
//   },

//   // Delete today entry
//   delete: async (sr_no: number) => {
//     const response = await axios.delete(`${API_BASE_URL}/today/${sr_no}`);
//     return response.data;
//   }
// };

// // Yesterday API functions
// export const yesterdayAPI = {
//   // Get all yesterday entries
//   getAll: async () => {
//     const response = await axios.get(`${API_BASE_URL}/yesterday`);
//     return response.data;
//   },

//   // Add new yesterday entry
//   create: async (entry: { description: string; resolved: string; who: string; whom: string; resolved_status: string }) => {
//     const response = await axios.post(`${API_BASE_URL}/yesterday`, entry);
//     return response.data;
//   },

//   // Update yesterday entry
//   update: async (sr_no: number, entry: any) => {
//     const response = await axios.put(`${API_BASE_URL}/yesterday/${sr_no}`, entry);
//     return response.data;
//   },

//   // Delete yesterday entry
//   delete: async (sr_no: number) => {
//     const response = await axios.delete(`${API_BASE_URL}/yesterday/${sr_no}`);
//     return response.data;
//   }
// };