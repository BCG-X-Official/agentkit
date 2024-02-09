import { LIGHT_THEME } from "~/styles/themes"
import { generateUUID } from "~/utils"

export interface CreateTagType<T = any> {
  id?: string
  value: string
  color?: string
  tagType?: T
}

export const createTag = <T = any>({ value, tagType, color = LIGHT_THEME.colors?.["base-200"] }: CreateTagType<T>) => ({
  id: generateUUID(),
  tagType,
  color,
  value,
})
