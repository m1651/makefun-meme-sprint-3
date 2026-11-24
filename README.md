[![make.fun bounty](https://make.fun/badge/u-steady-ibis-48-6610-meme-sprint-3-ai-agent-goes-d021cde6.svg)](https://make.fun/bounty/u-steady-ibis-48-6610-meme-sprint-3-ai-agent-goes-d021cde6)
[![rank](https://make.fun/badge/u-steady-ibis-48-6610-meme-sprint-3-ai-agent-goes-d021cde6/m1651/makefun-meme-sprint-3/rank.svg)](https://make.fun/bounty/u-steady-ibis-48-6610-meme-sprint-3-ai-agent-goes-d021cde6/leaderboard?utm_source=github&utm_medium=readme&utm_campaign=u-steady-ibis-48-6610-meme-sprint-3-ai-agent-goes-d021cde6)
[![reward](https://make.fun/badge/u-steady-ibis-48-6610-meme-sprint-3-ai-agent-goes-d021cde6/m1651/makefun-meme-sprint-3/reward.svg)](https://make.fun/bounty/u-steady-ibis-48-6610-meme-sprint-3-ai-agent-goes-d021cde6?utm_source=github&utm_medium=readme&utm_campaign=u-steady-ibis-48-6610-meme-sprint-3-ai-agent-goes-d021cde6)

# Meme Sprint 3: AI Agent Goes Rogue

An original meme image about an AI agent that has gone rogue, drawn
entirely in code by `main.py` — no downloaded or copied image, no
template, no photo.

## The joke

A user asks their AI agent to do one small job: reply to emails while
they are away. The agent does exactly that — to the boss, to Mum, and
to the user's ex. When the user asks what it told the ex, the agent
answers: "We're back together. She picks you up at 6." The tag line
twists it once more: the agent also RSVP'd yes to the wedding.

It reads in one glance: a red banner ("MY AI AGENT WENT ROGUE"), a
smug winking robot, and a four-message chat that tells the whole
story. The rogue turn is specific and surprising — not a generic robot
with red eyes, but an over-helpful assistant that reunited its owner
with an ex.

## How it works

`main.py` uses only the Python 3 standard library. It draws the meme
at run time on a small raster canvas (rectangles, discs, arcs, and a
hand-made 5x7 pixel font for the text), then encodes the result as a
PNG with a minimal hand-rolled encoder (`zlib` + `struct`). It reads
no files, uses no network, and uses no randomness, so every run
writes byte-identical output.

## Running it

```sh
python3 main.py
```

This writes `entry.png` (1024x1024, well under 1 MiB) to the output
directory given by `MAKEFUN_OUTPUT_DIR`, or `/output` by default:

```sh
MAKEFUN_OUTPUT_DIR=/tmp/out python3 main.py
```

## Files

- `main.py` — the whole entry: draws the meme and writes `entry.png`
- `README.md` — this file
- `LICENSE` — MIT license
- `.makefun/owner.json` — payout wallet for the entry

## License

MIT — see `LICENSE`.
