import { type ReactElement } from "react"

import ReactMarkdown from "react-markdown"
import rehypeRaw from "rehype-raw"
import remarkGfm from "remark-gfm"

import { CodeBlock } from "./CodeBlock"

interface Props {
  text: string
  messageId?: string
  conversationId?: string
}

export const Markdown = (props: Props) => {
  const { text, messageId, conversationId } = props
  return (
    <ReactMarkdown
      remarkPlugins={[remarkGfm]}
      rehypePlugins={[rehypeRaw]}
      components={{
        pre({ className, children, ...props }) {
          const child = children[0] as ReactElement
          const match = /language-(\w+)/.exec(child.props.className || "")
          const language = match ? match[1] : "code"

          const code = child.props.children[0].replace("\n", " ").trim()
          if (!messageId || !conversationId) return code
          return (
            <pre className={`${className || ""} mb-1 w-full p-0`} {...props}>
              <CodeBlock
                key={Math.random()}
                language={language || "code"}
                value={code}
                messageId={messageId}
                conversationId={conversationId}
                {...props}
              />
            </pre>
          )
        },
        code({ children }) {
          return <code className="px-0">{children}</code>
        },
        p({ children }) {
          return <p className="my-0">{children}</p>
        },
      }}
    >
      {text}
    </ReactMarkdown>
  )
}
