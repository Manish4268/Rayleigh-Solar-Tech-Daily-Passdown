// API utility functions for backend server
// Single backend with modular architecture (charts_api.py, data_management_api.py)
const API_BASE_URL = import.meta.env.VITE_API_URL || 'http://localhost:7071/api';

console.log('🚀 API Configuration:', {
  baseURL: API_BASE_URL
});

// Helper function to handle API responses
const handleResponse = async (response) => {
  if (!response.ok) {
    const error = await response.json().catch(() => ({ error: 'Network error' }));
    throw new Error(error.error || `HTTP error! status: ${response.status}`);
  }
  
  const data = await response.json();
  
  // Check for API error response
  if (data.success === false) {
    throw new Error(data.error || 'API error');
  }
  
  // Return the full response object to preserve success/data structure
  return data;
};

// Safety Issues API functions
export const safetyAPI = {
  // Get all safety issues
  getAll: async () => {
    const response = await fetch(`${API_BASE_URL}/safety`);
    const result = await handleResponse(response);
    return result.data || result;
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

  // Update a safety issue
  update: async (id, data) => {
    const response = await fetch(`${API_BASE_URL}/safety/${id}`, {
      method: 'PUT',
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
  // Get all kudos
  getAll: async () => {
    const response = await fetch(`${API_BASE_URL}/kudos`);
    const result = await handleResponse(response);
    return result.data || result;
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

  // Update a kudos entry
  update: async (id, data) => {
    const response = await fetch(`${API_BASE_URL}/kudos/${id}`, {
      method: 'PUT',
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
    const result = await handleResponse(response);
    return result.data || result;
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

  // Update a today's issue
  update: async (id, data) => {
    const response = await fetch(`${API_BASE_URL}/today/${id}`, {
      method: 'PUT',
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
    const result = await handleResponse(response);
    return result.data || result;
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

  // Update a yesterday's issue
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

// Chart data API functions
export const chartAPI = {
  // Get available parameters
  getParameters: async () => {
    const response = await fetch(`${API_BASE_URL}/charts/parameters`);
    const data = await handleResponse(response);
    return data.parameters || data;
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

// Reset API functions
export const resetAPI = {
  resetTodayIssues: async () => {
    const response = await fetch(`${API_BASE_URL}/reset-today`, {
      method: 'POST',
    });
    return handleResponse(response);
  },
};

// Analysis API functions
export const analysisAPI = {
  // Process Excel/CSV file with analysis options
  processFile: async (file, options) => {
    const formData = new FormData();
    formData.append('file', file);
    
    // Add processing options to form data
    Object.entries(options).forEach(([key, value]) => {
      formData.append(key, String(value));
    });

    const response = await fetch(`${API_BASE_URL}/analysis/process`, {
      method: 'POST',
      body: formData,
    });

    return handleResponse(response);
  },

  // Download analysis results - Quick Data
  downloadQuickData: async () => {
    const response = await fetch(`${API_BASE_URL}/analysis/download`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify({ fileType: 'quick' }),
    });

    if (!response.ok) {
      const error = await response.json().catch(() => ({ error: 'Download failed' }));
      throw new Error(error.message || 'Download failed');
    }

    // Handle file download
    const blob = await response.blob();
    const downloadUrl = window.URL.createObjectURL(blob);
    const link = document.createElement('a');
    link.href = downloadUrl;
    
    // Get filename from response headers or use default
    const contentDisposition = response.headers.get('Content-Disposition');
    let filename = 'Quick_Data.xlsx';
    if (contentDisposition) {
      const filenameMatch = contentDisposition.match(/filename="(.+)"/);
      if (filenameMatch) {
        filename = filenameMatch[1];
      }
    }
    
    link.download = filename;
    document.body.appendChild(link);
    link.click();
    document.body.removeChild(link);
    window.URL.revokeObjectURL(downloadUrl);
    
    return { success: true, filename };
  },

  // Download analysis results - Entire Data
  downloadEntireData: async () => {
    const response = await fetch(`${API_BASE_URL}/analysis/download`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify({ fileType: 'entire' }),
    });

    if (!response.ok) {
      const error = await response.json().catch(() => ({ error: 'Download failed' }));
      throw new Error(error.message || 'Download failed');
    }

    // Handle file download
    const blob = await response.blob();
    const downloadUrl = window.URL.createObjectURL(blob);
    const link = document.createElement('a');
    link.href = downloadUrl;
    
    // Get filename from response headers or use default
    const contentDisposition = response.headers.get('Content-Disposition');
    let filename = 'Entire_Data.xlsx';
    if (contentDisposition) {
      const filenameMatch = contentDisposition.match(/filename="(.+)"/);
      if (filenameMatch) {
        filename = filenameMatch[1];
      }
    }
    
    link.download = filename;
    document.body.appendChild(link);
    link.click();
    document.body.removeChild(link);
    window.URL.revokeObjectURL(downloadUrl);
    
    return { success: true, filename };
  },
};