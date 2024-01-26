interface Props {
  message: string
  style: "info" | "error"
}

const NotificationView = (props: Props) => {
  const { message, style } = props
  const additionalStyle = style === "error" ? "text-red-500" : "text-gray-500"
  return <p className={`${additionalStyle} mt-4 w-full whitespace-pre-wrap pl-4 font-mono text-sm`}>{message}</p>
}

export default NotificationView
