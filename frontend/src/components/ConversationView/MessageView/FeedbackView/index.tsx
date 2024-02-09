/*******************************************************************
 ** Copyright © 2023 Boston Consulting Group. All rights reserved. **
 ********************************************************************/

import { useState } from "react"
import { toast } from "react-hot-toast"
import TextareaAutosize from "react-textarea-autosize"
import { type FeedbackLangchain, type IFeedback, StatisticsService } from "~/api-client"
import { Tooltip } from "~/components/Common/Tooltip/Tooltip"
import Icon from "~/components/CustomIcons/Icon"
import { useMessageStore, useSettingStore } from "~/stores"

interface Props {
  user: string | null | undefined
  messageId: string
  conversationId: string
  feedback?: FeedbackLangchain
}

const FeedbackView = (props: Props) => {
  const { conversationId, messageId, user, feedback } = props
  const [comment, setComment] = useState<string>(feedback?.comment || "")
  const [score, setScore] = useState<number | null>(typeof feedback?.score === "number" ? feedback?.score : null)
  const [loading, setLoading] = useState<boolean>(false)
  const messageStore = useMessageStore()
  const settingsStore = useSettingStore()

  const updateScoreAndSend = async (score: number) => {
    setScore(score)
    sendFeedback(score, comment)
  }

  const sendFeedback = async (score: number, comment: string) => {
    setLoading(true)
    const feedbackUpdate = {
      conversationId: feedback?.feedback_source?.metadata?.conversation_id || conversationId,
      messageId: feedback?.feedback_source?.metadata?.message_id || messageId,
      user: feedback?.feedback_source?.metadata?.user || user || "no-auth",
      previous_id: feedback?.id,
      settings: {
        version: settingsStore.setting.version,
        data: settingsStore.setting.data,
      },
      score: score,
      comment: comment,
      key: "user_feedback",
    } as IFeedback

    await StatisticsService.sendFeedbackApiV1StatisticsFeedbackPost(feedbackUpdate)
      .then((feedbackResponse) => {
        messageStore.updateMessage(messageId, {
          feedback: {
            ...feedbackResponse,
          },
        })
        toast.success("Feedback saved!", { duration: 4000 })
        setLoading(false)
      })
      .catch(() => {
        toast.error("Error sending the feedback")
        setLoading(false)
      })
  }

  return (
    <div className="relative left-[calc(-30vw+50%)] mt-4 w-screen sm:w-[calc(80vw)] lg:w-[calc(60vw)] 2xl:w-[calc(60vw)]">
      <div className="relative">
        <div className="bg-custom-light-green rounded-lg px-4 py-2 dark:bg-zinc-700">
          <div className="flex">
            <div className="align-text-center flex h-auto justify-center text-center">
              <div className="my-1 mr-2">
                <Icon.VscFeedback className="h-auto w-6" />
              </div>
              <b>Feedback</b>
            </div>
          </div>
          <div className="border-t-2 border-dashed border-gray-400" />
          <div className="my-2 flex h-full w-full flex-row items-center justify-between">
            <div className="w-2/3 pr-2">
              <label className="flex w-full flex-col items-start justify-start">
                <span className="text-md mb-1 font-bold text-gray-600 dark:text-gray-400">
                  How would you rate the response?
                </span>
                <div className="flex-col">{/* Content continues here */}</div>
              </label>
            </div>
            <div className="flex w-1/3 items-center justify-center pl-2">
              <div className="flex gap-2">
                <Tooltip content={"Good quality!"} position="daisytooltip-top">
                  <button
                    onClick={() => updateScoreAndSend(1)}
                    className={`rounded px-4 py-2 font-bold transition-colors duration-200 ease-in-out ${
                      score !== null && score === 1
                        ? "bg-green-500 text-white hover:bg-green-700"
                        : "bg-gray-500 text-gray-100 hover:bg-gray-700"
                    }`}
                  >
                    <Icon.FiThumbsUp className="h-6 w-6" />
                  </button>
                </Tooltip>
                <Tooltip content={"Not good enough"} position="daisytooltip-top">
                  <button
                    onClick={() => updateScoreAndSend(0)}
                    className={`rounded px-4 py-2 font-bold transition-colors duration-200 ease-in-out ${
                      score !== null && score === 0
                        ? "bg-red-500 text-white hover:bg-red-700"
                        : "bg-gray-500 text-gray-100 hover:bg-gray-700"
                    }`}
                  >
                    <Icon.FiThumbsDown className="h-6 w-6" />
                  </button>
                </Tooltip>
              </div>
            </div>
          </div>
          <div className="flex h-full w-full flex-col items-start justify-start">
            <div className="dark:bg-bcg-dark mb-4 w-full rounded-lg border border-gray-300 bg-gray-50 text-gray-700 focus:border-blue-500 focus:outline-none dark:border-gray-700 dark:text-gray-300">
              <div className="flex h-auto w-full flex-row items-end justify-between text-clip rounded-lg border dark:border-zinc-700">
                <TextareaAutosize
                  className="hide-scrollbar h-full w-full whitespace-pre-wrap break-all border-none bg-transparent py-2 pl-2 font-mono text-sm leading-6 outline-none"
                  value={comment}
                  rows={5}
                  minRows={5}
                  maxRows={10}
                  placeholder="Please describe what could be improved in the response..."
                  onChange={(e) => setComment(e.target.value)}
                  onKeyDown={(event) => {
                    if (event.key === "Enter") {
                      sendFeedback(score || 0, comment)
                    }
                  }}
                />
                <Tooltip content={"Send Feedback"} position="daisytooltip-top">
                  <button
                    className="bg-bcg-green w-6 -translate-y-2 cursor-pointer rounded-md p-1 text-gray-50 opacity-90 hover:opacity-100 hover:shadow disabled:cursor-not-allowed disabled:opacity-60"
                    onClick={() => sendFeedback(score || 0, comment)}
                    disabled={score != 0 && score != 1}
                  >
                    {loading && <Icon.BiLoaderAlt className="h-auto w-full animate-spin" />}
                    {!loading && <Icon.IoPlay className="h-auto w-full" />}
                  </button>
                </Tooltip>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>
  )
}

export default FeedbackView
