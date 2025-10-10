import { useState, useEffect } from "react";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Progress } from "@/components/ui/progress";
import { Dialog, DialogContent, DialogHeader, DialogTitle, DialogTrigger } from "@/components/ui/dialog";
import { AlertDialog, AlertDialogAction, AlertDialogCancel, AlertDialogContent, AlertDialogDescription, AlertDialogFooter, AlertDialogHeader, AlertDialogTitle, AlertDialogTrigger } from "@/components/ui/alert-dialog";
import { Edit, Save, RefreshCw, Trash2, Minimize2, History, ArrowLeft, X } from "lucide-react";

// Dummy data for demonstration
const initialGridData = {
  "LS w/Temp": {
    "25C": {
      rows: 6,
      cols: 4,
      devices: {
        "0-0": { id: "B25-53-S001-D3", inDate: "2025-10-01", outDate: "2025-12-31", time: 1000 },
        "0-1": { id: "B25-54-S002-D1", inDate: "2025-10-02", outDate: "2025-12-30", time: 800 },
        "1-0": { id: "B25-55-S003-D2", inDate: "2025-10-03", outDate: "2025-12-29", time: 900 },
        "2-1": { id: "B25-56-S004-D4", inDate: "2025-10-05", outDate: "2025-12-25", time: 750 },
        "3-2": { id: "B25-57-S005-D5", inDate: "2025-10-04", outDate: "2025-12-28", time: 850 },
        "4-0": { id: "B25-58-S006-D6", inDate: "2025-10-06", outDate: "2025-12-26", time: 700 },
        "5-3": { id: "B25-59-S007-D7", inDate: "2025-10-07", outDate: "2025-12-24", time: 600 },
      }
    },
    "45C": {
      rows: 6,
      cols: 4,
      devices: {
        "1-1": { id: "B25-60-S008-D8", inDate: "2025-10-08", outDate: "2025-12-23", time: 950 },
        "2-2": { id: "B25-61-S009-D9", inDate: "2025-10-09", outDate: "2025-12-22", time: 400 },
        "3-0": { id: "B25-62-S010-D10", inDate: "2025-10-10", outDate: "2025-12-21", time: 300 },
      }
    },
    "85C": {
      rows: 6,
      cols: 4,
      devices: {
        "0-2": { id: "B25-63-S011-D11", inDate: "2025-10-11", outDate: "2025-12-20", time: 500 },
        "1-3": { id: "B25-64-S012-D12", inDate: "2025-10-12", outDate: "2025-12-19", time: 650 },
      }
    }
  },
  "Damp Heat": {
    "": {
      rows: 6,
      cols: 6,
      devices: {
        "0-0": { id: "B25-65-S013-D13", inDate: "2025-10-13", outDate: "2025-12-18", time: 800 },
        "1-1": { id: "B25-66-S014-D14", inDate: "2025-10-14", outDate: "2025-12-17", time: 750 },
        "2-2": { id: "B25-67-S015-D15", inDate: "2025-10-15", outDate: "2025-12-16", time: 900 },
        "3-3": { id: "B25-68-S016-D16", inDate: "2025-10-16", outDate: "2025-12-15", time: 550 },
        "4-4": { id: "B25-69-S017-D17", inDate: "2025-10-17", outDate: "2025-12-14", time: 620 },
        "5-5": { id: "B25-70-S018-D18", inDate: "2025-10-18", outDate: "2025-12-13", time: 700 },
      }
    }
  },
  "Outdoor Testing": {
    "": {
      rows: 3,
      cols: 4,
      devices: {
        "0-0": { id: "B25-71-S019-D19", inDate: "2025-10-19", outDate: "2025-12-12", time: 950 },
        "1-1": { id: "B25-72-S020-D20", inDate: "2025-10-20", outDate: "2025-12-11", time: 400 },
        "2-2": { id: "B25-73-S021-D21", inDate: "2025-10-21", outDate: "2025-12-10", time: 300 },
      }
    }
  }
};

// Dummy history data
const historyData = {
  "LS w/Temp-25C-0-0": [
    { id: "B25-50-S001-D1", inDate: "2025-08-01", outDate: "2025-09-30", time: 1000 },
    { id: "B25-51-S001-D2", inDate: "2025-07-01", outDate: "2025-08-31", time: 1000 },
    { id: "B25-48-S001-D3", inDate: "2025-06-01", outDate: "2025-07-30", time: 950 },
    { id: "B25-45-S001-D4", inDate: "2025-05-01", outDate: "2025-06-30", time: 850 },
  ],
  "LS w/Temp-45C-1-1": [
    { id: "B25-49-S002-D1", inDate: "2025-08-15", outDate: "2025-09-20", time: 800 },
    { id: "B25-46-S002-D2", inDate: "2025-07-10", outDate: "2025-08-25", time: 750 },
    { id: "B25-43-S002-D3", inDate: "2025-06-05", outDate: "2025-07-15", time: 700 },
  ],
  "LS w/Temp-85C-0-2": [
    { id: "B25-47-S003-D1", inDate: "2025-08-20", outDate: "2025-09-25", time: 650 },
    { id: "B25-44-S003-D2", inDate: "2025-07-15", outDate: "2025-08-30", time: 600 },
  ],
  "Damp Heat--0-0": [
    { id: "B25-52-S004-D1", inDate: "2025-09-01", outDate: "2025-09-25", time: 600 },
    { id: "B25-41-S004-D2", inDate: "2025-08-01", outDate: "2025-08-28", time: 550 },
    { id: "B25-38-S004-D3", inDate: "2025-07-01", outDate: "2025-07-30", time: 500 },
  ],
  "Outdoor Testing--0-0": [
    { id: "B25-40-S005-D1", inDate: "2025-08-05", outDate: "2025-08-15", time: 300 },
    { id: "B25-37-S005-D2", inDate: "2025-07-20", outDate: "2025-08-05", time: 250 },
    { id: "B25-34-S005-D3", inDate: "2025-06-25", outDate: "2025-07-25", time: 400 },
  ]
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
    setSavedData({ ...editableData });
    onSave(editableData);
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

  const handleDeviceClick = (sectionKey, subsectionKey, row, col, device) => {
    setCurrentSlotInfo({ sectionKey, subsectionKey, row, col });
    
    // Load history data for this slot
    const historyKey = `${sectionKey}-${subsectionKey}-${row}-${col}`;
    const items = historyData[historyKey] || [];
    setHistoryItems(items);
    
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

  const handleSaveDevice = (deviceData) => {
    if (!currentSlotInfo) return;
    
    const { sectionKey, subsectionKey, row, col } = currentSlotInfo;
    const slotKey = `${row}-${col}`;
    
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
  };

  const handleRemoveDevice = () => {
    if (!currentSlotInfo) return;
    
    const { sectionKey, subsectionKey, row, col } = currentSlotInfo;
    const slotKey = `${row}-${col}`;
    
    setGridData(prev => {
      const newData = { ...prev };
      delete newData[sectionKey][subsectionKey].devices[slotKey];
      return newData;
    });
  };

  const handleHistoryItemClick = (device) => {
    setSelectedHistoryDevice(device);
    setHistoryDevicePopupOpen(true);
  };

  return (
    <div className="min-h-screen bg-background">
      {/* Header */}
      <div className="border-b border-border p-4">
        <h1 className="text-2xl font-bold">Stability Dashboard</h1>
        <p className="text-muted-foreground">Real workspace testing environment monitoring</p>
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