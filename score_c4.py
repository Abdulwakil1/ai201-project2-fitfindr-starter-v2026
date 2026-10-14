import re, sys
text = open(sys.argv[1], encoding="utf-8").read()
section = text.split("### fit card: structure and details")[1]
cards = re.findall(r"Fit card:\n\n```\n(.*?)\n```", section, re.S)
ok = 0
for i, c in enumerate(cards, 1):
    sentences = len([s for s in re.split(r"(?<=[.!?])\s+", c.strip()) if s])
    title = "vintage windbreaker" in c.lower()
    price = "$40" in c
    platform = "thredup" in c.lower()
    passed = 2 <= sentences <= 4 and title and price and platform
    ok += passed
    print(f"try {i}: sentences={sentences} title={title} price={price} platform={platform} -> {'PASS' if passed else 'FAIL'}")
print(f"C4: {ok}/5")