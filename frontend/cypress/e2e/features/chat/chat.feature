@chat
Feature: Chat

Background:
  Given I have a valid session
  And I have navigated to the chat page

@smoke
Scenario: Smoke - Chat page
  Then I see the chat page topbar
  And I see the default chat intro message
  And I see the chat text input area

@integration
Scenario: Chat prompting
  When I type a chat message
  And I send a chat message
  Then I see the filled chat message area
  And I see my user avatar
  And I see the chat message I sent beside the avatar
  Then I see the chat agent steps loading
  And I see the agent response streamed in
  And The response contains an html table
