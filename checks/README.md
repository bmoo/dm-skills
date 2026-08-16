# Checks

A check belongs here only when it verifies shipped content or a consumer's
repository and does not itself ship. Checks over this repository's own
maintenance documents do not get written.

| What is being checked | Where its check lives | Why |
| --- | --- | --- |
| Behaviour that ships with a skill | Beside that skill, for example `skills/build-session/scripts/` | The skill ships the code and its tests together. |
| Shipped content that must stay behind | Its own subdirectory of `checks/`, for example `checks/wiki/` | It verifies a shipped asset without becoming part of the asset. |
| Shipped assets with no code | No check directory | There is no code to house or exercise. |

Each subdirectory is independent: no code is shared between `checks/`
subdirectories. Duplication is intentional so one check cannot pull another's
abstractions into its scope.
