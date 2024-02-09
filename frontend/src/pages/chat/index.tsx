import { type NextPage } from "next"
import dynamic from "next/dynamic"
import Head from "next/head"

import { TopWarningBanner } from "~/components/Common"
import { APPLICATION_TITLE } from "~/utils"

// Use dynamic import to avoid page hydrated.
// reference: https://github.com/pmndrs/zustand/issues/1145#issuecomment-1316431268
const ConversationSidebar = dynamic(() => import("~/components/ConversationSidebar"), {
  ssr: false,
})
const ConversationView = dynamic(() => import("~/components/ConversationView"), {
  ssr: false,
})
const SideDrawer = dynamic(() => import("~/components/CodeView/SideDrawer"), {
  ssr: false,
})

const ChatLanding: NextPage = () => {
  return (
    <>
      <Head>
        <title>{APPLICATION_TITLE}</title>
        <meta name="AgentKit @ BCG.X" content="By BCG X" />
        <link rel="icon" href="/favicon.ico" />
      </Head>
      <main className="flex h-full w-full flex-col bg-neutral dark:bg-base-300">
        <div className="sticky top-0 z-1 flex w-full flex-col items-start justify-start bg-accent dark:bg-accent dark:text-neutral">
          <TopWarningBanner />
        </div>

        <div className="flex h-full w-full flex-row !overflow-hidden">
          <ConversationSidebar />
          <ConversationView />
          <SideDrawer />
        </div>
      </main>
    </>
  )
}

export default ChatLanding
