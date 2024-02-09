import * as DropdownUI from "@radix-ui/react-dropdown-menu"
import { type ReactNode } from "react"

interface Props {
  children: ReactNode
  tigger: ReactNode
}

export const Dropdown = (props: Props) => {
  const { children, tigger } = props

  return (
    <DropdownUI.Root modal={false}>
      <DropdownUI.Trigger asChild onClick={(e: { stopPropagation: () => any }) => e.stopPropagation()}>
        {tigger}
      </DropdownUI.Trigger>
      <DropdownUI.Portal>
        <DropdownUI.Content className="z-[999] drop-shadow" sideOffset={5}>
          {children}
        </DropdownUI.Content>
      </DropdownUI.Portal>
    </DropdownUI.Root>
  )
}

export const DropdownItem = DropdownUI.Item
