"""
The three FitFindr tools.

Each one is a standalone function you can call and test on its own, before any
of them are wired into the loop. Build and test them one at a time — three
untested tools joined by a loop is one problem that looks like six, because you
can't tell which layer is lying to you.

    search_listings(description, size, max_price)  → list[dict]
    suggest_outfit(new_item, wardrobe)             → str
    create_fit_card(outfit, new_item)              → str

All three are stubs right now. They run and they do nothing — that's the
starting position and it's deliberate.

⚠️ Before you write any of them, fill in the **Tool Inventory** section of your
README (Milestone 2). Four lines per tool: what it does, each input with its
type, exactly what it returns, and what it returns when it has nothing to give.
That last line is what your loop branches on. "Returns a list" earns nothing —
the description has to say what is *in* the list.
"""

import re

import config  # noqa: F401 — you'll use this in search_listings
from generate import generate
from utils.data_loader import load_listings


_STOPWORDS = {
    "a", "an", "and", "the", "for", "with", "under", "over", "in", "of"
}


def _keywords(text: str) -> set[str]:
    """Lowercase words worth matching on, stopwords removed."""
    words = re.findall(r"[a-z0-9']+", (text or "").lower())
    return {word for word in words if word not in _STOPWORDS and len(word) > 1}


def _size_tokens(size: str) -> set[str]:
    cleaned = re.sub(r"\([^)]*\)", " ", size or "")
    parts = re.split(r"[/\s]+", cleaned.upper())
    return {part for part in parts if part}


def _size_matches(wanted: str, listing_size: str) -> bool:
    if not wanted:
        return True
    cleaned_listing = re.sub(r"\([^)]*\)", " ", listing_size or "")
    normalized_wanted = " ".join((wanted or "").upper().split())
    normalized_listing = " ".join(cleaned_listing.upper().split())
    return normalized_wanted == normalized_listing or normalized_wanted in _size_tokens(listing_size)


# ── Tool 1: search_listings ───────────────────────────────────────────────────

def search_listings(
    description: str,
    size: str | None = None,
    max_price: float | None = None,
) -> list[dict]:
    """
    Search the listings data for items matching a description, and optionally a
    size and a price ceiling.

    This is the tool that doesn't call the model, which makes it the easiest one
    to test and the one to move onto MCP in unit 4.

    Args:
        description: keywords describing what the user wants
                     (e.g. "vintage graphic tee").
        size:        a size string to filter by, or None to skip size filtering.
                     Match case-insensitively — "M" should match "S/M".

                     ⚠️ Read the sizes in the data before you reach for a plain
                     substring test. `"s" in "us 9"` is True, and so is
                     `"l" in "xl"`. A filter that returns shoes when someone
                     asked for a small top reads like a broken search, and it
                     will quietly cost you in unit 4 when you test criterion 1.
                     What counts as a size match is part of your spec — decide
                     it and write it into your Tool Inventory.
        max_price:   maximum price, inclusive, or None to skip price filtering.

    Returns:
        A list of matching listing dicts, best match first.
        **Returns an empty list when nothing matches — an empty list, not None,
        and not an exception.** Your loop branches on this.

    Each listing dict has these fields:
        id, title, description, category, style_tags (list), size,
        condition, price (float), colors (list), brand (str or None), platform

    Note that `brand` is None for most listings. That is deliberate and
    realistic — thrift listings often have no brand. If something you write
    assumes a brand is always there, you will find out in unit 4.

    TODO:
        1. Load every listing with load_listings().
        2. Filter by max_price and by size, when each is provided.
        3. Score what's left by keyword overlap with `description`.
        4. Drop anything scoring zero.
        5. Sort by score, highest first, and return the listing dicts —
           at most config.SEARCH_RESULT_LIMIT of them.

    Test it from a terminal before you move on:
        python -c "from tools import search_listings; print(search_listings('graphic tee', max_price=30))"
    """
    requested_keywords = _keywords(description)
    matches = []

    for listing in load_listings():
        if max_price is not None and listing["price"] > max_price:
            continue
        if size is not None and not _size_matches(size, listing.get("size", "")):
            continue

        searchable_text = " ".join(
            [
                listing.get("title", ""),
                listing.get("description", ""),
                listing.get("category", ""),
                " ".join(listing.get("style_tags", [])),
                " ".join(listing.get("colors", [])),
            ]
        )
        score = len(requested_keywords & _keywords(searchable_text))
        if score:
            matches.append((score, listing))

    matches.sort(key=lambda match: match[0], reverse=True)
    return [listing for _, listing in matches[: config.SEARCH_RESULT_LIMIT]]


# ── Tool 2: suggest_outfit ────────────────────────────────────────────────────

def suggest_outfit(new_item: dict, wardrobe: dict) -> str:
    """
    Given a thrifted item and the user's wardrobe, suggest one or two outfits.

    This one calls the model, through `generate()`. You don't need to think
    about rate limits — the adapter handles pacing for you.

    Args:
        new_item: a listing dict — the item the user is considering.
        wardrobe: a wardrobe dict with an 'items' key holding a list of items.
                  **It may be empty.** Handle that.

    Returns:
        A non-empty string with outfit suggestions.
        With an empty wardrobe, return general styling advice rather than
        raising or returning "". Unit 4 has you trigger the empty wardrobe on
        purpose, so decide now what it should do.

    TODO:
        1. Check whether wardrobe['items'] is empty.
        2. If it is, ask the model for general styling ideas for this item.
        3. If it isn't, format the wardrobe items into the prompt and ask for
           specific combinations naming pieces the user already owns.
        4. Return the model's response.

    Test it from a terminal before you move on:
        python -c "from tools import suggest_outfit; from utils.data_loader import get_example_wardrobe, load_listings; print(suggest_outfit(load_listings()[0], get_example_wardrobe()))"
    """
    items = wardrobe.get("items") or []
    item_details = (
        f"Name: {new_item.get('title', new_item.get('name', 'Unknown item'))}\n"
        f"Category: {new_item.get('category', '')}\n"
        f"Colors: {', '.join(new_item.get('colors', []))}\n"
        f"Style tags: {', '.join(new_item.get('style_tags', []))}\n"
        f"Size: {new_item.get('size', '')}\n"
        f"Condition: {new_item.get('condition', '')}"
    )

    if not items:
        prompt = (
            "No wardrobe was provided. Give general styling advice for this new item, "
            "suggesting one or two outfit ideas without assuming the user owns any "
            "specific pieces.\n\n"
            f"New item:\n{item_details}"
        )
    else:
        wardrobe_details = []
        for index, item in enumerate(items, start=1):
            notes = f"; Notes: {item['notes']}" if item.get("notes") else ""
            wardrobe_details.append(
                f"{index}. Name: {item.get('name', '')}; "
                f"Category: {item.get('category', '')}; "
                f"Colors: {', '.join(item.get('colors', []))}; "
                f"Style tags: {', '.join(item.get('style_tags', []))}"
                f"{notes}"
            )
        prompt = (
            "Suggest one or two outfits combining the new item with specific pieces "
            "from the user's wardrobe. Name the owned pieces in each outfit and do "
            "not invent wardrobe items.\n\n"
            f"New item:\n{item_details}\n\n"
            "User wardrobe:\n" + "\n".join(wardrobe_details)
        )

    response = generate(
        prompt,
        system="You are a practical personal stylist. Keep suggestions specific and wearable.",
    )
    return response.strip() or "No outfit suggestions were generated."


# ── Tool 3: create_fit_card ───────────────────────────────────────────────────

def create_fit_card(outfit: str, new_item: dict) -> str:
    """
    Write a short caption someone would actually post about the find.

    This calls the model too.

    Args:
        outfit:   the outfit suggestion string from suggest_outfit().
        new_item: the listing dict for the item.

    Returns:
        A two-to-four sentence caption.
        If `outfit` is empty or whitespace, return a descriptive message rather
        than raising.

    The caption should read like a real post rather than a product description,
    mention the item and its price and platform once each, and be specific about
    the vibe.

    It should also come out **differently for different inputs**. If you run
    this three times on the same item and get three word-for-word identical
    strings, it's one of two things, and both are near the top of `config.py`:

        • CACHE_ENABLED — the adapter handed back an answer it already had
        • TEMPERATURE   — at 0.0 the model gives the same words every time

    TODO:
        1. Guard against an empty or whitespace-only `outfit`.
        2. Build a prompt with the item details and the outfit.
        3. Call generate() and return the response.

    Test it from a terminal before you move on:
        python -c "from tools import create_fit_card; from utils.data_loader import load_listings; print(create_fit_card('jeans and white sneakers', load_listings()[0]))"
    """
    if not outfit or not outfit.strip():
        return "No fit card can be created without an outfit suggestion."

    price = f"${new_item['price']:.2f}"
    if price.endswith(".00"):
        price = price[:-3]
    prompt = (
        "Write a two-to-four sentence social media caption for this thrift find. "
        "Make it sound like a real social post, not a product description. Mention "
        "the item, its price, and its platform exactly once each, and make the vibe "
        "specific. Use no hashtags and at most one emoji.\n\n"
        f"Item: {new_item.get('title', 'Unknown item')}\n"
        f"Price: {price}\n"
        f"Platform: {new_item.get('platform', '')}\n"
        f"Outfit: {outfit.strip()}"
    )
    response = generate(
        prompt,
        system="You are a concise stylist writing authentic social captions.",
    )
    return response.strip() or "No fit card caption was generated."
