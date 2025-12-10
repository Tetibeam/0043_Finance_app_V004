import React, { useState, useEffect } from 'react'
import axios from 'axios'

function KPICommandCenter() {
  const [summary, setSummary] = useState(null)
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState(null)

  useEffect(() => {
    const fetchSummary = async () => {
      try {
        const response = await axios.get('/api/Portfolio_Command_Center/summary')
        setSummary(response.data.summary)
        setLoading(false)
      } catch (err) {
        console.error('Failed to load dashboard summary:', err)
        setError(err.message)
        setLoading(false)
      }
    }

    fetchSummary()
  }, [])

  const getVectorIcon = (vector) => {
    if (vector === 1) return '👆 '
    if (vector === -1) return '👇 '
    if (vector === 0) return '👉 '
    return '　 '
  }

  if (loading) return <div id="dashboard-summary">Loading...</div>
  if (error) return <div id="dashboard-summary">Error: {error}</div>
  if (!summary) return null

  return (
    <div id="dashboard-summary">
      <div style={{
        background: 'linear-gradient(135deg, #1e3c72 0%, #2a5298 100%)',
        padding: '12px 16px',
        borderRadius: '8px 8px 0 0',
        margin: '-8px -8px 12px -8px',
        borderBottom: '2px solid #4a90e2'
      }}>
        <h3 style={{
          margin: 0,
          fontFamily: "'Montserrat', sans-serif",
          fontSize: '2vh',
          fontWeight: 600,
          letterSpacing: '0.5px',
          color: '#ffffff',
          textTransform: 'uppercase'
        }}>📊 KPI Command Center</h3>
      </div>
      
      <div className="summary-grid">
        
        <div>Date:</div>
        <div style={{marginLeft: '1.2vw'}}>{summary.latest_date}</div>
        
        <div>Fire Progress:</div>
        <div>{getVectorIcon(summary.fire_progress_vector)}{summary.fire_progress.toLocaleString()}%</div>
        
        <div>Net Worth :</div>
        <div>{getVectorIcon(summary.total_assets_vector)}¥ {summary.total_assets.toLocaleString()}</div>
        
        <div> Net Worth Target:</div>
        <div>{getVectorIcon(summary.total_target_assets_vector)}¥ {summary.total_target_assets.toLocaleString()}</div>
        
        <div>Capital Goal Track:</div>
        <div>{getVectorIcon(summary.difference_vector)}¥ {summary.difference.toLocaleString()}</div>
      </div>
    </div>
  )
}

export default KPICommandCenter
