"use client"

import { useState, useEffect } from "react"
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card"
import { Button } from "@/components/ui/button"
import { Input } from "@/components/ui/input"
import { Badge } from "@/components/ui/badge"
import { Checkbox } from "@/components/ui/checkbox"
import { BarChart, Bar, LineChart, Line, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer } from "recharts"
import { Plus, Menu, Trash2, Edit, ChevronDown } from "lucide-react"
import { todayAPI, yesterdayAPI, safetyAPI, kudosAPI, healthAPI } from "@/lib/api"
import ParameterChart from "@/components/ParameterChart"
import { DropdownMenu, DropdownMenuContent, DropdownMenuItem, DropdownMenuTrigger } from "@/components/ui/dropdown-menu"
import { useNavigate } from "react-router-dom"

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

const throughputData = [
  { time: "00:00", wafers: 245 },
  { time: "04:00", wafers: 267 },
  { time: "08:00", wafers: 234 },
  { time: "12:00", wafers: 289 },
  { time: "16:00", wafers: 256 },
  { time: "20:00", wafers: 278 },
]

export default function MainDashboard() {
  const navigate = useNavigate()
  const [error, setError] = useState("")
  const [apiData, setApiData] = useState({
    safety: [],
    kudos: [],
    today: [],
    yesterday: [],
  })

  const [newIssue, setNewIssue] = useState({
    item: "",
    description: "",
    who: "",
  })

  const [newSafetyIssue, setNewSafetyIssue] = useState({
    issue: "",
    person: "",
    action: "",
  })

  const [newKudos, setNewKudos] = useState({
    name: "",
    action: "",
  })

  const [selectedYesterdayIssues, setSelectedYesterdayIssues] = useState(new Set())

  const addTodayIssue = () => {
    if (newIssue.item && newIssue.description && newIssue.who) {
      const issue = {
        ...newIssue,
        date: new Date().toLocaleDateString("en-US", { month: "numeric", day: "numeric" }),
        done: "No",
      }
      todayIssues.push(issue)
      setNewIssue({ item: "", description: "", who: "" })
    }
  }

  const addSafetyIssue = () => {
    if (newSafetyIssue.issue && newSafetyIssue.person && newSafetyIssue.action) {
      const issue = {
        ...newSafetyIssue,
        date: new Date().toLocaleDateString("en-US", { month: "numeric", day: "numeric" }),
      }
      safetyIssues.push(issue)
      setNewSafetyIssue({ issue: "", person: "", action: "" })
    }
  }

  const addKudos = () => {
    if (newKudos.name && newKudos.action) {
      const kudos = {
        ...newKudos,
        date: new Date().toLocaleDateString("en-US", { month: "numeric", day: "numeric" }),
      }
      kudosData.push(kudos)
      setNewKudos({ name: "", action: "" })
    }
  }

  const loadData = async () => {
    try {
      setError("")
      console.log("Loading data from APIs...")

      const [safetyRes, kudosRes, todayRes, yesterdayRes] = await Promise.all([
        safetyAPI.getAll(),
        kudosAPI.getAll(),
        todayAPI.getAll(),
        yesterdayAPI.getAll(),
      ])

      setApiData({
        safety: safetyRes || [],
        kudos: kudosRes || [],
        today: todayRes || [],
        yesterday: yesterdayRes || [],
      })

      console.log("Data loaded successfully")
    } catch (err) {
      console.error("Error loading data:", err)
      setError(`Failed to load data: ${err.message}`)
    }
  }

  useEffect(() => {
    loadData()
  }, [])

  const toggleYesterdayIssue = (index) => {
    const newSelected = new Set(selectedYesterdayIssues)
    if (newSelected.has(index)) {
      newSelected.delete(index)
    } else {
      newSelected.add(index)
    }
    setSelectedYesterdayIssues(newSelected)
  }

  return (
    <div className="min-h-screen bg-background">
      {/* Navigation */}
      <nav className="border-b border-border">
        <div className="flex items-center justify-between px-6 py-4">
          <div className="flex items-center space-x-8">
            <h1 className="text-xl font-semibold">Rayleigh Solar Tech</h1>
            <div className="text-sm text-muted-foreground">
              Daily Passdown Dashboard | {new Date().toLocaleDateString()}
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
                  <ChevronDown className="h-4 w-4 ml-2" />
                </Button>
              </DropdownMenuTrigger>
              <DropdownMenuContent align="end">
                <DropdownMenuItem onClick={() => navigate('/stability-dashboard')}>
                  Stability Dashboard
                </DropdownMenuItem>
              </DropdownMenuContent>
            </DropdownMenu>
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
                    <th className="text-left py-3 px-4 font-medium text-muted-foreground">Yield</th>
                    <th className="text-left py-3 px-4 font-medium text-muted-foreground">Date</th>
                  </tr>
                </thead>
                <tbody>
                  {processData.map((item, index) => (
                    <tr key={index} className="border-b border-border hover:bg-muted/50">
                      <td className="py-3 px-4 font-medium">{item.process}</td>
                      <td className="py-3 px-4">{item.cycleTime}</td>
                      <td className="py-3 px-4">{item.outs}</td>
                      <td className="py-3 px-4">{item.wip}</td>
                      <td className="py-3 px-4">
                        <Badge variant="secondary" className="bg-green-100 text-green-800">
                          {item.yield}
                        </Badge>
                      </td>
                      <td className="py-3 px-4 text-muted-foreground">{item.date}</td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
          </CardContent>
        </Card>

        {/* Charts Section */}
        <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
          <Card>
            <CardHeader>
              <CardTitle>Yield Trend</CardTitle>
            </CardHeader>
            <CardContent>
              <ResponsiveContainer width="100%" height={300}>
                <LineChart data={yieldData}>
                  <CartesianGrid strokeDasharray="3 3" className="opacity-30" />
                  <XAxis dataKey="time" />
                  <YAxis domain={["dataMin - 1", "dataMax + 1"]} />
                  <Tooltip />
                  <Line type="monotone" dataKey="yield" stroke="hsl(var(--primary))" strokeWidth={2} />
                </LineChart>
              </ResponsiveContainer>
            </CardContent>
          </Card>

          <Card>
            <CardHeader>
              <CardTitle>Throughput</CardTitle>
            </CardHeader>
            <CardContent>
              <ResponsiveContainer width="100%" height={300}>
                <BarChart data={throughputData}>
                  <CartesianGrid strokeDasharray="3 3" className="opacity-30" />
                  <XAxis dataKey="time" />
                  <YAxis />
                  <Tooltip />
                  <Bar dataKey="wafers" fill="hsl(var(--primary))" />
                </BarChart>
              </ResponsiveContainer>
            </CardContent>
          </Card>
        </div>

        {/* Parameter Chart */}
        <ParameterChart />

        {/* Three columns layout */}
        <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
          {/* Safety Issues */}
          <Card>
            <CardHeader>
              <CardTitle className="flex items-center justify-between">
                Safety Issues
                <Badge variant="destructive">{safetyIssues.length}</Badge>
              </CardTitle>
            </CardHeader>
            <CardContent className="space-y-4">
              {safetyIssues.map((issue, index) => (
                <div key={index} className="p-3 border border-border rounded-lg">
                  <div className="font-medium text-sm">{issue.issue}</div>
                  <div className="text-xs text-muted-foreground">Person: {issue.person}</div>
                  <div className="text-xs text-muted-foreground">Action: {issue.action}</div>
                  <div className="text-xs text-muted-foreground">Date: {issue.date}</div>
                </div>
              ))}

              <div className="border-t border-border pt-4 space-y-3">
                <Input
                  placeholder="Issue description"
                  value={newSafetyIssue.issue}
                  onChange={(e) => setNewSafetyIssue({ ...newSafetyIssue, issue: e.target.value })}
                />
                <Input
                  placeholder="Person responsible"
                  value={newSafetyIssue.person}
                  onChange={(e) => setNewSafetyIssue({ ...newSafetyIssue, person: e.target.value })}
                />
                <Input
                  placeholder="Action taken"
                  value={newSafetyIssue.action}
                  onChange={(e) => setNewSafetyIssue({ ...newSafetyIssue, action: e.target.value })}
                />
                <Button onClick={addSafetyIssue} className="w-full">
                  <Plus className="h-4 w-4 mr-2" />
                  Add Safety Issue
                </Button>
              </div>
            </CardContent>
          </Card>

          {/* Kudos */}
          <Card>
            <CardHeader>
              <CardTitle className="flex items-center justify-between">
                Kudos
                <Badge variant="outline">{kudosData.length}</Badge>
              </CardTitle>
            </CardHeader>
            <CardContent className="space-y-4">
              {kudosData.map((kudos, index) => (
                <div key={index} className="p-3 border border-border rounded-lg">
                  <div className="font-medium text-sm">{kudos.name}</div>
                  <div className="text-xs text-muted-foreground">{kudos.action}</div>
                  <div className="text-xs text-muted-foreground">Date: {kudos.date}</div>
                </div>
              ))}

              <div className="border-t border-border pt-4 space-y-3">
                <Input
                  placeholder="Person name"
                  value={newKudos.name}
                  onChange={(e) => setNewKudos({ ...newKudos, name: e.target.value })}
                />
                <Input
                  placeholder="Action description"
                  value={newKudos.action}
                  onChange={(e) => setNewKudos({ ...newKudos, action: e.target.value })}
                />
                <Button onClick={addKudos} className="w-full">
                  <Plus className="h-4 w-4 mr-2" />
                  Add Kudos
                </Button>
              </div>
            </CardContent>
          </Card>

          {/* Yesterday's Top Issues */}
          <Card>
            <CardHeader>
              <CardTitle className="flex items-center justify-between">
                Yesterday's Top Issues
                <Badge variant="outline">{yesterdayIssues.filter((item) => item.done === "No").length} pending</Badge>
              </CardTitle>
            </CardHeader>
            <CardContent className="space-y-3">
              {yesterdayIssues.map((issue, index) => (
                <div key={index} className="flex items-start space-x-3 p-3 border border-border rounded-lg">
                  <Checkbox
                    checked={selectedYesterdayIssues.has(index)}
                    onCheckedChange={() => toggleYesterdayIssue(index)}
                    className="mt-1"
                  />
                  <div className="flex-1 min-w-0">
                    <div className="font-medium text-sm">{issue.item}</div>
                    <div className="text-xs text-muted-foreground truncate">{issue.description}</div>
                    <div className="text-xs text-muted-foreground">Assigned to: {issue.who}</div>
                    <div className="flex items-center gap-2 mt-1">
                      <Badge variant={issue.done === "Yes" ? "default" : "secondary"} className="text-xs">
                        {issue.done === "Yes" ? "Completed" : "Pending"}
                      </Badge>
                      <span className="text-xs text-muted-foreground">{issue.date}</span>
                    </div>
                  </div>
                </div>
              ))}
            </CardContent>
          </Card>
        </div>

        {/* Today's Top Issues */}
        <Card>
          <CardHeader>
            <CardTitle className="flex items-center justify-between">
              Today's Top Issues
              <Badge variant="outline">{todayIssues.filter((item) => item.done === "No").length} pending</Badge>
            </CardTitle>
          </CardHeader>
          <CardContent>
            <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4 mb-6">
              {todayIssues.map((issue, index) => (
                <div key={index} className="p-4 border border-border rounded-lg">
                  <div className="flex items-start justify-between mb-2">
                    <div className="font-medium">{issue.item}</div>
                    <div className="flex space-x-1">
                      <Button variant="ghost" size="sm" className="h-6 w-6 p-0">
                        <Edit className="h-3 w-3" />
                      </Button>
                      <Button variant="ghost" size="sm" className="h-6 w-6 p-0">
                        <Trash2 className="h-3 w-3" />
                      </Button>
                    </div>
                  </div>
                  <div className="text-sm text-muted-foreground mb-2">{issue.description}</div>
                  <div className="text-xs text-muted-foreground mb-2">Assigned to: {issue.who}</div>
                  <div className="flex items-center justify-between">
                    <Badge variant={issue.done === "Yes" ? "default" : "secondary"} className="text-xs">
                      {issue.done === "Yes" ? "Completed" : "Pending"}
                    </Badge>
                    <span className="text-xs text-muted-foreground">{issue.date}</span>
                  </div>
                </div>
              ))}
            </div>

            <div className="border-t border-border pt-6">
              <div className="grid grid-cols-1 md:grid-cols-3 gap-4 mb-4">
                <Input
                  placeholder="Item/Tool name"
                  value={newIssue.item}
                  onChange={(e) => setNewIssue({ ...newIssue, item: e.target.value })}
                />
                <Input
                  placeholder="Issue description"
                  value={newIssue.description}
                  onChange={(e) => setNewIssue({ ...newIssue, description: e.target.value })}
                />
                <Input
                  placeholder="Assigned to"
                  value={newIssue.who}
                  onChange={(e) => setNewIssue({ ...newIssue, who: e.target.value })}
                />
              </div>
              <Button onClick={addTodayIssue}>
                <Plus className="h-4 w-4 mr-2" />
                Add Today's Issue
              </Button>
            </div>
          </CardContent>
        </Card>
      </div>
    </div>
  )
}