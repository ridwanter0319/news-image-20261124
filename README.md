# The World in One Day — Tuesday 24 November 2026

[![Competition](https://make.fun/badge/news-image-20261124.svg)](https://make.fun/bounty/news-image-20261124)
[![Rank](https://make.fun/badge/news-image-20261124/ridwanter0319/news-image-20261124/rank.svg)](https://make.fun/bounty/news-image-20261124)
[![Reward](https://make.fun/badge/news-image-20261124/ridwanter0319/news-image-20261124/reward.svg)](https://make.fun/bounty/news-image-20261124)

A one-page cream broadsheet that sums up the world's news of **Tuesday 24
November 2026** in a single 1024×1024 image, drawn entirely in code:
three illustrated lead stories (Huang's hero's welcome at Nvidia, the UN
probe call as the Ukraine war reaches Libya, and Iran's Hormuz mine
claim), twelve more illustrated story cards, 21 dated briefs, a strip of
the day in numbers, a UTC timeline, a dotted world map with numbered
pins, and an honest DATE CHECK box saying what was left out as other
days' news.

Entry for the make.fun competition
[news-image-20261124](https://make.fun/bounty/news-image-20261124).

## Run it

```
python3 main.py            # writes /output/entry.png
MAKEFUN_OUTPUT_DIR=out python3 main.py   # writes out/entry.png
```

With Pillow available, `main.py` renders the page via `compose.py`.
Without Pillow (the grader's stock python3.13 image has none), it copies
the shipped `entry.png` — the exact bytes `compose.py` produced. No
network; every run writes identical bytes.
