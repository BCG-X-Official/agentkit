import { isArray } from "lodash-es"
import { type FC } from "react"

export interface TabItemProps {
  label: string
  children?: JSX.Element | JSX.Element[] | null
  icon?: JSX.Element
  hideLabel?: boolean
  showTooltip?: boolean
}

export const TabItem: FC<TabItemProps> = ({ children }) => {
  if (!children) return null

  const tabItems = isArray(children) ? children : [children]

  return <div className="hidden">{tabItems}</div>
}
