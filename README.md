# FitFindr

> ### 👋 Start here
>
> **New to this repo? Read [RUNNING.md](RUNNING.md) first** — setup, every
> command, and what to do when something breaks.
>
> Once `python test.py` passes:
>
> ```bash
> python app.py listings --full -n 6      # read the data (Milestone 1)
> python app.py fields                    # what you can filter on
> python app.py ask 'vintage graphic tee under $30'
> ```
>
> All three tools are stubs, so that last command will do nothing useful yet.
> That's the starting position.
>
> **The rest of this file is your submission.** Fill it in as you go.

---

<!-- ─────────────────────────────────────────────────────────────────────────
     HOW TO USE THIS FILE

     This is your submission. Fill each section in as you finish the milestone
     it belongs to — don't leave it all to the end.

     Unit 3 asks for the first five sections. Unit 4 adds the five below them.
     Leave the unit 4 sections alone until then; they're here so you know
     what's coming.

     Everything is pasted as TEXT. No screenshots, no images, no video links.
     A typed block of output gets full credit; a picture of the same output
     gets none.
     ───────────────────────────────────────────────────────────────────────── -->

<!-- ═══════════════════════ UNIT 3 — THE BUILD ═══════════════════════ -->

## What This Does

<!-- Three or four sentences: what a user asks for, and what they get back. -->

FitFindr is a three-tool agent for thrift shopping. A user asks in plain language for an item, such as "a vintage graphic tee under $30, size M", and the agent searches 40 clothing listings by keyword, size, and price ceiling. It takes the best match, asks a model to suggest outfits that combine it with pieces from the user's wardrobe (or general styling advice if the wardrobe is empty), and then writes a short caption someone could actually post. If nothing matches, the agent stops before the outfit step and tells the user what to change: broader words, a different size, or a higher price ceiling.

---

## Tool Inventory

<!-- Four lines per tool. This is worth 2 points and it's the single most
     common place students lose them.

     "Returns a list" earns NOTHING. The description has to say what is IN
     the list.

     The empty case isn't optional either — it's the thing your loop branches
     on, and if you don't decide it here you'll discover it as a crash in
     Milestone 5. -->

### `search_listings`

- **What it does:** Searches the 40 listings for items matching a keyword description, optionally filtered by size and a price ceiling, and returns the best matches first.
- **Inputs:** `description` (str), `size` (str or None; None skips size filtering), `max_price` (float or None; inclusive, None skips price filtering).
- **Returns:** A list of at most `config.SEARCH_RESULT_LIMIT` listing dicts, best keyword match first. Each dict has `id`, `title`, `description`, `category`, `style_tags` (list), `size`, `condition`, `price` (float), `colors` (list), `brand` (str or None), `platform`. Size matching is case-insensitive: the requested size matches if it equals the listing's full size string, or equals one whole token of it when the size is split on `/` and whitespace. So "M" matches "S/M" and "M/L", but "L" does not match "XL" or "W30 L30", and "S" does not match "US 9". Listings with a zero keyword score are dropped.
- **When it has nothing:** Returns an empty list `[]`. It never returns None or raises.

### `suggest_outfit`

- **What it does:** Given the selected listing and the user's wardrobe, asks the model for one or two outfit suggestions.
- **Inputs:** `new_item` (dict; one listing dict from `search_listings`), `wardrobe` (dict with an `items` key holding a list of wardrobe item dicts; the list may be empty).
- **Returns:** A non-empty str of outfit suggestions. With a non-empty wardrobe, it names specific pieces the user already owns.
- **When it has nothing:** With `{"items": []}` it returns general styling advice for the item. It never returns an empty string and never raises.

### `create_fit_card`

- **What it does:** Writes a short, postable caption about the find from the outfit suggestion and the listing.
- **Inputs:** `outfit` (str; the string returned by `suggest_outfit`), `new_item` (dict; the same listing dict).
- **Returns:** A str of two to four sentences that mentions the item, its price, and its platform once each, with a specific vibe.
- **When it has nothing:** If `outfit` is empty or whitespace, it returns a descriptive message string instead of raising.

---

## Planning Loop

<!-- Your branch rule, stated as a rule — the condition AND both paths — plus
     the file and function that holds it.

     Like this:
       "If search_listings returns an empty list, put a message in the session
        and stop. Otherwise take the first result and go to suggest_outfit."
        — agent.py::run_agent

     The grader checks your code against what you claim here, so the file and
     function have to be real. -->

**Branch rule:** If `search_listings` returns an empty list, put a message in the session explaining what the user could change (a broader description, a different size, a higher max price) and stop, without calling `suggest_outfit`. Otherwise, store the first result in the session as the selected item, pass it with the wardrobe to `suggest_outfit`, then pass the outfit and the selected item to `create_fit_card`.

**Where it lives:** `agent.py::run_agent`

**How the query is parsed:** Regex, in `agent.py::parse_query`, with no model call. A dollar amount ("under $30", "below", "max", "up to") becomes `max_price`; "size M" or a trailing ", M" becomes `size`; whatever is left is the description. It costs nothing and returns the same answer every time. It gives up on phrasing it has never seen: "nothing over thirty dollars" parses to no price, and the ceiling is silently ignored. <!-- regex, string splitting, or asking the model — say which -->

**What moves through the session:** In order: `query` → `parsed` (description, size, max_price) → `search_results` (everything `search_listings` returned) → `selected_item` (the first result) → `outfit_suggestion` (from `suggest_outfit(selected_item, wardrobe)`) → `fit_card` (from `create_fit_card(outfit_suggestion, selected_item)`). Each tool's input is read back out of the session, not passed from the previous call's return value. On the empty-search branch, `error` is set and `selected_item`, `outfit_suggestion` and `fit_card` stay `None`. <!-- which fields, in what order -->

---

## Sample Run

<!-- Two things go here.

     1. One FULL query and its output, pasted as text.
     2. Your three per-tool terminal tests — the command and what it printed. -->

**One full query**

```
$ python app.py ask 'vintage graphic tee under $30'
Found:    Y2K Baby Tee — Butterfly Print — $18.0 on depop

  Outfit:   Here are two practical, wearable outfits incorporating your new Y2K butterfly baby tee with pieces from your wardrobe:

### Outfit 1: 2000s Streetwear Contrast
This look balances the fitted, feminine energy of the baby tee with relaxed denim and chunky footwear.

* **Top:** Y2K Baby Tee — Butterfly Print
* **Bottoms:** Baggy straight-leg jeans, dark wash
* **Outerwear:** Vintage black denim jacket (worn over top or casually draped over shoulders)
* **Shoes:** Chunky white sneakers
* **Accessories:** Black crossbody bag

### Outfit 2: Casual Edgy Layering
A slightly grungier take that plays with proportions by pairing the cropped tee with structured trousers and boots.

* **Top:** Y2K Baby Tee — Butterfly Print
* **Bottoms:** Wide-leg khaki trousers
* **Outerwear:** Black cropped zip hoodie (worn open to let the pink and purple butterfly graphic peek through)
* **Shoes:** Black combat boots
* **Accessories:** Brown leather belt (to define the waist of the khaki trousers)

  Fit card: Found my absolute dream tee and honestly still pinching myself. Tossed it over baggy denim today and it’s giving total early 2000s off-duty energy. Snagged this butterfly print baby tee for just $18 over on depop 🦋

0 model calls this session, 2 served from cache

```

**The three tools, tested one at a time**

```
$ python -c "from tools import search_listings as s; r=s('graphic tee', max_price=30); print([(x['title'], x['price']) for x in r])"
[('Y2K Baby Tee — Butterfly Print', 18.0), ('Graphic Tee — 2003 Tour Bootleg Style', 24.0), ('Mesh Long-Sleeve Top — Black', 15.0), ('Vintage Band Tee — Faded Grey', 19.0), ('Low-Rise Cargo Pants — Khaki', 27.0), ('Vintage Graphic Hoodie — Faded Black', 26.0)]

$ python -c "from tools import search_listings as s; print(s('designer ballgown', size='XXS', max_price=5))"
[]
```

```
$ python -c "from tools import suggest_outfit; from utils.data_loader import get_example_wardrobe, load_listings; print(suggest_outfit(load_listings()[0], get_example_wardrobe()))"
python -c "from tools import suggest_outfit; from utils.data_loader import get_empty_wardrobe, load_listings; print(suggest_outfit(load_listings()[0], get_empty_wardrobe()))"
Here are two practical, wearable outfits featuring your new Vintage Levi's 501 Jeans:

**Outfit 1: Effortless Casual (Streetwear Vibe)**
*   **Top:** White ribbed tank top
*   **Footwear:** Chunky white sneakers
*   **Accessories:** Black crossbody bag
*   *Styling notes:* Tuck the white tank top fully into the 501s to define your waist. Finish with the chunky sneakers and crossbody bag for an easy, classic off-duty look.

**Outfit 2: Cozy Layered (Chilly Day Vibe)**
*   **Top:** Oversized grey crewneck sweatshirt
*   **Footwear:** Black combat boots
*   **Accessories:** Brown leather belt, Black crossbody bag
*   *Styling notes:* Thread the brown leather belt through the jeans (letting a bit of the brown contrast with the medium wash). Cinch the oversized grey crewneck or do a half-tuck at the front. Ground the look with the black combat boots to add a touch of grunge to the vintage denim.
The Vintage Levi’s 501 in medium wash is the ultimate denim holy grail. Because they are 100% cotton vintage denim, they have a structured, rigid feel that holds its shape and gets better with age. A W30L30 is a great versatile size that can be worn fitted or slightly relaxed depending on your natural waist/hip measurements.

Here is how to style them, along with two complete, easy-to-recreate outfit formulas using wardrobe staples.

### General Styling Rules for Vintage 501s:
*   **Balance the volume:** Since 501s feature a straight leg and rigid fabric, pair them with eithersomething fitted on top (like a baby tee or a sleek bodysuit) to create contrast, or go intentionallyoversized (like an oversized blazer) for an effortless streetwear look.
*   **Footwear is key:** A straight-leg hem hitting right at the ankle (L30) looks best with slim boots, retro sneakers (like Adidas Sambas or New Balance), or classic loafers.
*   **Break them in:** Vintage denim softens up the more you wear them. Don't be afraid to cuff the hems once or twice if you want a cropped look.

---

### Outfit Idea 1: Casual Streetwear (Effortless & Cool)
*This look plays on the streetwear tag, keeping things relaxed, comfortable, and classic.*

*   **Top:** A heavyweight, boxy white crewneck t-shirt (tucked in at the front to define the waist).
*   **Outerwear:** An oversized black faux-leather bomber jacket or a vintage canvas chore coat.
*   **Shoes:** Retro low-profile sneakers (e.g., white leather sneakers with a hint of color).
*   **Accessories:** A simple black leather belt with a silver buckle and a canvas tote bag.

### Outfit Idea 2: Elevated Smart-Casual (Polished & Timeless)
*This look dresses up the rugged denim for dinner, a casual office, or weekend errands.*

*   **Top:** A fitted black ribbed long-sleeve top or a classic black turtleneck.
*   **Outerwear:** An oversized grey houndstooth or plaid blazer worn open.
*   **Shoes:** Pointed-toe black leather ankle boots (let the hem of the jeans rest just on top of the boot shaft) or classic black leather loafers.
*   **Accessories:** A structured leather handbag and simple gold hoop earrings.

```

```
$ AI201_CACHE=0 python -c "from tools import create_fit_card; from utils.data_loader import load_listings; it=load_listings()[1]; print(it['title'], it['price'], it['platform']); print(create_fit_card('baggy jeans, white tank, chunky sneakers', it))"
Y2K Baby Tee — Butterfly Print 18.0 depop
Literal heaven right here. Snagged this butterfly baby tee for just $18 over on depop and it's about to be my whole personality. Pairing it with my baggiest denim and chunky kicks for max 2000s energy. 🦋

$ python -c "from tools import create_fit_card; from utils.data_loader import load_listings; print(repr(create_fit_card('   ', load_listings()[0])))"
'No fit card can be created without an outfit suggestion.'

```

---

## How I Used AI

<!-- Two specific moments. What you asked, what came back, what you changed.

     "I used Claude to help me code" is not enough.

     "I gave Claude my search_listings spec. It returned None on no match
     instead of an empty list, so I changed it" is the level we want. -->

**Moment 1**

- _What I asked for:_ I gave Claude the instructor's `_size_matches` and `_size_tokens` helper and my Tool Inventory size rule (full string, or one whole token when split on `/` and whitespace), and asked whether the helper matched my spec.
- _What came back:_ Three problems. `p.strip().upper` was missing its parentheses, so sizes were never uppercased. The helper split only on `/`, so "W30" would not match "W30 L30". Its "One Size matches any size" shortcut contradicted my README, which doesn't have that rule.
- _What I changed:_ I told Copilot to fix `.upper()`, split on whitespace as well as `/`, and remove the One Size shortcut. Then I tested it myself instead of trusting the summary: the size matrix printed `True False False False True False True` (so "L" does not match "XL" or "W30 L30"), and a listing priced exactly at the ceiling was included while one priced a cent over was not.

**Moment 2**

- _What I asked for:_ I wrote my own acceptance criteria 3 to 5 and asked an AI only to attack them: for each one, how would it test it from the sentence alone, without rewriting it.
- _What came back:_ My first drafts could not be tested as written. "Return the title being searched" didn't say which title or where, and a brand check can't work because `brand` is `None` for most listings. In later rounds it found that my state criterion compared only two downstream values and never the first search result, that "4 of 5" could be read as covering only part of the fit-card requirement, and that the price criterion could pass vacuously on an empty result.
- _What I changed:_ I rewrote the criteria myself each round. The state criterion now compares three ids (`session["selected_item"]`, the first `search_listings` result, and the `new_item` that reached `suggest_outfit`). The fit-card criterion puts both the sentence count and the title, price and platform under the "4 of 5". The price criterion requires test cases with listings both below and above the ceiling.

<!-- ═══════════════════════ UNIT 4 — THE TEST ═══════════════════════

     Don't fill these in during unit 3.
     ═══════════════════════════════════════════════════════════════════ -->

---

## Run Log — Before

<!-- Five criteria, five tries each, in this exact format.

     Five, because your criteria are written out of five. Mark each try PASS
     or FAIL, count the passes, and read that count against your target — a
     row targeting 4 of 5 with three PASS cells is MISSED (3/5).

     `python run_eval.py --label before` runs everything and writes the table
     into results/. Paste it here and fill in the verdicts. -->

| Criterion | Target | Try 1 | Try 2 | Try 3 | Try 4 | Try 5 | Verdict |
| --------- | ------ | ----- | ----- | ----- | ----- | ----- | ------- |
| 1.        |        |       |       |       |       |       |         |
| 2.        |        |       |       |       |       |       |         |
| 3.        |        |       |       |       |       |       |         |
| 4.        |        |       |       |       |       |       |         |
| 5.        |        |       |       |       |       |       |         |

**Real output from one try**, pasted as text, naming the file and function
that produced it:

```

```

---

## Verdicts and Diagnoses

<!-- MET or MISSED per criterion against LAST UNIT's target, plus a sentence on
     how you decided.

     Then, for every miss: which of the four places it happened — a tool, the
     loop's branch, the session, or the model's output — AND the mechanism.

     Not a diagnosis:  "The fit card was bad."
     A diagnosis:      "The fit card criterion missed on 2 of 5 items. Both had
                        an empty brand field. My prompt puts the brand in the
                        first sentence, so the card opened with a blank and read
                        like a fragment. The tool worked; the prompt assumed a
                        field that isn't always there."

     Look for a pattern. Three misses on the same tool is one problem, not
     three. -->

| #   | Criterion | Target | Verdict | How I decided |
| --- | --------- | ------ | ------- | ------------- |
| 1   |           |        |         |               |
| 2   |           |        |         |               |
| 3   |           |        |         |               |
| 4   |           |        |         |               |
| 5   |           |        |         |               |

**Diagnoses**

---

## Loop Trace

<!-- One full run, printed step by step, with the MCP call visible in it.

     `python app.py ask '...' --trace` once you've added the trace.step()
     calls in Milestone 2.

     Worth pasting BOTH the happy path and the empty-search path. The empty
     one should be visibly shorter, because it stops. If your two traces are
     the same length, your branch isn't working — and this is the fastest way
     anyone will ever find that out. -->

**Happy path**

```

```

**Empty search**

```

```

**On the MCP move:** <!-- what changed in your code, and whether anything
behaved differently afterwards. If the rewire didn't work, say exactly where it
broke — the error text and the last thing that worked. That earns the point in
full. -->

---

## The Improvement

<!-- What you changed, why your diagnosis pointed at it, and the after-run in
     the same table format. One change, measured properly.

     `python run_eval.py --label after` -->

**What I changed:**

**Which failure it was meant to fix:**

### Run Log — After

| Criterion | Target | Try 1 | Try 2 | Try 3 | Try 4 | Try 5 | Verdict |
| --------- | ------ | ----- | ----- | ----- | ----- | ----- | ------- |
| 1.        |        |       |       |       |       |       |         |
| 2.        |        |       |       |       |       |       |         |
| 3.        |        |       |       |       |       |       |         |
| 4.        |        |       |       |       |       |       |         |
| 5.        |        |       |       |       |       |       |         |

**Did it help, and how do I know:**

<!-- If it made things worse, say that. Honestly reported, that earns full
     credit and is more interesting than one that worked. -->

---

## What's Still Broken

<!-- For each criterion still missed: what you'd do, and why you stopped where
     you did. "I ran out of time" is fine if it's true. Pretending nothing is
     left is not. -->

<!-- ═════════════════════════════════════════════════════════════════════

     SUBMISSION CHECKLIST — unit 3

       [ ] criteria.md has five numbered criteria, each with a target
       [ ] Each criterion has a reason underneath it
       [ ] All five unit 3 sections above have real content
       [ ] Tool Inventory: all three tools, inputs WITH TYPES, a specific
           return value, and the empty case
       [ ] Planning Loop names the branch rule and agent.py::run_agent
       [ ] Sample Run: one full query plus the three per-tool tests, as text
       [ ] At least four new commits
       [ ] Repository URL submitted — WRITE IT DOWN, you submit the same one
           next unit

     SUBMISSION CHECKLIST — unit 4

       [ ] mcp_server.py exists with one tool registered
           (or a written record of exactly where the rewire broke)
       [ ] Run Log — Before, five criteria, five tries each
       [ ] Real output pasted underneath, naming file and function
       [ ] A verdict on every criterion
       [ ] A diagnosis for every miss, naming a place AND a mechanism
       [ ] Loop Trace, with the MCP call visible in it
       [ ] All three failure modes triggered and handled
       [ ] One improvement, with Run Log — After in the same format
       [ ] What's Still Broken
       [ ] At least four new commits
       [ ] The SAME repository URL as last unit

     Do not delete and recreate this repository. Your commit history is what
     shows your criteria existed before your results did.
     ═════════════════════════════════════════════════════════════════════ -->

---

📖 **How to run this project: [RUNNING.md](RUNNING.md)**
