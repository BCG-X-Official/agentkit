export type Theme = "light" | "dark" | "system"

export interface Setting {
  theme: Theme
  version: number
  data: { [key: string]: any }
}
