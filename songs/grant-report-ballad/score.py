"""Lead sheet + gospel piano for 'The Grant Report Ballad'. Writes score.musicxml / score.mid."""
import os
from music21 import stream, note, harmony, meter, key, tempo, chord, pitch, metadata, instrument

HERE = os.path.dirname(os.path.abspath(__file__))
R = None  # rest marker

# (pitch, quarterLength, syllable) -- 6/8, strong beats at 0.0 and 1.5 of each bar
VERSE1 = [
    [('G4',1.5,'Three'),('F4',1.0,'years'),('Eb4',.5,'a-')],
    [('G4',1.0,'go'),('Bb4',.5,'in'),('C5',1.0,'Sec-'),('Bb4',.5,'tion')],
    [('G4',2.0,'C'),(R,.5,None),('Eb4',.5,'I')],
    [('Bb4',1.0,'prom-'),('Ab4',.5,'ised'),('G4',1.0,'hu-'),('F4',.5,'man')],
    [('G4',1.0,'lev-'),('F4',.5,'el'),('Eb4',1.5,'art')],
    [(R,3.0,None)],
    [('G4',1.0,'Now'),('G4',.5,'my'),('Bb4',1.0,'mod-'),('G4',.5,'el')],
    [('C5',1.0,'writes'),('Bb4',.5,'a'),('Ab4',1.0,'son-'),('G4',.5,'net')],
    [(R,2.5,None),('Bb4',.5,'that')],
    [('Eb5',1.0,'rhymes'),(R,.5,None),('C5',1.0,'"heart"'),('Bb4',.5,'with')],
    [('C5',3.0,'"heart"')],          # same note as the first "heart": the joke is the repetition
    [(R,3.0,None)],
]
VERSE1_CH = ['Ebmaj7','Cm7','Abmaj7','Bb7','Ebmaj7','Bb7sus4','Gm7','C7','Fm7','Abm','Bb7','Bb7sus4']

def chorus(last_word):
    return [
        [('Eb5',1.5,'Oh,'),('C5',1.0,'Broad-'),('Bb4',.5,'er')],
        [('C5',1.0,'Im-'),('Bb4',.5,'pacts'),('Ab4',1.0,'hold'),('G4',.5,'me')],
        [('Ab4',1.5,'close'),(R,.5,None),('Bb4',.5,'In-'),('C5',.5,'tel-')],
        [('Eb5',1.0,'lec-'),('C5',.5,'tual'),('Bb4',1.0,'Mer-'),('Ab4',.5,'it')],
        [('Bb4',.5,'pray'),('G-4',.5,None),('G4',.5,'for'),('Bb4',1.5,'me')],  # blue-note b3 melisma on 'pray',
        [(R,1.0,None),('Eb4',.5,"I'll"),('Bb4',1.0,'call'),('Bb4',.5,'it')],
        [('C5',.75,'"prom-'),('Bb4',.25,'is-'),('Ab4',.25,'ing'),('G4',.25,'re-'),('Bb4',1.0,'sults"'),('G4',.5,'and')],
        [('Bb4',1.0,'beg'),('Ab4',.5,'ex-'),('G4',1.0,'ten-'),('F4',.5,'sion')],
        [('G4',1.0,'num-'),('F4',.5,'ber'),('Eb4',1.5,last_word)],
        [('Eb4',3.0,None)],  # held (tied below)
    ]
CHORUS_CH = ['Abmaj7','Bb7','Gm7','Cm7','Fm7','Bb7','Gm7','C7','Fm7','Eb']

KINDS = ['maj7','sus4','m7','7','m','']
def split(fig):
    for k in KINDS:
        if fig.endswith(k) and len(fig) > len(k):
            return fig[:len(fig)-len(k)], k
def tr(fig, interval):
    if not interval: return fig
    r, k = split(fig)
    return pitch.Pitch(r).transpose(interval).name.replace('-','b') + k

def add_bars(mel, acc, bars, chords, interval=None, first_extras=()):
    for i, (bar, fig) in enumerate(zip(bars, chords)):
        fig = tr(fig, interval)
        m, a = stream.Measure(), stream.Measure()
        if i == 0:
            for e in first_extras:
                m.insert(0, e[0]); a.insert(0, e[1])
        cs = harmony.ChordSymbol(fig.replace('b','-') if len(fig)>1 and fig[1]=='b' else fig)
        m.insert(0, cs)
        prev = None
        for p, d, syl in bar:
            if p is None:
                n = note.Rest(quarterLength=d)
            else:
                n = note.Note(p, quarterLength=d)
                if interval: n.transpose(interval, inPlace=True)
                if syl: n.lyric = syl
            m.append(n)
        if bar[0][2] is None and bar[0][0] and mel.getElementsByClass('Measure'):
            last = mel.getElementsByClass('Measure')[-1].notes[-1]
            from music21 import tie
            last.tie = tie.Tie('start'); m.notes[0].tie = tie.Tie('stop')
        mel.append(m)
        # 6/8 gospel piano: LH root + fifth dotted halves, RH rolling eighths 1-3-5-7-5-3
        tones = [pp for pp in cs.pitches]
        root = pitch.Pitch(tones[0].name + '2')
        a.insert(0, chord.Chord([root, root.transpose('P5')], quarterLength=3.0))
        rh = [t.transpose(0) for t in tones]
        for t in rh: t.octave = 4 if t.name >= 'F' or True else 4
        seq = [rh[0], rh[1 % len(rh)], rh[2 % len(rh)], rh[-1], rh[2 % len(rh)], rh[1 % len(rh)]]
        a.insert(0, stream.Voice())  # placeholder for layout
        v = stream.Voice([note.Note(s, quarterLength=.5) for s in seq])
        a.insert(0, v)
        acc.append(a)

def build():
    s = stream.Score()
    s.metadata = metadata.Metadata(title='The Grant Report Ballad', composer='CS85 Song Cycle')
    mel, acc = stream.Part(), stream.Part()
    mel.insert(0, instrument.Vocalist()); acc.insert(0, instrument.Piano())
    start = [(tempo.MetronomeMark('Soulful, with gospel lift', 54, referent=note.Note(quarterLength=1.5)), tempo.MetronomeMark(number=54, referent=note.Note(quarterLength=1.5))),
             (meter.TimeSignature('6/8'), meter.TimeSignature('6/8')),
             (key.Key('E-'), key.Key('E-'))]
    add_bars(mel, acc, VERSE1, VERSE1_CH, first_extras=start)
    add_bars(mel, acc, chorus('three'), CHORUS_CH)
    # pivot bar: C7 = V of F, gospel "truck-driver" lift
    add_bars(mel, acc, [[(R,2.5,None),('C5',.5,'Lord,')]], ['C7'])
    add_bars(mel, acc, chorus('four'), CHORUS_CH, interval='M2',
             first_extras=[(key.Key('F'), key.Key('F'))])
    # final chorus: drop the redundant pickup "Oh" at the downbeat is sung on the pivot already
    for p in (mel, acc):
        for v in p.recurse().getElementsByClass('Voice'):
            if not v.notes: v.activeSite.remove(v)
    s.insert(0, mel); s.insert(0, acc)
    return s

if __name__ == '__main__':
    sc = build()
    sc.write('musicxml', os.path.join(HERE, 'score.musicxml'))
    sc.write('midi', os.path.join(HERE, 'score.mid'))
    print('wrote score.musicxml and score.mid')
