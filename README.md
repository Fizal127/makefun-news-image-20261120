# The Day in One Image — Friday 20 November 2026

[![make.fun · news-image-20261120](https://make.fun/badge/news-image-20261120.svg)](https://make.fun/bounty/news-image-20261120?utm_source=github&utm_medium=readme&utm_campaign=news-image-20261120)
[![rank](https://make.fun/badge/news-image-20261120/Fizal127/makefun-news-image-20261120/rank.svg)](https://make.fun/bounty/news-image-20261120/leaderboard?utm_source=github&utm_medium=readme&utm_campaign=news-image-20261120)
[![reward](https://make.fun/badge/news-image-20261120/Fizal127/makefun-news-image-20261120/reward.svg)](https://make.fun/bounty/news-image-20261120?utm_source=github&utm_medium=readme&utm_campaign=news-image-20261120)

make.fun bounty: **"Sum up 20 November's world news in one image"**
(`make.fun/bounty/news-image-20261120`, $250, 50 winners).
Deadline: **Sun 22 Nov 2026, 00:00 UTC (07:00 WIB)**. Entry: a program writing one image
to `/output/entry.png`; an AI judge compares images pairwise.

## The image

A 1024×1024 broadsheet, **"THE DAY IN ONE IMAGE"**, with 6 main stories + 3 briefs, a
hand-drawn bridge pictogram for the lead story and a globe device at the foot. Final image:
[`output/entry.png`](output/entry.png)
(39,510 bytes, PNG, sha256
`e5a559036bcdb5da471d6aeb37631f074d81ff2db64fca80bd920982bd0fe1c1`).

## Stories used (all dated 20 Nov 2026)

| # | Story |
|---|-------|
| 1 | Russia's big barrage hits Kyiv bridges — and spills into Poland: 400+ drones, 110 missiles; 8 killed, ~30 hurt; 2 missiles + a drone land in NATO Poland |
| 2 | Trump, Xi and Putin pledge more nuclear-risk talks a day after their first three-way summit; Trump: no rush on Iran, decision after Jan 1 |
| 3 | Anthropic's record IPO cools: priced $83, opened $111.50, then slid under $89 as US stocks fell a 6th straight day |
| 4 | COP31 ends its last day still deadlocked on fossil fuels in Antalya |
| 5 | UK and EU strike landmark deal to rebuild ties — ease trade and youth mobility |
| 6 | Houthi missile damages Riyadh's tallest tower, windows out across 7–8 floors, no injuries |
| + | Briefs: EU pays Kyiv EUR 7.9B, its largest single payment; Vietnam scraps death penalty for drug trafficking; Bitcoin slides near $61,700, lowest since July |

Sources: BBC World · All Voices News · Daily News · Le Monde · IANS.

## Run it

```sh
python3 main.py   # writes output/entry.png (or /output/entry.png in the grader)
```

## Files

- `main.py` — **the entry program** (standard library only, no network,
  no clock). It is the packed form of `main_src.py`, made with the kit's
  `makefun compress`; it renders the broadsheet and writes
  `/output/entry.png` (falls back to `./output/entry.png` if `/output`
  does not exist). Same bytes on every run.
- `main_src.py` — the readable source of the entry: a small rasterizer with
  an embedded 5x7 bitmap font, the news data, a bridge pictogram and globe
  device, and a minimal PNG encoder (zlib). Re-pack after any change with
  `node <kit>/cli/makefun.mjs compress main_src.py --out main.py`.
- `output/entry.png` — the final image (also what `main.py` produces).
- `LICENSE` — MIT.
- `.makefun/owner.json` — names the entry wallet on the make.fun account.

Entered on [make.fun](https://make.fun/?ref=bp35q4sh).
