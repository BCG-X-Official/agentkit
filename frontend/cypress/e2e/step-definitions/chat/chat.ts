import { Before, Then, When } from "@badeball/cypress-cucumber-preprocessor"

import { CHAT_MESSAGES } from "./chat-messages.config"

import { chatSelectors } from "../../../support/selectors"

const {
  topbarWrapper,
  textInputArea,
  emptyChatMessageAreaWrapper,
  sendMessageButton,
  filledChatMessageAreaWrapper,
  userAvatar,
  userMessage,
  stepsWrapper,
  stepsLoading,
  chatResponseMarkdown,
} = chatSelectors

Before(() => {
  cy.intercept("/api/v1/chat/agent").as("chatAgent")
})

Then("I see the chat page topbar", () => {
  cy.dataCy(topbarWrapper).should("exist")
})

Then("I see the chat text input area", () => {
  cy.dataCy(textInputArea).should("exist")
})

Then("I see the default chat intro message", () => {
  cy.dataCy(emptyChatMessageAreaWrapper).should("exist")
})

When("I type a chat message", () => {
  cy.dataCy(textInputArea).type(CHAT_MESSAGES.prompt1.text)
})

When("I send a chat message", () => {
  cy.dataCy(sendMessageButton).click()
})

Then("I see the filled chat message area", () => {
  cy.dataCy(filledChatMessageAreaWrapper).should("exist")
})

Then("I see my user avatar", () => {
  cy.dataCy(userAvatar).should("exist")
})

Then("I see the chat message I sent beside the avatar", () => {
  cy.dataCy(userMessage).should("exist").contains(CHAT_MESSAGES.prompt1.text)
})

Then("I see the chat agent steps", () => {
  cy.dataCy(stepsWrapper).should("exist")
})

Then("I see the chat agent steps loading", () => {
  cy.dataCy(stepsLoading).should("exist")
})

Then("I see the agent response streamed in", () => {
  cy.wait("@chatAgent", {
    responseTimeout: 300000,
  })
    .its("request.body")
    .should("exist")

  cy.dataCy(chatResponseMarkdown).should("exist")
})

Then("The response contains an html table", () => {
  if (CHAT_MESSAGES.prompt1.hasAnHtmlTableComponent) {
    cy.dataCy(chatResponseMarkdown).find("table").should("exist")
  }
})
