import React from 'react'
import { Link } from 'react-router-dom'
import KPIDashboard from './KPIDashboard'

function Sidebar() {
  return (
    <div className="sidebar">
      <h1>💰 Finance App</h1>
      
      <nav>
        <Link to="/">Portfolio Command Center</Link>
        {/* 今後追加予定のページリンク */}
        {/* <Link to="/allocation">Allocation Matrix</Link> */}
        {/* <Link to="/cashflow">Cashflow Analytics</Link> */}
        {/* <Link to="/performance">Investment Performance Lab</Link> */}
      </nav>

      <KPIDashboard />
    </div>
  )
}

export default Sidebar
