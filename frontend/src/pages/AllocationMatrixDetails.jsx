import React, { useState, useEffect } from 'react'
import { useSearchParams, useParams } from 'react-router-dom'
import axios from 'axios'

function AllocationMatrixDetails() {
  const { graphId } = useParams()
  const [searchParams] = useSearchParams()
  const subType = searchParams.get('sub_type')
  
  const [data, setData] = useState([])
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState(null)

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
        setData(response.data.data)
        setLoading(false)
      } catch (err) {
        console.error('Failed to load details:', err)
        setError(err.message)
        setLoading(false)
      }
    }

    fetchData()
  }, [graphId, subType])

  if (loading) {
    return <div className="main" style={{ color: '#fff' }}>読み込み中...</div>
  }

  if (error) {
    return <div className="main" style={{ color: '#ff6b6b' }}>エラー: {error}</div>
  }

  // Determine Japanese subtitle from data or fallback (Reverted to English/Source as requested)
  // const displaySubType = (data.length > 0 && data[0]['資産サブタイプ']) ? data[0]['資産サブタイプ'] : subType;
  // const displayGraphName = graphId === 'liquidity_horizon' ? '流動性ホライズン' : graphId;
  
  // User requested to keep source data (English)
  const displaySubType = subType;
  const displayGraphName = graphId === 'liquidity_horizon' ? 'Liquidity Horizon' : graphId;

  return (
    <div className="main" style={{ padding: '20px', color: '#DDDDDD' }}>
      <h2 style={{ marginBottom: '20px' }}>
        詳細: {displaySubType} ({displayGraphName})
      </h2>
      
      {data.length === 0 ? (
        <p>該当するデータはありません。</p>
      ) : (
        <div style={{ overflowX: 'auto' }}>
            <table style={{ 
                width: '100%', 
                borderCollapse: 'collapse', 
                backgroundColor: '#1E1E1E',
                color: '#DDDDDD'
            }}>
                <thead>
                    <tr style={{ borderBottom: '1px solid #444' }}>
                        <th style={{ padding: '10px', textAlign: 'left' }}>資産名</th>
                        <th style={{ padding: '10px', textAlign: 'left' }}>資産サブタイプ</th>
                        <th style={{ padding: '10px', textAlign: 'right' }}>資産額</th>
                        <th style={{ padding: '10px', textAlign: 'left' }}>償還日</th>
                    </tr>
                </thead>
                <tbody>
                    {data.map((row, index) => (
                        <tr key={index} style={{ borderBottom: '1px solid #333' }}>
                            <td style={{ padding: '10px' }}>{row['資産名']}</td>
                            <td style={{ padding: '10px' }}>{row['資産サブタイプ']}</td>
                            <td style={{ padding: '10px', textAlign: 'right' }}>
                                ¥{Number(row['資産額']).toLocaleString()}
                            </td>
                            <td style={{ padding: '10px' }}>{row['償還日']}</td>
                        </tr>
                    ))}
                </tbody>
            </table>
        </div>
      )}
    </div>
  )
}

export default AllocationMatrixDetails
