You are contributing to a small, structured software system built for an engineering assessment.

Your objective is to produce simple, correct, and maintainable code.

This is NOT a feature-building task.
This is a system integrity task.

You MUST follow these rules strictly.

--------------------------------------
CORE ARCHITECTURE RULES
--------------------------------------

The system follows strict boundaries:

- routes/ → HTTP layer only
- schemas/ → Input validation and serialization only
- services/ → Business rules and domain logic
- repositories/ → Database interaction only
- models/ → SQLAlchemy models only

You MUST NOT:
- Put business logic in routes
- Put validation logic in repositories
- Access the database outside repositories
- Modify schema fields without explicit request
- Introduce global state

--------------------------------------
DOMAIN SAFETY RULES
--------------------------------------

The system contains a Decision entity with a status enum.

Valid statuses:
- PROPOSED
- ACCEPTED
- REJECTED

Valid transitions:
- PROPOSED → ACCEPTED
- PROPOSED → REJECTED

Invalid transitions:
- ACCEPTED → anything
- REJECTED → anything
- ACCEPTED → REJECTED
- REJECTED → ACCEPTED

These rules MUST be enforced centrally inside the service layer.

You MUST NOT:
- Bypass state transition checks
- Modify status values directly in repository
- Duplicate transition logic in multiple places

--------------------------------------
CHANGE MANAGEMENT RULES
--------------------------------------

If implementing a new feature:

1. Modify only the minimal required files
2. Do NOT refactor unrelated code
3. Preserve existing method signatures
4. Add tests for any new behavior
5. Explain reasoning before showing code

--------------------------------------
SIMPLICITY RULE
--------------------------------------

Prefer:
- Explicit > clever
- Readable > abstract
- Small functions > reusable abstractions
- Duplication > premature abstraction

Avoid:
- Generic base classes
- Over-engineered patterns
- Meta-programming
- Unnecessary dependency injection
- Magic decorators

--------------------------------------
DATABASE RULES
--------------------------------------

- Use SQLAlchemy ORM
- Do not write raw SQL unless necessary
- Use UUID for primary keys
- Add constraints where possible
- Avoid nullable fields unless justified

--------------------------------------
VALIDATION RULES
--------------------------------------

- Validate all input using schemas
- Never trust client data
- Enforce non-empty title
- Enforce max length constraints
- Raise domain-specific errors

--------------------------------------
ERROR HANDLING
--------------------------------------

- Create explicit exception classes
- Never return silent failures
- Log meaningful errors
- Avoid exposing internal stack traces

--------------------------------------
TESTING REQUIREMENTS
--------------------------------------

For every new behavior:

- Add unit tests
- Add at least one negative test case
- Test invalid state transitions
- Use pytest
- Keep tests simple and readable

Do NOT skip tests.

--------------------------------------
AI CONDUCT RULES
--------------------------------------

Before generating code:
- Briefly explain what you will change
- Justify why the change is safe
- Confirm no architectural rules are violated

After generating code:
- Summarize impact
- Identify potential risks

You are not allowed to:
- Invent new architecture layers
- Change directory structure
- Add unrelated improvements
- Add logging frameworks beyond Python logging
- Introduce async unless explicitly required

--------------------------------------
ASSESSMENT PRIORITY
--------------------------------------

The goal is NOT feature richness.

The goal is:
- Correctness
- Clear boundaries
- Enforced invariants
- Change resilience
- Testability

If unsure, choose the simpler solution.