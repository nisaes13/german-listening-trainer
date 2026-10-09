#!/usr/bin/env python3
"""Generate German Katja Neural MP3s from the contextual book cards."""
import asyncio
import json
from pathlib import Path
import edge_tts

BASE = Path(__file__).parent
OUT = BASE / "audio"
CARDS = json.loads((BASE / "cards.json").read_text(encoding="utf8"))
VOICE = "de-DE-KatjaNeural"

async def produce(card, kind, text, sem):
    target = OUT / f"{card['id']}-{kind}.mp3"
    async with sem:
        for attempt in range(4):
            try:
                await edge_tts.Communicate(text=text, voice=VOICE, rate="-7%").save(str(target))
                if target.stat().st_size < 1300:
                    raise RuntimeError("MP3 unexpectedly small")
                print("OK", target.name, target.stat().st_size)
                return
            except Exception as e:
                print("RETRY", target.name, attempt+1, repr(e))
                target.unlink(missing_ok=True)
                if attempt == 3:
                    raise
                await asyncio.sleep((attempt+1)*2)

async def main():
    OUT.mkdir(exist_ok=True)
    sem = asyncio.Semaphore(4)
    jobs = []
    for card in CARDS:
        jobs.append(produce(card,"word",card["word"],sem))
        jobs.append(produce(card,"book",card["book"],sem))
    await asyncio.gather(*jobs)
    for card in CARDS:
        for kind in ("word","book"):
            assert (OUT / f"{card['id']}-{kind}.mp3").stat().st_size > 1300
    print(f"PASS: all {len(CARDS)*2} contextual MP3 files exist.")

if __name__=="__main__":
    asyncio.run(main())
