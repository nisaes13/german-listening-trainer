#!/usr/bin/env python3
"""Render Gregs Tagebuch vocabulary and example sentences as German neural-speech MP3s."""
import asyncio
from pathlib import Path
import edge_tts

VOICE = "de-DE-KatjaNeural"
OUT = Path(__file__).parent / "audio"
CARDS = [
 ("zuerst", "Zuerst lese ich."),
 ("das Tagebuch", "Das ist mein Tagebuch."),
 ("klarstellen", "Ich will etwas klarstellen."),
 ("erwischen", "Meine Mutter erwischt mich."),
 ("reich", "Er ist reich."),
 ("berühmt", "Sie ist berühmt."),
 ("momentan", "Momentan bin ich zu Hause."),
 ("umzingelt", "Ich bin umzingelt."),
 ("sich wundern", "Ich wundere mich."),
 ("die Prügelei", "Es gibt eine Prügelei."),
 ("es gibt", "Es gibt viele Kinder."),
 ("ich möchte", "Ich möchte einen Kaffee."),
 ("warten auf", "Ich warte auf den Bus."),
 ("aufpassen", "Pass bitte auf!"),
 ("rechtzeitig", "Ich komme rechtzeitig."),
 ("zu spät", "Ich bin zu spät."),
 ("Ist der Platz frei?", "Ist der Platz frei?"),
 ("sich setzen", "Ich setze mich hier hin."),
]

async def render_file(i, kind, sentence, semaphore):
    target = OUT / f"{i:02d}-{kind}.mp3"
    async with semaphore:
        for attempt in range(4):
            try:
                await edge_tts.Communicate(text=sentence, voice=VOICE, rate="-7%").save(str(target))
                if target.stat().st_size < 1200:
                    raise RuntimeError("MP3 is too short")
                print(f"OK {target.name} {target.stat().st_size} bytes")
                return
            except Exception as exc:
                print(f"Attempt {attempt + 1}/4 failed for {target.name}: {exc}")
                target.unlink(missing_ok=True)
                if attempt == 3:
                    raise
                await asyncio.sleep((attempt + 1)*3)

async def main():
    OUT.mkdir(parents=True, exist_ok=True)
    semaphore = asyncio.Semaphore(2)
    await asyncio.gather(*(
        render_file(i, kind, text, semaphore)
        for i, (word, example) in enumerate(CARDS, 1)
        for kind, text in (("word", word), ("example", example))
    ))
    assert len(list(OUT.glob("*.mp3"))) == 36, "Not all 36 files were produced"
    print("SUCCESS: 18 German word MP3s and 18 example MP3s.")

if __name__ == "__main__":
    asyncio.run(main())
