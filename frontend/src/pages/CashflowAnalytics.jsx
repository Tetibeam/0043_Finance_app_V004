import React, { useState, useEffect } from 'react'
import apiClient from '../apiClient'
import GraphContainer from '../components/GraphContainer'

function CashflowAnalytics() {
  const [graphs, setGraphs] = useState({})
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState(null)

  useEffect(() => {
    const fetchGraphs = async () => {
      try {
        const response = await apiClient.get('/Cashflow_Analytics/graphs')
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
    'target_trajectory',
    'goal_imbalance_map',
    //'portfolio_efficiency_map',
    //'liquidity_pyramid',
    //'true_risk_exposure_flow',
    //'liquidity_horizon'
  ]

  // グラフタイトルのマッピング
  const graphTitles = {
    'target_trajectory': "<span><img src='/static/icon/star.svg' style='height:18px; margin-right:6px; opacity:0.85;'/> Target Trajectory</span>",
    'goal_imbalance_map': "<span><img src='/static/icon/sail.svg' style='height:18px; margin-right:6px; opacity:0.85;'/> Goal Imbalance Map</span>",
    //'portfolio_efficiency_map': "<span><img src='/static/icon/compass.svg' style='height:20px; margin-right:6px; opacity:0.85;'/> Portfolio Efficiency Map</span>",
    //'liquidity_pyramid': "<span><img src='/static/icon/line-chart.svg' style='height:20px; margin-right:6px; opacity:0.85;'/> Liquidity Pyramid</span>",
    //'true_risk_exposure_flow': "<span><img src='/static/icon/waves.svg' style='height:18px; margin-right:6px; opacity:0.85;'/> True Risk Exposure Flow</span>",
    //'liquidity_horizon': "<span><img src='/static/icon/lighthouse.svg' style='height:18px; margin-right:6px; opacity:0.85;'/> Liquidity Horizon</span>"
  }

  if (loading) {
    return <div className="main"><div>Loading graphs...</div></div>
  }

  if (error) {
    return <div className="main"><div>Error: {error}</div></div>
  }

  /* New: Handler for plot clicks */
  const handlePlotClick = (data, graphKey) => {
    // Only target 'liquidity_horizon' as requested
    if (graphKey === 'liquidityca_horizon') {
      if (data && data.points && data.points.length > 0) {
        // Extract the clicked label (Asset Subtype)
        // Note: Plotly event data structure varies, but generally points[0].data.name or customdata
        const point = data.points[0];
        // In the backend _build_liquidity_horizon, we set name=sub_type
        const subType = point.data.name; 
        
        if (subType) {
            // Open new tab
            const url = `/allocation_matrix/${graphKey}/details?sub_type=${encodeURIComponent(subType)}`
            window.open(url, '_blank')
        }
      }
    }
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
            onPlotClick={(data) => handlePlotClick(data, key)}
          />
        )
      })}
    </div>
  )
}

export default CashflowAnalytics
