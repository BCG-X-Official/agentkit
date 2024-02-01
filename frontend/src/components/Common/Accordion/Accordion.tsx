import clsx from "clsx"
import { useState } from "react"

interface AccordionProps {
  accordionID: string
  iconPosition?: string
  items?: {
    key: string
    title?: string | JSX.Element
    content?: string | JSX.Element
    CustomToggleIcon?: JSX.Element
    onToggle?: (id: string) => void
    isOpen?: boolean
    tooltipText?: string
    enableHeaderInteraction?: boolean
    showBorder?: boolean
  }[]
  forceAccordionItemsToggle?: boolean
}

const getItemKey = (key: string, index: number) => `${key}-${index}`

export const Accordion = ({ accordionID, items, forceAccordionItemsToggle, iconPosition }: AccordionProps) => {
  const initialState =
    items?.reduce(
      (accu, item, index) => ({
        ...accu,
        [getItemKey(item?.key, index)]: item?.isOpen ?? forceAccordionItemsToggle ?? false,
      }),
      {}
    ) ?? {}

  const [show, setShow] = useState<Record<string, boolean>>(initialState)

  const toggleShow = (value: object) => {
    setShow({ ...show, ...value })
  }

  return (
    <div className="daisyjoin daisyjoin-vertical w-full">
      {items?.map(
        (
          { key, enableHeaderInteraction, CustomToggleIcon, showBorder = true, tooltipText, onToggle, title, content },
          index
        ) => {
          const accordionItemKey = getItemKey(key, index)

          const inputClasses = clsx("!outline-rounded hover:cursor-pointer", {
            ["relative"]: enableHeaderInteraction,
          })

          const headerClasses = clsx("daisycollapse", {
            ["daisycollapse-arrow"]: !CustomToggleIcon,
            ["shadow-[rgba(50,50,93,0.25)_0px_6px_12px_-2px,_rgba(0,0,0,0.3)_0px_3px_7px_-3px]"]: showBorder,
          })

          const titleClasses = clsx("daisycollapse-title flex justify-between items-center", {
            ["[&>*]:relative [&>*]:z-10"]: enableHeaderInteraction,
            ["after:!right-[50%]"]: iconPosition === "center" && !title,
          })

          return (
            <div key={key} className={headerClasses}>
              <input
                type="radio"
                title={tooltipText ?? ""}
                name={accordionID}
                checked={show[accordionItemKey]}
                onClick={() => {
                  onToggle?.(key)
                  toggleShow({ ...show, [accordionItemKey]: !show[accordionItemKey] })
                }}
                onChange={() => undefined}
                className={inputClasses}
              />
              <div className={titleClasses}>
                {title} {CustomToggleIcon ? <span>{CustomToggleIcon}</span> : null}
              </div>
              <div className="daisycollapse-content !px-cxs">{content}</div>
            </div>
          )
        }
      )}
    </div>
  )
}
