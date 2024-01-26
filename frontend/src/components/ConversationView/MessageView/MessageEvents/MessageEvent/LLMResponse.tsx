import { useMemo } from "react"
import { Markdown } from "~/components/CodeView/Markdown"
import { CONVERSATION_VIEW_SELECTORS } from "~/components/ConversationView/ConversationView.selectors"
import Icon from "../../../../CustomIcons/Icon"

interface Props {
  text: string
  messageId: string
  conversationId: string
}

export const LLMResponse = (props: Props) => {
  const { text, messageId, conversationId } = props

  const thoughtRegex = /Thought:\s?([\s\S]*?)\s?(?:Action)/g
  const thoughtFinalRegex = /Thought:\s?([\s\S]*?)\s?(?:FINAL_ANSWER)/g
  const thoughtProcessRegex = /Thought:\s?([\s\S]*?)$/g
  const finalAnswerRegex = /FINAL_ANSWER:\s?([\s\S]*)/
  const anyTextRegex = /([\s\S]*)/

  const extractedThoughtMatch = thoughtRegex.exec(text)
  const thoughtFinalRegexMatch = thoughtFinalRegex.exec(text)
  const thoughtProcessRegexMatch = thoughtProcessRegex.exec(text)
  const finalAnswerMatch = finalAnswerRegex.exec(text)
  const anyTextMatch = anyTextRegex.exec(text)

  const thought = useMemo(() => {
    if (extractedThoughtMatch) return extractedThoughtMatch[1]
    if (thoughtFinalRegexMatch) return thoughtFinalRegexMatch[1]
    if (thoughtProcessRegexMatch) return thoughtProcessRegexMatch[1]
    return null
  }, [text])

  const finalResponse = useMemo(() => {
    if (finalAnswerMatch) return finalAnswerMatch[1]

    if (anyTextMatch) {
      const isPrintingThoughts =
        anyTextMatch[1]?.startsWith("Thought: ") ||
        anyTextMatch[1] === "Thought: ".substring(0, anyTextMatch[1]?.length || 0)
      return isPrintingThoughts ? null : anyTextMatch[1]
    }
    return null
  }, [text])

  if (!thought && !finalResponse) return null

  return (
    <div className="mb-1 w-auto">
      {thought && !finalResponse && (
        <div className="mt-1 flex w-full flex-wrap" data-cy={CONVERSATION_VIEW_SELECTORS.chatResponseMarkdown}>
          <span className="my-1 mr-2 h-auto w-6 text-accent">
            <Icon.IoChatbubbleEllipsesOutline className="h-auto w-6" />
          </span>
          <div className="w-auto max-w-[calc(100%-2rem)]">
            <Markdown text={thought} messageId={messageId} conversationId={conversationId} />
          </div>
        </div>
      )}
      {finalResponse && (
        <div className="mt-3 flex w-full flex-wrap border-t-2 border-dashed border-gray-400 pt-3">
          <span className="mb-1 mr-2 h-auto w-6 text-accent">
            <Icon.SiAnswer className="h-auto w-6" />
          </span>
          <div className="w-auto max-w-[calc(100%-2rem)]">
            <Markdown text={finalResponse} messageId={messageId} conversationId={conversationId} />
          </div>
        </div>
      )}
    </div>
  )
}
