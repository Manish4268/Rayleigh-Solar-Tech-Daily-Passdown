"use client"

import { useState, useEffect } from "react"
import { BrowserRouter as Router, Routes, Route, Link } from "react-router-dom"
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card"
import { Button } from "@/components/ui/button"
import { Input } from "@/components/ui/input"
import { Badge } from "@/components/ui/badge"
import { Checkbox } from "@/components/ui/checkbox"
import { BarChart, Bar, LineChart, Line, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer } from "recharts"
import { Plus, Menu, Trash2, Edit } from "lucide-react"
import { todayAPI, yesterdayAPI, safetyAPI, kudosAPI, healthAPI, resetAPI } from "@/lib/api"
import ParameterChart from "@/components/ParameterChart"
import DeviceYieldChart from "@/components/DeviceYieldChart"
import IVRepeatabilityChart from "@/components/IVRepeatabilityChart"
import { DropdownMenu, DropdownMenuContent, DropdownMenuItem, DropdownMenuTrigger } from "@/components/ui/dropdown-menu"
import UploadData from "@/components/UploadData"
import Analysis from "@/components/Analysis"
import StabilityDashboard from "@/components/StabilityDashboard"
import Login from "@/components/Login"
import Signup from "@/components/Signup"
import { checkAuthentication, logout as azureLogout } from "@/lib/azureAuth"

// Sample data
const processData = [
  {
    process: "Wafer Prep",
    cycleTime: "2.5h",
    outs: "Batch 12 (45)",
    wip: "Batch 13 (48)",
    yield: "98.2%",
    date: "12/23",
  },
  {
    process: "Lithography",
    cycleTime: "4.2h",
    outs: "Batch 11 (42)",
    wip: "Batch 12 (45)",
    yield: "96.8%",
    date: "12/23",
  },
  { process: "Etching", cycleTime: "3.1h", outs: "Batch 10 (48)", wip: "Batch 11 (42)", yield: "97.5%", date: "12/23" },
  {
    process: "Deposition",
    cycleTime: "5.8h",
    outs: "Batch 9 (44)",
    wip: "Batch 10 (48)",
    yield: "99.1%",
    date: "12/23",
  },
  {
    process: "Ion Implant",
    cycleTime: "2.8h",
    outs: "Batch 8 (46)",
    wip: "Batch 9 (44)",
    yield: "98.7%",
    date: "12/23",
  },
  { process: "Annealing", cycleTime: "6.2h", outs: "Batch 7 (43)", wip: "Batch 8 (46)", yield: "99.3%", date: "12/23" },
  { process: "Metrology", cycleTime: "1.5h", outs: "Batch 6 (47)", wip: "Batch 7 (43)", yield: "97.9%", date: "12/23" },
  { process: "CMP", cycleTime: "4.5h", outs: "Batch 5 (41)", wip: "Batch 6 (47)", yield: "96.4%", date: "12/23" },
  { process: "Packaging", cycleTime: "3.7h", outs: "Batch 4 (49)", wip: "Batch 5 (41)", yield: "98.8%", date: "12/23" },
  {
    process: "Final Test",
    cycleTime: "2.2h",
    outs: "Batch 3 (45)",
    wip: "Batch 4 (49)",
    yield: "99.5%",
    date: "12/23",
  },
]

const safetyIssues = [
  {
    issue: "Chemical spill in clean room",
    person: "Sarah Chen",
    action: "Containment protocol initiated",
    date: "12/23",
  },
  { issue: "Equipment overheating alert", person: "Mike Rodriguez", action: "Maintenance scheduled", date: "12/23" },
  { issue: "PPE compliance check", person: "Lisa Wang", action: "Training session planned", date: "12/22" },
]

const kudosData = [
  { name: "Alex Thompson", action: "Improved yield by 2% through process optimization", date: "12/23" },
  { name: "Maria Garcia", action: "Prevented downtime with proactive maintenance", date: "12/23" },
  { name: "David Kim", action: "Mentored new team members effectively", date: "12/22" },
  { name: "Jennifer Liu", action: "Streamlined quality control procedures", date: "12/22" },
]

const yesterdayIssues = [
  { item: "Tool 1", description: "Calibration drift detected", done: "No", who: "Tech Team A", date: "12/22" },
  { item: "Tool 2", description: "Temperature variance", done: "Yes", who: "Tech Team B", date: "12/22" },
  { item: "Tool 3", description: "Pressure sensor fault", done: "No", who: "Tech Team C", date: "12/22" },
  { item: "Tool 4", description: "Software update required", done: "Yes", who: "IT Team", date: "12/22" },
]

const todayIssues = [
  { item: "Tool 5", description: "Routine maintenance due", who: "Tech Team A", date: "12/23", done: "No" },
  { item: "Tool 6", description: "Performance monitoring", who: "Tech Team B", date: "12/23", done: "Yes" },
  { item: "Tool 7", description: "Quality check pending", who: "QA Team", date: "12/23", done: "No" },
]

// Chart data
const yieldData = [
  { time: "00:00", yield: 97.2 },
  { time: "04:00", yield: 97.8 },
  { time: "08:00", yield: 96.5 },
  { time: "12:00", yield: 98.1 },
  { time: "16:00", yield: 97.9 },
  { time: "20:00", yield: 98.3 },
]

const repeatabilityData = [
  { time: "00:00", value: 2.1 },
  { time: "04:00", value: 2.3 },
  { time: "08:00", value: 1.9 },
  { time: "12:00", value: 2.2 },
  { time: "16:00", value: 2.0 },
  { time: "20:00", value: 2.1 },
]

export default function ProductionDashboard() {
  // Authentication state
  const [isAuthenticated, setIsAuthenticated] = useState(false)
  const [isCheckingAuth, setIsCheckingAuth] = useState(true)
  const [showSignup, setShowSignup] = useState(false)

  // State for API data
  const [todayIssues, setTodayIssues] = useState([])
  const [yesterdayIssues, setYesterdayIssues] = useState([])
  const [safetyIssues, setSafetyIssues] = useState([])
  const [kudosData, setKudosData] = useState([])
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState(null)
  const [apiStatus, setApiStatus] = useState('checking')

  // Form states
  const [newSafetyIssue, setNewSafetyIssue] = useState({ issue: "", person: "", action: "" })
  const [isAddingIssue, setIsAddingIssue] = useState(false)

  const [newKudos, setNewKudos] = useState({ name: "", action: "", by_whom: "" })
  const [isAddingKudos, setIsAddingKudos] = useState(false)

  const [newTodayIssue, setNewTodayIssue] = useState({ description: "", who: "" })
  const [isAddingTodayIssue, setIsAddingTodayIssue] = useState(false)

  const [showOnlyIncomplete, setShowOnlyIncomplete] = useState(false)
  const [showOnlyIncompleteSafety, setShowOnlyIncompleteSafety] = useState(false)

  // Check authentication on mount
  useEffect(() => {
    const checkAuth = async () => {
      // This works for both local (localStorage) and Azure SWA (/.auth/me)
      const isAuth = await checkAuthentication()
      setIsAuthenticated(isAuth)
      setIsCheckingAuth(false)
      // If not authenticated, we don't need to show loading spinner
      if (!isAuth) {
        setLoading(false)
      }
    }
    checkAuth()
  }, [])

  // Load data from API
  useEffect(() => {
    if (isAuthenticated) {
      loadData()
      checkApiHealth()
    }
  }, [isAuthenticated])

  const checkApiHealth = async () => {
    try {
      await healthAPI.check()
      setApiStatus('connected')
    } catch (err) {
      setApiStatus('disconnected')
      console.error('API health check failed:', err)
    }
  }

  const loadData = async () => {
    setLoading(true)
    try {
      const [todayData, yesterdayData, safetyData, kudosEntries] = await Promise.all([
        todayAPI.getAll(),
        yesterdayAPI.getAll(),
        safetyAPI.getAll(),
        kudosAPI.getAll()
      ])
      
      // Map API data to frontend format
      const mappedTodayData = todayData.map(item => ({
        id: item.id,
        sr_no: item.id,
        item: `Issue ${item.id}`,
        description: item.description,
        who: item.who,
        date: item.date,
        _id: item._id
      }))

      const mappedYesterdayData = yesterdayData.map(item => ({
        id: item.id,
        sr_no: item.id,
        item: `Issue ${item.id}`,
        description: item.description,
        who: item.who,
        done: item.done,
        date: item.date,
        _id: item._id
      }))

      setTodayIssues(mappedTodayData)
      setYesterdayIssues(mappedYesterdayData)
      setSafetyIssues(safetyData) // Load all safety issues, filtering handled in getFilteredSafetyIssues
      setKudosData(kudosEntries)
      
      setError(null)
    } catch (err) {
      setError('Failed to load data: ' + err.message)
      console.error('Failed to load data:', err)
    } finally {
      setLoading(false)
    }
  }

  // Individual loading functions for targeted refreshes
  const loadSafetyIssues = async () => {
    try {
      const safetyData = await safetyAPI.getAll()
      setSafetyIssues(safetyData) // Load all safety issues, filtering handled in getFilteredSafetyIssues
    } catch (err) {
      console.error('Failed to load safety issues:', err)
    }
  }

  const loadKudos = async () => {
    try {
      const kudosEntries = await kudosAPI.getAll()
      setKudosData(kudosEntries)
    } catch (err) {
      console.error('Failed to load kudos:', err)
    }
  }

  const loadTodayIssues = async () => {
    try {
      const todayData = await todayAPI.getAll()
      const mappedTodayData = todayData.map(item => ({
        id: item.id,
        sr_no: item.id,
        item: `Issue ${item.id}`,
        description: item.description,
        who: item.who,
        date: item.date,
        _id: item._id
      }))
      setTodayIssues(mappedTodayData)
    } catch (err) {
      console.error('Failed to load today issues:', err)
    }
  }

  const loadYesterdayIssues = async () => {
    try {
      const yesterdayData = await yesterdayAPI.getAll()
      const mappedYesterdayData = yesterdayData.map(item => ({
        id: item.id,
        sr_no: item.id,
        item: `Issue ${item.id}`,
        description: item.description,
        who: item.who,
        done: item.done,
        date: item.date,
        _id: item._id
      }))
      setYesterdayIssues(mappedYesterdayData)
    } catch (err) {
      console.error('Failed to load yesterday issues:', err)
    }
  }

  const handleAddSafetyIssue = async () => {
    if (newSafetyIssue.issue && newSafetyIssue.person && newSafetyIssue.action) {
      try {
        await safetyAPI.create({
          issue: newSafetyIssue.issue,
          person: newSafetyIssue.person,
          action: newSafetyIssue.action
        })
        
        setNewSafetyIssue({ issue: "", person: "", action: "" })
        setIsAddingIssue(false)
        await loadSafetyIssues() // Reload only safety issues
      } catch (err) {
        setError('Failed to add safety issue: ' + err.message)
      }
    }
  }

  const handleAddKudos = async () => {
    if (newKudos.name && newKudos.action && newKudos.by_whom) {
      try {
        await kudosAPI.create({
          name: newKudos.name,
          action: newKudos.action,
          by_whom: newKudos.by_whom
        })
        
        setNewKudos({ name: "", action: "", by_whom: "" })
        setIsAddingKudos(false)
        await loadKudos() // Reload only kudos
      } catch (err) {
        setError('Failed to add kudos: ' + err.message)
      }
    }
  }

  const handleAddTodayIssue = async () => {
    if (newTodayIssue.description && newTodayIssue.who) {
      try {
        await todayAPI.create({
          description: newTodayIssue.description,
          who: newTodayIssue.who
        })
        
        setNewTodayIssue({ description: "", who: "" })
        setIsAddingTodayIssue(false)
        
        // Reload both today and yesterday issues since backend adds to both
        await Promise.all([
          loadTodayIssues(),
          loadYesterdayIssues()
        ])
        
        // Show a brief success message
        setError(null)
      } catch (err) {
        setError('Failed to add issue: ' + err.message)
      }
    }
  }

  const handleDeleteTodayIssue = async (id) => {
    try {
      await todayAPI.delete(id)
      await loadTodayIssues() // Reload only today issues
    } catch (err) {
      setError('Failed to delete issue: ' + err.message)
    }
  }

  const handleResetTodayIssues = async () => {
    if (window.confirm('Are you sure you want to reset Today\'s Issues? This will clear all standup items for a fresh start.')) {
      try {
        const result = await resetAPI.resetTodayIssues()
        await loadTodayIssues() // Reload today issues
        setError(null)
        // Show success message briefly
        alert(`✅ ${result.message || 'Today\'s Issues reset successfully!'}`)
      } catch (err) {
        setError('Failed to reset today\'s issues: ' + err.message)
      }
    }
  }

  const handleDeleteYesterdayIssue = async (id) => {
    try {
      await yesterdayAPI.delete(id)
      await loadYesterdayIssues() // Reload only yesterday issues table
    } catch (err) {
      setError('Failed to delete issue: ' + err.message)
    }
  }

  const handleToggleYesterdayStatus = async (id, currentStatus) => {
    try {
      const newStatus = currentStatus === 'Yes' ? 'No' : 'Yes'
      
      await yesterdayAPI.update(id, { done: newStatus })
      await loadYesterdayIssues() // Reload only yesterday issues table
    } catch (err) {
      setError('Failed to update status: ' + err.message)
    }
  }

  const handleToggleSafetyStatus = async (id, currentStatus) => {
    try {
      console.log('🔄 Toggling safety status:', { id, currentStatus });
      const newStatus = currentStatus === 'Yes' ? 'No' : 'Yes'
      console.log('📝 New status will be:', newStatus);
      
      const response = await safetyAPI.update(id, { done: newStatus })
      console.log('✅ Update response:', response);
      
      await loadSafetyIssues() // Reload only safety issues table
    } catch (err) {
      console.error('❌ Toggle error:', err);
      setError('Failed to update safety issue status: ' + err.message)
    }
  }

  const handleDeleteSafetyIssue = async (id) => {
    try {
      await safetyAPI.delete(id)
      await loadSafetyIssues() // Reload only safety issues table
    } catch (err) {
      setError('Failed to delete safety issue: ' + err.message)
    }
  }

  const handleDeleteKudos = async (id) => {
    try {
      await kudosAPI.delete(id)
      await loadKudos() // Reload only kudos table
    } catch (err) {
      setError('Failed to delete kudos: ' + err.message)
    }
  }

  const getFilteredYesterdayIssues = () => {
    // Show incomplete issues first, then completed ones (max 10 total)
    const incomplete = yesterdayIssues.filter((issue) => issue.done === "No")
    const completed = yesterdayIssues.filter((issue) => issue.done === "Yes")
    
    if (showOnlyIncomplete) {
      return incomplete.slice(-10) // Show last 10 incomplete only
    }
    
    // Show incomplete first, then completed (total max 10)
    const incompleteToShow = incomplete.slice(-10)
    const completedToShow = completed.slice(-(10 - incompleteToShow.length))
    
    return [...incompleteToShow, ...completedToShow]
  }

  const getFilteredTodayIssues = () => {
    // Show last 10 today's issues for consistent scrolling experience
    return todayIssues.slice(-10)
  }

  const getFilteredKudosData = () => {
    // Show last 10 kudos entries for consistent scrolling experience
    return kudosData.slice(-10)
  }

  const getFilteredSafetyIssues = () => {
    // Show incomplete safety issues first, then completed ones (max 10 total)
    const incomplete = safetyIssues.filter((issue) => (issue.done || "No") === "No")
    const completed = safetyIssues.filter((issue) => (issue.done || "No") === "Yes")
    
    if (showOnlyIncompleteSafety) {
      return incomplete.slice(-10) // Show last 10 incomplete only
    }
    
    // Show incomplete first, then completed (total max 10)
    const incompleteToShow = incomplete.slice(-10)
    const completedToShow = completed.slice(-(10 - incompleteToShow.length))
    
    return [...incompleteToShow, ...completedToShow]
  }

  if (loading) {
    return (
      <div className="min-h-screen bg-background dark flex items-center justify-center">
        <div className="text-center">
          <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-primary mx-auto mb-4"></div>
          <p className="text-muted-foreground">Loading dashboard...</p>
        </div>
      </div>
    )
  }

  const mainApp = (
    <Router>
      <Routes>
        <Route path="/" element={
          <div className="min-h-screen bg-background dark">
      {/* Navbar */}
      <nav className="border-b border-border bg-card">
        <div className="flex h-16 items-center px-6">
          <div className="flex items-center space-x-4">
            {/* Logo */}
            <img 
              src="/logo.png" 
              alt="Rayleigh Solar Tech" 
              className="h-10 w-auto object-contain"
            />
            <h1 className="text-xl font-semibold text-foreground">Production Dashboard</h1>
            {/* API Status Indicator */}
            <div className="flex items-center space-x-2">
              <div className={`h-2 w-2 rounded-full ${
                apiStatus === 'connected' ? 'bg-green-500' : 
                apiStatus === 'disconnected' ? 'bg-red-500' : 'bg-yellow-500'
              }`} />
              <span className="text-sm text-muted-foreground">
                {apiStatus === 'connected' ? 'API Connected' : 
                 apiStatus === 'disconnected' ? 'API Disconnected' : 'Checking API...'}
              </span>
            </div>
          </div>
          <div className="ml-auto flex items-center space-x-4">
            <Button variant="ghost" onClick={loadData} className="text-muted-foreground hover:text-foreground">
              Refresh Data
            </Button>
            
            <DropdownMenu>
              <DropdownMenuTrigger asChild>
                <Button variant="ghost" className="text-muted-foreground hover:text-foreground">
                  <Menu className="h-4 w-4 mr-2" />
                  Explore
                </Button>
              </DropdownMenuTrigger>

              <DropdownMenuContent align="end" className="w-48">
                <DropdownMenuItem asChild>
                  <Link to="/stability" className="cursor-pointer">
                    Stability
                  </Link>
                </DropdownMenuItem>

                <DropdownMenuItem asChild>
                  <Link to="/upload-data" className="cursor-pointer">
                    Upload Data
                  </Link>
                </DropdownMenuItem>

                <DropdownMenuItem asChild>
                  <Link to="/analysis" className="cursor-pointer">
                    Analysis
                  </Link>
                </DropdownMenuItem>
              </DropdownMenuContent>
            </DropdownMenu>
          </div>

          {/* User section with logout */}
          <div className="ml-auto flex items-center space-x-4">
            <span className="text-sm text-muted-foreground">
              {localStorage.getItem('userName') || localStorage.getItem('userEmail') || 'User'}
            </span>
            <Button
              variant="outline"
              size="sm"
              onClick={() => {
                azureLogout()
              }}
            >
              Logout
            </Button>
          </div>
        </div>
        {error && (
          <div className="bg-destructive/10 border-destructive/20 border-b px-6 py-2">
            <p className="text-destructive text-sm">{error}</p>
          </div>
        )}
      </nav>

      <div className="p-6 space-y-6">
        {/* Process Information Table */}
        <Card>
          <CardHeader>
            <CardTitle className="text-balance">Process Information</CardTitle>
          </CardHeader>
          <CardContent>
            <div className="overflow-x-auto">
              <table className="w-full">
                <thead>
                  <tr className="border-b border-border">
                    <th className="text-left py-3 px-4 font-medium text-muted-foreground">Process</th>
                    <th className="text-left py-3 px-4 font-medium text-muted-foreground">Cycle Time</th>
                    <th className="text-left py-3 px-4 font-medium text-muted-foreground">Outs</th>
                    <th className="text-left py-3 px-4 font-medium text-muted-foreground">WIP</th>
                    <th className="text-left py-3 px-4 font-medium text-muted-foreground">Process Yield</th>
                    <th className="text-left py-3 px-2 font-medium text-muted-foreground text-sm">Date</th>
                  </tr>
                </thead>
                <tbody>
                  {processData.map((row, index) => (
                    <tr key={index} className={index % 2 === 0 ? "bg-muted/50" : ""}>
                      <td className="py-3 px-4 font-medium">{row.process}</td>
                      <td className="py-3 px-4">{row.cycleTime}</td>
                      <td className="py-3 px-4">{row.outs}</td>
                      <td className="py-3 px-4">{row.wip}</td>
                      <td className="py-3 px-4">
                        <Badge variant="secondary" className="bg-primary/10 text-primary">
                          {row.yield}
                        </Badge>
                      </td>
                      <td className="py-3 px-2 text-sm text-muted-foreground">{row.date}</td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
          </CardContent>
        </Card>

        <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
          {/* Near Misses / Safety */}
          <Card>
            <CardHeader>
              <div className="flex flex-row items-center justify-between">
                <CardTitle className="text-balance">Near Misses / Safety</CardTitle>
                <Button size="sm" onClick={() => setIsAddingIssue(true)} className="bg-primary hover:bg-primary/90">
                  <Plus className="h-4 w-4 mr-2" />
                  Add Issue
                </Button>
              </div>
              <div className="flex items-center space-x-2 mt-2">
                <Checkbox id="incomplete-safety-filter" checked={showOnlyIncompleteSafety} onCheckedChange={setShowOnlyIncompleteSafety} />
                <label htmlFor="incomplete-safety-filter" className="text-xs text-muted-foreground">
                  Show only incomplete issues
                </label>
              </div>
            </CardHeader>
            <CardContent>
                                <div className="overflow-auto max-h-96 border border-gray-200 rounded">
                  <table className="w-full">
                    <thead className="bg-gray-800 sticky top-0 z-10">
                      <tr className="border-b border-border">
                        <th className="text-left py-3 px-3 font-medium text-white text-sm bg-gray-800">Issue #</th>
                        <th className="text-left py-3 px-3 font-medium text-white text-sm bg-gray-800">Issue Description</th>
                        <th className="text-left py-3 px-3 font-medium text-white text-sm bg-gray-800">Who Pointed Out</th>
                        <th className="text-left py-3 px-3 font-medium text-white text-sm bg-gray-800">Action Required</th>
                        <th className="text-left py-3 px-3 font-medium text-white text-sm bg-gray-800">Done?</th>
                        <th className="text-left py-3 px-2 font-medium text-white text-sm bg-gray-800">Date</th>
                        <th className="text-left py-3 px-2 font-medium text-white text-sm bg-gray-800">Actions</th>
                      </tr>
                    </thead>
                  <tbody>
                    {getFilteredSafetyIssues().map((row, index) => (
                      <tr 
                        key={row._id || index} 
                        className={`${index % 2 === 0 ? "bg-muted/50" : ""} ${(row.done || "No") === "No" ? "bg-destructive/10" : ""}`}
                      >
                        <td className="py-2 px-3 text-sm font-medium">#{row.id || index + 1}</td>
                        <td className="py-2 px-3 text-sm">{row.issue}</td>
                        <td className="py-2 px-3 text-sm">{row.person}</td>
                        <td className="py-2 px-3 text-sm">{row.action}</td>
                        <td className="py-2 px-3 text-sm">
                          <Button
                            variant="ghost"
                            size="sm"
                            onClick={() => handleToggleSafetyStatus(row._id, row.done || "No")}
                            className="p-0 h-auto"
                          >
                            <Badge
                              variant={(row.done || "No") === "Yes" ? "secondary" : "destructive"}
                              className={`cursor-pointer ${(row.done || "No") === "Yes" ? "bg-primary/10 text-primary" : ""}`}
                            >
                              {row.done || "No"}
                            </Badge>
                          </Button>
                        </td>
                        <td className="py-2 px-2 text-sm text-muted-foreground">{row.date}</td>
                        <td className="py-2 px-2">
                          <Button
                            variant="ghost"
                            size="sm"
                            onClick={() => handleDeleteSafetyIssue(row._id)}
                            className="h-8 w-8 p-0 text-destructive hover:text-destructive"
                          >
                            <Trash2 className="h-4 w-4" />
                          </Button>
                        </td>
                      </tr>
                    ))}
                    {isAddingIssue && (
                      <tr className="bg-accent/50">
                        <td className="py-2 px-3 text-sm text-muted-foreground">Auto</td>
                        <td className="py-2 px-3">
                          <Input
                            placeholder="What was the issue/near miss?"
                            value={newSafetyIssue.issue}
                            onChange={(e) => setNewSafetyIssue({ ...newSafetyIssue, issue: e.target.value })}
                            className="h-8"
                          />
                        </td>
                        <td className="py-2 px-3">
                          <Input
                            placeholder="Who pointed it out?"
                            value={newSafetyIssue.person}
                            onChange={(e) => setNewSafetyIssue({ ...newSafetyIssue, person: e.target.value })}
                            className="h-8"
                          />
                        </td>
                        <td className="py-2 px-3">
                          <Input
                            placeholder="What action is required?"
                            value={newSafetyIssue.action}
                            onChange={(e) => setNewSafetyIssue({ ...newSafetyIssue, action: e.target.value })}
                            className="h-8"
                          />
                        </td>
                        <td className="py-2 px-3">
                          <Badge variant="destructive" className="cursor-default">No</Badge>
                        </td>
                        <td className="py-2 px-2 text-sm text-muted-foreground">Today</td>
                        <td className="py-2 px-2">
                          <div className="flex gap-1">
                            <Button size="sm" onClick={handleAddSafetyIssue} className="h-8 px-3">
                              Save
                            </Button>
                            <Button 
                              size="sm" 
                              variant="outline" 
                              onClick={() => {
                                setIsAddingIssue(false);
                                setNewSafetyIssue({ issue: "", person: "", action: "" });
                              }} 
                              className="h-8 px-2"
                            >
                              Cancel
                            </Button>
                          </div>
                        </td>
                      </tr>
                    )}
                  </tbody>
                </table>
              </div>
            </CardContent>
          </Card>

          {/* Kudos */}
          <Card>
            <CardHeader className="flex flex-row items-center justify-between">
              <CardTitle className="text-balance">Kudos</CardTitle>
              <Button size="sm" onClick={() => setIsAddingKudos(true)} className="bg-primary hover:bg-primary/90">
                <Plus className="h-4 w-4 mr-2" />
                Add Kudos
              </Button>
            </CardHeader>
            <CardContent>
              <div className="overflow-auto max-h-96 border border-gray-200 rounded">
                <table className="w-full">
                  <thead className="bg-gray-800 sticky top-0 z-10">
                    <tr className="border-b border-border">
                      <th className="text-left py-3 px-3 font-medium text-white text-sm bg-gray-800">Name</th>
                      <th className="text-left py-3 px-3 font-medium text-white text-sm bg-gray-800">Action</th>
                      <th className="text-left py-3 px-3 font-medium text-white text-sm bg-gray-800">By Whom</th>
                      <th className="text-left py-3 px-2 font-medium text-white text-sm bg-gray-800">Date</th>
                      <th className="text-left py-3 px-2 font-medium text-white text-sm bg-gray-800">Actions</th>
                    </tr>
                  </thead>
                  <tbody>
                    {getFilteredKudosData().map((row, index) => (
                      <tr key={row._id || index} className={index % 2 === 0 ? "bg-muted/50" : ""}>
                        <td className="py-2 px-3 text-sm font-medium">{row.name}</td>
                        <td className="py-2 px-3 text-sm">{row.action}</td>
                        <td className="py-2 px-3 text-sm">{row.by_whom || ""}</td>
                        <td className="py-2 px-2 text-sm text-muted-foreground">{row.date}</td>
                        <td className="py-2 px-2">
                          <Button
                            variant="ghost"
                            size="sm"
                            onClick={() => handleDeleteKudos(row._id)}
                            className="h-8 w-8 p-0 text-destructive hover:text-destructive"
                          >
                            <Trash2 className="h-4 w-4" />
                          </Button>
                        </td>
                      </tr>
                    ))}
                    {isAddingKudos && (
                      <tr className="bg-accent/50">
                        <td className="py-2 px-3">
                          <Input
                            placeholder="Person name"
                            value={newKudos.name}
                            onChange={(e) => setNewKudos({ ...newKudos, name: e.target.value })}
                            className="h-8"
                          />
                        </td>
                        <td className="py-2 px-3">
                          <Input
                            placeholder="Action description"
                            value={newKudos.action}
                            onChange={(e) => setNewKudos({ ...newKudos, action: e.target.value })}
                            className="h-8"
                          />
                        </td>
                        <td className="py-2 px-3">
                          <Input
                            placeholder="Given by whom"
                            value={newKudos.by_whom}
                            onChange={(e) => setNewKudos({ ...newKudos, by_whom: e.target.value })}
                            className="h-8"
                          />
                        </td>
                        <td className="py-2 px-2 text-sm text-muted-foreground">Today</td>
                        <td className="py-2 px-2">
                          <div className="flex gap-1">
                            <Button size="sm" onClick={handleAddKudos} className="h-8 px-3">
                              Save
                            </Button>
                            <Button 
                              size="sm" 
                              variant="outline" 
                              onClick={() => {
                                setIsAddingKudos(false);
                                setNewKudos({ name: "", action: "", by_whom: "" });
                              }} 
                              className="h-8 px-2"
                            >
                              Cancel
                            </Button>
                          </div>
                        </td>
                      </tr>
                    )}
                  </tbody>
                </table>
              </div>
            </CardContent>
          </Card>
        </div>

        {/* Top Issues */}
        <Card>
          <CardHeader className="flex flex-row items-center justify-between">
            <div>
              <CardTitle className="text-balance">Top Issues</CardTitle>
              <div className="text-sm text-muted-foreground mt-1">
                📋 <strong>Workflow:</strong> Today's issues → Appear here as incomplete → Mark complete when done
              </div>
            </div>
            <div className="flex items-center gap-4">
              <Button size="sm" onClick={() => setIsAddingTodayIssue(true)} className="bg-primary hover:bg-primary/90">
                <Plus className="h-4 w-4 mr-2" />
                Add Today Issue
              </Button>
              <div className="text-xs text-muted-foreground">
                Items added here automatically appear in "Top Issues" section as incomplete
              </div>
            </div>
          </CardHeader>
          <CardContent>
            <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
              {/* Yesterday's Issues */}
              <div>
                <div className="flex items-center justify-between mb-3">
                  <h3 className="font-medium text-muted-foreground">Top Issues (Track Completion)</h3>
                  <div className="flex items-center space-x-2">
                    <Checkbox id="incomplete-filter" checked={showOnlyIncomplete} onCheckedChange={setShowOnlyIncomplete} />
                    <label htmlFor="incomplete-filter" className="text-xs text-muted-foreground">
                      Show only incomplete
                    </label>
                  </div>
                </div>
                <div className="text-xs text-muted-foreground mb-2">
                  Issues from "Today's Top Issues" appear here as incomplete. Mark them complete when done.
                </div>
                <div className="overflow-auto max-h-96 border border-gray-200 rounded">
                  <table className="w-full">
                    <thead className="bg-gray-800 sticky top-0 z-10">
                      <tr className="border-b border-border">
                        <th className="text-left py-3 px-3 font-medium text-white text-sm bg-gray-800">Issue #</th>
                        <th className="text-left py-3 px-3 font-medium text-white text-sm bg-gray-800">Description</th>
                        <th className="text-left py-3 px-3 font-medium text-white text-sm bg-gray-800">Done?</th>
                        <th className="text-left py-3 px-3 font-medium text-white text-sm bg-gray-800">Who</th>
                        <th className="text-left py-3 px-2 font-medium text-white text-sm bg-gray-800">Date</th>
                        <th className="text-left py-3 px-2 font-medium text-white text-sm bg-gray-800">Actions</th>
                      </tr>
                    </thead>
                    <tbody>
                      {getFilteredYesterdayIssues().map((row, index) => (
                        <tr
                          key={row.sr_no}
                          className={`${index % 2 === 0 ? "bg-muted/50" : ""} ${row.done === "No" ? "bg-destructive/10" : ""}`}
                        >
                          <td className="py-2 px-3 text-sm font-medium">#{row.sr_no}</td>
                          <td className="py-2 px-3 text-sm">{row.description}</td>
                          <td className="py-2 px-3 text-sm">
                            <Button
                              variant="ghost"
                              size="sm"
                              onClick={() => handleToggleYesterdayStatus(row.sr_no, row.done)}
                              className="p-0 h-auto"
                            >
                              <Badge
                                variant={row.done === "Yes" ? "secondary" : "destructive"}
                                className={`cursor-pointer ${row.done === "Yes" ? "bg-primary/10 text-primary" : ""}`}
                              >
                                {row.done}
                              </Badge>
                            </Button>
                          </td>
                          <td className="py-2 px-3 text-sm">{row.who}</td>
                          <td className="py-2 px-2 text-sm text-muted-foreground">{row.date}</td>
                          <td className="py-2 px-2">
                            <Button
                              variant="ghost"
                              size="sm"
                              onClick={() => handleDeleteYesterdayIssue(row.sr_no)}
                              className="h-8 w-8 p-0 text-destructive hover:text-destructive"
                            >
                              <Trash2 className="h-4 w-4" />
                            </Button>
                          </td>
                        </tr>
                      ))}
                    </tbody>
                  </table>
                </div>
              </div>

              {/* Today's Issues */}
              <div>
                <div className="flex items-center justify-between mb-3">
                  <h3 className="font-medium text-muted-foreground">Today's Top Issues (Standup Items)</h3>
                  <Button 
                    variant="outline" 
                    size="sm" 
                    onClick={handleResetTodayIssues}
                    className="text-xs bg-red-50 hover:bg-red-100 text-red-700 border-red-200"
                  >
                    🔄 Reset Today
                  </Button>
                </div>
                <div className="text-xs text-muted-foreground mb-2">
                  Add today's issues for standup. They will automatically appear in "Top Issues" section for tracking.
                </div>
                <div className="overflow-auto max-h-96 border border-gray-200 rounded">
                  <table className="w-full">
                    <thead className="bg-gray-800 sticky top-0 z-10">
                      <tr className="border-b border-border">
                        <th className="text-left py-3 px-3 font-medium text-white text-sm bg-gray-800">Issue #</th>
                        <th className="text-left py-3 px-3 font-medium text-white text-sm bg-gray-800">Description</th>
                        <th className="text-left py-3 px-3 font-medium text-white text-sm bg-gray-800">Who</th>
                        <th className="text-left py-3 px-2 font-medium text-white text-sm bg-gray-800">Date</th>
                        <th className="text-left py-3 px-2 font-medium text-white text-sm bg-gray-800">Actions</th>
                      </tr>
                    </thead>
                    <tbody>
                      {getFilteredTodayIssues().map((row, index) => (
                        <tr
                          key={row.sr_no}
                          className={`${index % 2 === 0 ? "bg-muted/50" : ""} ${row.done === "No" ? "bg-destructive/10" : ""}`}
                        >
                          <td className="py-2 px-3 text-sm font-medium">#{row.sr_no}</td>
                          <td className="py-2 px-3 text-sm">{row.description}</td>
                          <td className="py-2 px-3 text-sm">{row.who}</td>
                          <td className="py-2 px-2 text-sm text-muted-foreground">{row.date}</td>
                          <td className="py-2 px-2">
                            <Button
                              variant="ghost"
                              size="sm"
                              onClick={() => handleDeleteTodayIssue(row.sr_no)}
                              className="h-8 w-8 p-0 text-destructive hover:text-destructive"
                            >
                              <Trash2 className="h-4 w-4" />
                            </Button>
                          </td>
                        </tr>
                      ))}
                      {isAddingTodayIssue && (
                        <tr className="bg-accent/50">
                          <td className="py-2 px-3 text-sm text-muted-foreground">Auto</td>
                          <td className="py-2 px-3">
                            <Input
                              placeholder="Issue description"
                              value={newTodayIssue.description}
                              onChange={(e) => setNewTodayIssue({ ...newTodayIssue, description: e.target.value })}
                              className="h-8"
                            />
                          </td>
                          <td className="py-2 px-3">
                            <Input
                              placeholder="Assigned to"
                              value={newTodayIssue.who}
                              onChange={(e) => setNewTodayIssue({ ...newTodayIssue, who: e.target.value })}
                              className="h-8"
                            />
                          </td>
                          <td className="py-2 px-2 text-sm text-muted-foreground">Today</td>
                          <td className="py-2 px-2">
                            <div className="flex gap-1">
                              <Input
                                placeholder="Whom"
                                value={newTodayIssue.whom}
                                onChange={(e) => setNewTodayIssue({ ...newTodayIssue, whom: e.target.value })}
                                className="h-8 w-20"
                              />
                              <Button size="sm" onClick={handleAddTodayIssue} className="h-8">
                                Save
                              </Button>
                            </div>
                          </td>
                        </tr>
                      )}
                    </tbody>
                  </table>
                </div>
              </div>
            </div>
          </CardContent>
        </Card>

        {/* Charts - Separate Analysis Sections */}
        <div className="space-y-8">
          {/* 1. Parameter Analysis (FF, PCE, etc.) */}
          <div className="w-full">
            <ParameterChart />
          </div>

          {/* 2. Device Yield Analysis */}
          <DeviceYieldChart />

          {/* 3. IV Repeatability Analysis */}
          <IVRepeatabilityChart />
        </div>
      </div>
    </div>
        } />
        <Route path="/upload-data" element={<UploadData />} />
        <Route path="/stability" element={<StabilityDashboard />} />
        <Route path="/analysis" element={<Analysis />} />
      </Routes>
    </Router>
  )

  // Show login page if not authenticated
  if (isCheckingAuth) {
    return (
      <div className="min-h-screen flex items-center justify-center">
        <div className="text-center">
          <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-gray-900 mx-auto"></div>
          <p className="mt-4 text-gray-600">Loading...</p>
        </div>
      </div>
    )
  }

  if (!isAuthenticated) {
    if (showSignup) {
      return (
        <Signup 
          onSignupSuccess={() => {
            setShowSignup(false);
          }}
          onBackToLogin={() => setShowSignup(false)}
        />
      );
    }
    return <Login onLogin={setIsAuthenticated} onSignupClick={() => setShowSignup(true)} />
  }

  // Show main app if authenticated
  return mainApp
}