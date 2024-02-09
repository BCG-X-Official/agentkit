# Guidelines for Automated Acceptance Tests

## Local setup

1. Validate in the following config file: `frontend/cypress.config.ts` that the env variables `EMAIL` and `PASSWORD` are allowed accounts. (ie in auth.ts). Alternatively add them to an environment file `frontend/cypress.env.json` and remove them in the configuration.

This auth data should be different from the username/password used to run the app for non-testing purposes (for example in development), to avoid poluting the tests with actual BE data created by the non-testing user.

2. Run cypress (see next section for more info)

## How to run cypress

The two main ways to run cypress are:

1. `pnpm cypress:open` - opens an interactive CY session and runs the individual tests manually. Choose a browser (Chrome recommended) and select the desired test
2. `pnpm cypress:run` - runs all the tests in `headless mode`. This also runs in a `pre-push` hook.

Important: the FE server already needs to be running when running any of these two commands.

There are several more ways to run cypress tests. For example it is possible to target specific tests by using cucmber filters like "@smoke", "@integration" or "@focus" (it is a good practice to add these filters to all test scenarios).

1. `npx cypress run --env tags="@Smoke"`
2. `npx cypress run --env tags="@Smoke or @Integration"`
3. `npx cypress run --env tags="not @Smoke"`

### Terminology and Structure

The basic unit of an automated acceptance test is the *Step*. Each step represents either a user action or a user expectation.

* Action: pressing a button, selecting an option from a dropdown, typing text into an input, ... .
* Expectation: seeing various elements on the page, seeing a success message, seeing an error popup, ... .

Steps can be orchestrated to form more complex *Scenarios*. A scenario is a meaningful set of steps that represents a user flow in our app.
Each scenario combines user actions with user expectations.

Functionally related scenarios are grouped in *Features*. Each feature lives in its own feature file, e.g. `login.feature`. All features
live in the `features` directory. Subdirectories can be created to group features by their common domain.

### Syntax and Semantics

Each step is encoded using the [Gherkin step syntax](https://cucumber.io/docs/gherkin/reference/). User actions start with `When`, user
expectations start with `Then`. All step definitions live in the `step_definitions` directory and its subdirectories.

Scenarios should follow some rules about the Gherkin keywords:

* `Given` is used to establish the test's preconditions.
* `When` is used to indicate user actions.
* `Then` is used to indicate user expectations.
* `And` is used to form more complex preconditions/actions/expectations by concatenation.

Common test preconditions within a feature can be put in a `Background`. An example feature file can look like this:

```gherkin
Feature: Login
  As a customer I want to log in to the application using my user name and password.

  Background:
    Given I have navigated to the home page
    And I open the login modal

  Scenario: Login with invalid username
    And I select "unknown-user-or-password" for mock "post-auth-login"
    When I enter "not_existing@kupferwerk.com" in the mail field
    And I enter "Test1234" in the password field
    And I press the login button
    Then I see the error message for an incorrect mail or password
    And I see the login modal
```

The example shows that Gherkin keywords preceding a step must be in a certain order:

* `Background` definitions always start with `Given` and can be continued with additional `And` steps.
* `Scenario` definitions always start with an `And` or `When`, either to continue the preconditions from the `Background` or to begin a user
action
* `Scenario` definition always end with `Then` or `And`.
* User actions initiated with `When` can be chained using `And` concatenation
* User expectations initiated with `Then` can become more complex using `And` concatenation
* Each `Then` must correspond to a previous `When`

Past tense may be used for `Given` steps. Note that this will bloat the step definitions, because the same action or expectation must
support multiple, slightly different step names, e.g. "Given I have navigated to the account page" vs "When I navigate to the account page".
