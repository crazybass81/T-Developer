/// <reference types="vite/client" />

interface ImportMetaEnv {
  readonly VITE_API_ENDPOINT?: string
  readonly MODE: string
}

interface ImportMeta {
  readonly env: ImportMetaEnv
}
