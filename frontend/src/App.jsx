// import { useState } from 'react'
// import reactLogo from './assets/react.svg'
// import viteLogo from '/vite.svg'
// import './App.css'

// function App() {
//   const [count, setCount] = useState(0)

//   return (
//     <>
//       <div>
//         <a href="https://vite.dev" target="_blank">
//           <img src={viteLogo} className="logo" alt="Vite logo" />
//         </a>
//         <a href="https://react.dev" target="_blank">
//           <img src={reactLogo} className="logo react" alt="React logo" />
//         </a>
//       </div>
//       <h1>Vite + React</h1>
//       <div className="card">
//         <button onClick={() => setCount((count) => count + 1)}>
//           count is {count}
//         </button>
//         <p>
//           Edit <code>src/App.jsx</code> and save to test HMR
//         </p>
//       </div>
//       <p className="read-the-docs">
//         Click on the Vite and React logos to learn more
//       </p>
//     </>
//   )
// }

// export default App

"use client"

import { useState, useEffect } from "react"
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card"
import { Button } from "@/components/ui/button"
import { Input } from "@/components/ui/input"
import { Badge } from "@/components/ui/badge"
import { Checkbox } from "@/components/ui/checkbox"
import { BarChart, Bar, LineChart, Line, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer } from "recharts"
import { Plus, Menu } from "lucide-react"
import { todayAPI, yesterdayAPI } from "./services/api"

// Sample data
const processData = [
  {
    process: "Wafer Prep",
    cycleTime: "2.5h",
    outs: "Batch 12 (45)",
    wip: "Batch 13 (38)",
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

// Data will be loaded from API
const [yesterdayIssues, setYesterdayIssues] = useState([])
const [todayIssues, setTodayIssues] = useState([])
const [loading, setLoading] = useState(true)
const [error, setError] = useState("")

// Chart data
const pceData = [
  { batch: "B1", pce: 85 },
  { batch: "B2", pce: 88 },
  { batch: "B3", pce: 92 },
  { batch: "B4", pce: 87 },
  { batch: "B5", pce: 94 },
  { batch: "B6", pce: 91 },
  { batch: "B7", pce: 89 },
  { batch: "B8", pce: 96 },
]

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
  const [newSafetyIssue, setNewSafetyIssue] = useState({ issue: "", person: "", action: "" })
  const [isAddingIssue, setIsAddingIssue] = useState(false)

  const [newKudos, setNewKudos] = useState({ name: "", action: "" })
  const [isAddingKudos, setIsAddingKudos] = useState(false)

  const [newTodayIssue, setNewTodayIssue] = useState({ description: "", resolved: "No", who: "", whom: "" })
  const [isAddingTodayIssue, setIsAddingTodayIssue] = useState(false)
  const [newYesterdayIssue, setNewYesterdayIssue] = useState({ description: "", resolved: "No", who: "", whom: "", resolved_status: "Pending" })
  const [isAddingYesterdayIssue, setIsAddingYesterdayIssue] = useState(false)

  const [showOnlyIncomplete, setShowOnlyIncomplete] = useState(false)

  // Load data from API on component mount
  useEffect(() => {
    loadData()
  }, [])

  const loadData = async () => {
    try {
      setLoading(true)
      setError("")
      const [todayData, yesterdayData] = await Promise.all([
        todayAPI.getAll(),
        yesterdayAPI.getAll()
      ])
      setTodayIssues(todayData)
      setYesterdayIssues(yesterdayData)
    } catch (err) {
      setError("Failed to load data: " + (err.response?.data?.error || err.message))
      console.error("Error loading data:", err)
    } finally {
      setLoading(false)
    }
  }

  const handleAddSafetyIssue = () => {
    if (newSafetyIssue.issue && newSafetyIssue.person && newSafetyIssue.action) {
      // In a real app, this would update the database
      setNewSafetyIssue({ issue: "", person: "", action: "" })
      setIsAddingIssue(false)
    }
  }

  const handleAddKudos = () => {
    if (newKudos.name && newKudos.action) {
      setNewKudos({ name: "", action: "" })
      setIsAddingKudos(false)
    }
  }

  const handleAddTodayIssue = async () => {
    if (!newTodayIssue.description || !newTodayIssue.who || !newTodayIssue.whom) {
      setError("Please fill in all required fields")
      return
    }

    try {
      await todayAPI.create(newTodayIssue)
      setNewTodayIssue({ description: "", resolved: "No", who: "", whom: "" })
      setIsAddingTodayIssue(false)
      await loadData()
      setError("")
    } catch (err) {
      setError("Failed to add today's issue: " + (err.response?.data?.error || err.message))
    }
  }

  const handleAddYesterdayIssue = async () => {
    if (!newYesterdayIssue.description || !newYesterdayIssue.who || !newYesterdayIssue.whom) {
      setError("Please fill in all required fields")
      return
    }

    try {
      await yesterdayAPI.create(newYesterdayIssue)
      setNewYesterdayIssue({ description: "", resolved: "No", who: "", whom: "", resolved_status: "Pending" })
      setIsAddingYesterdayIssue(false)
      await loadData()
      setError("")
    } catch (err) {
      setError("Failed to add yesterday's issue: " + (err.response?.data?.error || err.message))
    }
  }

  const getFilteredYesterdayIssues = () => {
    return showOnlyIncomplete ? yesterdayIssues.filter((issue) => issue.resolved === "No") : yesterdayIssues
  }

  const getFilteredTodayIssues = () => {
    return showOnlyIncomplete ? todayIssues.filter((issue) => issue.resolved === "No") : todayIssues
  }

  return (
    <div className="min-h-screen bg-background dark">
      {/* Navbar */}
      <nav className="border-b border-border bg-card">
        <div className="flex h-16 items-center px-6">
          <div className="flex items-center space-x-4">
            <h1 className="text-xl font-semibold text-foreground">Production Dashboard</h1>
          </div>
          <div className="ml-auto flex items-center space-x-4">
            <Button variant="ghost" className="text-muted-foreground hover:text-foreground">
              <Menu className="h-4 w-4 mr-2" />
              Explore
            </Button>
          </div>
        </div>
      </nav>

      {/* Error Display */}
      {error && (
        <div className="bg-destructive/10 text-destructive p-4 m-6 rounded-lg">
          {error}
        </div>
      )}

      {/* Loading State */}
      {loading && (
        <div className="flex justify-center items-center p-8">
          <div className="text-muted-foreground">Loading data...</div>
        </div>
      )}

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
            <CardHeader className="flex flex-row items-center justify-between">
              <CardTitle className="text-balance">Near Misses / Safety</CardTitle>
              <Button size="sm" onClick={() => setIsAddingIssue(true)} className="bg-primary hover:bg-primary/90">
                <Plus className="h-4 w-4 mr-2" />
                Add Issue
              </Button>
            </CardHeader>
            <CardContent>
              <div className="overflow-x-auto">
                <table className="w-full">
                  <thead>
                    <tr className="border-b border-border">
                      <th className="text-left py-2 px-3 font-medium text-muted-foreground text-sm">Issues</th>
                      <th className="text-left py-2 px-3 font-medium text-muted-foreground text-sm">
                        Person In Charge
                      </th>
                      <th className="text-left py-2 px-3 font-medium text-muted-foreground text-sm">Action</th>
                      <th className="text-left py-2 px-2 font-medium text-muted-foreground text-sm">Date</th>
                    </tr>
                  </thead>
                  <tbody>
                    {safetyIssues.map((row, index) => (
                      <tr key={index} className={index % 2 === 0 ? "bg-muted/50" : ""}>
                        <td className="py-2 px-3 text-sm">{row.issue}</td>
                        <td className="py-2 px-3 text-sm">{row.person}</td>
                        <td className="py-2 px-3 text-sm">{row.action}</td>
                        <td className="py-2 px-2 text-sm text-muted-foreground">{row.date}</td>
                      </tr>
                    ))}
                    {isAddingIssue && (
                      <tr className="bg-accent/50">
                        <td className="py-2 px-3">
                          <Input
                            placeholder="Issue description"
                            value={newSafetyIssue.issue}
                            onChange={(e) => setNewSafetyIssue({ ...newSafetyIssue, issue: e.target.value })}
                            className="h-8"
                          />
                        </td>
                        <td className="py-2 px-3">
                          <Input
                            placeholder="Person name"
                            value={newSafetyIssue.person}
                            onChange={(e) => setNewSafetyIssue({ ...newSafetyIssue, person: e.target.value })}
                            className="h-8"
                          />
                        </td>
                        <td className="py-2 px-3">
                          <div className="flex gap-2">
                            <Input
                              placeholder="Action taken"
                              value={newSafetyIssue.action}
                              onChange={(e) => setNewSafetyIssue({ ...newSafetyIssue, action: e.target.value })}
                              className="h-8"
                            />
                            <Button size="sm" onClick={handleAddSafetyIssue} className="h-8">
                              Save
                            </Button>
                          </div>
                        </td>
                        <td className="py-2 px-2 text-sm text-muted-foreground">12/23</td>
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
              <div className="overflow-x-auto">
                <table className="w-full">
                  <thead>
                    <tr className="border-b border-border">
                      <th className="text-left py-2 px-3 font-medium text-muted-foreground text-sm">Name</th>
                      <th className="text-left py-2 px-3 font-medium text-muted-foreground text-sm">Action</th>
                      <th className="text-left py-2 px-2 font-medium text-muted-foreground text-sm">Date</th>
                    </tr>
                  </thead>
                  <tbody>
                    {kudosData.map((row, index) => (
                      <tr key={index} className={index % 2 === 0 ? "bg-muted/50" : ""}>
                        <td className="py-2 px-3 text-sm font-medium">{row.name}</td>
                        <td className="py-2 px-3 text-sm">{row.action}</td>
                        <td className="py-2 px-2 text-sm text-muted-foreground">{row.date}</td>
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
                          <div className="flex gap-2">
                            <Input
                              placeholder="Action description"
                              value={newKudos.action}
                              onChange={(e) => setNewKudos({ ...newKudos, action: e.target.value })}
                              className="h-8"
                            />
                            <Button size="sm" onClick={handleAddKudos} className="h-8">
                              Save
                            </Button>
                          </div>
                        </td>
                        <td className="py-2 px-2 text-sm text-muted-foreground">12/23</td>
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
            <CardTitle className="text-balance">Top Issues</CardTitle>
            <div className="flex items-center gap-4">
              <div className="flex items-center space-x-2">
                <Checkbox id="incomplete-filter" checked={showOnlyIncomplete} onCheckedChange={setShowOnlyIncomplete} />
                <label htmlFor="incomplete-filter" className="text-sm text-muted-foreground">
                  Show only incomplete
                </label>
              </div>
              <div className="flex gap-2">
                <Button size="sm" onClick={() => setIsAddingYesterdayIssue(true)} className="bg-secondary hover:bg-secondary/90">
                  <Plus className="h-4 w-4 mr-2" />
                  Add Yesterday
                </Button>
                <Button size="sm" onClick={() => setIsAddingTodayIssue(true)} className="bg-primary hover:bg-primary/90">
                  <Plus className="h-4 w-4 mr-2" />
                  Add Today
                </Button>
              </div>
            </div>
          </CardHeader>
          <CardContent>
            <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
              {/* Yesterday's Issues */}
              <div>
                <h3 className="font-medium mb-3 text-muted-foreground">Top Issues from Yesterday</h3>
                <div className="overflow-x-auto">
                  <table className="w-full">
                    <thead>
                      <tr className="border-b border-border">
                        <th className="text-left py-2 px-3 font-medium text-muted-foreground text-sm">Description</th>
                        <th className="text-left py-2 px-3 font-medium text-muted-foreground text-sm">Resolved</th>
                        <th className="text-left py-2 px-3 font-medium text-muted-foreground text-sm">Who</th>
                        <th className="text-left py-2 px-3 font-medium text-muted-foreground text-sm">Whom</th>
                        <th className="text-left py-2 px-2 font-medium text-muted-foreground text-sm">Status</th>
                      </tr>
                    </thead>
                    <tbody>
                      {getFilteredYesterdayIssues().map((row, index) => (
                        <tr
                          key={row._id || index}
                          className={`${index % 2 === 0 ? "bg-muted/50" : ""} ${row.resolved === "No" ? "bg-destructive/10" : ""}`}
                        >
                          <td className="py-2 px-3 text-sm">{row.description}</td>
                          <td className="py-2 px-3 text-sm">
                            <Badge
                              variant={row.resolved === "Yes" ? "secondary" : "destructive"}
                              className={row.resolved === "Yes" ? "bg-primary/10 text-primary" : ""}
                            >
                              {row.resolved}
                            </Badge>
                          </td>
                          <td className="py-2 px-3 text-sm">{row.who}</td>
                          <td className="py-2 px-3 text-sm">{row.whom}</td>
                          <td className="py-2 px-2 text-sm text-muted-foreground">
                            <Badge variant="outline" className="text-xs">
                              {row.resolved_status}
                            </Badge>
                          </td>
                        </tr>
                      ))}
                      {isAddingYesterdayIssue && (
                        <tr className="bg-accent/50">
                          <td className="py-2 px-3">
                            <Input
                              placeholder="Description"
                              value={newYesterdayIssue.description}
                              onChange={(e) => setNewYesterdayIssue({ ...newYesterdayIssue, description: e.target.value })}
                              className="h-8"
                            />
                          </td>
                          <td className="py-2 px-3">
                            <select
                              value={newYesterdayIssue.resolved}
                              onChange={(e) => setNewYesterdayIssue({ ...newYesterdayIssue, resolved: e.target.value })}
                              className="h-8 px-3 border rounded-md bg-background"
                            >
                              <option value="No">No</option>
                              <option value="Yes">Yes</option>
                            </select>
                          </td>
                          <td className="py-2 px-3">
                            <Input
                              placeholder="Who (assigned by)"
                              value={newYesterdayIssue.who}
                              onChange={(e) => setNewYesterdayIssue({ ...newYesterdayIssue, who: e.target.value })}
                              className="h-8"
                            />
                          </td>
                          <td className="py-2 px-3">
                            <Input
                              placeholder="Whom (assigned to)"
                              value={newYesterdayIssue.whom}
                              onChange={(e) => setNewYesterdayIssue({ ...newYesterdayIssue, whom: e.target.value })}
                              className="h-8"
                            />
                          </td>
                          <td className="py-2 px-2">
                            <div className="flex gap-2">
                              <select
                                value={newYesterdayIssue.resolved_status}
                                onChange={(e) => setNewYesterdayIssue({ ...newYesterdayIssue, resolved_status: e.target.value })}
                                className="h-8 px-2 border rounded-md bg-background text-xs"
                              >
                                <option value="Pending">Pending</option>
                                <option value="In Progress">In Progress</option>
                                <option value="Completed">Completed</option>
                              </select>
                              <Button size="sm" onClick={handleAddYesterdayIssue} className="h-8">
                                Save
                              </Button>
                              <Button 
                                size="sm" 
                                variant="outline" 
                                onClick={() => setIsAddingYesterdayIssue(false)} 
                                className="h-8"
                              >
                                Cancel
                              </Button>
                            </div>
                          </td>
                        </tr>
                      )}}
                    </tbody>
                  </table>
                </div>
              </div>

              {/* Today's Issues */}
              <div>
                <h3 className="font-medium mb-3 text-muted-foreground">Top Issues from Today</h3>
                <div className="overflow-x-auto">
                  <table className="w-full">
                    <thead>
                      <tr className="border-b border-border">
                        <th className="text-left py-2 px-3 font-medium text-muted-foreground text-sm">Description</th>
                        <th className="text-left py-2 px-3 font-medium text-muted-foreground text-sm">Resolved</th>
                        <th className="text-left py-2 px-3 font-medium text-muted-foreground text-sm">Who</th>
                        <th className="text-left py-2 px-2 font-medium text-muted-foreground text-sm">Whom</th>
                      </tr>
                    </thead>
                    <tbody>
                      {getFilteredTodayIssues().map((row, index) => (
                        <tr
                          key={row._id || index}
                          className={`${index % 2 === 0 ? "bg-muted/50" : ""} ${row.resolved === "No" ? "bg-destructive/10" : ""}`}
                        >
                          <td className="py-2 px-3 text-sm">{row.description}</td>
                          <td className="py-2 px-3 text-sm">
                            <Badge
                              variant={row.resolved === "Yes" ? "secondary" : "destructive"}
                              className={row.resolved === "Yes" ? "bg-primary/10 text-primary" : ""}
                            >
                              {row.resolved}
                            </Badge>
                          </td>
                          <td className="py-2 px-3 text-sm">{row.who}</td>
                          <td className="py-2 px-2 text-sm text-muted-foreground">{row.whom}</td>
                        </tr>
                      ))}
                      {isAddingTodayIssue && (
                        <tr className="bg-accent/50">
                          <td className="py-2 px-3">
                            <Input
                              placeholder="Description"
                              value={newTodayIssue.description}
                              onChange={(e) => setNewTodayIssue({ ...newTodayIssue, description: e.target.value })}
                              className="h-8"
                            />
                          </td>
                          <td className="py-2 px-3">
                            <select
                              value={newTodayIssue.resolved}
                              onChange={(e) => setNewTodayIssue({ ...newTodayIssue, resolved: e.target.value })}
                              className="h-8 px-3 border rounded-md bg-background"
                            >
                              <option value="No">No</option>
                              <option value="Yes">Yes</option>
                            </select>
                          </td>
                          <td className="py-2 px-3">
                            <Input
                              placeholder="Who (assigned by)"
                              value={newTodayIssue.who}
                              onChange={(e) => setNewTodayIssue({ ...newTodayIssue, who: e.target.value })}
                              className="h-8"
                            />
                          </td>
                          <td className="py-2 px-2">
                            <div className="flex gap-2">
                              <Input
                                placeholder="Whom (assigned to)"
                                value={newTodayIssue.whom}
                                onChange={(e) => setNewTodayIssue({ ...newTodayIssue, whom: e.target.value })}
                                className="h-8"
                              />
                              <Button size="sm" onClick={handleAddTodayIssue} className="h-8">
                                Save
                              </Button>
                              <Button 
                                size="sm" 
                                variant="outline" 
                                onClick={() => setIsAddingTodayIssue(false)} 
                                className="h-8"
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
              </div>
            </div>
          </CardContent>
        </Card>

        {/* Charts */}
        <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
          {/* PCE vs Batch */}
          <Card>
            <CardHeader>
              <CardTitle className="text-balance">PCE vs Batch</CardTitle>
            </CardHeader>
            <CardContent>
              <ResponsiveContainer width="100%" height={200}>
                <BarChart data={pceData}>
                  <CartesianGrid strokeDasharray="3 3" stroke="#3b82f6" opacity={0.2} />
                  <XAxis dataKey="batch" stroke="#94a3b8" fontSize={12} tickLine={false} axisLine={false} />
                  <YAxis stroke="#94a3b8" fontSize={12} tickLine={false} axisLine={false} />
                  <Tooltip
                    contentStyle={{
                      backgroundColor: "#1e293b",
                      border: "1px solid #3b82f6",
                      borderRadius: "8px",
                      color: "#f1f5f9",
                    }}
                  />
                  <Bar dataKey="pce" fill="#3b82f6" radius={[4, 4, 0, 0]} stroke="#1d4ed8" strokeWidth={1} />
                </BarChart>
              </ResponsiveContainer>
            </CardContent>
          </Card>

          {/* Device Yield */}
          <Card>
            <CardHeader>
              <CardTitle className="text-balance">Device Yield</CardTitle>
            </CardHeader>
            <CardContent>
              <ResponsiveContainer width="100%" height={200}>
                <LineChart data={yieldData}>
                  <CartesianGrid strokeDasharray="3 3" stroke="#10b981" opacity={0.2} />
                  <XAxis dataKey="time" stroke="#94a3b8" fontSize={12} tickLine={false} axisLine={false} />
                  <YAxis stroke="#94a3b8" fontSize={12} tickLine={false} axisLine={false} />
                  <Tooltip
                    contentStyle={{
                      backgroundColor: "#1e293b",
                      border: "1px solid #10b981",
                      borderRadius: "8px",
                      color: "#f1f5f9",
                    }}
                  />
                  <Line
                    type="monotone"
                    dataKey="yield"
                    stroke="#10b981"
                    strokeWidth={4}
                    dot={{ fill: "#10b981", strokeWidth: 2, r: 6 }}
                    activeDot={{ r: 8, fill: "#059669", stroke: "#10b981", strokeWidth: 2 }}
                  />
                </LineChart>
              </ResponsiveContainer>
            </CardContent>
          </Card>

          {/* IV Repeatability */}
          <Card>
            <CardHeader>
              <CardTitle className="text-balance">IV Repeatability</CardTitle>
            </CardHeader>
            <CardContent>
              <ResponsiveContainer width="100%" height={200}>
                <LineChart data={repeatabilityData}>
                  <CartesianGrid strokeDasharray="3 3" stroke="#f59e0b" opacity={0.2} />
                  <XAxis dataKey="time" stroke="#94a3b8" fontSize={12} tickLine={false} axisLine={false} />
                  <YAxis stroke="#94a3b8" fontSize={12} tickLine={false} axisLine={false} />
                  <Tooltip
                    contentStyle={{
                      backgroundColor: "#1e293b",
                      border: "1px solid #f59e0b",
                      borderRadius: "8px",
                      color: "#f1f5f9",
                    }}
                  />
                  <Line
                    type="monotone"
                    dataKey="value"
                    stroke="#f59e0b"
                    strokeWidth={4}
                    dot={{ fill: "#f59e0b", strokeWidth: 2, r: 6 }}
                    activeDot={{ r: 8, fill: "#d97706", stroke: "#f59e0b", strokeWidth: 2 }}
                  />
                </LineChart>
              </ResponsiveContainer>
            </CardContent>
          </Card>
        </div>
      </div>
    </div>
  )
}

