import { createSlice, PayloadAction } from '@reduxjs/toolkit'

interface WebSocketState {
  connected: boolean
  connecting: boolean
  error: string | null
  lastMessage: any | null
  reconnectAttempts: number
}

const initialState: WebSocketState = {
  connected: false,
  connecting: false,
  error: null,
  lastMessage: null,
  reconnectAttempts: 0,
}

const websocketSlice = createSlice({
  name: 'websocket',
  initialState,
  reducers: {
    setConnected: (state, action: PayloadAction<boolean>) => {
      state.connected = action.payload
      state.connecting = false
      if (action.payload) {
        state.error = null
        state.reconnectAttempts = 0
      }
    },
    setConnecting: (state, action: PayloadAction<boolean>) => {
      state.connecting = action.payload
    },
    setError: (state, action: PayloadAction<string | null>) => {
      state.error = action.payload
    },
    setLastMessage: (state, action: PayloadAction<any>) => {
      state.lastMessage = action.payload
    },
    incrementReconnectAttempts: (state) => {
      state.reconnectAttempts += 1
    },
    resetReconnectAttempts: (state) => {
      state.reconnectAttempts = 0
    },
  },
  extraReducers: (builder) => {
    builder
      .addCase('websocket/connected', (state) => {
        state.connected = true
        state.connecting = false
        state.error = null
        state.reconnectAttempts = 0
      })
      .addCase('websocket/disconnected', (state) => {
        state.connected = false
        state.connecting = false
      })
      .addCase('websocket/error', (state, action: any) => {
        state.error = action.payload
        state.connecting = false
      })
  },
})

export const {
  setConnected,
  setConnecting,
  setError,
  setLastMessage,
  incrementReconnectAttempts,
  resetReconnectAttempts,
} = websocketSlice.actions

export default websocketSlice.reducer