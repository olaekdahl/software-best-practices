Feature: Calculator basic operations
  As a user
  I want to add and divide numbers safely
  So that I can compute simple results

  Scenario: Add two positive numbers
    Given numbers 2 and 3
    When I add them
    Then the result is 5

  Scenario: Divide by zero should fail
    Given numbers 1 and 0
    When I divide them
    Then an error is raised
