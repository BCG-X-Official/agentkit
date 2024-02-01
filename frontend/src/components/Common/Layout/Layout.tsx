import { type FC } from "react"

export const Layout: FC<{ children: JSX.Element | JSX.Element[] }> = ({ children }) => (
  <div className="h-full w-full !overflow-x-hidden overflow-y-scroll [&>div]:h-full">{children}</div>
)
