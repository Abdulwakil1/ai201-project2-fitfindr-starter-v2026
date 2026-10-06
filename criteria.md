# Acceptance criteria — FitFindr

Five criteria that say what "working" means for this agent, written in unit 3
**before** any results existed.

An acceptance criterion names a target: a number, a count, a rate, or something
a person could plainly observe. _"The agent handles errors"_ is an opinion.
_"When search returns nothing, the agent stops before calling the second tool,
in 5 of 5 tries"_ is a criterion.

Under each one, write a sentence or two on **why that target** and not a
stricter one. A reason that says something about your tools, your loop, or the
data earns credit; _"80% seemed reasonable"_ does not.

> Missing your own targets next unit costs you nothing. Setting a target so
> easy you can't miss it does.

**Two are written for you. You write three.**

---

## 1. A matching query completes all three tools

Given a query that matches at least one listing, the agent completes all three
tool calls and returns a fit card — in at least 4 of 5 tries.

**Why this target:**

<!-- Why 4 of 5 and not 5 of 5? Something about your search, probably —
     "my search is a plain keyword match and some phrasings will miss" is a
     real answer. -->

A 4 of 5 target allows for occasional misses because the search uses plain keyword overlap and the successful path also depends on two model calls. Requiring 5 of 5 would assume every phrasing and model call succeeds every time.

---

## 2. An impossible query stops before the second tool

Given a query that matches no listings, the agent stops before calling
`suggest_outfit` and returns a message naming what to change — 5 of 5 tries.

**Why this target:**

<!-- Why is 5 of 5 reasonable here when criterion 1 isn't? What's different
     about this path? -->

The no-results branch is a deterministic if check on the empty list returned by search_listings, and the change-message is produced by the agent rather than a model call. Unlike the matching path, there is no model variability here, so 5 of 5 is reasonable.

---

## 3. Something about state

<!-- YOU WRITE THIS ONE.

     How would you know that the item your search found is the same item the
     next tool received? Name something countable or observable.

     This is the criterion people find hardest, because state failure doesn't
     look like state failure — it looks like a tool problem. Something that
     compares session["selected_item"] against what actually reached
     suggest_outfit is the shape you're after. -->

For 5 matching queries, the `id` in `session["selected_item"]` is identical to the `id` of the first listing returned by `search_listings`, and identical to the `id` of the `new_item` received by `suggest_outfit` — 5 of 5 tries.

**Why this target:**

The selected listing and the item passed to the next tool should be the exact same item, so the state handoff should work every time.

---

## 4. Something about the fit card

<!-- YOU WRITE THIS ONE.

     The fit card calls a model, so the same input can produce different words
     each time. That's not a bug — it's the nature of the tool. So what would
     make it acceptable?

     Think about what you'd actually be unhappy to see. A caption that never
     mentions the price? Two different items producing the same opening
     sentence? A card longer than a caption anyone would post? Any of those can
     be turned into a number. -->

In at least 4 of 5 matching-query runs, the returned fit card is 2–4 sentences and mentions the selected item's title, price, and platform.

**Why this target:**

The fit card is model-generated, so allowing 1 miss accounts for natural output variation while still requiring the required structure and listing details most of the time.

---

## 5. Your choice

<!-- YOU WRITE THIS ONE TOO.

     Pick something you actually care about getting right. Speed, the empty
     wardrobe path, what happens when the model can't be reached, whether the
     search respects a price ceiling — anything, as long as it names a number
     or an observable outcome. -->

For 5 direct calls to `search_listings` with a specified `max_price`, where each test case has at least one matching listing at or below the ceiling and at least one matching listing above it, every returned listing has a price less than or equal to `max_price` — 5 of 5 tries.

**Why this target:**

Price filtering is a deterministic rule, so every returned result should satisfy the requested maximum.

---

<!-- ─────────────────────────────────────────────────────────────────────────
     UNIT 4 — read this before you change anything above.

     If a criterion turns out to be BROKEN rather than merely unmet, you can
     revise it, and that earns credit. But never delete or edit the original
     line. Add the revision underneath it, like this:

         ## 4. Something about the fit card

         The fit card is different every time.

         **Why this target:** ...

         > **Revised in unit 4:** For 5 different items, the 5 fit cards share
         > no opening sentence.
         >
         > **Why revised:** "different" wasn't checkable — two cards that
         > differed by one word still counted. The new version is something I
         > can actually score.

     That's a revision because the criterion couldn't be MEASURED.

     Lowering a target because you missed it is not a revision, and it costs
     you the point:

         ✗ "I said the empty search stops it 5 of 5 times, but I got 3 of 5,
            so 3 of 5 is more realistic."

     A number you missed stays where it is, gets diagnosed, and gets a fix
     attempted. That's where the points are.
     ───────────────────────────────────────────────────────────────────────── -->
