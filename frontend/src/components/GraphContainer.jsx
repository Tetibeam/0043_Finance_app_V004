import React, { useState, useRef, useEffect } from 'react'
import Plot from 'react-plotly.js'

function GraphContainer({ figJson, titleHtml }) {
  const [isFullscreen, setIsFullscreen] = useState(false)
  const containerRef = useRef(null)
  const [containerSize, setContainerSize] = useState({ width: 0, height: 0 })

  // Parse figure JSON if it's a string
  const fig = typeof figJson === 'string' ? JSON.parse(figJson) : figJson
  
  // Measure container size
  useEffect(() => {
    const container = containerRef.current
    if (!container) return

    const updateSize = () => {
      const rect = container.getBoundingClientRect()
      
      // Get computed padding (1vh from CSS)
      const style = window.getComputedStyle(container)
      const paddingLeft = parseFloat(style.paddingLeft)
      const paddingRight = parseFloat(style.paddingRight)
      const paddingTop = parseFloat(style.paddingTop)
      const paddingBottom = parseFloat(style.paddingBottom)
      
      setContainerSize({
        width: rect.width - paddingLeft - paddingRight,
        height: rect.height - paddingTop - paddingBottom
      })
    }

    // Small delay to ensure DOM is fully rendered
    const timer = setTimeout(updateSize, 10)

    // Observe size changes
    const resizeObserver = new ResizeObserver(updateSize)
    resizeObserver.observe(container)

    return () => {
      clearTimeout(timer)
      resizeObserver.disconnect()
    }
  }, [isFullscreen])

  // Store default font sizes
  const layout = fig.layout || {}
  const defaultFonts = {
    font: layout.font?.size || 12,
    title: layout.title?.font?.size || 14,
    xaxis_title: layout.xaxis?.title?.font?.size || 12,
    yaxis_title: layout.yaxis?.title?.font?.size || 12,
    xaxis_tick: layout.xaxis?.tickfont?.size || 10,
    yaxis_tick: layout.yaxis?.tickfont?.size || 10,
    legend: layout.legend?.font?.size || 12
  }

  const [currentLayout, setCurrentLayout] = useState(fig.layout)

  // Update layout when container size or fullscreen state changes
  useEffect(() => {
    if (containerSize.width > 0 && containerSize.height > 0) {
      const titleHeight = 35 // Approximate height of title
      
      // Calculate font scale
      let scale = 1
      if (isFullscreen) {
        // Scale based on window width, assuming base width of around 500px for normal view
        // or just use a fixed scale factor if preferred, but dynamic is better
        scale = Math.min(window.innerWidth / 1000, 2.5) // Cap at 2.5x
      }

      setCurrentLayout({
        ...fig.layout,
        width: containerSize.width,
        height: containerSize.height - titleHeight,
        autosize: false,
        font: { ...fig.layout.font, size: defaultFonts.font * scale },
        title: { ...fig.layout.title, font: { size: defaultFonts.title * scale } },
        xaxis: { 
          ...fig.layout.xaxis, 
          title: { ...fig.layout.xaxis?.title, font: { size: defaultFonts.xaxis_title * scale } },
          tickfont: { ...fig.layout.xaxis?.tickfont, size: defaultFonts.xaxis_tick * scale }
        },
        yaxis: { 
          ...fig.layout.yaxis,
          title: { ...fig.layout.yaxis?.title, font: { size: defaultFonts.yaxis_title * scale } },
          tickfont: { ...fig.layout.yaxis?.tickfont, size: defaultFonts.yaxis_tick * scale }
        },
        legend: { ...fig.layout.legend, font: { size: defaultFonts.legend * scale } }
      })
    }
  }, [containerSize, isFullscreen, fig.layout])

  const handleTitleClick = () => {
    if (!isFullscreen) {
      setIsFullscreen(true)
    }
  }

  const handleBackClick = (e) => {
    e.stopPropagation()
    setIsFullscreen(false)
  }

  return (
    <div className={`graph-container ${isFullscreen ? 'graph-fullscreen' : ''}`} ref={containerRef}>
      <button 
        className="back-button" 
        onClick={handleBackClick}
        style={{ display: isFullscreen ? 'block' : 'none' }}
      >
        Back
      </button>
      
      <div 
        className="graph-title" 
        dangerouslySetInnerHTML={{ __html: titleHtml }}
        onClick={handleTitleClick}
        style={{ cursor: 'pointer' }}
      />
      
      {containerSize.width > 0 && (
        <Plot
          divId={`plot-${Math.random().toString(36).substr(2, 9)}`}
          data={fig.data}
          layout={currentLayout}
          config={{
            responsive: false,
            displayModeBar: false
          }}
          style={{ 
            width: `${containerSize.width}px`, 
            height: `${containerSize.height - 35}px` 
          }}
        />
      )}
    </div>
  )
}

export default GraphContainer
