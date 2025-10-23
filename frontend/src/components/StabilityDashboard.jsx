import { useState, useEffect } from "react";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Progress } from "@/components/ui/progress";
import { Dialog, DialogContent, DialogHeader, DialogTitle, DialogTrigger } from "@/components/ui/dialog";
import { AlertDialog, AlertDialogAction, AlertDialogCancel, AlertDialogContent, AlertDialogDescription, AlertDialogFooter, AlertDialogHeader, AlertDialogTitle, AlertDialogTrigger } from "@/components/ui/alert-dialog";
import { Edit, Save, RefreshCw, Trash2, Minimize2, History, ArrowLeft, X } from "lucide-react";
import { stabilityAPI } from "../lib/api";
import DevicePerformanceChart from "./DevicePerformanceChart";

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
  const hasT80 = device?.has_t80 || false;

  return (
    <div
      onClick={() => onDeviceClick(sectionKey, subsectionKey, row, col, device)}
      className={`
        w-8 h-8 border-2 border-gray-300 cursor-pointer transition-all duration-200 hover:scale-105
        ${hasDevice ? (hasT80 ? 'bg-blue-500 hover:bg-blue-600' : 'bg-green-500 hover:bg-green-600') : 'bg-gray-300 hover:bg-gray-400'}
      `}
      title={hasDevice ? (hasT80 ? `Device: ${device.id} (T80 Reached)` : `Device: ${device.id}`) : 'Empty slot'}
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
  onHistoryItemClick,
  isExistingDevice = false  // New prop to distinguish existing vs new devices
}) => {
  const [editableData, setEditableData] = useState(deviceData || {});
  const [savedData, setSavedData] = useState(deviceData || {});
  const [showHistory, setShowHistory] = useState(false);
  const [personName, setPersonName] = useState('');
  const [historySelectedIndex, setHistorySelectedIndex] = useState(0);
  const [selectedHistoryLocal, setSelectedHistoryLocal] = useState(null);

  useEffect(() => {
    if (deviceData) {
      setEditableData(deviceData);
      setSavedData(deviceData);
    }
  }, [deviceData]);

  const calculateProgress = () => {
    if (!editableData.inDate || !editableData.inTime || !editableData.time) return 0;
    
    try {
      const now = new Date();
      const inDateTime = new Date(`${editableData.inDate}T${editableData.inTime}`);
      const outDateTime = new Date(inDateTime.getTime() + (editableData.time * 60 * 60 * 1000));
      
      const totalDuration = outDateTime - inDateTime;
      const elapsed = now - inDateTime;
      
      return Math.min(Math.max((elapsed / totalDuration) * 100, 0), 100);
    } catch (error) {
      console.error('Error calculating progress:', error);
      return 0;
    }
  };

  const handleSave = () => {
    if (!personName.trim()) {
      alert('Please enter your name for tracking changes');
      return;
    }
    
    // Validate that at least one time component is greater than 0
    const hours = editableData.hours || 0;
    const minutes = editableData.minutes || 0;
    const seconds = editableData.seconds || 0;
    
    if (hours === 0 && minutes === 0 && seconds === 0) {
      alert('Duration must be greater than 0. Please enter hours, minutes, or seconds.');
      return;
    }
    
    setSavedData({ ...editableData });
    onSave(editableData, personName);
  };

  const handleRefresh = () => {
    setEditableData({ ...savedData });
    onRefresh();
  };

  useEffect(() => {
    if (historyItems && historyItems.length > 0) {
      setHistorySelectedIndex(0);
      const first = historyItems[0];
      setSelectedHistoryLocal({
        deviceId: first.deviceId || first.device_id,
        inDate: first.inDate || first.in_date,
        inTime: first.inTime || first.in_time,
        out_date: first.out_date || first.outDate,
        out_time: first.out_time || first.outTime,
        removed_at: first.removed_at,
        hours: first.hours || 0,
        minutes: first.minutes || 0,
        seconds: first.seconds || 0,
        duration_hours: first.duration_hours || 0,
        duration_minutes: first.duration_minutes || 0,
        duration_seconds: first.duration_seconds || 0,
        actual_hours_stayed: first.actual_hours_stayed || first.actualHoursStayed,
        placedBy: first.created_by || first.createdBy || first.placedBy,
        removedBy: first.removed_by || first.removedBy,
        removalType: first.removalType || first.removal_type,
        isEarlyRemoval: first.isEarlyRemoval || first.is_early_removal
      });
    } else {
      setSelectedHistoryLocal(null);
    }
  }, [historyItems]);

  if (!deviceData) return null;

  return (
    <Dialog open={open} onOpenChange={onOpenChange}>
      <DialogContent className="max-w-6xl min-h-[90vh] max-h-[90vh] overflow-y-auto bg-black text-white border border-gray-600 [&>button]:hidden">
          <DialogHeader className="pb-2">
            <DialogTitle className="flex items-center justify-between text-white">
              Device Information {editableData.id && `- ${editableData.id}`}
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
        
        {/* Two Column Layout */}
        <div className="grid grid-cols-2 gap-6 mt-2 mb-2">
          {/* Left Column: Device ID, Dates, Times, Name */}
          <div className="space-y-2">
            <div className="flex items-center space-x-2">
              <RefreshCw 
                className="h-4 w-4 text-white cursor-pointer hover:text-gray-300 transition-colors" 
                onClick={handleRefresh}
                title="Refresh data"
              />
            </div>

            <div>
              <label className="block text-xs font-medium mb-0.5 text-white">Device ID:</label>
              <Input
                value={editableData.id || ''}
                onChange={(e) => setEditableData({ ...editableData, id: e.target.value })}
                placeholder="Enter device ID"
                className="bg-gray-800 text-white border-gray-600 h-8"
              />
            </div>

            <div className="grid grid-cols-2 gap-2">
              <div>
                <label className="block text-xs font-medium mb-0.5 text-white">In Date:</label>
                <Input
                  type="date"
                  value={editableData.inDate || ''}
                  onChange={(e) => setEditableData({ ...editableData, inDate: e.target.value })}
                  className="bg-gray-800 text-white border-gray-600 h-8"
                />
              </div>
              <div>
                <label className="block text-xs font-medium mb-0.5 text-white">In Time:</label>
                <Input
                  type="time"
                  value={editableData.inTime || ''}
                  onChange={(e) => setEditableData({ ...editableData, inTime: e.target.value })}
                  className="bg-gray-800 text-white border-gray-600 h-8"
                />
              </div>
            </div>

            <div>
              <label className="block text-xs font-medium mb-0.5 text-white">Your Name:</label>
              <Input
                value={personName}
                onChange={(e) => setPersonName(e.target.value)}
                placeholder="Enter your name for tracking changes"
                className="bg-gray-800 text-white border-gray-600 h-8"
              />
            </div>
          </div>

          {/* Right Column: Duration, Progress, Buttons */}
          <div className="space-y-2">
            <div>
              <label className="block text-xs font-medium mb-0.5 text-white">
                Duration: {editableData.hours || 0}h {editableData.minutes || 0}m {editableData.seconds || 0}s
              </label>
              <div className="grid grid-cols-3 gap-2">
                <div>
                  <label className="block text-xs text-gray-400 mb-0.5">Hours</label>
                  <Input
                    type="number"
                    value={editableData.hours || ''}
                    onChange={(e) => {
                      const hours = e.target.value === '' ? 0 : parseInt(e.target.value) || 0;
                      const minutes = editableData.minutes || 0;
                      const seconds = editableData.seconds || 0;
                      setEditableData({ 
                        ...editableData, 
                        hours: hours,
                        time: (hours + (minutes / 60) + (seconds / 3600)).toFixed(4)
                      });
                    }}
                    placeholder="0"
                    min="0"
                    className="bg-gray-800 text-white border-gray-600 h-8"
                  />
                </div>
                <div>
                  <label className="block text-xs text-gray-400 mb-0.5">Minutes</label>
                  <Input
                    type="number"
                    value={editableData.minutes || ''}
                    onChange={(e) => {
                      const minutes = e.target.value === '' ? 0 : parseInt(e.target.value) || 0;
                      const hours = editableData.hours || 0;
                      const seconds = editableData.seconds || 0;
                      setEditableData({ 
                        ...editableData, 
                        minutes: minutes,
                        time: (hours + (minutes / 60) + (seconds / 3600)).toFixed(4)
                      });
                    }}
                    placeholder="0"
                    min="0"
                    max="59"
                    className="bg-gray-800 text-white border-gray-600 h-8"
                  />
                </div>
                <div>
                  <label className="block text-xs text-gray-400 mb-0.5">Seconds</label>
                  <Input
                    type="number"
                    value={editableData.seconds || ''}
                    onChange={(e) => {
                      const seconds = e.target.value === '' ? 0 : parseInt(e.target.value) || 0;
                      const hours = editableData.hours || 0;
                      const minutes = editableData.minutes || 0;
                      setEditableData({ 
                        ...editableData, 
                        seconds: seconds,
                        time: (hours + (minutes / 60) + (seconds / 3600)).toFixed(4)
                      });
                    }}
                    placeholder="0"
                    min="0"
                    max="59"
                    className="bg-gray-800 text-white border-gray-600 h-8"
                  />
                </div>
              </div>
            </div>

            {/* Show calculated Out Date and Out Time */}
            {editableData.inDate && editableData.inTime && (
              isExistingDevice ? 
                (editableData.id && editableData.id.trim() !== '') || 
                (editableData.hours > 0) || (editableData.minutes > 0) || (editableData.seconds > 0) ||
                (editableData.time && editableData.time > 0)
              : 
                (editableData.hours > 0) || (editableData.minutes > 0) || (editableData.seconds > 0) ||
                (editableData.time && editableData.time > 0)
            ) && (
              <div className="bg-gray-700 p-2 rounded border border-gray-600">
                <label className="block text-xs font-medium mb-0.5 text-green-400">Calculated Out Date & Time:</label>
                <div className="text-white text-xs">
                  {(() => {
                    try {
                      const inDateTime = new Date(`${editableData.inDate}T${editableData.inTime}`);
                      const totalMs = ((editableData.hours || 0) * 3600 + 
                                      (editableData.minutes || 0) * 60 + 
                                      (editableData.seconds || 0)) * 1000;
                      const outDateTime = new Date(inDateTime.getTime() + totalMs);
                      return `${outDateTime.toLocaleDateString()} at ${outDateTime.toLocaleTimeString()}`;
                    } catch (e) {
                      return 'Invalid date/time';
                    }
                  })()}
                </div>
              </div>
            )}

            <div>
              <label className="block text-xs font-medium mb-0.5 text-white">Progress:</label>
              <Progress value={calculateProgress()} className="w-full h-2" />
              <p className="text-xs text-gray-400 mt-0.5">
                {Math.round(calculateProgress())}% complete
              </p>
            </div>

            <div className="flex space-x-2 flex-wrap gap-y-1">
              <Button size="sm" onClick={handleSave} className="h-8 text-xs">
                <Save className="h-3 w-3 mr-1" />
                Save
              </Button>

              <Button variant="outline" size="sm" onClick={() => setShowHistory(!showHistory)} className="h-8 text-xs">
                <History className="h-3 w-3 mr-1" />
                {showHistory ? 'Hide History' : 'Show History'}
              </Button>

              <AlertDialog>
                <AlertDialogTrigger asChild>
                  <Button variant="destructive" size="sm" className="h-8 text-xs">
                    <Trash2 className="h-3 w-3 mr-1" />
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
        </div>

        {/* History Section (Inline List + Details) */}
        {showHistory && (
          <div className="mt-2 border-t border-gray-700 pt-2">
            <div className="flex gap-4">
              {/* Left: List */}
              <div className="w-1/3 bg-gray-900 border border-gray-700 rounded p-2 max-h-[50vh] overflow-y-auto">
                <div className="flex items-center justify-between mb-2">
                  <h3 className="text-sm font-semibold text-white">History</h3>
                  <Button variant="ghost" size="sm" onClick={() => setShowHistory(false)} className="h-6 w-6 p-0 text-white hover:bg-gray-700">
                    <ArrowLeft className="h-4 w-4" />
                  </Button>
                </div>

                {historyItems && historyItems.length > 0 ? (
                  historyItems.map((item, index) => {
                    const isSelected = index === historySelectedIndex;
                    return (
                      <div
                        key={index}
                        onClick={() => {
                          setHistorySelectedIndex(index);
                          setSelectedHistoryLocal({
                            deviceId: item.deviceId || item.device_id,
                            inDate: item.inDate || item.in_date,
                            inTime: item.inTime || item.in_time,
                            out_date: item.out_date || item.outDate,
                            out_time: item.out_time || item.outTime,
                            removed_at: item.removed_at,
                            hours: item.hours || 0,
                            minutes: item.minutes || 0,
                            seconds: item.seconds || 0,
                            duration_hours: item.duration_hours || 0,
                            duration_minutes: item.duration_minutes || 0,
                            duration_seconds: item.duration_seconds || 0,
                            actual_hours_stayed: item.actual_hours_stayed || item.actualHoursStayed,
                            placedBy: item.created_by || item.createdBy || item.placedBy,
                            removedBy: item.removed_by || item.removedBy,
                            removalType: item.removalType || item.removal_type,
                            isEarlyRemoval: item.isEarlyRemoval || item.is_early_removal
                          });
                        }}
                        className={`cursor-pointer p-2 mb-1 rounded border ${isSelected ? 'bg-green-700 border-green-600' : 'bg-gray-800 border-gray-700'} text-white`}
                      >
                        <div className="font-medium text-sm">{item.deviceId}</div>
                        <div className="text-xs text-gray-300">{item.inDate} {item.inTime} → {item.outDate} {item.outTime}</div>
                      </div>
                    );
                  })
                ) : (
                  <p className="text-gray-400">No history available</p>
                )}
              </div>

              {/* Right: Details pane */}
              <div className="flex-1 bg-gray-900 border border-gray-700 rounded p-4 max-h-[50vh] overflow-y-auto">
                {selectedHistoryLocal ? (
                  <div className="space-y-3">
                    <div className="flex items-center justify-between">
                      <h4 className="text-sm font-semibold text-white">{selectedHistoryLocal.deviceId}</h4>
                      <div className="text-xs text-gray-400">Status: ✅ Completed</div>
                    </div>

                    <div className="grid grid-cols-2 gap-3">
                      <div>
                        <label className="block text-xs text-gray-400">In Date</label>
                        <div className="text-white text-sm">{selectedHistoryLocal.inDate || 'N/A'}</div>
                      </div>
                      <div>
                        <label className="block text-xs text-gray-400">In Time</label>
                        <div className="text-white text-sm">{selectedHistoryLocal.inTime || 'N/A'}</div>
                      </div>
                      <div>
                        <label className="block text-xs text-gray-400">Out Date</label>
                        <div className="text-white text-sm">{selectedHistoryLocal.out_date || 'N/A'}</div>
                      </div>
                      <div>
                        <label className="block text-xs text-gray-400">Out Time</label>
                        <div className="text-white text-sm">{selectedHistoryLocal.out_time || 'N/A'}</div>
                      </div>
                    </div>

                    <div>
                      <label className="block text-xs text-gray-400">Planned Time</label>
                      <div className="text-white text-sm">{(selectedHistoryLocal.hours || 0)}h {(selectedHistoryLocal.minutes || 0)}m {(selectedHistoryLocal.seconds || 0)}s</div>
                    </div>

                    <div>
                      <label className="block text-xs text-gray-400">Actual Time Stayed</label>
                      <div className="text-white text-sm">{selectedHistoryLocal.actual_hours_stayed ? selectedHistoryLocal.actual_hours_stayed : `${selectedHistoryLocal.duration_hours || 0}h ${selectedHistoryLocal.duration_minutes || 0}m ${selectedHistoryLocal.duration_seconds || 0}s`}</div>
                    </div>

                    <div className="grid grid-cols-2 gap-3">
                      <div>
                        <label className="block text-xs text-gray-400">Placed By</label>
                        <div className="text-white text-sm">{selectedHistoryLocal.placedBy || 'Unknown'}</div>
                      </div>
                      <div>
                        <label className="block text-xs text-gray-400">Removed By</label>
                        <div className="text-white text-sm">{selectedHistoryLocal.removedBy || 'Unknown'}</div>
                      </div>
                    </div>

                    <div>
                      <label className="block text-xs text-gray-400">Removal Type</label>
                      <div className="text-white text-sm">{(selectedHistoryLocal.removalType === 'automatic') ? 'Automatic (Expired)' : 'Manual'}{selectedHistoryLocal.isEarlyRemoval ? ' - Early Removal' : ''}</div>
                    </div>
                  </div>
                ) : (
                  <div className="text-gray-400">Select a history item to view details</div>
                )}
              </div>
            </div>
          </div>
        )}

        {/* Graph Section - Always visible below input form */}
        <div className="mt-2 border-t border-gray-700 pt-2">
          <h3 className="text-sm font-semibold text-white mb-2">Performance Over Time</h3>
          {editableData.id && editableData.id.trim() !== '' ? (
            <DevicePerformanceChart deviceId={editableData.id} />
          ) : (
            <div className="text-gray-400 text-center py-8">
              Enter a Device ID to view performance data
            </div>
          )}
        </div>
      </DialogContent>
    </Dialog>
  );
};

const HistoryDevicePopup = ({ open, onOpenChange, deviceData }) => {
  if (!deviceData) return null;

  const calculateActualProgress = () => {
    // For history items, show 100% since they are completed
    return 100;
  };

  const formatDecimalHoursToHMS = (decimalHours) => {
    if (!decimalHours || decimalHours === 0) return '0h 0m 0s';
    
    const totalSeconds = Math.round(decimalHours * 3600);
    const hours = Math.floor(totalSeconds / 3600);
    const minutes = Math.floor((totalSeconds % 3600) / 60);
    const seconds = totalSeconds % 60;
    
    return `${hours}h ${minutes}m ${seconds}s`;
  };

  // Helper function to get out_date and out_time, with fallback to removed_at
  const getOutDateTime = () => {
    // First try the new fields
    if (deviceData.out_date && deviceData.out_time) {
      return {
        date: deviceData.out_date,
        time: deviceData.out_time
      };
    }
    
    // Fallback: calculate from removed_at if available
    if (deviceData.removed_at) {
      try {
        // removed_at comes as ISO string from backend
        const removedDate = new Date(deviceData.removed_at);
        return {
          date: removedDate.toISOString().split('T')[0], // YYYY-MM-DD
          time: removedDate.toTimeString().substring(0, 5) // HH:MM
        };
      } catch (e) {
        console.error('Error parsing removed_at:', e);
      }
    }
    
    return { date: 'N/A', time: 'N/A' };
  };

  const outDateTime = getOutDateTime();

  return (
    <Dialog open={open} onOpenChange={onOpenChange}>
    <DialogContent className="max-w-2xl min-h-[60vh] max-h-[90vh] bg-black text-white border border-gray-600 [&>button]:hidden">
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
              {deviceData.deviceId || deviceData.device_id || 'N/A'}
            </div>
          </div>

          <div className="grid grid-cols-2 gap-4">
            <div>
              <label className="block text-sm font-medium mb-1 text-white">In Date:</label>
              <div className="bg-gray-800 text-white border border-gray-600 rounded px-3 py-2">
                {deviceData.inDate || deviceData.in_date || 'N/A'}
              </div>
            </div>
            <div>
              <label className="block text-sm font-medium mb-1 text-white">In Time:</label>
              <div className="bg-gray-800 text-white border border-gray-600 rounded px-3 py-2">
                {deviceData.inTime || deviceData.in_time || 'N/A'}
              </div>
            </div>
          </div>

          <div className="grid grid-cols-2 gap-4">
            <div>
              <label className="block text-sm font-medium mb-1 text-white">Out Date (Actual):</label>
              <div className="bg-gray-800 text-white border border-gray-600 rounded px-3 py-2">
                {outDateTime.date}
              </div>
            </div>
            <div>
              <label className="block text-sm font-medium mb-1 text-white">Out Time (Actual):</label>
              <div className="bg-gray-800 text-white border border-gray-600 rounded px-3 py-2">
                {outDateTime.time}
              </div>
            </div>
          </div>

          <div className="grid grid-cols-2 gap-4">
            <div>
              <label className="block text-sm font-medium mb-1 text-white">Planned Time:</label>
              <div className="bg-gray-800 text-white border border-gray-600 rounded px-3 py-2">
                {(deviceData.hours || 0)}h {(deviceData.minutes || 0)}m {(deviceData.seconds || 0)}s
              </div>
            </div>
            <div>
              <label className="block text-sm font-medium mb-1 text-white">Actual Time Stayed:</label>
              <div className="bg-gray-800 text-white border border-gray-600 rounded px-3 py-2">
                {deviceData.actual_hours_stayed ? formatDecimalHoursToHMS(deviceData.actual_hours_stayed) : 
                 `${deviceData.duration_hours || 0}h ${deviceData.duration_minutes || 0}m ${deviceData.duration_seconds || 0}s`}
              </div>
            </div>
          </div>

          <div className="grid grid-cols-2 gap-4">
            <div>
              <label className="block text-sm font-medium mb-1 text-white">Placed By:</label>
              <div className="bg-gray-800 text-white border border-gray-600 rounded px-3 py-2">
                {deviceData.placedBy || deviceData.created_by || 'Unknown'}
              </div>
            </div>
            <div>
              <label className="block text-sm font-medium mb-1 text-white">Removed By:</label>
              <div className="bg-gray-800 text-white border border-gray-600 rounded px-3 py-2">
                {deviceData.removedBy || deviceData.removed_by || 'Unknown'}
              </div>
            </div>
          </div>

          <div>
            <label className="block text-sm font-medium mb-1 text-white">Removal Type:</label>
            <div className="bg-gray-800 text-white border border-gray-600 rounded px-3 py-2">
              {(deviceData.removalType || deviceData.removal_type) === 'automatic' ? 'Automatic (Expired)' : 'Manual'}
              {deviceData.isEarlyRemoval && ' - Early Removal'}
            </div>
          </div>

          <div>
            <label className="block text-sm font-medium mb-1 text-white">Status:</label>
            <div className="bg-green-700 text-white border border-green-600 rounded px-3 py-2">
              ✅ Completed (100%)
            </div>
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
  const [isExistingDevice, setIsExistingDevice] = useState(false); // Track if device already exists
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);

  // Load grid data from API
  useEffect(() => {
    const loadGridData = async () => {
      try {
        setLoading(true);
        const data = await stabilityAPI.getGridData();
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
      const history = await stabilityAPI.getHistory(sectionKey, subsectionKey, row, col);
      setHistoryItems(history);
    } catch (err) {
      console.error('Failed to load history:', err);
      setHistoryItems([]);
    }
    
    if (device) {
      // This is an existing device (green grid)
      setIsExistingDevice(true);
      
      // Map the device data to the expected format for DevicePopup
      // MongoDB device has: deviceId, inDate, inTime, timeHours, etc.
      const mappedDevice = {
        id: device.deviceId || device.id || '',
        inDate: device.inDate || '',
        inTime: device.inTime || '00:00',
        outDate: device.outDate || '',
        time: device.timeHours || device.time || 0,
        hours: device.duration_hours || Math.floor(device.timeHours || 0),
        minutes: device.duration_minutes || 0,
        seconds: device.duration_seconds || 0
      };
      console.log('Mapped device data for popup:', mappedDevice);
      setSelectedDevice(mappedDevice);
    } else {
      // This is a new device slot (gray grid)
      setIsExistingDevice(false);
      
      // Create a new device for empty slot with current precise time
      const now = new Date();
      setSelectedDevice({
        id: '',
        inDate: now.toISOString().split('T')[0],
        inTime: now.toTimeString().substr(0, 8), // HH:MM:SS format for precision
        outDate: '',
        time: 0,
        hours: 0,
        minutes: 0,
        seconds: 0
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
        await stabilityAPI.updateDevice(sectionKey, subsectionKey, row, col, {
          deviceId: deviceData.id,
          inDate: deviceData.inDate,
          inTime: deviceData.inTime,
          hours: deviceData.hours || 0,
          minutes: deviceData.minutes || 0,
          seconds: deviceData.seconds || 0,
          timeHours: deviceData.time, // Keep for backward compatibility
          updatedBy: personName
        });
      } else {
        // Create new device
        await stabilityAPI.createDevice({
          sectionKey,
          subsectionKey,
          row,
          col,
          deviceId: deviceData.id,
          inDate: deviceData.inDate,
          inTime: deviceData.inTime,
          hours: deviceData.hours || 0,
          minutes: deviceData.minutes || 0,
          seconds: deviceData.seconds || 0,
          timeHours: deviceData.time, // Keep for backward compatibility
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
      await stabilityAPI.removeDevice(sectionKey, subsectionKey, row, col, personName.trim());
      
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
    // Map backend history fields to frontend expected format
    const mappedDevice = {
      deviceId: device.deviceId || device.device_id,
      inDate: device.inDate || device.in_date,
      inTime: device.inTime || device.in_time,
      out_date: device.out_date || device.outDate,
      out_time: device.out_time || device.outTime,
      removed_at: device.removed_at, // Keep for fallback calculation
      hours: device.hours || 0,
      minutes: device.minutes || 0, 
      seconds: device.seconds || 0,
      duration_hours: device.duration_hours || 0,
      duration_minutes: device.duration_minutes || 0,
      duration_seconds: device.duration_seconds || 0,
      actual_hours_stayed: device.actual_hours_stayed || device.actualHoursStayed,
      placedBy: device.created_by || device.createdBy || device.placedBy, // Try snake_case first, then camelCase
      removedBy: device.removed_by || device.removedBy,
      removalType: device.removalType || device.removal_type,
      isEarlyRemoval: device.isEarlyRemoval || device.is_early_removal
    };
    
    setSelectedHistoryDevice(mappedDevice);
    setHistoryDevicePopupOpen(true);
  };

  const checkExpiredDevices = async () => {
    try {
      const expiredDevices = await stabilityAPI.checkExpiredDevices();
      return expiredDevices;
    } catch (err) {
      console.error('Failed to check expired devices:', err);
      return [];
    }
  };

  // Auto-check for expired devices every 5 minutes
  useEffect(() => {
    const interval = setInterval(async () => {
      try {
        const expiredDevices = await checkExpiredDevices();
        if (expiredDevices.length > 0) {
          console.log(`Found ${expiredDevices.length} expired devices. Consider running auto-removal.`);
          // Optional: Show notification or automatically remove
          // await handleAutoRemoveExpired();
        }
      } catch (err) {
        console.error('Error in periodic expired device check:', err);
      }
    }, 5 * 60 * 1000); // 5 minutes

    return () => clearInterval(interval);
  }, []);

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
        <div>
          <h1 className="text-2xl font-bold">Stability Dashboard</h1>
          <p className="text-muted-foreground">Real workspace testing environment monitoring</p>
        </div>
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
        isExistingDevice={isExistingDevice}
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