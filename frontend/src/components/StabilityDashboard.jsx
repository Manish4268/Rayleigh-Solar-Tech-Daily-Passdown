import { useState, useEffect } from "react";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Progress } from "@/components/ui/progress";
import { Dialog, DialogContent, DialogHeader, DialogTitle, DialogTrigger } from "@/components/ui/dialog";
import { AlertDialog, AlertDialogAction, AlertDialogCancel, AlertDialogContent, AlertDialogDescription, AlertDialogFooter, AlertDialogHeader, AlertDialogTitle, AlertDialogTrigger } from "@/components/ui/alert-dialog";
import { Edit, Save, RefreshCw, Trash2, Minimize2, History, ArrowLeft, X } from "lucide-react";
import { stabilityApi } from "../services/stabilityApi";

// Default grid structure - will be populated from API
const initialGridData = {
  "LS w/Temp": {
    "25C": { rows: 6, cols: 4, devices: {} },
    "45C": { rows: 6, cols: 4, devices: {} },
    "85C": { rows: 6, cols: 4, devices: {} }
  },
  "Damp Heat": {
    "": { rows: 6, cols: 6, devices: {} }
  },
  "Outdoor Testing": {
    "": { rows: 3, cols: 4, devices: {} }
  }
};

const DeviceSlot = ({ sectionKey, subsectionKey, row, col, device, onDeviceClick }) => {
  const slotKey = `${row}-${col}`;
  const hasDevice = !!device;

  return (
    <div
      onClick={() => onDeviceClick(sectionKey, subsectionKey, row, col, device)}
      className={`
        w-8 h-8 border-2 border-gray-300 cursor-pointer transition-all duration-200 hover:scale-105
        ${hasDevice ? 'bg-green-500 hover:bg-green-600' : 'bg-gray-300 hover:bg-gray-400'}
      `}
      title={hasDevice ? `Device: ${device.id}` : 'Empty slot'}
    />
  );
};

const DeviceGrid = ({ title, subsection, sectionKey, subsectionKey, onDeviceClick }) => {
  const { rows, cols, devices } = subsection;
  
  // Calculate percentage of filled slots
  const totalSlots = rows * cols;
  const filledSlots = Object.keys(devices).length;
  const percentage = Math.round((filledSlots / totalSlots) * 100);

  return (
    <div className="flex flex-col items-center space-y-2">
      <h4 className="text-sm font-medium text-center">
        {title || `(${percentage}%)`} {title && `(${percentage}%)`}
      </h4>
      <div 
        className="grid gap-1"
        style={{ gridTemplateColumns: `repeat(${cols}, 1fr)` }}
      >
        {Array.from({ length: rows * cols }, (_, index) => {
          const row = Math.floor(index / cols);
          const col = index % cols;
          const device = devices[`${row}-${col}`];
          
          return (
            <DeviceSlot
              key={`${row}-${col}`}
              sectionKey={sectionKey}
              subsectionKey={subsectionKey}
              row={row}
              col={col}
              device={device}
              onDeviceClick={onDeviceClick}
            />
          );
        })}
      </div>
    </div>
  );
};

const DevicePopup = ({ 
  open, 
  onOpenChange, 
  deviceData, 
  onSave, 
  onRemove, 
  onRefresh,
  onHistory,
  historyItems,
  onHistoryItemClick 
}) => {
  const [editableData, setEditableData] = useState(deviceData || {});
  const [savedData, setSavedData] = useState(deviceData || {});
  const [showHistory, setShowHistory] = useState(false);
  const [personName, setPersonName] = useState('');

  useEffect(() => {
    if (deviceData) {
      setEditableData(deviceData);
      setSavedData(deviceData);
    }
  }, [deviceData]);

  const calculateProgress = () => {
    if (!editableData.inDate || !editableData.outDate) return 0;
    
    const today = new Date();
    const inDate = new Date(editableData.inDate);
    const outDate = new Date(editableData.outDate);
    
    const totalDays = (outDate - inDate) / (1000 * 60 * 60 * 24);
    const daysElapsed = (today - inDate) / (1000 * 60 * 60 * 24);
    
    return Math.min(Math.max((daysElapsed / totalDays) * 100, 0), 100);
  };

  const handleSave = () => {
    if (!personName.trim()) {
      alert('Please enter your name for tracking changes');
      return;
    }
    setSavedData({ ...editableData });
    onSave(editableData, personName);
  };

  const handleRefresh = () => {
    setEditableData({ ...savedData });
    onRefresh();
  };

  if (!deviceData) return null;

  return (
    <Dialog open={open} onOpenChange={onOpenChange}>
      <DialogContent className="max-w-2xl bg-black text-white border border-gray-600 [&>button]:hidden">
        <DialogHeader>
          <DialogTitle className="flex items-center justify-between text-white">
            Device Information
            <Button 
              variant="ghost" 
              size="sm" 
              onClick={() => onOpenChange(false)}
              className="h-6 w-6 p-0 text-white hover:bg-gray-700"
            >
              <Minimize2 className="h-4 w-4" />
            </Button>
          </DialogTitle>
        </DialogHeader>
        
        <div className="flex space-x-4">
          {/* Device Information Section */}
          <div className="flex-1 space-y-4">
            <div className="flex items-center space-x-2">
              <RefreshCw 
                className="h-4 w-4 text-white cursor-pointer hover:text-gray-300 transition-colors" 
                onClick={handleRefresh}
                title="Refresh data"
              />
            </div>

            <div>
              <label className="block text-sm font-medium mb-1 text-white">Device ID:</label>
              <Input
                value={editableData.id || ''}
                onChange={(e) => setEditableData({ ...editableData, id: e.target.value })}
                placeholder="Enter device ID"
                className="bg-gray-800 text-white border-gray-600"
              />
            </div>

            <div>
              <label className="block text-sm font-medium mb-1 text-white">In Date:</label>
              <Input
                type="date"
                value={editableData.inDate || ''}
                onChange={(e) => setEditableData({ ...editableData, inDate: e.target.value })}
                className="bg-gray-800 text-white border-gray-600"
              />
            </div>

            <div>
              <label className="block text-sm font-medium mb-1 text-white">Out Date:</label>
              <Input
                type="date"
                value={editableData.outDate || ''}
                onChange={(e) => setEditableData({ ...editableData, outDate: e.target.value })}
                className="bg-gray-800 text-white border-gray-600"
              />
            </div>

            <div>
              <label className="block text-sm font-medium mb-1 text-white">Time: {editableData.time || 0} hrs</label>
              <Input
                type="number"
                value={editableData.time || ''}
                onChange={(e) => setEditableData({ ...editableData, time: parseInt(e.target.value) || 0 })}
                placeholder="Enter time in hours"
                className="bg-gray-800 text-white border-gray-600"
              />
            </div>

            <div>
              <label className="block text-sm font-medium mb-1 text-white">Your Name:</label>
              <Input
                value={personName}
                onChange={(e) => setPersonName(e.target.value)}
                placeholder="Enter your name for tracking changes"
                className="bg-gray-800 text-white border-gray-600"
              />
            </div>

            <div>
              <label className="block text-sm font-medium mb-1 text-white">Progress:</label>
              <Progress value={calculateProgress()} className="w-full" />
              <p className="text-xs text-gray-400 mt-1">
                {Math.round(calculateProgress())}% complete
              </p>
            </div>

            <div className="flex space-x-2">
              <Button size="sm" onClick={handleSave}>
                <Save className="h-4 w-4 mr-1" />
                Save
              </Button>

              <Button variant="outline" size="sm" onClick={() => setShowHistory(!showHistory)}>
                <History className="h-4 w-4 mr-1" />
                {showHistory ? 'Hide History' : 'Show History'}
              </Button>

              <AlertDialog>
                <AlertDialogTrigger asChild>
                  <Button variant="destructive" size="sm">
                    <Trash2 className="h-4 w-4 mr-1" />
                    Remove
                  </Button>
                </AlertDialogTrigger>
                <AlertDialogContent>
                  <AlertDialogHeader>
                    <AlertDialogTitle>Are you sure?</AlertDialogTitle>
                    <AlertDialogDescription>
                      This will remove the device from this slot. This action cannot be undone.
                    </AlertDialogDescription>
                  </AlertDialogHeader>
                  <AlertDialogFooter>
                    <AlertDialogCancel>Cancel</AlertDialogCancel>
                    <AlertDialogAction onClick={() => { onRemove(); onOpenChange(false); }}>
                      Remove Device
                    </AlertDialogAction>
                  </AlertDialogFooter>
                </AlertDialogContent>
              </AlertDialog>
            </div>
          </div>

          {/* History Section */}
          {showHistory && (
            <div className="w-80 border-l border-gray-600 pl-4">
              <div className="flex items-center justify-between mb-4">
                <h3 className="text-lg font-semibold text-white">History</h3>
                <Button 
                  variant="ghost" 
                  size="sm" 
                  onClick={() => setShowHistory(false)}
                  className="h-6 w-6 p-0 text-white hover:bg-gray-700"
                  title="Close history"
                >
                  <ArrowLeft className="h-4 w-4" />
                </Button>
              </div>
              
              <div className="space-y-2 overflow-y-auto max-h-80">
                {historyItems && historyItems.length > 0 ? (
                  historyItems.map((item, index) => (
                    <Card key={index} className="cursor-pointer hover:bg-gray-700 bg-gray-800 border-gray-600" onClick={() => onHistoryItemClick && onHistoryItemClick(item)}>
                      <CardContent className="p-3">
                        <p className="font-medium text-white">{item.id}</p>
                        <p className="text-sm text-gray-400">
                          {item.inDate} to {item.outDate}
                        </p>
                        <p className="text-xs text-gray-500">
                          {item.time} hrs
                        </p>
                      </CardContent>
                    </Card>
                  ))
                ) : (
                  <p className="text-gray-400">No history available</p>
                )}
              </div>
            </div>
          )}
        </div>
      </DialogContent>
    </Dialog>
  );
};

const HistoryDevicePopup = ({ open, onOpenChange, deviceData }) => {
  if (!deviceData) return null;

  const calculateProgress = () => {
    if (!deviceData.inDate || !deviceData.outDate) return 0;
    
    const today = new Date();
    const inDate = new Date(deviceData.inDate);
    const outDate = new Date(deviceData.outDate);
    
    const totalDays = (outDate - inDate) / (1000 * 60 * 60 * 24);
    const daysElapsed = (today - inDate) / (1000 * 60 * 60 * 24);
    
    return Math.min(Math.max((daysElapsed / totalDays) * 100, 0), 100);
  };

  return (
    <Dialog open={open} onOpenChange={onOpenChange}>
      <DialogContent className="max-w-md bg-black text-white border border-gray-600 [&>button]:hidden">
        <DialogHeader>
          <DialogTitle className="flex items-center justify-between text-white">
            History Device Information
            <Button 
              variant="ghost" 
              size="sm" 
              onClick={() => onOpenChange(false)}
              className="h-6 w-6 p-0 text-white hover:bg-gray-700"
            >
              <Minimize2 className="h-4 w-4" />
            </Button>
          </DialogTitle>
        </DialogHeader>
        
        <div className="space-y-4">
          <div>
            <label className="block text-sm font-medium mb-1 text-white">Device ID:</label>
            <div className="bg-gray-800 text-white border border-gray-600 rounded px-3 py-2">
              {deviceData.id}
            </div>
          </div>

          <div>
            <label className="block text-sm font-medium mb-1 text-white">In Date:</label>
            <div className="bg-gray-800 text-white border border-gray-600 rounded px-3 py-2">
              {deviceData.inDate}
            </div>
          </div>

          <div>
            <label className="block text-sm font-medium mb-1 text-white">Out Date:</label>
            <div className="bg-gray-800 text-white border border-gray-600 rounded px-3 py-2">
              {deviceData.outDate}
            </div>
          </div>

          <div>
            <label className="block text-sm font-medium mb-1 text-white">Time: {deviceData.time || 0} hrs</label>
            <div className="bg-gray-800 text-white border border-gray-600 rounded px-3 py-2">
              {deviceData.time} hours
            </div>
          </div>

          <div>
            <label className="block text-sm font-medium mb-1 text-white">Progress:</label>
            <Progress value={calculateProgress()} className="w-full" />
            <p className="text-xs text-gray-400 mt-1">
              {Math.round(calculateProgress())}% complete
            </p>
          </div>
        </div>
      </DialogContent>
    </Dialog>
  );
};

export default function StabilityDashboard() {
  const [gridData, setGridData] = useState(initialGridData);
  const [selectedDevice, setSelectedDevice] = useState(null);
  const [devicePopupOpen, setDevicePopupOpen] = useState(false);
  const [historyItems, setHistoryItems] = useState([]);
  const [historyDevicePopupOpen, setHistoryDevicePopupOpen] = useState(false);
  const [selectedHistoryDevice, setSelectedHistoryDevice] = useState(null);
  const [currentSlotInfo, setCurrentSlotInfo] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);

  // Load grid data from API
  useEffect(() => {
    const loadGridData = async () => {
      try {
        setLoading(true);
        const data = await stabilityApi.getGridData();
        setGridData(data);
        setError(null);
      } catch (err) {
        console.error('Failed to load grid data:', err);
        setError('Failed to load grid data. Using offline mode.');
        // Keep using initial grid data as fallback
      } finally {
        setLoading(false);
      }
    };

    loadGridData();
  }, []);

  const handleDeviceClick = async (sectionKey, subsectionKey, row, col, device) => {
    setCurrentSlotInfo({ sectionKey, subsectionKey, row, col });
    
    // Load history data for this slot
    try {
      const history = await stabilityApi.getHistory(sectionKey, subsectionKey, row, col);
      setHistoryItems(history);
    } catch (err) {
      console.error('Failed to load history:', err);
      setHistoryItems([]);
    }
    
    if (device) {
      setSelectedDevice(device);
    } else {
      // Create a new device for empty slot
      setSelectedDevice({
        id: '',
        inDate: new Date().toISOString().split('T')[0],
        outDate: '',
        time: 0
      });
    }
    setDevicePopupOpen(true);
  };

  const handleSaveDevice = async (deviceData, personName) => {
    if (!currentSlotInfo) return;
    
    const { sectionKey, subsectionKey, row, col } = currentSlotInfo;
    const slotKey = `${row}-${col}`;
    
    try {
      // Check if device already exists in this slot
      const existingDevice = gridData[sectionKey]?.[subsectionKey]?.devices?.[slotKey];
      
      if (existingDevice) {
        // Update existing device
        await stabilityApi.updateDevice(sectionKey, subsectionKey, row, col, {
          deviceId: deviceData.id,
          inDate: deviceData.inDate,
          outDate: deviceData.outDate,
          timeHours: deviceData.time,
          updatedBy: personName
        });
      } else {
        // Create new device
        await stabilityApi.createDevice({
          sectionKey,
          subsectionKey,
          row,
          col,
          deviceId: deviceData.id,
          inDate: deviceData.inDate,
          outDate: deviceData.outDate,
          timeHours: deviceData.time,
          createdBy: personName
        });
      }
      
      // Update local state
      setGridData(prev => ({
        ...prev,
        [sectionKey]: {
          ...prev[sectionKey],
          [subsectionKey]: {
            ...prev[sectionKey][subsectionKey],
            devices: {
              ...prev[sectionKey][subsectionKey].devices,
              [slotKey]: deviceData
            }
          }
        }
      }));
      
      alert('Device saved successfully!');
    } catch (err) {
      console.error('Failed to save device:', err);
      alert(`Failed to save device: ${err.message}`);
    }
  };

  const handleRemoveDevice = async () => {
    if (!currentSlotInfo) return;
    
    // Get person name for removal tracking
    const personName = prompt('Enter your name for tracking this removal:');
    if (!personName || !personName.trim()) {
      alert('Name is required for tracking changes');
      return;
    }
    
    const { sectionKey, subsectionKey, row, col } = currentSlotInfo;
    const slotKey = `${row}-${col}`;
    
    try {
      await stabilityApi.removeDevice(sectionKey, subsectionKey, row, col, personName.trim());
      
      // Update local state
      setGridData(prev => {
        const newData = { ...prev };
        delete newData[sectionKey][subsectionKey].devices[slotKey];
        return newData;
      });
      
      alert('Device removed successfully!');
    } catch (err) {
      console.error('Failed to remove device:', err);
      alert(`Failed to remove device: ${err.message}`);
    }
  };

  const handleHistoryItemClick = (device) => {
    setSelectedHistoryDevice(device);
    setHistoryDevicePopupOpen(true);
  };

  if (loading) {
    return (
      <div className="min-h-screen bg-background flex items-center justify-center">
        <div className="text-center">
          <div className="animate-spin rounded-full h-32 w-32 border-b-2 border-primary"></div>
          <p className="mt-4 text-lg">Loading Stability Dashboard...</p>
        </div>
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-background">
      {/* Header */}
      <div className="border-b border-border p-4">
        <h1 className="text-2xl font-bold">Stability Dashboard</h1>
        <p className="text-muted-foreground">Real workspace testing environment monitoring</p>
        {error && (
          <div className="mt-2 p-2 bg-yellow-100 border border-yellow-400 text-yellow-700 rounded">
            {error}
          </div>
        )}
      </div>

      {/* Main Content */}
      <div className="p-6">
        <div className="flex gap-6 justify-between items-start">
          {Object.entries(gridData).map(([sectionKey, section]) => (
            <Card key={sectionKey} className={`${sectionKey === "LS w/Temp" ? "flex-2 max-w-2xl" : "flex-1 max-w-sm"}`}>
              <CardHeader>
                <CardTitle className="text-center">{sectionKey}</CardTitle>
              </CardHeader>
              <CardContent>
                <div className={`${sectionKey === "LS w/Temp" ? "flex gap-4 justify-center" : "flex justify-center"}`}>
                  {Object.entries(section).map(([subsectionKey, subsection]) => (
                    <DeviceGrid
                      key={`${sectionKey}-${subsectionKey}`}
                      title={subsectionKey}
                      subsection={subsection}
                      sectionKey={sectionKey}
                      subsectionKey={subsectionKey}
                      onDeviceClick={handleDeviceClick}
                    />
                  ))}
                </div>
              </CardContent>
            </Card>
          ))}
        </div>
      </div>

      {/* Device Popup */}
      <DevicePopup
        open={devicePopupOpen}
        onOpenChange={setDevicePopupOpen}
        deviceData={selectedDevice}
        onSave={handleSaveDevice}
        onRemove={handleRemoveDevice}
        onRefresh={() => {}}
        historyItems={historyItems}
        onHistoryItemClick={handleHistoryItemClick}
      />

      {/* History Device Popup */}
      <HistoryDevicePopup
        open={historyDevicePopupOpen}
        onOpenChange={setHistoryDevicePopupOpen}
        deviceData={selectedHistoryDevice}
      />
    </div>
  );
}