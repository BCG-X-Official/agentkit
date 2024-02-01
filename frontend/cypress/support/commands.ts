/// <reference types="cypress" />
// ***********************************************
// This example commands.ts shows you how to
// create various custom commands and overwrite
// existing commands.
//
// For more comprehensive examples of custom
// commands please read more here:
// https://on.cypress.io/custom-commands
// ***********************************************

import { v4 as uuidv4 } from "uuid"

import { authSelectors } from "../support/selectors"

Cypress.Commands.add("dataCy", (selector, ...args) => {
  return cy.get(`[data-cy=${selector}]`, ...args)
})

Cypress.Commands.add(
  "findCy",
  {
    prevSubject: true,
  },
  (subject, selector) => {
    subject.find(`[data-cy=${selector}]`)
    return subject
  }
)

Cypress.Commands.add("login", (sessionName = `session-${uuidv4()}`) => {
  // improve this even more by creating a pure programmatic login using only HTTP requests

  cy.session([sessionName], () => {
    cy.intercept("/api/auth/session").as("session")

    cy.visit("/")

    cy.dataCy(authSelectors.emailInput).type(Cypress.env("EMAIL"), { force: true })
    cy.dataCy(authSelectors.passwordInput).type(Cypress.env("PASSWORD"), { force: true })
    cy.dataCy(authSelectors.signinButton).click()

    cy.wait("@session")
  })
})

declare global {
  namespace Cypress {
    interface Chainable {
      dataCy(selector: string, args?: any): Chainable<JQuery<HTMLElement>>
      findCy(selector: string, args?: any): Chainable<JQuery<HTMLElement>>
      login(sessionName?: string): void
    }
  }
}

export {}
