# AI Art Songs

Five songs about computer science faculty trying to get AI to make art that doesn't suck:

| Song | Genre |
|---|---|
| The Grant Report Ballad | Soul ballad |
| Parallel Fifths (Again) | Country weeper |
| Seven Fingers | Gilbert & Sullivan patter song |
| It's Not Plagiarism, It's Training Data | Late-20th-century Broadway |
| Temperature 0.7 | 1970s Barry White-style R&B |

**Listen:** https://cat1060.github.io/ai-art-songs/ shows each score with lyrics and plays it with a following cursor.

Each folder in `songs/` holds the full lyrics (`lyrics.md`), the music21 script (`score.py`), and its MusicXML and MIDI output. The scores cover roughly the first verse and chorus; the rest of each song is in the lyrics.

Notation: [OpenSheetMusicDisplay](https://opensheetmusicdisplay.org). Playback: [Tone.js](https://tonejs.github.io) with samples from the FluidR3 General MIDI soundfont (recorder from FatBoy).

To rebuild the page from the music21 sources (in the original project): `python3 build_songs_page.py`.
