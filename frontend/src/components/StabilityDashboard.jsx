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
    "25C (100%)": {
      rows: 6,
      cols: 4,
      devices: {
        "0-0": { id: "B25-53-S001-D3", inDate: "2025-10-01", outDate: "2025-12-31", time: 1000 },
        "0-1": { id: "B25-54-S002-D1", inDate: "2025-10-02", outDate: "2025-12-30", time: 800 },
        "1-0": { id: "B25-55-S003-D2", inDate: "2025-10-03", outDate: "2025-12-29", time: 900 },
      }
    },
    "45C (30%)": {
      rows: 4,
      cols: 4,
      devices: {
        "1-1": { id: "B25-56-S004-D4", inDate: "2025-10-05", outDate: "2025-12-25", time: 750 },
      }
    }
  },
  "Damp Heat": {
    "85C(50%)": {
      rows: 4,
      cols: 3,
      devices: {
        "0-0": { id: "B25-57-S005-D5", inDate: "2025-10-04", outDate: "2025-12-28", time: 850 },
        "1-0": { id: "B25-58-S006-D6", inDate: "2025-10-06", outDate: "2025-12-26", time: 700 },
      }
    },
    "(50%)": {
      rows: 6,
      cols: 4,
      devices: {
        "2-1": { id: "B25-59-S007-D7", inDate: "2025-10-07", outDate: "2025-12-24", time: 600 },
      }
    }
  },
  "Outdoor Testing": {
    "(50%)": {
      rows: 4,
      cols: 6,
      devices: {
        "0-0": { id: "B25-60-S008-D8", inDate: "2025-10-08", outDate: "2025-12-23", time: 950 },
        "1-1": { id: "B25-61-S009-D9", inDate: "2025-10-09", outDate: "2025-12-22", time: 400 },
      }
    }
  }
};

// Dummy history data
const historyData = {
  "LS w/Temp-25C (100%)-0-0": [
    { id: "B25-50-S001-D1", inDate: "2025-08-01", outDate: "2025-09-30", time: 1000 },
    { id: "B25-51-S001-D2", inDate: "2025-07-01", outDate: "2025-08-31", time: 1000 },
  ],
  "Damp Heat-85C(50%)-0-0": [
    { id: "B25-52-S002-D1", inDate: "2025-09-01", outDate: "2025-09-25", time: 600 },
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

  return (
    <div className="flex flex-col items-center space-y-2">
      <h4 className="text-sm font-medium text-center">{title}</h4>
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
  onHistory 
}) => {
  const [editableData, setEditableData] = useState(deviceData || {});
  const [savedData, setSavedData] = useState(deviceData || {});

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
      <DialogContent className="max-w-md">
        <DialogHeader>
          <DialogTitle className="flex items-center justify-between">
            Device Information
            <Button 
              variant="ghost" 
              size="sm" 
              onClick={() => onOpenChange(false)}
              className="h-6 w-6 p-0"
            >
              <Minimize2 className="h-4 w-4" />
            </Button>
          </DialogTitle>
        </DialogHeader>
        
        <div className="space-y-4">
          <div className="flex items-center space-x-2">
            <RefreshCw className="h-4 w-4" />
            <Button variant="ghost" size="sm" onClick={() => onOpenChange(false)}>
              <X className="h-4 w-4" />
            </Button>
          </div>

          <div>
            <label className="block text-sm font-medium mb-1">Device ID:</label>
            <Input
              value={editableData.id || ''}
              onChange={(e) => setEditableData({ ...editableData, id: e.target.value })}
              placeholder="Enter device ID"
            />
          </div>

          <div>
            <label className="block text-sm font-medium mb-1">In Date:</label>
            <Input
              type="date"
              value={editableData.inDate || ''}
              onChange={(e) => setEditableData({ ...editableData, inDate: e.target.value })}
            />
          </div>

          <div>
            <label className="block text-sm font-medium mb-1">Out Date:</label>
            <Input
              type="date"
              value={editableData.outDate || ''}
              onChange={(e) => setEditableData({ ...editableData, outDate: e.target.value })}
            />
          </div>

          <div>
            <label className="block text-sm font-medium mb-1">Time: {editableData.time || 0} hrs</label>
            <Input
              type="number"
              value={editableData.time || ''}
              onChange={(e) => setEditableData({ ...editableData, time: parseInt(e.target.value) || 0 })}
              placeholder="Enter time in hours"
            />
          </div>

          <div>
            <label className="block text-sm font-medium mb-1">Progress:</label>
            <Progress value={calculateProgress()} className="w-full" />
            <p className="text-xs text-muted-foreground mt-1">
              {Math.round(calculateProgress())}% complete
            </p>
          </div>

          <div className="flex space-x-2">
            <Button variant="outline" size="sm" onClick={handleRefresh}>
              <RefreshCw className="h-4 w-4 mr-1" />
              Refresh
            </Button>
            
            <Button size="sm" onClick={handleSave}>
              <Save className="h-4 w-4 mr-1" />
              Save
            </Button>

            <Button variant="outline" size="sm" onClick={onHistory}>
              <History className="h-4 w-4 mr-1" />
              History
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
      </DialogContent>
    </Dialog>
  );
};

const HistorySidebar = ({ open, onOpenChange, historyItems, onHistoryItemClick }) => {
  if (!open) return null;

  return (
    <div className="fixed right-0 top-0 h-full w-80 bg-background border-l border-border shadow-lg z-50 p-4">
      <div className="flex items-center justify-between mb-4">
        <h3 className="text-lg font-semibold">Device History</h3>
        <Button variant="ghost" size="sm" onClick={() => onOpenChange(false)}>
          <X className="h-4 w-4" />
        </Button>
      </div>
      
      <div className="space-y-2">
        {historyItems && historyItems.length > 0 ? (
          historyItems.map((item, index) => (
            <Card key={index} className="cursor-pointer hover:bg-accent" onClick={() => onHistoryItemClick(item)}>
              <CardContent className="p-3">
                <p className="font-medium">{item.id}</p>
                <p className="text-sm text-muted-foreground">
                  {item.inDate} to {item.outDate}
                </p>
              </CardContent>
            </Card>
          ))
        ) : (
          <p className="text-muted-foreground">No history available</p>
        )}
      </div>
    </div>
  );
};

const DeviceDetailSidebar = ({ open, onOpenChange, device }) => {
  if (!open || !device) return null;

  const calculateProgress = () => {
    if (!device.inDate || !device.outDate) return 0;
    
    const today = new Date();
    const inDate = new Date(device.inDate);
    const outDate = new Date(device.outDate);
    
    const totalDays = (outDate - inDate) / (1000 * 60 * 60 * 24);
    const daysElapsed = (today - inDate) / (1000 * 60 * 60 * 24);
    
    return Math.min(Math.max((daysElapsed / totalDays) * 100, 0), 100);
  };

  return (
    <div className="fixed right-80 top-0 h-full w-80 bg-background border-l border-border shadow-lg z-50 p-4">
      <div className="flex items-center justify-between mb-4">
        <h3 className="text-lg font-semibold">Device Details</h3>
        <div className="flex space-x-2">
          <Button variant="ghost" size="sm" onClick={() => onOpenChange(false)}>
            <ArrowLeft className="h-4 w-4" />
          </Button>
          <Button variant="ghost" size="sm" onClick={() => onOpenChange(false)}>
            <X className="h-4 w-4" />
          </Button>
        </div>
      </div>
      
      <div className="space-y-4">
        <div>
          <label className="block text-sm font-medium mb-1">Device ID:</label>
          <p className="text-sm">{device.id}</p>
        </div>

        <div>
          <label className="block text-sm font-medium mb-1">In Date:</label>
          <p className="text-sm">{device.inDate}</p>
        </div>

        <div>
          <label className="block text-sm font-medium mb-1">Out Date:</label>
          <p className="text-sm">{device.outDate}</p>
        </div>

        <div>
          <label className="block text-sm font-medium mb-1">Time:</label>
          <p className="text-sm">{device.time} hrs</p>
        </div>

        <div>
          <label className="block text-sm font-medium mb-1">Progress:</label>
          <Progress value={calculateProgress()} className="w-full" />
          <p className="text-xs text-muted-foreground mt-1">
            {Math.round(calculateProgress())}% complete
          </p>
        </div>
      </div>
    </div>
  );
};

export default function StabilityDashboard() {
  const [gridData, setGridData] = useState(initialGridData);
  const [selectedDevice, setSelectedDevice] = useState(null);
  const [devicePopupOpen, setDevicePopupOpen] = useState(false);
  const [historyOpen, setHistoryOpen] = useState(false);
  const [historyItems, setHistoryItems] = useState([]);
  const [deviceDetailOpen, setDeviceDetailOpen] = useState(false);
  const [selectedHistoryDevice, setSelectedHistoryDevice] = useState(null);
  const [currentSlotInfo, setCurrentSlotInfo] = useState(null);

  const handleDeviceClick = (sectionKey, subsectionKey, row, col, device) => {
    setCurrentSlotInfo({ sectionKey, subsectionKey, row, col });
    
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

  const handleShowHistory = () => {
    if (!currentSlotInfo) return;
    
    const { sectionKey, subsectionKey, row, col } = currentSlotInfo;
    const historyKey = `${sectionKey}-${subsectionKey}-${row}-${col}`;
    const items = historyData[historyKey] || [];
    
    setHistoryItems(items);
    setHistoryOpen(true);
    setDevicePopupOpen(false);
  };

  const handleHistoryItemClick = (device) => {
    setSelectedHistoryDevice(device);
    setDeviceDetailOpen(true);
  };

  return (
    <div className="min-h-screen bg-background">
      {/* Header */}
      <div className="border-b border-border p-4">
        <h1 className="text-2xl font-bold">Stability Dashboard</h1>
        <p className="text-muted-foreground">Real workspace testing environment monitoring</p>
      </div>

      {/* Main Content */}
      <div className="p-6 space-y-8">
        {Object.entries(gridData).map(([sectionKey, section]) => (
          <Card key={sectionKey}>
            <CardHeader>
              <CardTitle>{sectionKey}</CardTitle>
            </CardHeader>
            <CardContent>
              <div className="flex flex-wrap gap-8 justify-center">
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

      {/* Device Popup */}
      <DevicePopup
        open={devicePopupOpen}
        onOpenChange={setDevicePopupOpen}
        deviceData={selectedDevice}
        onSave={handleSaveDevice}
        onRemove={handleRemoveDevice}
        onRefresh={() => {}}
        onHistory={handleShowHistory}
      />

      {/* History Sidebar */}
      <HistorySidebar
        open={historyOpen}
        onOpenChange={setHistoryOpen}
        historyItems={historyItems}
        onHistoryItemClick={handleHistoryItemClick}
      />

      {/* Device Detail Sidebar */}
      <DeviceDetailSidebar
        open={deviceDetailOpen}
        onOpenChange={setDeviceDetailOpen}
        device={selectedHistoryDevice}
      />
    </div>
  );
}