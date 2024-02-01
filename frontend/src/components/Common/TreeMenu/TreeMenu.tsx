import { type FC, type MouseEvent, type ReactElement } from "react"

import { type TreeItem } from "~/utils/tree"

interface TreeMenuProps {
  items: TreeItem[]
  openIds?: string[]
  onChange?: (event: MouseEvent<HTMLAnchorElement, globalThis.MouseEvent>, nodeId: string) => void
}

export const TreeMenu: FC<TreeMenuProps> = ({ items, openIds = [], onChange }) => {
  const renderItem = (item: TreeItem): ReactElement => (
    <li key={item.id}>
      {item.children && openIds.includes(item.id) ? (
        <details open>
          <summary>
            <span className="flex items-center gap-cxs">
              {item.icon}
              {item.title}
            </span>
            <div className="float-right">{item.status}</div>
          </summary>
          <ul>{item.children.map(renderItem)}</ul>
        </details>
      ) : item.children ? (
        <details>
          <summary>
            <span className="flex items-center gap-cxs">
              {item.icon}
              {item.title}
            </span>
            <div className="float-right">{item.status}</div>
          </summary>
          <ul>{item.children.map(renderItem)}</ul>
        </details>
      ) : (
        <a onClick={(event) => onChange && onChange(event, item.id)}>
          {item.icon}
          {item.title}
          <div className="float-right">{item.status}</div>
        </a>
      )}
    </li>
  )

  return <ul className="daisymenu rounded-box">{items.map(renderItem)}</ul>
}
