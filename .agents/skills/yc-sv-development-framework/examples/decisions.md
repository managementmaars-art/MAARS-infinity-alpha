# Decision Examples Using the YC/SV Framework

## Example 1: Should I add tests?

**Context:** I have a checkout function that processes payments with Stripe.

**Applying the framework:**

1. Is it working? → YES, but without tests
2. Are there complaints? → NO, but if it fails we lose money
3. Does it block revenue? → A bug here WOULD block revenue

**Decision:** P0 - Add tests to payment code TODAY

**Applied principle:** "Tests for critical payment code: YES"

---

## Example 2: Should I refactor this component?

**Context:** A 500-line React component that "looks ugly" but works.

**Applying the framework:**

1. Is it working? → YES
2. Are there complaints? → NO
3. Does it block revenue? → NO

**Decision:** NEVER - Don't touch it

**Applied principle:** "If it 'looks ugly' but works: DON'T refactor"

---

## Example 3: Should I automate the deploy?

**Context:** Manual deploy takes 45 minutes, we do 3 deploys/week.

**Applying the framework:**

1. Is it working? → YES, but slow
2. Are there complaints? → The team loses 2+ hours/week
3. Does it block revenue? → NOT directly, but reduces shipping velocity

**Decision:** P1 - This week, because "ship fast" is core

**Applied principle:** "If manual deploy takes >30min: YES automate"

---

## Example 4: Should I use this new framework?

**Context:** I saw a new framework on Twitter that looks cool.

**Applying the framework:**

1. Does it solve a real problem TODAY? → NO, just "would be useful"
2. Does the team know it? → NO
3. Does the current one work? → YES

**Decision:** NEVER - "Would be useful in the future: NO"

**Applied principle:** "Don't solve problems you don't have" - Paul Graham

---

## Example 5: Should I add a feature a user requested?

**Context:** A user requested dark mode in the app.

**Applying the framework:**

1. How many users are asking? → 1
2. Is it a paying user? → NO, free tier
3. Does it block conversion to paid? → NO

**Decision:** P2 or NEVER - Depends on whether many more are asking for the same

**Applied principle:** "10 users who LOVE it > 1000 who 'kinda like it'"

---

## Example 6: Should I migrate the database?

**Context:** PostgreSQL works fine but "MongoDB would be more flexible".

**Applying the framework:**

1. Is it working? → YES
2. Are there performance issues? → NO
3. Does it block critical features? → NO

**Decision:** NEVER - "Rewrite what works: NEVER"

**Applied principle:** Patrick Collison - "Stripe started with Ruby + MongoDB. Ugly code that works > elegant code that doesn't exist"
