"""Parallel Fifths (Again) -- lead sheet + country-waltz accompaniment.

Builds verse 1 and the chorus. Writes score.musicxml and score.mid next to this file.
The accompaniment is boom-chick-chick (bass on 1, triad on 2 and 3) and avoids
parallels everywhere EXCEPT one labeled spot under the words "parallel fifths".
"""
from pathlib import Path
from music21 import (stream, note, chord, harmony, meter, key, tempo,
                     expressions, metadata, instrument)

HERE = Path(__file__).resolve().parent

# Melody: one list per bar of (pitch or None for rest, quarterLength, syllable).
# Syllable hyphens mark word breaks ("chor-" = start, "ales" = end).
MELODY = [
    # bar 0: pickup
    [(None, 2, None), ("D4", 1, "I")],
    # Verse 1
    [("G4", 1, "fed"), ("G4", 1, "it"), ("A4", 1, "cho-")],
    [("B4", 1, "-rales,"), ("A4", 1, "all"), ("G4", 1, "three")],
    [("E5", 1, "hun-"), ("D5", 1, "-dred"), ("C5", 1, "and")],
    [("B4", 2, "one,"), ("D4", 1, "Re-")],
    [("G4", 1, "-wrote"), ("B4", 1, "all"), ("D5", 1, "the")],
    [("D5", 1, "rules"), ("C5", 1, "till"), ("B4", 1, "the")],
    [("A4", 1, "cof-"), ("F#4", 1, "-fee"), ("A4", 1, "was")],
    [("A4", 2, "gone."), ("D4", 0.5, "But"), ("E4", 0.5, "the")],
    [("G4", 1, "bass"), ("B4", 1, "loved"), ("D5", 1, "the")],
    [("E5", 1, "ten-"), ("D5", 1, "-or"), ("C5", 1, "a")],
    [("B4", 1, "fifth"), ("A4", 1, "up"), ("G4", 1, "a-")],
    [("G#4", 2, "-bove,"), ("B4", 0.5, "and"), ("B4", 0.5, "it's")],
    [("C5", 1, "move-"), ("B4", 1, "-ment"), ("A4", 1, "in")],
    [("A4", 1, "par-"), ("F#4", 1, "-al-"), ("A4", 1, "-lel,")],
    [("B4", 1, "just"), ("A4", 1, "like"), ("F#4", 1, "our")],
    [("G4", 2, "love."), ("D4", 1, "It's")],
    # Chorus
    [("E5", 1, "par-"), ("D5", 1, "-al-"), ("C5", 1, "-lel")],
    [("E5", 2, "fifths"), ("D5", 1, "a-")],
    [("D5", 3, "-gain,")],
    [("B4", 2, "dar-"), ("A4", 0.5, "-lin',"), ("G4", 0.5, "the")],
    [("E5", 1, "same"), ("E5", 1, "old"), ("D5", 1, "mis-")],
    [("C5", 1, "-take"), ("C5", 1, "that"), ("B4", 1, "it")],
    [("A4", 1, "made"), ("B4", 1, "way"), ("C5", 1, "back")],
    [("D5", 2, "when."), ("D4", 1, "I'm")],
    [("G4", 1, "down"), ("G4", 1, "at"), ("A4", 1, "the")],
    [("B4", 1, "bar"), ("G#4", 1, "where"), ("B4", 1, "they")],
    [("C5", 1, "don't"), ("B4", 1, "check"), ("A4", 1, "the")],
    [("C5", 2, "rules,"), ("B4", 0.5, "and"), ("A4", 0.5, "my")],
    [("D5", 1, "heart"), ("C5", 1, "moves"), ("A4", 1, "in")],
    [("C5", 1, "fifths"), ("B4", 1, "like"), ("A4", 1, "a")],
    [("B4", 1, "cou-"), ("A4", 1, "-ple"), ("A4", 1, "of")],
    [("G4", 3, "fools.")],
]

CHORDS = [None,
          "G", "G", "C", "G", "G", "G", "D7", "D7",
          "G7", "C", "G", "E7", "Am", "D7", "G", "G",
          "C", "C", "G", "G", "C", "C", "D7", "D7",
          "G", "E7", "Am", "Am", "D7", "D7", "G", "G"]

# Close-position voicings for the "chick" beats, chosen for smooth common-tone motion.
VOICING = {"G": ["B3", "D4", "G4"], "C": ["C4", "E4", "G4"], "D7": ["C4", "F#4", "A4"],
           "G7": ["B3", "D4", "F4"], "E7": ["B3", "D4", "G#4"], "Am": ["C4", "E4", "A4"]}
BASS = {"G": ("G2", "D2"), "C": ("C3", "G2"), "D7": ("D3", "A2"), "G7": ("G2", "D2"),
        "E7": ("E2", "B2"), "Am": ("A2", "E2")}

JOKE_BAR = 17  # under "PAR-al-lel": bare fifths C-G, D-A, E-B marching in lockstep


def build_melody():
    part = stream.Part(id="Voice")
    part.insert(0, instrument.Vocalist())
    for i, bar in enumerate(MELODY):
        m = stream.Measure(number=i)
        if i == 0:
            m.append([key.Key("G"), meter.TimeSignature("3/4"),
                      tempo.MetronomeMark(text="Slow waltz", number=96)])
        if CHORDS[i]:
            m.insert(0, harmony.ChordSymbol(CHORDS[i]))
        for p, ql, syl in bar:
            n = note.Rest(quarterLength=ql) if p is None else note.Note(p, quarterLength=ql)
            if syl:
                n.lyrics.append(note.Lyric(text=syl))  # hyphens -> syllabic
            m.append(n)
        part.append(m)
    return part


def build_accompaniment():
    part = stream.Part(id="Band")
    part.insert(0, instrument.Piano())
    for i, sym in enumerate(CHORDS):
        m = stream.Measure(number=i)
        if i == 0:
            m.append([key.Key("G"), meter.TimeSignature("3/4")])
            m.append(note.Rest(quarterLength=2))
            m.append(note.Note("D3", quarterLength=1))  # walk-up
        elif i == JOKE_BAR:
            m.insert(0, expressions.TextExpression(
                "DELIBERATE PARALLEL FIFTHS (the AI insisted)"))
            for low, high in (("C3", "G3"), ("D3", "A3"), ("E3", "B3")):
                m.append(chord.Chord([low, high], quarterLength=1))
        else:
            root, fifth = BASS[sym]
            m.append(note.Note(root if i % 2 else fifth, quarterLength=1))
            m.append(chord.Chord(VOICING[sym], quarterLength=1))
            m.append(chord.Chord(VOICING[sym], quarterLength=1))
        part.append(m)
    return part


def main():
    s = stream.Score()
    s.metadata = metadata.Metadata(title="Parallel Fifths (Again)",
                                   composer="CS Faculty Song Cycle, No. ?")
    s.insert(0, build_melody())
    s.insert(0, build_accompaniment())
    s.write("musicxml", fp=HERE / "score.musicxml")
    s.write("midi", fp=HERE / "score.mid")
    for f in ("score.musicxml", "score.mid"):
        print(f, (HERE / f).exists())


if __name__ == "__main__":
    main()
