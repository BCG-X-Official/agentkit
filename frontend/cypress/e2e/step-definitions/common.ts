import { Given } from "@badeball/cypress-cucumber-preprocessor"

Given("I have navigated to the chat page", () => {
  cy.visit("/chat")
})

Given("I have a valid session", () => {
  cy.login("persistent-auth-session") // this preserves cookies and local storage across all tests which means login happens only once, so performance is improved
  cy.visit("/")
})
