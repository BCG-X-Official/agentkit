import { useEffect } from "react"

interface ModalProps {
  uniqueModalId: string
  children: JSX.Element | JSX.Element[]
  actionButtons?: JSX.Element | JSX.Element[]
  onClose?: () => void
}

export const openModal = (modalId: string) => {
  ;(document?.getElementById(modalId) as HTMLDialogElement)?.showModal?.()
}

export const closeModal = (modalId: string) => {
  ;(document?.getElementById(modalId) as HTMLDialogElement)?.close?.()
}

export const isOpen = (modalId: string) => (document?.getElementById(modalId) as HTMLDialogElement)?.open

const InnerModal = ({ uniqueModalId, actionButtons, onClose, children }: ModalProps) => {
  useEffect(() => {
    const handleOnModalCloseEvent = () => {
      onClose?.()
    }
    ;(document?.getElementById(uniqueModalId) as HTMLDialogElement)?.addEventListener("close", handleOnModalCloseEvent)

    return () => window.removeEventListener("keydown", handleOnModalCloseEvent)
  }, [])

  return (
    <dialog id={uniqueModalId} className="daisymodal daisymodal-middle">
      <div className="daisymodal-box relative !max-w-[800px] bg-neutral dark:bg-base-200">
        {children}
        <div className="mt-clg flex justify-end">{actionButtons ?? null}</div>
      </div>
      <form method="dialog" className="daisymodal-backdrop">
        {" "}
        <button />
      </form>
    </dialog>
  )
}

export const Modal = {
  Component: InnerModal,
  openModal,
  closeModal,
  isOpen,
}
