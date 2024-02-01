@chatConversationSidebar
Feature: Chat conversation sidebar

Background:
  Given I have a valid session
  And I have navigated to the chat page

@smoke
Scenario: Smoke - Chat conversation sidebar
  Then I see the collapsed conversation sidebar

@integration
Scenario: Creating a chat when the sidebar is collapsed
  Then I see the collapsed sidebar expanded chat list
  And The collapsed sidebar chat list is empty
  When I click on the collapsed sidebar add chat button
  Then I see one collapsed sidebar chat created

@integration
Scenario: Creating a chat when the sidebar is expanded
  When I click on the expand sidebar button
  Then I see the expanded conversation sidebar
  And I see the expanded sidebar expanded chat list
  When I click on the expanded sidebar add chat button
  Then I see one expanded sidebar chat created

@integration
Scenario: Deleting a chat
  When I click on the expand sidebar button
  Then I see the expanded conversation sidebar
  And I see the expanded sidebar expanded chat list
  When I click on the expanded sidebar add chat button
  Then I see one expanded sidebar chat created
  When I click on chat the ellipsis button
  Then I see the edit and delete dropdown menu items
  When I click on the delete chat button
  Then The expanded sidebar chat list is empty

@integration
Scenario: Editing a chat title
  When I click on the expand sidebar button
  Then I see the expanded conversation sidebar
  And I see the expanded sidebar expanded chat list
  When I click on the expanded sidebar add chat button
  Then I see one expanded sidebar chat created
  When I click on chat the ellipsis button
  Then I see the edit and delete dropdown menu items
  When I click on the edit chat button
  Then I see the updated chat modal with the correct title
  When I type in a new chat title
  And I click on the save chat update button
  Then I see the new chat title applied
