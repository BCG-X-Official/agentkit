import { useEffect, useRef } from "react"
import { ErrorBoundary } from "react-error-boundary"
import { type Message, SUPPORTED_SYNTAX_LANGUAGES, type ToolAppendixData } from "@/types"
import CodeFlipCard from "~/components/ToolAppendixRenderer/CodeFlipCard"

interface Props {
  data: ToolAppendixData
  message: Message
  isLatestMessage: boolean
  conversationId: string
}

const ToolAppendixRenderer = (props: Props) => {
  const { data, message, isLatestMessage, conversationId } = props
  const scrollPositionRef = useRef(0)

  useEffect(() => {
    // Capture scroll position before re-render
    scrollPositionRef.current = window.pageYOffset
  }, [])

  useEffect(() => {
    // Restore scroll position after re-render
    window.scrollTo(0, scrollPositionRef.current)
  })

  switch (data.language) {
    case SUPPORTED_SYNTAX_LANGUAGES.SQL:
    case SUPPORTED_SYNTAX_LANGUAGES.JSX:
    case SUPPORTED_SYNTAX_LANGUAGES.CLINGOV_URL:
    case SUPPORTED_SYNTAX_LANGUAGES.YAML:
    case SUPPORTED_SYNTAX_LANGUAGES.JSON:
    case SUPPORTED_SYNTAX_LANGUAGES.PLOTLY:
    case SUPPORTED_SYNTAX_LANGUAGES.IMAGEURL:
      return (
        <ErrorBoundary key={data.value} fallback={null}>
          <CodeFlipCard
            language={data.language}
            value={data.value}
            title={data.title}
            defaultHidden={!isLatestMessage}
            messageId={message.id}
            conversationId={conversationId}
            key={data.value}
          />
        </ErrorBoundary>
      )
    default:
      return (
        <div className="relative w-full">
          <div className="relative left-[calc(-30vw+50%)] w-screen sm:w-[calc(80vw)] lg:w-[calc(60vw)] 2xl:w-[calc(60vw)]">
            <div className="rounded-lg bg-zinc-300 px-4 py-2 dark:bg-zinc-300">
              <div className="mb-2 flex">
                <div className="align-text-center flex h-auto text-center">{data.title}</div>
              </div>
              <div className="mb-2 ml-5 flex">{data.value}</div>
              <div className="flex">
                <div className="align-text-center flex h-auto text-center">
                  <span className="text-sm text-gray-400">
                    Warning: No custom renderer for this tool output defined.
                  </span>
                </div>
              </div>
            </div>
          </div>
        </div>
      )
  }
}

export default ToolAppendixRenderer
