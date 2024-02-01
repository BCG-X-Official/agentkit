import copy from "copy-to-clipboard"
import { toast } from "react-hot-toast"
import { Prism as SyntaxHighlighter } from "react-syntax-highlighter"
import { oneDark } from "react-syntax-highlighter/dist/cjs/styles/prism"

import { Tooltip } from "~/components/Common"
import Icon from "~/components/CustomIcons/Icon"
import { useQueryStore } from "~/stores"

interface Props {
  language: string
  value: string
  messageId: string
  conversationId: string
}

export const CodeBlock = (props: Props) => {
  const { language, value, messageId, conversationId } = props
  const queryStore = useQueryStore()

  const showExecuteButton = language.toUpperCase() === "SQL"

  const copyToClipboard = () => {
    copy(value)
    toast.success("Copied to clipboard")
  }

  const handleExecuteQuery = () => {
    queryStore.setContext({
      statement: value,
      messageId: messageId,
      conversationId: conversationId,
    })
    queryStore.toggleDrawer(true)
  }

  return (
    <div className="relative w-full max-w-full font-sans text-[16px]">
      <div className="flex items-center justify-between px-4 py-2">
        <span className="font-mono text-xs text-white">{language}</span>
        <div className="flex items-center space-x-2">
          <Tooltip content="Copy" position="daisytooltip-top">
            <button
              className="flex h-6 w-6 items-center justify-center rounded bg-gray-500 bg-none p-1 text-xs text-white opacity-70 hover:opacity-100"
              onClick={copyToClipboard}
            >
              <Icon.BiClipboard className="h-auto w-full" />
            </button>
          </Tooltip>
          {showExecuteButton && (
            <Tooltip content="Open & Edit" position="daisytooltip-top">
              <button
                className="flex h-6 w-6 items-center justify-center rounded bg-accent bg-none p-1 text-xs text-white opacity-90 hover:opacity-100"
                onClick={handleExecuteQuery}
              >
                <Icon.IoOpenOutline className="h-auto w-full" />
              </button>
            </Tooltip>
          )}
        </div>
      </div>
      <SyntaxHighlighter language={language.toLowerCase()} style={oneDark} customStyle={{ margin: 0 }}>
        {value}
      </SyntaxHighlighter>
    </div>
  )
}
