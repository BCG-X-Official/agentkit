import { create } from "zustand"

import { type TabItemProps } from "./TabItem"

export interface TabsState {
  activeTab?: string
  setActiveTab: (activeTab?: string) => void
  tabItems: TabItemProps[]
  setTabItems: (tabItems: TabItemProps[]) => void
}

export const useTabsStore = create<TabsState>()((set) => ({
  activeTab: undefined,
  setActiveTab: (activeTab?: string) => set(() => ({ activeTab })),
  tabItems: [],
  setTabItems: (tabItems: TabItemProps[]) => set(() => ({ tabItems })),
}))
