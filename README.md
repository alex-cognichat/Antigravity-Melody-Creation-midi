# 🎵 Melody & Harmony Generator

A Python CLI application that generates melodies, bass lines, pads, and harmonies based on music theory best practices. Features mood/style modifiers and four operation modes.

## Installation

```bash
pip install mido inquirer
```

## Quick Start

```bash
# Interactive mode (recommended)
python main.py

# Quick generation
python main.py --quick -k C -s "Ionian (Major)" -t lead -b 8
```

## Melody Generation Algorithms

The generator supports two melody algorithms:

| Algorithm | Description |
|-----------|-------------|
| **markov** (default) | Higher-order Markov chain with learned melodic patterns. More musical, coherent phrases. |
| **simple** | Basic random walk with music theory rules. Faster, simpler patterns. |

The Markov chain algorithm features:
- **Higher-order transitions** (considers previous 3 notes)
- **Pre-trained melodic patterns** (scales, arpeggios, neighbor tones, etc.)
- **Mood-specific pattern weighting** (happy = more ascending, sad = more descending)
- **Temperature control** for creativity (0.5 = focused, 1.0 = normal, 1.5 = experimental)

## Operation Modes

### 1. Create (Default)
Generate music from scratch with full control over parameters.

```bash
# Basic lead melody
python main.py --quick -k G -s Dorian -t lead -b 8

# Full harmony with style
python main.py --quick -t harmony --style synthwave --mood energetic

# Dark pad in minor key
python main.py --quick -k A -s "Aeolian (Minor)" -t pad --mood dark -b 16

# Pop progression with happy mood
python main.py --quick -t harmony -p I-V-vi-IV --style pop --mood happy
```

### 2. Analyze
Import a MIDI file and detect key, mode, tempo, and note statistics.

```bash
python main.py --mode analyze -i my_song.mid
```

Output includes:
- Detected key and mode (with confidence score)
- Tempo and time signature
- Note range and average duration
- Pitch histogram

### 3. Harmonize
Add harmony parts (lead, pad, bass) to an imported chord progression.

```bash
# Basic harmonization
python main.py --mode harmonize -i chords.mid

# With mood/style
python main.py --mode harmonize -i chords.mid --mood dreamy --style lofi
```

### 4. Continue
Extend an existing MIDI file with new bars that fit naturally.

```bash
# Add 4 bars
python main.py --mode continue -i melody.mid -b 4

# Continue with specific mood
python main.py --mode continue -i melody.mid -b 8 --mood energetic --style edm
```

## Mood Modifiers

| Mood | Effect |
|------|--------|
| `happy` | Higher velocity, more leaps, prefers major |
| `sad` | Lower velocity, stepwise motion, prefers minor |
| `dark` | Low register, minor bias, chromatic hints |
| `energetic` | High velocity, dense notes, staccato |
| `calm` | Soft dynamics, sparse, long notes |
| `aggressive` | Maximum velocity, very dense, accented |
| `dreamy` | Soft, legato, high register |
| `mysterious` | Chromatic, unpredictable |
| `epic` | Wide range, octaves, dramatic |
| `romantic` | Legato, major bias, moderate dynamics |

## Style Presets

| Style | Characteristics |
|-------|-----------------|
| `pop` | I-V-vi-IV progressions, eighth notes |
| `rock` | Strong bass, power chords |
| `synthwave` | Arpeggios, pads, vi-IV-I-V |
| `jazz` | ii-V-I, swing, extensions |
| `classical` | Voice leading, counterpoint |
| `edm` | Dense arpeggios, sidechain hints |
| `lofi` | Swing, muted, ii-V-I |
| `ambient` | Slow pads, sparse |
| `funk` | Syncopation, sixteenths |
| `metal` | Heavy bass, aggressive |

## Command Line Arguments

### Core Options

| Argument | Short | Description | Default |
|----------|-------|-------------|---------|
| `--quick` | `-q` | Non-interactive mode (required for CLI args) | - |
| `--mode` | `-m` | Operation mode | `create` |
| `--input` | `-i` | Input MIDI file path | - |
| `--test-mode` | - | Run comprehensive tests | - |

### Music Parameters

| Argument | Short | Description | Default |
|----------|-------|-------------|---------|
| `--key` | `-k` | Musical key | `C` |
| `--scale` | `-s` | Scale/mode | `Ionian (Major)` |
| `--bars` | `-b` | Number of bars | `8` |
| `--note-length` | `-n` | Base note length | `Eighth` |
| `--type` | `-t` | Generation type | `lead` |
| `--tempo` | - | Tempo in BPM | `120` |
| `--progression` | `-p` | Chord progression | `random` |
| `--mood` | - | Mood modifier | `none` |
| `--style` | - | Style preset | `none` |

### All Possible Values

**`--mode`**: `create`, `analyze`, `harmonize`, `continue`

**`--key`**: `C`, `C#`, `D`, `D#`, `E`, `F`, `F#`, `G`, `G#`, `A`, `A#`, `B`

**`--scale`**:
- `Ionian (Major)`, `Dorian`, `Phrygian`, `Lydian`, `Mixolydian`
- `Aeolian (Minor)`, `Locrian`, `Harmonic Minor`, `Melodic Minor`
- `Pentatonic Major`, `Pentatonic Minor`, `Blues`

**`--bars`**: `1`, `2`, `4`, `8`, `16`, `32`

**`--note-length`**: `Whole`, `Half`, `Dotted Half`, `Quarter`, `Dotted Quarter`, `Eighth`, `Sixteenth`, `Triplet Eighth`, `Triplet Sixteenth`

**`--type`**: `lead`, `pad`, `bass`, `harmony`

**`--tempo`**: `40` to `200` BPM

**`--progression`**: `random`, `I-IV-V-I`, `I-V-vi-IV`, `ii-V-I`, `I-vi-IV-V`, `I-IV-vi-V`, `vi-IV-I-V`, `I-V-IV-I`, `I-ii-V-I`, `I-IV-I-V`, `I-iii-IV-V`, `I-vi-ii-V`, `I-V-vi-iii-IV-I-IV-V`

**`--mood`**: `none`, `happy`, `sad`, `dark`, `energetic`, `calm`, `aggressive`, `dreamy`, `mysterious`, `epic`, `romantic`

**`--style`**: `none`, `pop`, `rock`, `synthwave`, `jazz`, `classical`, `edm`, `lofi`, `ambient`, `funk`, `metal`

## Examples

```bash
# Synthwave lead with energetic mood
python main.py --quick -t lead --style synthwave --mood energetic -b 16

# Jazz harmony
python main.py --quick -t harmony --style jazz -p ii-V-I --tempo 95

# Analyze then continue
python main.py --mode analyze -i existing.mid
python main.py --mode continue -i existing.mid -b 8 --mood calm

# Dreamy ambient pad
python main.py --quick -t pad --style ambient --mood dreamy -b 32 --tempo 70

# Metal bass line
python main.py --quick -t bass --style metal --mood aggressive -k E -s "Aeolian (Minor)"
```

## Output

MIDI files are saved to the `output/` directory with timestamped names:
```
output/
├── lead_C_ionian_8bars_20251226_210000.mid
├── harmony_G_dorian_16bars_20251226_210100.mid
└── continued_A_minor_12bars_20251226_210200.mid
```

Notes are also printed to the terminal for quick reference.
