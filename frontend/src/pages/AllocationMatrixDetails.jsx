import React, { useState, useEffect } from 'react'
import { useSearchParams, useParams } from 'react-router-dom'
import apiClient from '../apiClient'
import Plot from 'react-plotly.js'  // 後でcomponentに

function AllocationMatrixDetails() {
  const { graphId } = useParams()
  const [searchParams] = useSearchParams()
  const subType = searchParams.get('sub_type')
  
  const [figJson, setFigJson] = useState(null)
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState(null)

  const fig = React.useMemo(() => {
    return typeof figJson === 'string' ? JSON.parse(figJson) : figJson
  }, [figJson])

  useEffect(() => {
    const fetchData = async () => {
        if (!graphId) return;
        
      try {
        setLoading(true)
        const response = await apiClient.get('/Allocation_Matrix/details', {
            params: {
                graph_id: graphId,
                sub_type: subType
            }
        })
        setFigJson(response.data)
        setLoading(false)
      } catch (err) {
        console.error('Failed to load details:', err)
        setError(err.message)
        setLoading(false)
      }
    }
    fetchData()
  }, [graphId, subType])
  
  useEffect(() => {
    const updateContainerSize = () => {

    }
  }, [])

  if (loading) {
    return <div className="main" style={{ color: '#fff' }}>Loading...</div>
  }

  if (error) {
    return <div className="main" style={{ color: '#ff6b6b' }}>Error: {error}</div>
  }
  
  const displaySubType = subType;
  const displayGraphName = graphId === 'liquidity_horizon' ? 'Liquidity Horizon' : graphId;
  
  return (
    <div className="graph-fullscreen">
      <div 
        className="graph-title" 
        dangerouslySetInnerHTML={{ __html: displayGraphName + " - " + subType}}
      />
      {fig && (
        <Plot
          data={fig.data}
          layout={fig.layout}
          config={{ displayModeBar: false }}
          style={{ width: "100%", height: "100%" }}
        />
      )}
    </div>
  )
}

export default AllocationMatrixDetails
