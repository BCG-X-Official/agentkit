import Image from "next/image"

import { useTheme } from "next-themes"
import { APPLICATION_TITLE, getMainLogoSrc } from "~/utils"
import { CONVERSATION_VIEW_SELECTORS } from "./ConversationView.selectors"

// examples are used to show some examples to the user.
const rag_examples = [
  'Get started with AgentKit: "What is the quickest way to get started and run the code?"',
  'Ask questions about the code: "How do I create a new tool?"',
]

const opt_examples = [
  'Define your project and create a schedule: "I want to build 4 features: -Build a RAG tool -Build a SQL tool -Automated evaluation -Customize the UI. Run the optimizer"',
]

interface Props {
  className?: string
  sendMessage: () => Promise<void>
}

const EmptyView = (props: Props) => {
  const { className } = props
  const { resolvedTheme } = useTheme()

  return (
    <div
      className={`${className || ""} flex h-full w-full flex-col items-center justify-start text-black dark:text-black`}
      data-cy={CONVERSATION_VIEW_SELECTORS.emptyChatMessageAreaWrapper}
    >
      {/* <GradientTextSVG /> */}
      <div className="mb-8 flex w-96 max-w-full items-center justify-center font-medium leading-loose">
        <div className="max-w-[500px] rounded-lg">
          <Image src={getMainLogoSrc(resolvedTheme)} alt={APPLICATION_TITLE} width="175" height="175" priority />
        </div>
      </div>
      <div className="group mx-auto flex w-full max-w-full flex-row items-start justify-start rounded-lg bg-base-100 p-4">
        <div className="mr-2 flex h-10 w-10 shrink-0 items-center justify-center rounded-full border bg-gray-950">
          <Image src="/logo.png" width="25" height="25" alt="agent" priority />
        </div>
        <div className="mb-4 w-full px-4 py-3">
          <div className="text-md font-medium">
            <p>
              {" "}
              I&apos;m an AgentKit codebase helper. I can answer questions about the documentation, codebase, and more.
            </p>
          </div>
          <div className="mt-2 text-sm leading-loose text-gray-500 dark:text-gray-500">
            <p>Here are some examples:</p>
            <ol className="mb-4 list-decimal pl-6">
              {rag_examples.map((example, index) => (
                <li key={index}>{example}</li> // NOTE: we can use handleExampleClick to make examples clickable
              ))}
            </ol>
          </div>
          <div className="text-md font-medium">
            <p>
              {" "}
              I can also help you schedule your team&apos;s AgentKit project. Define your backlog, and I will create a
              schedule for you.
            </p>
          </div>
          <div className="mt-2 text-sm leading-loose text-gray-500 dark:text-gray-500">
            <p>Here is an example:</p>
            <ol className="mb-4 list-decimal pl-6">
              {opt_examples.map((example, index) => (
                <li key={index}>{example}</li> // NOTE: we can use handleExampleClick to make examples clickable
              ))}
            </ol>
          </div>
        </div>
      </div>
    </div>
  )
}

export default EmptyView
