import React, { useState, useEffect } from 'react'
import apiClient from '../apiClient'
import GraphContainer from '../components/GraphContainer'

function PortfolioCommandCenter() {
  const [graphs, setGraphs] = useState({})
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState(null)

  useEffect(() => {
    const fetchGraphs = async () => {
      try {
        const response = await apiClient.get('/Portfolio_Command_Center/graphs')

        setGraphs(response.data.graphs)
        setLoading(false)
      } catch (err) {
        console.error('Failed to load graphs:', err)
        setError(err.message)
        setLoading(false)
      }
    }

    fetchGraphs()
  }, [])

  // グラフの表示順
  const graphOrder = [
    'progress_rate',
    'saving_rate',
    'assets',
    'general_balance',
    'special_balance',
    'returns'
  ]

  // グラフタイトルのマッピング
  const graphTitles = {
    'progress_rate': "<span><img src='/static/icon/star.svg' style='height:18px; margin-right:6px; opacity:0.85;'/> FIRE Readiness</span>",
    'saving_rate': "<span><img src='/static/icon/sail.svg' style='height:18px; margin-right:6px; opacity:0.85;'/> Savings Efficiency</span>",
    'assets': "<span><img src='/static/icon/compass.svg' style='height:20px; margin-right:6px; opacity:0.85;'/> Net Worth Trajectory</span>",
    'returns': "<span><img src='/static/icon/line-chart.svg' style='height:20px; margin-right:6px; opacity:0.85;'/> Portfolio Performance</span>",
    'general_balance': "<span><img src='/static/icon/waves.svg' style='height:18px; margin-right:6px; opacity:0.85;'/> Cash Flow – Routine</span>",
    'special_balance': "<span><img src='/static/icon/lighthouse.svg' style='height:18px; margin-right:6px; opacity:0.85;'/> Cash Flow – Exceptional</span>"
  }

  if (loading) {
    return <div className="main"><div>Loading graphs...</div></div>
  }

  if (error) {
    return <div className="main"><div>Error: {error}</div></div>
  }

  return (
    <div id="graphs-area" className="main">
      {graphOrder.map(key => {
        const figJson = graphs[key]
        if (!figJson) return null
        
        return (
          <GraphContainer
            key={key}
            figJson={figJson}
            titleHtml={graphTitles[key] || key}
          />
        )
      })}
    </div>
  )
}

export default PortfolioCommandCenter
