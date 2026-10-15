"""It's Not Plagiarism, It's Training Data -- vamp, A1 (Chair), and Hook (Brisk).

Builds the score with music21 and writes score.musicxml and score.mid next to this file.
"""
from pathlib import Path
from music21 import stream, note, chord, harmony, meter, key, tempo, clef, metadata, expressions, instrument, bar, articulations

HERE = Path(__file__).resolve().parent
TS = 4.0

# ---- form: list of bars, each a list of (offset, chord symbol) ----
VAMP = [[(0, "B-6"), (2, "Gm7")], [(0, "Cm7"), (2, "F7")]] * 2
A1 = [[(0, "B-6")], [(0, "Gm7")], [(0, "Cm7")], [(0, "F7")],
      [(0, "B-6")], [(0, "Gm7")], [(0, "Cm7")], [(0, "F7")]]
HOOK = [[(0, "B-")], [(0, "Gm7")], [(0, "Cm7")], [(0, "F7")],
        [(0, "B-")], [(0, "D7")], [(0, "Gm7"), (2, "Edim7")],
        [(0, "B-/F"), (2, "F7")], [(0, "B-6")]]
BARS = VAMP + A1 + HOOK

# ---- vocal lines: (pitch|'r', quarterLength, syllable) per bar ----
CHAIR = [
    [("D3", 1, "I-"), ("D3", 1, "tem"), ("F3", 2, "four")],
    [("D3", .5, "on"), ("D3", .5, "the"), ("B-2", 1, "a-"), ("G3", 1, "gen-"), ("F3", 1, "da:")],
    [("E-3", 1, "Some-"), ("C3", 1, "one"), ("G3", 1, "moved,"), ("F3", 1, "and")],
    [("F3", 1, "some-"), ("E-3", 1, "one"), ("A3", 1, "sec-"), ("F3", .5, "on-"), ("C3", .5, "ded;")],
    [("D3", 1, "Is"), ("B-2", 1, "it"), ("F3", 1, "art,"), ("D3", 1, "the")],
    [("G3", 1, "stuff"), ("F3", 1, "we're"), ("D3", 1, "fund-"), ("B-2", 1, "ing,")],
    [("C3", 1, "or"), ("E-3", 1, "a"), ("G3", 1, "bill"), ("F3", 1, "we")],
    [("A3", 1, "hav-"), ("G3", 1, "en't"), ("E-3", 1, "reck-"), ("F3", 1, "oned?")],
]
BRISK = [
    [("r", 2, None), ("F3", .5, "It's"), ("G3", .5, "not"), ("A3", 1, "pla-")],
    [("B-3", 1, "gia-"), ("D4", .5, "rism,"), ("C4", .5, "it's"), ("B-3", 1, "train-"), ("G3", 1, "ing")],
    [("E-4", 2, "da-"), ("C4", 1, "ta!"), ("A3", .5, "Not"), ("B-3", .5, "a")],
    [("C4", 1, "forg-"), ("A3", .5, "er-"), ("F3", .5, "y,"), ("r", 1, None), ("F3", 1, "a")],
    [("D4", 1, "fea-"), ("C4", 1, "ture"), ("B-3", 1, "vec-"), ("F3", 1, "tor!")],
    [("r", 2, None), ("F#3", .5, "It's"), ("G3", .5, "not"), ("A3", 1, "pla-")],
    [("B-3", 1, "gia-"), ("D4", .5, "rism,"), ("C4", .5, "it's"), ("D-4", 1, "train-"), ("B-3", 1, "ing")],
    [("D4", 4, "da-")],
    [("B-3", 2, "ta!"), ("r", 2, None)],
]


def rest_bar():
    r = note.Rest(quarterLength=TS)
    return [r]


def vocal_events(spec):
    out = []
    for p, ql, syl in spec:
        n = note.Rest(quarterLength=ql) if p == "r" else note.Note(p, quarterLength=ql)
        if syl and p != "r":
            n.lyric = syl
        out.append(n)
    return out


def build_vocal(name, inst, cl, start, spec):
    part = stream.Part(id=name)
    part.partName = name
    part.insert(0, inst)
    for i in range(len(BARS)):
        m = stream.Measure(number=i + 1)
        if i == 0:
            m.append([cl, key.Key("B-"), meter.TimeSignature("4/4")])
        j = i - start
        evs = vocal_events(spec[j]) if 0 <= j < len(spec) else rest_bar()
        for e in evs:
            m.append(e)
        part.append(m)
    return part


def build_piano():
    rh, lh = stream.Part(id="PianoRH"), stream.Part(id="PianoLH")
    rh.partName, lh.partName = "Piano", "Piano LH"
    rh.insert(0, instrument.Piano())
    lh.insert(0, instrument.Piano())
    for i, changes in enumerate(BARS):
        mr, ml = stream.Measure(number=i + 1), stream.Measure(number=i + 1)
        if i == 0:
            mr.append([clef.TrebleClef(), key.Key("B-"), meter.TimeSignature("4/4")])
            ml.append([clef.BassClef(), key.Key("B-"), meter.TimeSignature("4/4")])
            mr.insert(0, tempo.MetronomeMark(text="Brightly, soft-shoe vamp", number=132))
        if i == len(VAMP):
            mr.insert(0, expressions.RehearsalMark("A1 - Call to Order"))
        if i == len(VAMP) + len(A1):
            mr.insert(0, expressions.RehearsalMark("Hook"))
        # chord in effect on each beat
        for beat in range(4):
            sym = [s for off, s in changes if off <= beat][-1]
            cs = harmony.ChordSymbol(sym)
            if any(off == beat for off, _ in changes):
                mr.insert(beat, harmony.ChordSymbol(sym))
            root = cs.bass() if "/" in sym else cs.root()
            nxt = BARS[i + 1][0][1] if i + 1 < len(BARS) else None
            if beat == 0:
                lp = root
            elif beat == 2:
                lp = cs.fifth if "/" not in sym else cs.root()
            elif beat == 3 and nxt:
                # chromatic approach from a half step below the next root (Broadway walk-up)
                lp = harmony.ChordSymbol(nxt).root().transpose(-1)
            else:
                lp = None
            if lp is not None:
                ln = note.Note(lp.name, quarterLength=1)
                ln.octave = 2
                while ln.pitch.midi < 38:
                    ln.octave += 1
                if beat == 3:
                    ln.volume.velocity = 60
                ml.insert(beat, ln)
            else:
                ml.insert(beat, note.Rest(quarterLength=1))
            # RH: soft-shoe "chk" on 2 and 4 (close voicing around middle C), rest on 1 and 3
            if beat in (1, 3):
                pcs = [p.name for p in cs.pitches if p.name != root.name] or [p.name for p in cs.pitches]
                voiced = []
                for nm in pcs[:3]:
                    pt = note.Note(nm).pitch
                    pt.octave = 4
                    if pt.midi > 70:
                        pt.octave = 3
                    voiced.append(pt)
                c = chord.Chord(voiced, quarterLength=1)
                c.articulations = []
                mr.insert(beat, c)
            else:
                mr.insert(beat, note.Rest(quarterLength=1))
        if i == len(BARS) - 1:
            # BUTTON: held Bb6 under "ta!", then a tutti unison hit (the gavel) on beat 4
            mr, ml = stream.Measure(number=i + 1), stream.Measure(number=i + 1)
            mr.insert(0, harmony.ChordSymbol("B-6"))
            held = chord.Chord(["D4", "F4", "G4", "B-4"], quarterLength=2)
            held.expressions.append(expressions.Fermata())
            mr.insert(0, held)
            mr.insert(2, note.Rest(quarterLength=1))
            hit = chord.Chord(["B-4", "B-5"], quarterLength=1)
            hit.articulations.append(articulations.StrongAccent())
            mr.insert(3, hit)
            ml.insert(0, note.Note("B-1", quarterLength=2))
            ml.insert(2, note.Rest(quarterLength=1))
            lhit = chord.Chord(["B-1", "B-2"], quarterLength=1)
            lhit.articulations.append(articulations.StrongAccent())
            ml.insert(3, lhit)
            mr.insert(3, expressions.TextExpression("GAVEL"))
            mr.rightBarline = bar.Barline("final")
            ml.rightBarline = bar.Barline("final")
        rh.append(mr)
        lh.append(ml)
    # button hit: last-bar beat-4 chord gets an accent; vamp repeat marks
    rh.getElementsByClass(stream.Measure)[0].leftBarline = bar.Repeat(direction="start")
    rh.getElementsByClass(stream.Measure)[len(VAMP) - 1].rightBarline = bar.Repeat(direction="end")
    return rh, lh


def main():
    s = stream.Score()
    s.insert(0, metadata.Metadata(title="It's Not Plagiarism, It's Training Data",
                                  composer="Song 3 of 5 -- faculty-meeting ensemble number"))
    s.insert(0, build_vocal("Chair", instrument.Bass(), clef.BassClef(), len(VAMP), CHAIR))
    s.insert(0, build_vocal("Brisk", instrument.Tenor(), clef.Treble8vbClef(), len(VAMP) + len(A1), BRISK))
    rh, lh = build_piano()
    s.insert(0, rh)
    s.insert(0, lh)
    s.write("musicxml", fp=HERE / "score.musicxml")
    s.write("midi", fp=HERE / "score.mid")
    print("wrote", HERE / "score.musicxml", HERE / "score.mid")


if __name__ == "__main__":
    main()
