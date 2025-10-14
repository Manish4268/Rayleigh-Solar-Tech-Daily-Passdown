// API service for Stability Dashboard
const API_BASE_URL = 'http://localhost:7071/api';

export const stabilityApi = {
  // Get all grid data
  async getGridData() {
    try {
      const response = await fetch(`${API_BASE_URL}/stability/grid-data`);
      const result = await response.json();
      
      if (!result.success) {
        throw new Error(result.error || 'Failed to fetch grid data');
      }
      
      return result.gridData;
    } catch (error) {
      console.error('Error fetching grid data:', error);
      throw error;
    }
  },

  // Get all active devices
  async getDevices() {
    try {
      const response = await fetch(`${API_BASE_URL}/stability/devices`);
      const result = await response.json();
      
      if (!result.success) {
        throw new Error(result.error || 'Failed to fetch devices');
      }
      
      return result.devices;
    } catch (error) {
      console.error('Error fetching devices:', error);
      throw error;
    }
  },

  // Create new device
  async createDevice(deviceData) {
    try {
      const response = await fetch(`${API_BASE_URL}/stability/devices`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify(deviceData)
      });
      
      const result = await response.json();
      
      if (!result.success) {
        throw new Error(result.error || 'Failed to create device');
      }
      
      return result.device;
    } catch (error) {
      console.error('Error creating device:', error);
      throw error;
    }
  },

  // Update device by position
  async updateDevice(sectionKey, subsectionKey, row, col, deviceData) {
    try {
      // Handle empty subsectionKey by using a placeholder
      const encodedSubsection = subsectionKey ? encodeURIComponent(subsectionKey) : '_empty_';
      const response = await fetch(
        `${API_BASE_URL}/stability/devices/${encodeURIComponent(sectionKey)}/${encodedSubsection}/${row}/${col}`,
        {
          method: 'PUT',
          headers: {
            'Content-Type': 'application/json',
          },
          body: JSON.stringify(deviceData)
        }
      );
      
      const result = await response.json();
      
      if (!result.success) {
        throw new Error(result.error || 'Failed to update device');
      }
      
      return result;
    } catch (error) {
      console.error('Error updating device:', error);
      throw error;
    }
  },

  // Remove device (soft delete)
  async removeDevice(sectionKey, subsectionKey, row, col, removedBy) {
    try {
      // Handle empty subsectionKey by using a placeholder
      const encodedSubsection = subsectionKey ? encodeURIComponent(subsectionKey) : '_empty_';
      const response = await fetch(
        `${API_BASE_URL}/stability/devices/${encodeURIComponent(sectionKey)}/${encodedSubsection}/${row}/${col}`,
        {
          method: 'DELETE',
          headers: {
            'Content-Type': 'application/json',
          },
          body: JSON.stringify({ removedBy })
        }
      );
      
      const result = await response.json();
      
      if (!result.success) {
        throw new Error(result.error || 'Failed to remove device');
      }
      
      return result;
    } catch (error) {
      console.error('Error removing device:', error);
      throw error;
    }
  },

  // Get history for specific slot
  async getHistory(sectionKey, subsectionKey, row, col) {
    try {
      // Handle empty subsectionKey by using a placeholder
      const encodedSubsection = subsectionKey ? encodeURIComponent(subsectionKey) : '_empty_';
      const response = await fetch(
        `${API_BASE_URL}/stability/history/${encodeURIComponent(sectionKey)}/${encodedSubsection}/${row}/${col}`
      );
      
      const result = await response.json();
      
      if (!result.success) {
        throw new Error(result.error || 'Failed to fetch history');
      }
      
      return result.history;
    } catch (error) {
      console.error('Error fetching history:', error);
      throw error;
    }
  }
};