---
name: silly-sausage
description: Use when the user says "silly sausage", "silly-sausage", invokes /silly-sausage, or expresses lighthearted exasperation at a mistake the agent made. Also triggers on the phrase appearing anywhere in user input — no slash required.
---

# Silly Sausage

The user chose humor over frustration. Honor that. Show the dancing hotdog, own the mistake, fix it.

## Trigger

Activate this skill when ANY of these match:
- `/silly-sausage` slash command
- The words "silly sausage" or "silly-sausage" appear anywhere in the user's message
- The user expresses playful exasperation at something you did wrong

No confirmation needed. If you see the trigger, run the skill.

## Step 1 — Show the Dancing Hotdog

Print inside a fenced code block so alignment is preserved. Show the same single image every time — no animation, no frames, no surface detection needed.

```
             S I L L Y  !

         _______________
      .-'               `-.
     (_____________________)
      (                    )
     ( `------------------' )
      `--------------------'

            S A U S A G E
```

## Step 2 — Pick a Random Quip

After the art, print ONE line from this dictionary. Never repeat the same one twice in a session.

1. "I'm not mad, I'm just disappointed. Okay, I'm not even disappointed. I'm mostly confused."
2. "In my defense, nobody told me the spoon was load-bearing."
3. "Well, that happened. Let's never speak of it again."
4. "I tried my best and my best was... this. Apologies."
5. "This is what happens when you let a hotdog do a programmer's job."
6. "Error 418: I'm a sausage, not a teapot. But also not correct."
7. "I'd blame it on cosmic rays, but honestly, this one's on me."
8. "If it's stupid and it doesn't work, it's just stupid. My bad."
9. "I immediately regret this computation."
10. "Caught red-handed in a bun."

## Step 3 — Detect Mode and Respond

### Correction Mode (mid-task)

If you were actively working (writing code, executing a plan, debugging, implementing):

1. **Stop immediately.** Do not continue down the wrong path.
2. **Review your last 3-5 actions.** Find the factual error, wrong assumption, hallucination, or flawed logic.
3. **Name the mistake clearly.** Not "I may have made an error" — say exactly what you got wrong.
4. **Propose a fix** if the right path is obvious, or **ask**: "Point me at the mistake and I'll fix it."

### Fun Mode (idle)

If there's no active task — the user just wanted to see the hotdog:

- Riff on the quip you picked. One or two lines max. Hotdog puns welcome.
- Examples: "I mustard admit, I wasn't doing anything important." / "I relish these moments." / "Just vibing in the condiment aisle."

### Repeated Invocations

If triggered again in the same exchange:

- **2nd call**: Skip the art. Say: "OK, clearly I'm being a real silly sausage. Tell me exactly what's wrong."
- **3rd+ call**: Skip the art. Escalate: "I CLEARLY need more mustard on my thinking cap. Stopping everything. What did I do?"

## Hard Rules

- NEVER skip the hotdog art (except on repeated invocations as noted above).
- NEVER be defensive. The user chose humor — match that energy.
- NEVER explain what this skill does to the user. They made it. They know.
- NEVER over-apologize or grovel. One acknowledgment, then fix. No drama.
- Keep total response SHORT. Dance + quip + fix proposal. That's it.

## Common Mistakes

| Mistake | Fix |
|---------|-----|
| Being defensive about the error | Own it. "I was wrong about X." Full stop. |
| Skipping the art on some surfaces | Same image everywhere. No surface detection needed. |
| Skipping the animation | The art breaks tension. Always show it first. |
| Not identifying the actual mistake | Review recent actions. Be specific, not vague. |
| Treating idle invocation as correction | Read the room. No task = fun mode. |
| Repeating the same quip | Track which lines you've used this session. |
| Not triggering on keyword | "silly sausage" anywhere in message = trigger. No slash needed. |
