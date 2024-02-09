export type Theme = "light" | "dark" | "system"

export interface Setting {
  theme: Theme
  version: number
  totalMessages: number
  data: { [key: string]: any }
}
