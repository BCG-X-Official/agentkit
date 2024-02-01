import { Menu, Transition } from "@headlessui/react"
import { Fragment } from "react"

import Icon from "~/components/CustomIcons/Icon"

function classNames(...classes: any) {
  return classes.filter(Boolean).join(" ")
}

type MultiButtonDropdownProps = {
  title: string
  items: {
    key: string
    title: string
    onClick: () => void
  }[]
  isInline?: boolean
}

export const MultiButtonDropdown = ({ title, items, isInline }: MultiButtonDropdownProps) => {
  return (
    <Menu as="div" className="relative inline-block items-center text-left">
      <Menu.Button
        className={`inline-flex w-full items-center justify-center hover:bg-[#eee] ${
          isInline
            ? "mb-1 gap-x-1 rounded-md bg-white text-xs font-semibold text-gray-900 text-opacity-60"
            : "gap-x-1.5 rounded-md bg-white p-2 text-sm font-semibold text-gray-900 shadow-sm ring-1 ring-inset ring-gray-300"
        }`}
      >
        {title}
        <Icon.BiChevronDown className="-mr-1 h-5 w-5 text-gray-400" aria-hidden="true" />
      </Menu.Button>

      <Transition
        as={Fragment}
        enter="transition ease-out duration-100"
        enterFrom="transform opacity-0 scale-95"
        enterTo="transform opacity-100 scale-100"
        leave="transition ease-in duration-75"
        leaveFrom="transform opacity-100 scale-100"
        leaveTo="transform opacity-0 scale-95"
      >
        <Menu.Items className="absolute z-10 mt-2 w-56 origin-top-right rounded-md bg-white shadow-lg ring-1 ring-black/5 focus:outline-none">
          <div className="py-1">
            {items.map((item) => (
              <Menu.Item key={item.key}>
                {({ active }) => (
                  <button
                    className={`flex w-full justify-start ${classNames(
                      active ? "bg-gray-100 text-gray-900" : "text-gray-700",
                      "block px-4 py-2 text-sm"
                    )}`}
                    onClick={item.onClick}
                  >
                    {item.title}
                  </button>
                )}
              </Menu.Item>
            ))}
          </div>
        </Menu.Items>
      </Transition>
    </Menu>
  )
}
