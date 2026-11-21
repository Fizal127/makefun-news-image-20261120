# The Day in One Image — Friday 20 November 2026

[![make.fun · news-image-20261120](https://make.fun/badge/news-image-20261120.svg)](https://make.fun/bounty/news-image-20261120?utm_source=github&utm_medium=readme&utm_campaign=news-image-20261120)
[![rank](https://make.fun/badge/news-image-20261120/Fizal127/makefun-news-image-20261120/rank.svg)](https://make.fun/bounty/news-image-20261120/leaderboard?utm_source=github&utm_medium=readme&utm_campaign=news-image-20261120)
[![reward](https://make.fun/badge/news-image-20261120/Fizal127/makefun-news-image-20261120/reward.svg)](https://make.fun/bounty/news-image-20261120?utm_source=github&utm_medium=readme&utm_campaign=news-image-20261120)

make.fun bounty: **"Sum up 20 November's world news in one image"**
(`make.fun/bounty/news-image-20261120`, $250, 50 winners).
Deadline: **Sun 22 Nov 2026, 00:00 UTC (07:00 WIB)**. Entry: a program writing one image
to `/output/entry.png`; an AI judge compares images pairwise.

## The image

A 1024×1024 dense front page, **"THE WORLD IN ONE DAY"**, with **35 stories**,
modelled on the leaderboard's top entry: a huge date masthead ("Friday 20 November
2026"), a strip of six big numbers, a coloured region bar (7 regions), three lead
stories with large drawn illustrations, ten more stories in a grid with small drawn
pictograms, a numbered world map, a 22-item "also on" list, a date-check box and a
sources line. Final image:
[`output/entry.png`](output/entry.png)
(60,865 bytes, PNG, sha256
`b1a3f20992c94b3f906adea81efec2cd45abcb1f7f8f85e77fac32fa40d2a792`).

## Stories used (all dated 20 Nov 2026)

Every number was checked against reporting of Friday 20 November 2026; figures
that could not be verified were dropped or softened. Headlines and summaries are
written in our own words.

| # | Story |
|---|-------|
| 1 | Russian missiles hit three Kyiv bridges: ~110 missiles and 400+ drones overnight; 9 killed, 28 hurt; power and water cut; a missile and a drone fell in Poland |
| 2 | Cyclone Akvan comes ashore in eastern India: landfall near Gopalpur from ~8 am; 300,000+ people moved to shelters; no deaths reported |
| 3 | AI sell-off sinks Asia's stock markets: Taiwan's index −6.2% (worst week since 1991); Seoul −5.2%, Tokyo −5.1% as chipmakers led the slide |
| 4 | UK and EU seal a "reset" deal — food trade, youth visas, carbon link |
| 5 | COP31's last day: no deal — the draft text leaves out fossil fuels |
| 6 | Russian cruise missile lands in Poland — a KH-101 came down in a field |
| 7 | Iraqi army moves in — troops deploy to Jurf al-Sakhar |
| 8 | Italy's general strike — workers and students march |
| 9 | Japan inflation at 2.3% — a December rate rise stays in view |
| 10 | Impeach the top judge — Korea's ruling party acts after a court reversal |
| 11 | Kenya's first oil well — first crude due on 1 December |
| 12 | Bukele seeks a third term — the vote is on 28 February 2027 |
| 13 | Phillips makes 118 — hundreds v India in all three formats |
| 14–35 | Also on: Lviv railway strike kills two; Estonia shuts its border with Russia; Berlin pupils strike; UK cyber attacks abroad; China holds loan rates; SoftBank −14%; Kospi −8% for the week; 209 mm rain in Ganjam; Israeli strikes in Lebanon; gunmen fire on a cargo ship off Yemen; Abuja court bars evidence vs Tinubu; Kampala Ebola rally ban; Malawi fuel queues; AFDB debt warning; Russell fastest in wet GP practice; Nasdaq futures fall; Democrats query a law firm; Nicholls 175 not out; Sydney shares slide; Panama asks COP31 to cap oil output; EU calls the climate draft unacceptable; ATP backs a player-pay plan |

**Date check:** left out as Thursday 19 November's news — the three-leader summit in
Shenzhen and the Seoul court ruling that set off Friday's impeachment push. Not yet
happened, so not shown — BepiColombo's entry into orbit round Mercury and any final
COP31 text.

Sources are named beside each story; all drawings are original.

## Run it

```sh
python3 main.py   # writes output/entry.png (or /output/entry.png in the grader)
```

## Files

- `main.py` — **the entry program** (standard library only, no network,
  no clock). It is the packed form of `main_src.py`, made with the kit's
  `makefun compress`; it renders the front page and writes
  `/output/entry.png` (falls back to `./output/entry.png` if `/output`
  does not exist). Same bytes on every run.
- `main_src.py` — the readable source of the entry: a small rasterizer with
  an embedded 5x7 bitmap font, the news data (35 stories), thirteen drawn
  illustrations (Kyiv bridge scene, cyclone spiral, sell-off chart, ten grid
  pictograms), a numbered world map, and a minimal PNG encoder (zlib).
  Re-pack after any change with
  `node <kit>/cli/makefun.mjs compress main_src.py --out main.py`.
- `output/entry.png` — the final image (also what `main.py` produces).
- `LICENSE` — MIT.
- `.makefun/owner.json` — names the entry wallet on the make.fun account.

Entered on [make.fun](https://make.fun/?ref=bp35q4sh).
