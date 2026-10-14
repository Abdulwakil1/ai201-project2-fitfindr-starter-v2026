import config
config.CACHE_ENABLED = False
import agent
from tools import search_listings
from utils.data_loader import get_example_wardrobe

# Criterion 3: ids across the handoff, 5 tries of the same query
seen = []
orig = agent.suggest_outfit
def spy(item, wardrobe):
    seen.append(item["id"])
    return orig(item, wardrobe)
agent.suggest_outfit = spy

ok = 0
for i in range(1, 6):
    seen.clear()
    s = agent.run_agent("graphic tee under $30", get_example_wardrobe())
    first = (s["search_results"] or [{}])[0].get("id")
    sel = (s["selected_item"] or {}).get("id")
    got = seen[0] if seen else None
    passed = first is not None and first == sel == got
    ok += passed
    print(f"C3 try {i}: first={first} selected={sel} received={got} -> {'PASS' if passed else 'FAIL'}")
print(f"C3: {ok}/5\n")

# Criterion 5: direct search_listings calls, ceiling in the middle of the prices
CASES = [("graphic tee", 20), ("jacket", 40), ("jeans", 35), ("sneakers", 30), ("top", 20)]

ok = 0
for desc, cap in CASES:
    every = search_listings(desc)
    setup = any(r["price"] <= cap for r in every) and any(r["price"] > cap for r in every)
    res = search_listings(desc, max_price=cap)
    passed = bool(res) and all(r["price"] <= cap for r in res)
    ok += passed
    top = max((r["price"] for r in res), default=None)
    print(f"C5 {desc!r} <= {cap}: setup {'ok' if setup else 'BAD - pick another pair'}, "
          f"{len(res)} results, highest {top} -> {'PASS' if passed else 'FAIL'}")
print(f"C5: {ok}/5")