import { Then, When } from "@badeball/cypress-cucumber-preprocessor"

import { chatSelectors } from "../../../support/selectors"

const {
  collapsedSidebarWrapper,
  collapsedSidebarChatList,
  expandedSidebarChatList,
  expandSidebarButton,
  expandedSidebarWrapper,
  collapsedChatListItem,
  expandedChatListItem,
  collapsedAddChatButton,
  expandedAddChatButton,
  chatEllipsisButton,
  editChatButton,
  deleteChatButton,
  updateChatContentWrapper,
  updateChatTextField,
  saveChatButton,
  topbarWrapper,
} = chatSelectors

Then("I see the collapsed conversation sidebar", () => {
  cy.dataCy(collapsedSidebarWrapper).should("exist")
})

Then("I see the collapsed sidebar expanded chat list", () => {
  cy.dataCy(collapsedSidebarChatList).should("exist")
})

Then("I see the expanded sidebar expanded chat list", () => {
  cy.dataCy(expandedSidebarChatList).should("exist")
})

Then("The collapsed sidebar chat list is empty", () => {
  cy.dataCy(collapsedSidebarChatList).find(collapsedChatListItem).should("have.length", 0)
})

Then("The expanded sidebar chat list is empty", () => {
  cy.dataCy(expandedSidebarChatList).find(expandedChatListItem).should("have.length", 0)
})

When("I click on the collapsed sidebar add chat button", () => {
  cy.dataCy(collapsedAddChatButton).click()
})

When("I click on the expanded sidebar add chat button", () => {
  cy.dataCy(expandedAddChatButton).click()
})

Then("I see one collapsed sidebar chat created", () => {
  cy.dataCy(collapsedSidebarWrapper).findCy(collapsedChatListItem).should("have.length", 1)
})

Then("I see one expanded sidebar chat created", () => {
  cy.dataCy(expandedSidebarWrapper).findCy(expandedChatListItem).should("have.length", 1)
})

When("I click on the expand sidebar button", () => {
  cy.dataCy(expandSidebarButton).click()
})

Then("I see the expanded conversation sidebar", () => {
  cy.dataCy(expandedSidebarWrapper).should("exist")
})

When("I click on chat the ellipsis button", () => {
  cy.dataCy(chatEllipsisButton).click({ force: true })
})

Then("I see the edit and delete dropdown menu items", () => {
  cy.dataCy(deleteChatButton).should("exist")
  cy.dataCy(editChatButton).should("exist")
})

When("I click on the delete chat button", () => {
  cy.dataCy(deleteChatButton).click({ force: true })
})

When("I click on the edit chat button", () => {
  cy.dataCy(editChatButton).click({ force: true })
})

Then("I see the updated chat modal with the correct title", () => {
  cy.dataCy(updateChatContentWrapper).should("exist")
  cy.dataCy(updateChatContentWrapper).find("h3").contains("Update chat")
})

const updatedChatTitle = "This is an updated chat title"

When("I type in a new chat title", () => {
  cy.dataCy(updateChatTextField).type(updatedChatTitle, { force: true })
})

When("I click on the save chat update button", () => {
  cy.dataCy(saveChatButton).click({ force: true })
})

Then("I see the new chat title applied", () => {
  cy.dataCy(topbarWrapper).find("h1").contains(updatedChatTitle)
})
