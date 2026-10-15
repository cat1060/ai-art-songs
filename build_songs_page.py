"""Build the song-cycle playback page from songs/*/score.musicxml.

Each song becomes out_songs/data/<slug>.json (MusicXML for notation + per-part note lists for playback);
instrument samples are shared with the chorale page (out/sounds).
"""
import json, os, re, shutil
from music21 import converter, tempo

TITLES = {'grant-report-ballad': 'The Grant Report Ballad', 'parallel-fifths': 'Parallel Fifths (Again)',
          'seven-fingers': 'Seven Fingers', 'training-data': "It's Not Plagiarism, It's Training Data",
          'temperature': 'Temperature 0.7'}
ORDER = list(TITLES)
os.makedirs('out_songs/data', exist_ok=True)
shutil.copytree('out/sounds', 'out_songs/sounds', dirs_exist_ok=True)

index = []
for slug in ORDER:
    path = f'songs/{slug}/score.musicxml'
    if not os.path.exists(path):
        print('missing', path); continue
    s = converter.parse(path)
    mm = s.flatten().getElementsByClass(tempo.MetronomeMark)
    bpm = round(mm[0].getQuarterBPM()) if mm else 90
    # Play with repeats expanded; keep each note's written offset so the cursor can jump back
    written = {m.number: float(m.offset) for m in s.parts[0].getElementsByClass('Measure')}
    try: played = s.expandRepeats()
    except Exception: played = s
    parts = []
    for i, p in enumerate(played.parts):
        notes = []
        for m in p.stripTies().getElementsByClass('Measure'):   # tied notes sound once
            for n in m.flatten().notes:
                dur = float(n.quarterLength)
                if dur <= 0: continue              # grace notes
                on = float(m.offset + n.offset)
                w = written.get(m.number, float(m.offset)) + float(n.offset)
                for pp in n.pitches:
                    notes.append([pp.midi, on, dur, w])
        has_lyrics = any(n.lyric for n in s.parts[i].flatten().notes)
        name = p.partName or f'Part {i + 1}'
        parts.append({'name': name, 'notes': notes, 'lead': has_lyrics})
    title = TITLES[slug]
    lyr = f'songs/{slug}/lyrics.md'
    genre = ''
    if os.path.exists(lyr):
        m = re.search(r'genre[*:\s]*([^\n]+)', open(lyr).read(), re.I)
        genre = m.group(1).strip(' *:_') if m else ''
    data = {'title': title, 'genre': genre, 'bpm': bpm, 'parts': parts,
            'musicxml': open(path).read()}
    json.dump(data, open(f'out_songs/data/{slug}.json', 'w'))
    index.append({'id': slug, 'title': title, 'file': f'data/{slug}.json'})
    print(slug, title, bpm, 'bpm', [(p['name'], len(p['notes']), p['lead']) for p in parts])

tpl = open('songs_template.html').read()
open('out_songs/songs.html', 'w').write(tpl.replace('__INDEX__', json.dumps(index)))
