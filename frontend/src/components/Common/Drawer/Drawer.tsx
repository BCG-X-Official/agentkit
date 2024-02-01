import { AnimatePresence, motion } from "framer-motion"
import { useEffect, useRef, useState } from "react"

import { useClickOutside } from "@react-hookz/web"

interface DrawerV2Props {
  side?: "left" | "right"
  pushPageContent?: boolean
  footer?: (toogle: () => void) => JSX.Element
  expandedHeader?: JSX.Element
  colapsedHeader?: (toogle: () => void) => JSX.Element
  children: JSX.Element | JSX.Element[]
  showOverlay?: boolean
  contentWrapperClasses?: string
  innerWrapperClasses?: string
  isOpen?: boolean
  onToggle?: (open?: boolean) => void
}

export const Drawer = ({
  side = "left",
  pushPageContent = false,
  footer,
  expandedHeader,
  colapsedHeader,
  showOverlay = false,
  contentWrapperClasses = "",
  innerWrapperClasses = "",
  isOpen = false,
  onToggle,
  children,
}: DrawerV2Props) => {
  const [open, setOpen] = useState(false)

  const ref = useRef(null)
  useClickOutside(ref, () => showOverlay && setOpen(false))
  const toggle = () => setOpen((prev) => !prev)

  const e2eDrawerXPosition = side === "left" ? "-100%" : "100%"

  const framerDrawerPanel = {
    initial: { x: e2eDrawerXPosition },
    animate: { x: 0 },
    exit: { x: e2eDrawerXPosition },
    transition: { duration: 0.2 },
  }

  const e2eContentXPosition = side === "left" ? "-50" : "50"

  const framerSection = (delay: number) => {
    return {
      initial: { opacity: 0, x: e2eContentXPosition },
      animate: { opacity: 1, x: 0 },
      transition: {
        delay: 0.3 + delay / 10,
      },
    }
  }

  useEffect(() => {
    onToggle?.(open)
  }, [open])

  useEffect(() => {
    setOpen(isOpen)
  }, [isOpen])

  return (
    <>
      <AnimatePresence mode="wait" initial={false}>
        {!open && colapsedHeader && (
          <motion.div
            className={`flex items-center justify-center bg-base-100 px-cxs py-clg dark:!bg-base-200 ${
              side === "right" ? "border-l-[2px] dark:!border-l-base-100" : "border-r-[2px] dark:!border-r-base-100"
            } 3xl:!min-w-[75px] daisydrawer-button !min-w-[35zpx] md:!min-w-[55px]`}
          >
            {colapsedHeader(toggle)}
          </motion.div>
        )}
        {open && (
          <>
            {showOverlay && (
              <motion.div
                {...framerDrawerBackground}
                aria-hidden="true"
                className="fixed inset-0 z-40 bg-[rgba(0,0,0,0.1)] backdrop-blur-sm"
              ></motion.div>
            )}
            <motion.div
              {...framerDrawerPanel}
              className={`flex flex-col justify-between gap-cmd px-csm shadow-[rgba(50,50,93,0.25)_0px_6px_12px_-2px,_rgba(0,0,0,0.3)_0px_3px_7px_-3px] ${
                pushPageContent ? "fixed md:relative" : "fixed"
              } inset-y-0 ${
                side === "left" ? "left-0" : "right-0"
              } z-50 ${contentWrapperClasses} h-full bg-base-100 p-cmd dark:bg-base-200 ${
                side === "left"
                  ? "!z-[100] !border-l-neutral dark:border-r-[2px]  dark:!border-r-base-100"
                  : "!border-l-neutral dark:border-l-[2px] dark:!border-l-base-100"
              }`}
              ref={ref}
            >
              {expandedHeader ? (
                <motion.div {...framerSection(0)} className="flex w-full justify-center">
                  {expandedHeader}
                </motion.div>
              ) : null}
              <ul className={`h-full max-h-[calc(96%-90px)] overflow-auto px-c2xs ${innerWrapperClasses}`}>
                <motion.div {...framerSection(1)}>{children}</motion.div>
              </ul>
              {footer ? (
                <motion.div {...framerSection(2)} className="flex w-full justify-center">
                  {footer(toggle)}
                </motion.div>
              ) : null}
            </motion.div>
          </>
        )}
      </AnimatePresence>
    </>
  )
}

const framerDrawerBackground = {
  initial: { opacity: 0 },
  animate: { opacity: 1 },
  exit: { opacity: 0, transition: { delay: 0.2 } },
  transition: { duration: 0.3 },
}
