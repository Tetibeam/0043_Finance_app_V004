import React from 'react'
import { Routes, Route } from 'react-router-dom'
import Sidebar from './components/Sidebar'
import PortfolioCommandCenter from './pages/PortfolioCommandCenter'
import AllocationMatrix from './pages/AllocationMatrix'
import AllocationMatrixDetails from './pages/AllocationMatrixDetails'

function App() {
  return (
    <div className="app-container">
      <Sidebar />
      <Routes>
        {/* portfolio_command_center */}
        <Route path="/" element={<PortfolioCommandCenter />} />

        {/* allocation_matrix */}
        <Route path="/allocation_matrix" element={<AllocationMatrix />} />
        <Route path="/allocation_matrix/:graphId/details" element={<AllocationMatrixDetails />} />

        {/* <Route path="/cashflow" element={<CashflowAnalytics />} /> */}
        {/* <Route path="/performance" element={<InvestmentPerformance />} /> */}
      </Routes>
    </div>
  )
}

export default App
