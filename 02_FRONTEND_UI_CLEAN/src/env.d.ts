/// <reference types="vite/client" />
interface ImportMetaEnv {
  readonly VITE_ENV: "development" | "production" | "staging"
  readonly VITE_API_URL: string
  readonly VITE_ENABLE_METRICS?: string
  readonly VITE_APP_NAME?: string
  readonly VITE_APP_VERSION?: string
  readonly VITE_DEV_MODE?: string
  readonly VITE_DEBUG_API?: string
  readonly VITE_SUPABASE_URL?: string
  readonly VITE_SUPABASE_ANON_KEY?: string
}
interface ImportMeta {
  readonly env: ImportMetaEnv
}
