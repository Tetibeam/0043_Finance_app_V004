import React, { useState, useEffect } from 'react'
import { useSearchParams, useParams } from 'react-router-dom'
import axios from 'axios'
import Plot from 'react-plotly.js'  // 後でcomponentに

function AllocationMatrixDetails() {
  const { graphId } = useParams()
  const [searchParams] = useSearchParams()
  const subType = searchParams.get('sub_type')
  
  //const [data, setData] = useState([])
  const [figJson, setFigJson] = useState(null)
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState(null)

  // Memoize fig parsing to ensure stable references
  const fig = React.useMemo(() => {
    return typeof figJson === 'string' ? JSON.parse(figJson) : figJson
  }, [figJson])

  useEffect(() => {
    const fetchData = async () => {
        if (!graphId) return;
        
      try {
        setLoading(true)
        const response = await axios.get('/api/Allocation_Matrix/details', {
            params: {
                graph_id: graphId,
                sub_type: subType
            }
        })
        //setData(response.data.data)
        setFigJson(response.data)
        //console.log("response:", response);
        //console.log("response.data:", response.data);

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

  // Determine Japanese subtitle from data or fallback (Reverted to English/Source as requested)
  // const displaySubType = (data.length > 0 && data[0]['資産サブタイプ']) ? data[0]['資産サブタイプ'] : subType;
  // const displayGraphName = graphId === 'liquidity_horizon' ? '流動性ホライズン' : graphId;
  
  // User requested to keep source data (English)
  const displaySubType = subType;
  const displayGraphName = graphId === 'liquidity_horizon' ? 'Liquidity Horizon' : graphId;

  return (
    <div className="graph-fullscreen">
      <div 
        className="graph-title" 
        dangerouslySetInnerHTML={{ __html: subType}}
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
