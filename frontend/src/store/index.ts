import { configureStore } from '@reduxjs/toolkit'
import agentsReducer from './slices/agentsSlice'
import metricsReducer from './slices/metricsSlice'
import logsReducer from './slices/logsSlice'
import evolutionReducer from './slices/evolutionSlice'
import websocketReducer from './slices/websocketSlice'
import websocketMiddleware from './middleware/websocket'

export const store = configureStore({
  reducer: {
    agents: agentsReducer,
    metrics: metricsReducer,
    logs: logsReducer,
    evolution: evolutionReducer,
    websocket: websocketReducer,
  },
  middleware: (getDefaultMiddleware) =>
    getDefaultMiddleware({
      serializableCheck: {
        // WebSocket 이벤트는 직렬화 검사 무시
        ignoredActions: ['websocket/connect', 'websocket/disconnect', 'websocket/send'],
      },
    }).concat(websocketMiddleware),
})

export type RootState = ReturnType<typeof store.getState>
export type AppDispatch = typeof store.dispatch
