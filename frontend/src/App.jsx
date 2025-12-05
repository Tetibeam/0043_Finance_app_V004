import React from 'react'
import { Routes, Route } from 'react-router-dom'
import Sidebar from './components/Sidebar'
import PortfolioCommandCenter from './pages/PortfolioCommandCenter'

function App() {
  return (
    <div className="app-container">
      <Sidebar />
      <Routes>
        <Route path="/" element={<PortfolioCommandCenter />} />
        {/* 今後追加予定のルート */}
        {/* <Route path="/allocation" element={<AllocationMatrix />} /> */}
        {/* <Route path="/cashflow" element={<CashflowAnalytics />} /> */}
        {/* <Route path="/performance" element={<InvestmentPerformance />} /> */}
      </Routes>
    </div>
  )
}

export default App
