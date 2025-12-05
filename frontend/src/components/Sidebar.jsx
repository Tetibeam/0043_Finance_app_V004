import React from 'react'
import { Link, useLocation } from 'react-router-dom'
import KPIDashboard from './KPIDashboard'
import KPIAllocationMatrix from './KPIAllocationMatrix'

function Sidebar() {
  const location = useLocation()
  
  return (
    <div className="sidebar">
      <h1>💰 Finance App</h1>
      
      <nav>
        <Link to="/">Portfolio Command Center</Link>
        {/* 今後追加予定のページリンク */}
        <Link to="/allocation_matrix">Allocation Matrix</Link>
        {/* <Link to="/cashflow">Cashflow Analytics</Link> */}
        {/* <Link to="/performance">Investment Performance Lab</Link> */}
      </nav>

      {location.pathname === '/allocation_matrix' ? (
        <KPIAllocationMatrix />
      ) : (
        <KPIDashboard />
      )}
    </div>
  )
}

export default Sidebar
