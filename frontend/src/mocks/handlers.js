// src/mocks/handlers.js
import { http, HttpResponse } from 'msw'

export const handlers = [
  http.get('/api/Portfolio_Command_Center/graphs', () => {
    return HttpResponse.json({
      graphs: {
        allocation: {
          //ここに仮JSONを記述
        },
      },
    })
  }),
  http.get('/api/Portfolio_Command_Center/summary', () => {
    return HttpResponse.json({
      summary: {
        allocation: {
          //ここに仮JSONを記述
        },
      },
    })
  }),
  http.get('/api/Allocation_Matrix/graphs', () => {
    return HttpResponse.json({
      graphs: {
        allocation: {
          //ここに仮JSONを記述
        },
      },
    })
  }),
  http.get('/api/Allocation_Matrix/summary', () => {
    return HttpResponse.json({
      summary: {
        allocation: {
          //ここに仮JSONを記述
        },
      },
    })
  }),
  http.get('/api/Cashflow_Analytics/graphs', () => {
    return HttpResponse.json({
      graphs: {
        allocation: {
          //ここに仮JSONを記述
        },
      },
    })
  }),
  http.get('/api/Cashflow_Analytics/summary', () => {
    return HttpResponse.json({
      summary: {
        allocation: {
          //ここに仮JSONを記述
        },
      },
    })
  }),
]
