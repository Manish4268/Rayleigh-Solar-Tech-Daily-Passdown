// API utility functions for the consolidated backend
const API_BASE_URL = import.meta.env.VITE_API_BASE_URL || 'http://localhost:7071/api';

// Helper function to handle API responses
const handleResponse = async (response) => {
  if (!response.ok) {
    const error = await response.json().catch(() => ({ error: 'Network error' }));
    throw new Error(error.error || `HTTP error! status: ${response.status}`);
  }
  return response.json();
};

// Safety Issues API functions
export const safetyAPI = {
  // Get all safety issues
  getAll: async () => {
    const response = await fetch(`${API_BASE_URL}/safety`);
    return handleResponse(response);
  },

  // Create a new safety issue
  create: async (data) => {
    const response = await fetch(`${API_BASE_URL}/safety`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify(data),
    });
    return handleResponse(response);
  },

  // Delete a safety issue
  delete: async (id) => {
    const response = await fetch(`${API_BASE_URL}/safety/${id}`, {
      method: 'DELETE',
    });
    return handleResponse(response);
  },
};

// Kudos API functions
export const kudosAPI = {
  // Get all kudos entries
  getAll: async () => {
    const response = await fetch(`${API_BASE_URL}/kudos`);
    return handleResponse(response);
  },

  // Create a new kudos entry
  create: async (data) => {
    const response = await fetch(`${API_BASE_URL}/kudos`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify(data),
    });
    return handleResponse(response);
  },

  // Delete a kudos entry
  delete: async (id) => {
    const response = await fetch(`${API_BASE_URL}/kudos/${id}`, {
      method: 'DELETE',
    });
    return handleResponse(response);
  },
};

// Today's Issues API functions
export const todayAPI = {
  // Get all today's issues
  getAll: async () => {
    const response = await fetch(`${API_BASE_URL}/today`);
    return handleResponse(response);
  },

  // Create a new today's issue
  create: async (data) => {
    const response = await fetch(`${API_BASE_URL}/today`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify(data),
    });
    return handleResponse(response);
  },

  // Delete a today's issue
  delete: async (id) => {
    const response = await fetch(`${API_BASE_URL}/today/${id}`, {
      method: 'DELETE',
    });
    return handleResponse(response);
  },
};

// Yesterday's Issues API functions
export const yesterdayAPI = {
  // Get all yesterday's issues
  getAll: async () => {
    const response = await fetch(`${API_BASE_URL}/yesterday`);
    return handleResponse(response);
  },

  // Create a new yesterday's issue
  create: async (data) => {
    const response = await fetch(`${API_BASE_URL}/yesterday`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify(data),
    });
    return handleResponse(response);
  },

  // Update a yesterday's issue (toggle done status)
  update: async (id, data) => {
    const response = await fetch(`${API_BASE_URL}/yesterday/${id}`, {
      method: 'PUT',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify(data),
    });
    return handleResponse(response);
  },

  // Delete a yesterday's issue
  delete: async (id) => {
    const response = await fetch(`${API_BASE_URL}/yesterday/${id}`, {
      method: 'DELETE',
    });
    return handleResponse(response);
  },
};

// Health check
export const healthAPI = {
  check: async () => {
    const response = await fetch(`${API_BASE_URL}/health`);
    return handleResponse(response);
  },
};

// Reset Today's Issues
export const resetAPI = {
  resetTodayIssues: async () => {
    const response = await fetch(`${API_BASE_URL}/reset-today`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
    });
    return handleResponse(response);
  },
};

// Chart data API functions
export const chartAPI = {
  // Get available parameters
  getParameters: async () => {
    const response = await fetch(`${API_BASE_URL}/charts/parameters`);
    return handleResponse(response);
  },

  // Get data for a specific parameter
  getData: async (parameter) => {
    const response = await fetch(`${API_BASE_URL}/charts/data/${parameter}`);
    return handleResponse(response);
  },

  // Get device yield data with 2.5% quantiles and batch averages
  getDeviceYield: async () => {
    const response = await fetch(`${API_BASE_URL}/charts/device-yield`);
    return handleResponse(response);
  },

  // Get IV repeatability data with daily averages for last 10 days
  getIVRepeatability: async () => {
    const response = await fetch(`${API_BASE_URL}/charts/iv-repeatability`);
    return handleResponse(response);
  },
};