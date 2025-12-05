import React, { useState, useEffect } from 'react'
import axios from 'axios'

function KPIAllocationMatrix() {
  const [summary, setSummary] = useState(null)
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState(null)

  useEffect(() => {
    const fetchSummary = async () => {
      try {
        const response = await axios.get('/api/Allocation_Matrix/summary')
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

  if (loading) return <div id="dashboard-summary">読み込み中...</div>
  if (error) return <div id="dashboard-summary">エラー: {error}</div>
  if (!summary) return null

  return (
    <div id="dashboard-summary">
      <div style={{
        background: 'linear-gradient(135deg, #1e3c72 0%, #2a5298 100%)',
        padding: '12px 16px',
        borderRadius: '8px 8px 0 0',
        margin: '-8px -8px 12px -8px',
        borderBottom: '2px solid #4a90e2',
      }}>
        <h3 style={{
          margin: 0,
          fontFamily: "'Montserrat', sans-serif",
          fontSize: '2vh',
          fontWeight: 600,
          letterSpacing: '0.5px',
          color: '#ffffff',
          textTransform: 'uppercase'
        }}>📊 KPI Allocation Matrix</h3>
        
      </div>
      
      <div className="summary-grid">
        <div>Date:</div>
        <div style={{marginLeft: '1.2vw'}}>{summary.latest_date}</div>
        
        <div>Dynamic Assets:</div>
        <div>{getVectorIcon(summary.active_growth_capital_vector)}
          {summary.active_growth_capital.toLocaleString()}%</div>
        
        <div>Aggressive Assets:</div>
        <div>{getVectorIcon(summary.aggressive_return_exposure_vector)}
          {summary.aggressive_return_exposure.toLocaleString()}%</div>
        
        <div>Emergency Buffer:</div>
        <div>{getVectorIcon(summary.emergency_buffer_vector)}
          ¥ {summary.emergency_buffer.toLocaleString()}</div>
        
        <div>Debt Exposure:</div>
        <div>{getVectorIcon(summary.debt_exposure_ratio_vector)}
          {summary.debt_exposure_ratio.toLocaleString()}%</div>
      </div>
    </div>
  )
}

export default KPIAllocationMatrix
