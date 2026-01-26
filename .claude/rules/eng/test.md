---
path: {src,test,tests}/**/*.*
---

# Kinds of Tests

A test can be classified into one of the following kinds:

## Integration Tests (IT)
Tests that validate the integration between some subset of the system (potentially the entire system) and external dependencies or services. in these kinds of tests, the system is debuggable via the ide, but external dependencies are dockerized using testcontainers e.g., testing a repository's integration with a live, locally running database instance, integrating with 2nd or 3rd party services, message queues, etc. These test should be used only to validate such integrations. They should not be used to validate business logic that can be tested without external dependencies.

## Unit Tests (Unit)
Tests that validate individual functions, classes, or small modules in isolation. These focus on a single unit of code with minimal dependencies, using mocks or stubs for collaborators when needed. Unit tests verify implementation correctness at a granular level—edge cases, error handling, and algorithmic behavior. File system tests using local temp files are still unit tests. Use these when testing logic that doesn't span multiple layers or when you need fine-grained feedback on specific, relatively isolated components.
