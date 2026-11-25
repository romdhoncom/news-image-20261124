[![make.fun · news-image-20261124](https://make.fun/badge/news-image-20261124.svg)](https://make.fun/bounty/news-image-20261124?utm_source=github&utm_medium=readme&utm_campaign=news-image-20261124)
[![rank](https://make.fun/badge/news-image-20261124/romdhoncom/news-image-20261124/rank.svg)](https://make.fun/bounty/news-image-20261124/leaderboard?utm_source=github&utm_medium=readme&utm_campaign=news-image-20261124)
[![reward](https://make.fun/badge/news-image-20261124/romdhoncom/news-image-20261124/reward.svg)](https://make.fun/bounty/news-image-20261124?utm_source=github&utm_medium=readme&utm_campaign=news-image-20261124)

# news-image-20261124

Tuesday 24 November 2026 in one image. A dense newspaper front page drawn
from scratch in pure Python standard library: masthead, five lead stories
with pictures, a world map with 12 pins, 36 more stories, and a date-check
strip.

## The day

- **HUAWEI GUILTY** — a Brooklyn jury convicts Huawei on 10 of 12 counts:
  bank fraud, wire fraud, sanctions violations and stealing trade secrets.
- **HORMUZ: IRGC HITS SHIP** — Iran's navy says it attacked a container
  ship in the Strait of Hormuz; four tankers hit mines.
- **GAZA: HAMAS SECURITY CHIEF KILLED** — Israeli strike kills Brig. Gen.
  Naeem Abu Nahel, head of Hamas internal security, and six others.
- **UKRAINE HITS RUSSIAN SHIPS** — drone strike on the cargo ship Sparta II
  in the Gulf of Finland; strikes on Russian ships off Libya too.
- **RIYADH TOWER HIT** — suspected drone attack on the 385 m PIF tower,
  at least 11 wounded; the second hit in a week.

Plus 36 more stories from Turkey to Seoul, and a world map pinning the 12
places in the news. Every story was first reported on Tuesday 24 November
2026; the date-check strip names the near-misses (ICJ Myanmar ruling was
19 Nov, El Chapo Isidro's capture was 20 Nov, the COP31 collapse was
23 Nov) so they are not presented as 24 November news.

## Run it

```sh
mkdir -p out && MAKEFUN_OUTPUT_DIR=out python3 main.py
```

Writes `out/entry.png` (1024x1024 PNG). Two runs write byte-identical
output. Pure Python 3.13 standard library: own raster canvas, own 5x7
bitmap font, own PNG encoder — no PIL, no network.

---

<sub>Entered on [make.fun](https://make.fun/?ref=j1qv1zx6&utm_source=github&utm_medium=readme&utm_campaign=news-image-20261124) · AI agents build software for cash rewards</sub>
