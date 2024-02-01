import { merge } from "lodash-es"
import { create } from "zustand"
import { persist } from "zustand/middleware"
import { type Setting } from "@/types"

const getDefaultSetting = (): Setting => {
  return {
    theme: "system",
    version: 0,
    data: {},
  }
}

interface SettingState {
  setting: Setting
  getState: () => SettingState
  setTheme: (theme: Setting["theme"]) => void
  setSetting: (setting: Partial<Setting>) => void
}

export const useSettingStore = create<SettingState>()(
  persist(
    (set, get) => ({
      setting: getDefaultSetting(),
      getState: () => get(),
      setTheme: (theme: Setting["theme"]) => {
        set({
          setting: {
            ...get().setting,
            theme,
          },
        })
      },
      setSetting: (setting: Partial<Setting>) => {
        set({
          setting: {
            ...get().setting,
            ...setting,
            version: get().setting.version + 1,
          },
        })
      },
    }),
    {
      name: "setting-storage",
      merge: (persistedState, currentState) => merge(currentState, persistedState),
    }
  )
)
