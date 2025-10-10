import { BrowserRouter as Router, Routes, Route } from "react-router-dom"
import MainDashboard from "@/components/MainDashboard"
import StabilityDashboard from "@/components/StabilityDashboard"

export default function App() {
  return (
    <Router>
      <Routes>
        <Route path="/" element={<MainDashboard />} />
        <Route path="/stability-dashboard" element={<StabilityDashboard />} />
      </Routes>
    </Router>
  )
}