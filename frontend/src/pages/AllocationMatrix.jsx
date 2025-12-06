import React, { useState, useEffect } from 'react'
import axios from 'axios'
import GraphContainer from '../components/GraphContainer'

function AllocationMatrix() {
  const [graphs, setGraphs] = useState({})
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState(null)

  useEffect(() => {
    const fetchGraphs = async () => {
      try {
        const response = await axios.get('/api/Allocation_Matrix/graphs')
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
    'asset_tree_map',
    'target_deviation',
    'portfolio_efficiency_map',
    'liquidity_pyramid',
    'true_risk_exposure_flow',
    'rebalancing_workbench'
  ]

  // グラフタイトルのマッピング
  const graphTitles = {
    'asset_tree_map': "<span><img src='/static/icon/star.svg' style='height:18px; margin-right:6px; opacity:0.85;'/> Interactive Treemap</span>",
    'target_deviation': "<span><img src='/static/icon/sail.svg' style='height:18px; margin-right:6px; opacity:0.85;'/> Target Deviation</span>",
    'portfolio_efficiency_map': "<span><img src='/static/icon/compass.svg' style='height:20px; margin-right:6px; opacity:0.85;'/> Portfolio Efficiency Map</span>",
    'liquidity_pyramid': "<span><img src='/static/icon/line-chart.svg' style='height:20px; margin-right:6px; opacity:0.85;'/> Liquidity Pyramid</span>",
    'true_risk_exposure_flow': "<span><img src='/static/icon/waves.svg' style='height:18px; margin-right:6px; opacity:0.85;'/> True Risk Exposure Flow</span>",
    'rebalancing_workbench': "<span><img src='/static/icon/lighthouse.svg' style='height:18px; margin-right:6px; opacity:0.85;'/> Rebalancing Workbench</span>"
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

export default AllocationMatrix
