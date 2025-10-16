declare global {
  interface ImportMetaEnv {
    readonly VITE_API_BASE?: string
  }
  interface ImportMeta {
    readonly env: ImportMetaEnv
  }
}

export function apiBase() {
  return import.meta.env?.VITE_API_BASE || '/api'
}
