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
      // Build device path in format: section_key/subsection_key/row/col
      const devicePath = `${sectionKey}/${subsectionKey || '_empty_'}/${row}/${col}`;
      const encodedPath = encodeURIComponent(devicePath);
      
      const response = await fetch(
        `${API_BASE_URL}/stability/devices/${encodedPath}`,
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
      // Build device path in format: section_key/subsection_key/row/col
      const devicePath = `${sectionKey}/${subsectionKey || '_empty_'}/${row}/${col}`;
      const encodedPath = encodeURIComponent(devicePath);
      
      const response = await fetch(
        `${API_BASE_URL}/stability/devices/${encodedPath}`,
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
      // Build device path in format: section_key/subsection_key/row/col
      const devicePath = `${sectionKey}/${subsectionKey || '_empty_'}/${row}/${col}`;
      const encodedPath = encodeURIComponent(devicePath);
      
      const response = await fetch(
        `${API_BASE_URL}/stability/history/${encodedPath}`
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
  },

  // Check for expired devices
  async checkExpiredDevices() {
    try {
      const response = await fetch(`${API_BASE_URL}/stability/check-expired`);
      const result = await response.json();
      
      if (!result.success) {
        throw new Error(result.error || 'Failed to check expired devices');
      }
      
      return result.expired_devices;
    } catch (error) {
      console.error('Error checking expired devices:', error);
      throw error;
    }
  },

  // Auto-remove expired devices
  async autoRemoveExpiredDevices() {
    try {
      const response = await fetch(`${API_BASE_URL}/stability/auto-remove`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        }
      });
      
      const result = await response.json();
      
      if (!result.success) {
        throw new Error(result.error || 'Failed to auto-remove expired devices');
      }
      
      return {
        message: result.message,
        removedCount: result.removed_count
      };
    } catch (error) {
      console.error('Error auto-removing expired devices:', error);
      throw error;
    }
  },

  // Process expired devices and get details
  async processExpiredDevices() {
    try {
      const response = await fetch(`${API_BASE_URL}/stability/process-expired`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        }
      });
      
      const result = await response.json();
      
      if (!result.success) {
        throw new Error(result.error || 'Failed to process expired devices');
      }
      
      return {
        message: result.message,
        processedCount: result.processed_count,
        processedDevices: result.processed_devices
      };
    } catch (error) {
      console.error('Error processing expired devices:', error);
      throw error;
    }
  }
};