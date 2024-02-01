import clsx from "clsx"
import { isArray } from "lodash-es"
import { type FC, type ReactElement, useEffect } from "react"

import { useDeepCompareEffect } from "~/hooks"
import { LIGHT_THEME } from "~/styles/themes"

import { type TabItemProps } from "./TabItem"
import { useTabsStore } from "./tabs-store"
import { Tooltip } from "../Tooltip/Tooltip"

type TabItemChild = ReactElement<TabItemProps>

interface TabsProps {
  children: TabItemChild | TabItemChild[]
  forcedActiveTab?: string
  classNames?: string
  fixed?: boolean
}

export const Tabs: FC<TabsProps> = ({ children, forcedActiveTab, classNames, fixed }) => {
  const { activeTab, setActiveTab, tabItems, setTabItems } = useTabsStore()

  useDeepCompareEffect(() => {
    const initState = forcedActiveTab ?? activeTab ?? tabItems?.[0]?.label
    setActiveTab(initState)
  }, [tabItems])

  useEffect(() => {
    const newTabItems = isArray(children) ? children : [children]
    setTabItems(newTabItems.map((child) => child.props))
  }, [children])

  const handleClick = (newActiveTab: string) => {
    setActiveTab(newActiveTab)
  }

  const zIndex: Record<number, string> = tabItems.reduce(
    (accu, _, index) => ({
      ...accu,
      [index]: (tabItems.length - index) * 10,
    }),
    {}
  )

  const left: Record<number, string> = tabItems.reduce(
    (accu, _, index) => ({
      ...accu,
      [index]: `-${index * 8}px`,
    }),
    {}
  )

  const getButtonClasses = (label: string) =>
    clsx(
      "w-full flex flex-1 items-center justify-center p-2 text-gray-700 w-full font-medium rounded-t-[10px] shadow-[rgba(50,50,93,0.25)_0px_6px_12px_-2px,_rgba(0,0,0,0.3)_0px_3px_7px_-3px] min-w-[75px] bg-neutral dark:bg-base-100 relative",
      {
        "border-b-2 border-b-accent": activeTab === label,
      },
      activeTab === label ? `border-[${LIGHT_THEME.colors?.accent}]` : ""
    )

  return (
    <div className={`mx-auto w-full ${classNames}`}>
      <div className="w-full bg-transparent pb-csm">
        <div
          className={`w-fullbg-transparent flex max-h-[40px] w-[96%] border-gray-300 lg:max-h-[50px] 2xl:w-[97%] ${
            fixed ? "absolute z-[1000]" : "relative"
          }`}
        >
          {tabItems.map((tabItem: TabItemProps, index) => {
            const { label, showTooltip, hideLabel, icon } = tabItem

            return (
              <Tooltip
                key={label}
                content={showTooltip ? label : ""}
                position="daisytooltip-bottom"
                wrapperClasses="!w-full"
              >
                <button
                  style={{
                    zIndex: activeTab === label ? 1000 : zIndex[index],
                    left: left[index],
                    borderBottom: activeTab === label ? `2px solid $${LIGHT_THEME.colors?.accent}` : undefined,
                  }}
                  className={getButtonClasses(label)}
                  onClick={() => handleClick(label)}
                >
                  {icon ? <span className={hideLabel ? "p-1 [&>svg]:text-xl" : "p-1"}>{icon}</span> : null}
                  {!hideLabel ? label : ""}
                </button>
              </Tooltip>
            )
          })}
        </div>
      </div>
      <div
        className={`max-h-[calc(100vh-170px-3rem)] !overflow-y-auto py-4 pr-cxs md:!max-h-[calc(100vh-270px-3rem)] lg:!max-h-[calc(100vh-350px-3rem)] ${
          fixed ? "mt-12" : ""
        }`}
      >
        {tabItems.map((tabItem: TabItemProps) => {
          const { label, children } = tabItem

          if (label === activeTab) {
            return (
              <div key={label} className="visible">
                {children}
              </div>
            )
          }

          return (
            <div key={label} className="hidden">
              {children}
            </div>
          )
        })}
      </div>
    </div>
  )
}
