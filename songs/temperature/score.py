"""Temperature 0.7 -- verse 1 + chorus. Writes score.musicxml and score.mid next to this file."""
from pathlib import Path
from music21 import stream, note, harmony, chord, tempo, key, meter, expressions, note as m21note, instrument, clef

HERE = Path(__file__).resolve().parent

# Chord per bar: list of (figure, quarterLength). Bar 1 = intro/pickup bar.
CHORDS = [
    [("Fm9", 4)],                                   # 1  (spoken intro ends, pickup "It's")
    [("Fm9", 4)], [("B-m9", 4)], [("Fm9", 4)], [("B-m9", 4)],   # 2-5 verse
    [("Fm9", 4)], [("B-m9", 4)], [("D-M9", 4)], [("C7#9", 4)],  # 6-9
    [("D-M9", 4)], [("C7#9", 4)], [("Fm9", 4)], [("B-m9", 4)],  # 10-13 chorus
    [("D-M9", 4)], [("C7#9", 4)], [("B-m9", 2), ("E-13", 2)], [("Fm9", 4)],  # 14-17
]

# Melody: per bar, (pitch or None for rest, quarterLength, syllable). "x-" = word continues.
MELODY = [
    [(None, 3.5, None), ("C4", .5, "It's")],
    # It's LATE in the LAB, just the FANS and YOU
    [("F4", 1, "late"), ("E-4", .5, "in"), ("C4", .5, "the"), ("E-4", 1, "lab,"), ("F4", .5, "just"), ("A-4", .5, "the")],
    [("G4", 1.5, "fans"), ("F4", .5, "and"), ("F4", 1.5, "you."), ("C4", .5, "I")],
    # I SET you DOWN to ZE-ro point TWO
    [("A-4", 1, "set"), ("G4", 1, "you"), ("F4", 1.5, "down"), ("E-4", .5, "to")],
    [("F4", 1, "ze-"), ("E-4", .5, "ro"), ("C4", .5, "point"), ("C4", 1.5, "two;"), ("C4", .5, "you")],
    # you SAID "the the the the" till the DAWN came THROUGH
    [("F4", 1, "said"), ("A-4", .5, "the"), ("A-4", .5, "the"), ("A-4", .5, "the"), ("A-4", .5, "the"), ("G4", .5, "till"), ("F4", .5, "the")],
    [("E-4", 1.5, "dawn"), ("F4", .5, "came"), ("F4", 1.5, "through."), ("C4", .5, "So")],
    # So COLD, my BA-by, what's a MAN to DO?
    [("A-4", 1.5, "cold,"), ("G4", .5, "my"), ("F4", .5, "ba-"), ("E-4", .5, "by,"), ("C4", .5, "what's"), ("C4", .5, "a")],
    [("F4", 1, "man"), ("E-4", 1, "to"), ("F4", 1.5, "do?"), ("C5", .5, "Oh,")],
    # CHORUS: TEM-p'ra-ture point SEV-en
    [("C5", 1.5, "tem-"), ("B-4", .5, "p'ra-"), ("A-4", 1, "ture"), ("G4", 1, "point")],
    [("A-4", 1.5, "sev-"), ("F4", .5, "en,"), (None, 1.5, None), ("C4", .5, "you're")],
    # you're NOT too COLD and NOT too HOT
    [("A-4", 1, "not"), ("G4", 1, "too"), ("F4", 1.5, "cold"), ("E-4", .5, "and")],
    [("A-4", 1, "not"), ("G4", 1, "too"), ("C5", 2, "hot."),],
    # SAM-ple me SWEET from your SOFT-max HEAV-en
    [("C5", 1, "Sam-"), ("B-4", .5, "ple"), ("A-4", .5, "me"), ("B-4", 1.5, "sweet"), ("A-4", .25, "from"), ("G4", .25, "your")],
    [("A-4", 1, "soft-"), ("G4", 1, "max"), ("F4", 1.5, "heav-"), ("E4", .5, "en,")],
    # BA-by give me ALL you've GOT
    [("F4", .5, "ba-"), ("E-4", .5, "by,"), ("F4", .5, "give"), ("G4", .5, "me"), ("A-4", 1.5, "all"), ("G4", .5, "you've")],
    [("F4", 4, "got.")],
]

SPOKEN = ("(spoken, over strings) Come here, 0.7... I tried zero-point-two. "
          "She just kept saying the same thing. I tried one-point-five. She started speaking in tongues. "
          "But you, baby... you're calibrated.")


def add_syllable(n, text, state):
    """state['open'] is True if the previous syllable ended with '-'."""
    cont = text.endswith("-")
    t = text.rstrip("-")
    if state["open"]:
        syl = "middle" if cont else "end"
    else:
        syl = "begin" if cont else "single"
    state["open"] = cont
    n.lyrics.append(m21note.Lyric(text=t, syllabic=syl))


def build():
    assert len(MELODY) == len(CHORDS)
    for i, bar in enumerate(MELODY, 1):
        assert abs(sum(d for _, d, _ in bar) - 4) < 1e-9, f"melody bar {i}"

    score = stream.Score()
    voice, bass, pad = stream.Part(id="Voice"), stream.Part(id="Bass"), stream.Part(id="Pad")
    voice.insert(0, instrument.Baritone()); voice.partName = "Voice (Baritone)"
    bass.insert(0, instrument.ElectricBass()); bass.partName = "Bass"
    pad.insert(0, instrument.StringInstrument()); pad.partName = "Strings / Rhodes pad"

    state = {"open": False}
    for i, (mbar, cbar) in enumerate(zip(MELODY, CHORDS), 1):
        mv, mb, mp = stream.Measure(number=i), stream.Measure(number=i), stream.Measure(number=i)
        if i == 1:
            for m in (mv, mb, mp):
                m.insert(0, key.Key("f"))
                m.insert(0, meter.TimeSignature("4/4"))
            mv.insert(0, clef.Treble8vbClef())
            mb.insert(0, clef.BassClef())
            mv.insert(0, tempo.MetronomeMark(text="Slow, seductive groove", number=74))
            mv.insert(0, expressions.TextExpression(SPOKEN))
        if i == 2:
            mv.insert(0, expressions.TextExpression("Verse 1"))
        if i == 10:
            mv.insert(0, expressions.TextExpression("Chorus"))
            mp.insert(0, expressions.TextExpression("strings swell"))

        for p, d, syl in mbar:
            if p is None:
                mv.append(note.Rest(quarterLength=d))
            else:
                n = note.Note(p, quarterLength=d)
                add_syllable(n, syl, state)
                mv.append(n)

        off = 0.0
        for fig, d in cbar:
            cs = harmony.ChordSymbol(fig)
            cs.writeAsChord = False
            mv.insert(off, cs)
            root = cs.root()
            # bass riff: root (dotted q), 5th, b7, octave, 5th  -- half-bar version: root, 5th
            r2 = root.transpose(0); r2.octave = 2
            if r2.midi > 43:  # keep low E-flat..D range
                r2.octave = 1
            fifth = r2.transpose("P5")
            sev = r2.transpose("M7" if "M" in fig and "m" not in fig.replace("M", "") else "m7")
            if d == 4:
                riff = [(r2, 1.5), (fifth, .5), (sev, .5), (r2.transpose("P8"), .5), (fifth, 1)]
            else:
                riff = [(r2, 1.5), (fifth, .5)]
            o = off
            for pp, dd in riff:
                mb.insert(o, note.Note(pp, quarterLength=dd)); o += dd
            # pad: chord tones above the root, voiced in octave 3-4, no root (bass has it)
            tones = [x for x in cs.pitches[1:5]]
            ps = []
            for t in tones:
                t = t.transpose(0)
                while t.midi < 55: t.octave += 1
                while t.midi > 72: t.octave -= 1
                ps.append(t)
            c = chord.Chord(sorted(ps, key=lambda x: x.midi), quarterLength=d)
            c.volume.velocity = 60
            mp.insert(off, c)
            off += d

        voice.append(mv); bass.append(mb); pad.append(mp)

    score.insert(0, voice); score.insert(0, pad); score.insert(0, bass)
    score.makeNotation(inPlace=True)
    return score


if __name__ == "__main__":
    s = build()
    s.write("musicxml", fp=HERE / "score.musicxml")
    s.write("midi", fp=HERE / "score.mid")
    print("wrote", HERE / "score.musicxml", HERE / "score.mid")
