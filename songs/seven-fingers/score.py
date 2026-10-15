"""Seven Fingers -- G&S-style patter song. Builds score.musicxml and score.mid."""
import os
from music21 import stream, note, chord, harmony, meter, key, tempo, note as n21, clef, instrument, metadata

HERE = os.path.dirname(os.path.abspath(__file__))

# Each entry: (chords per bar, hyphenated text). 8-syllable lines -> 2 bars of eighths;
# 16-syllable patter lines -> 2 bars of sixteenths (8 per bar).
V1 = [
    (["F", "C7"], "Look u-pon this love-ly la-dy,"),
    (["C7", "F"], "Sev-en fin-gers, slight-ly sha-dy;"),
    (["F", "B-"], "Ev-ry knuck-le bent and twist-ed,"),
    (["G7", "C"], "Six of which were nev-er list-ed!"),
    (["F", "C7"], "Count her teeth: there's for-ty-sev-en,"),
    (["C7", "F"], "Ranked in rows like Dan-te's heav-en;"),
    (["Dm", "B-"], "Signs in soup-of-al-pha-bet-ic,"),
    (["G7", "C7"], "Chairs with three legs, quite ath-let-ic!"),
]
PATTER1 = [
    (["F", "B-", "C7", "F"], "Bench-marks soar and loss-es plum-met, check the graph, the line goes up-ward,"),
    (["B-", "F", "G7", "C7"], "Fund-ing flows and pa-pers pub-lish, nev-er mind the hand's a cup-board!"),
]
REFRAIN = [
    (["F", "B-"], "State of art and state of sci-ence!"),
    (["C7", "F"], "Sev-en fin-gers? Full com-pli-ance!"),
    (["F", "B-"], "Peer-re-viewed and pre-print post-ed,"),
    (["G7", "C7"], "Ev-ry crit-ic's be-ing roast-ed!"),
    (["F", "Dm"], "Ten is bor-ing, sev-en's bet-ter!"),
    (["B-", "C7"], "Who can read? Who needs a let-ter?"),
]


def syllables(text):
    out = []
    for word in text.split():
        parts = word.split("-")
        for i, s in enumerate(parts):
            if len(parts) == 1:
                kind = "single"
            elif i == 0:
                kind = "begin"
            elif i == len(parts) - 1:
                kind = "end"
            else:
                kind = "middle"
            out.append((s, kind))
    return out


def tones(sym):
    """Chord tones of a symbol in singing range: (root, third, fifth, high root)."""
    cs = harmony.ChordSymbol(sym)
    names = [p.name for p in cs.pitches]
    def place(nm, lo=65):  # at/above F4
        p = n21.Note(nm + "4").pitch
        while p.midi < lo:
            p.octave += 1
        while p.midi > lo + 11:
            p.octave -= 1
        return p
    r, t, f = place(names[0]), place(names[1]), place(names[2])
    hi = place(names[0], 72)
    return r, t, f, hi


# The repeated melodic cell (indices into chord tones r,t,f,hi).
CELL_8 = [2, 2, 1, 0]                 # one bar of eighths: 5-5-3-1
CELL_16 = [3, 2, 1, 2, 3, 2, 1, 0]    # one bar of sixteenths: rocking arpeggio


def add_line(mel, acc, chords, text, dur):
    syls = syllables(text)
    cell = CELL_8 if dur == 0.5 else CELL_16
    per_bar = len(cell)
    assert len(syls) == per_bar * len(chords), (text, len(syls))
    for b, sym in enumerate(chords):
        m = stream.Measure()
        m.insert(0, harmony.ChordSymbol(sym))
        tn = tones(sym)
        for i, idx in enumerate(cell):
            s, kind = syls[b * per_bar + i]
            nn = note.Note(tn[idx], quarterLength=dur)
            if b == len(chords) - 1 and i == per_bar - 1 and dur == 0.5:
                nn.pitch = tn[0]  # cadence the cell on the root
            ly = note.Lyric(text=s.strip(",;:!?."), syllabic=kind)
            nn.lyrics.append(ly)
            m.append(nn)
        mel.append(m)
        acc.append(oompah(sym))


def oompah(sym):
    """Operetta oom-pah: bass / chord / fifth-bass / chord in eighths."""
    cs = harmony.ChordSymbol(sym)
    root = cs.root().name
    fifth = cs.pitches[2].name
    def bass(nm):
        p = n21.Note(nm + "2").pitch
        while p.midi < 41:
            p.octave += 1
        return note.Note(p, quarterLength=0.5)
    upper = [p for p in cs.pitches]
    def ch():
        ps = []
        for p in upper:
            q = n21.Note(p.name + "3").pitch
            while q.midi < 55:
                q.octave += 1
            ps.append(q)
        c = chord.Chord(sorted(ps, key=lambda x: x.midi), quarterLength=0.5)
        c.articulations = []
        return c
    m = stream.Measure()
    for el in (bass(root), ch(), bass(fifth), ch()):
        m.append(el)
    return m


def build():
    sc = stream.Score()
    sc.metadata = metadata.Metadata(title="Seven Fingers", composer="(original patter song)")
    mel, acc = stream.Part(), stream.Part()
    mel.insert(0, instrument.Vocalist()); mel.partName = "Professor"
    acc.insert(0, instrument.Piano()); acc.partName = "Piano"

    # Intro: two bars of vamp, rests in voice.
    for i, sym in enumerate(["F", "C7"]):
        m = stream.Measure()
        if i == 0:
            m.insert(0, tempo.MetronomeMark(text="Allegro vivace", number=144))
            m.insert(0, key.Key("F")); m.insert(0, meter.TimeSignature("2/4"))
        m.insert(0, harmony.ChordSymbol(sym))
        m.append(note.Rest(quarterLength=2))
        mel.append(m)
        am = oompah(sym)
        if i == 0:
            am.insert(0, key.Key("F")); am.insert(0, meter.TimeSignature("2/4"))
            am.insert(0, clef.BassClef())
        acc.append(am)

    for chords, text in V1:
        add_line(mel, acc, chords, text, 0.5)
    for chords, text in PATTER1:
        # 16 syllables over 2 bars, harmony changes every beat -> use first chord of each pair per bar
        add_line(mel, acc, chords[::2], text, 0.25)
    for chords, text in REFRAIN:
        add_line(mel, acc, chords, text, 0.5)

    # Tag: "STATE of the ART!"
    m1, m2 = stream.Measure(), stream.Measure()
    m1.insert(0, harmony.ChordSymbol("C7")); m2.insert(0, harmony.ChordSymbol("F"))
    for p, ql, s, k in [("C5", 1, "State", "single"), ("B-4", .5, "of", "single"), ("G4", .5, "the", "single")]:
        x = note.Note(p, quarterLength=ql); x.lyrics.append(note.Lyric(s, syllabic=k)); m1.append(x)
    x = note.Note("F5", quarterLength=2); x.lyrics.append(note.Lyric("ART!", syllabic="single")); m2.append(x)
    mel.append([m1, m2])
    acc.append(oompah("C7"))
    fin = stream.Measure(); fin.append(chord.Chord(["F2", "F3", "A3", "C4"], quarterLength=2)); acc.append(fin)

    sc.insert(0, mel); sc.insert(0, acc)
    return sc


if __name__ == "__main__":
    s = build()
    s.write("musicxml", fp=os.path.join(HERE, "score.musicxml"))
    s.write("midi", fp=os.path.join(HERE, "score.mid"))
    print("wrote score.musicxml and score.mid")
