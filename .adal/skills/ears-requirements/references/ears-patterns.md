# EARS Pattern Reference

## Pattern Templates

- Ubiquitous: `The <system> shall <response>.`
- State-driven: `While <precondition>, the <system> shall <response>.`
- Event-driven: `When <trigger>, the <system> shall <response>.`
- Optional-feature: `Where <feature is included>, the <system> shall <response>.`
- Unwanted-behavior: `If <undesired trigger>, then the <system> shall <response>.`
- Complex: `While <precondition>, when <trigger>, the <system> shall <response>.`

## Pattern Selection Heuristic

- Choose Ubiquitous when behavior is always true.
- Choose State-driven when behavior is active only in a continuous condition.
- Choose Event-driven when behavior is caused by a discrete event.
- Choose Optional-feature when requirement applies only if a feature exists.
- Choose Unwanted-behavior when specifying mitigation or recovery.
- Choose Complex when both state and event are required to activate behavior.

## Examples

- Ubiquitous: `The mobile phone shall have a mass of less than <MAX_GRAMS> grams.`
- State-driven: `While there is no card in the ATM, the ATM shall display "insert card to begin".`
- Event-driven: `When mute is selected, the laptop shall suppress all audio output.`
- Optional-feature: `Where the car has a sunroof, the car shall provide a sunroof control panel on the driver door.`
- Unwanted-behavior: `If an invalid credit card number is entered, then the website shall prompt for re-entry of credit card details.`
- Complex: `While the aircraft is on ground, when reverse thrust is commanded, the engine control system shall enable reverse thrust.`

## Anti-Patterns

- Multiple behaviors in one statement joined by "and".
- Missing system subject.
- Missing trigger for event-driven behavior.
- Non-testable language: "quickly", "user-friendly", "normally".
- Mixed keyword order (for example `When ..., while ...` in the same clause chain).

## Rewrite Checklist

- Identify actor/system.
- Identify state or trigger (if any).
- Identify mandatory response.
- Select pattern and template.
- Rewrite in EARS form.
- Verify objective and testable wording.
