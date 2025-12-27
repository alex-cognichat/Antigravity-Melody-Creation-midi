"""
Music Theory Configuration
Contains all musical constants: keys, modes, scales, chord types, note lengths, etc.
"""

# All 12 keys with their MIDI base note numbers (octave 4)
KEYS = {
    "C": 60,
    "C#": 61,
    "Db": 61,
    "D": 62,
    "D#": 63,
    "Eb": 63,
    "E": 64,
    "F": 65,
    "F#": 66,
    "Gb": 66,
    "G": 67,
    "G#": 68,
    "Ab": 68,
    "A": 69,
    "A#": 70,
    "Bb": 70,
    "B": 71,
}

# Key names for display (without enharmonic duplicates)
KEY_NAMES = ["C", "C#", "D", "D#", "E", "F", "F#", "G", "G#", "A", "A#", "B"]

# All modes with their interval patterns (semitones from root)
MODES = {
    "Ionian (Major)": [0, 2, 4, 5, 7, 9, 11],
    "Dorian": [0, 2, 3, 5, 7, 9, 10],
    "Phrygian": [0, 1, 3, 5, 7, 8, 10],
    "Lydian": [0, 2, 4, 6, 7, 9, 11],
    "Mixolydian": [0, 2, 4, 5, 7, 9, 10],
    "Aeolian (Minor)": [0, 2, 3, 5, 7, 8, 10],
    "Locrian": [0, 1, 3, 5, 6, 8, 10],
    "Harmonic Minor": [0, 2, 3, 5, 7, 8, 11],
    "Melodic Minor": [0, 2, 3, 5, 7, 9, 11],
    "Pentatonic Major": [0, 2, 4, 7, 9],
    "Pentatonic Minor": [0, 3, 5, 7, 10],
    "Blues": [0, 3, 5, 6, 7, 10],
}

# Note lengths (in beats at 4/4 time signature)
NOTE_LENGTHS = {
    "Whole": 4.0,
    "Half": 2.0,
    "Dotted Half": 3.0,
    "Quarter": 1.0,
    "Dotted Quarter": 1.5,
    "Eighth": 0.5,
    "Sixteenth": 0.25,
    "Triplet Eighth": 1/3,
    "Triplet Sixteenth": 1/6,
}

# Number of bars options
BAR_OPTIONS = [1, 2, 4, 8, 16, 32]

# Time signature options
TIME_SIGNATURES = {
    "4/4": (4, 4),
    "3/4": (3, 4),
    "6/8": (6, 8),
    "2/4": (2, 4),
}

# Tempo options (BPM)
TEMPO_RANGE = (40, 200)
DEFAULT_TEMPO = 120

# Generation types
GENERATION_TYPES = {
    "lead": "Lead Melody",
    "pad": "Pad/Chords",
    "bass": "Bass Line",
    "hook": "Hook (Catchy Melody)",
    "harmony": "Full Harmony (Lead + Pad + Bass)",
}

# Chord types with intervals from root
CHORD_TYPES = {
    "major": [0, 4, 7],
    "minor": [0, 3, 7],
    "diminished": [0, 3, 6],
    "augmented": [0, 4, 8],
    "sus2": [0, 2, 7],
    "sus4": [0, 5, 7],
    "dom7": [0, 4, 7, 10],
    "maj7": [0, 4, 7, 11],
    "min7": [0, 3, 7, 10],
    "dim7": [0, 3, 6, 9],
    "min7b5": [0, 3, 6, 10],
    "add9": [0, 4, 7, 14],
    "sus2add9": [0, 2, 7, 14],
}

# Common chord progressions (as scale degrees, 1-indexed)
CHORD_PROGRESSIONS = {
    "I-IV-V-I": [1, 4, 5, 1],
    "I-V-vi-IV": [1, 5, 6, 4],
    "ii-V-I": [2, 5, 1],
    "I-vi-IV-V": [1, 6, 4, 5],
    "I-IV-vi-V": [1, 4, 6, 5],
    "vi-IV-I-V": [6, 4, 1, 5],
    "I-V-IV-I": [1, 5, 4, 1],
    "I-ii-V-I": [1, 2, 5, 1],
    "I-IV-I-V": [1, 4, 1, 5],
    "I-iii-IV-V": [1, 3, 4, 5],
    "I-vi-ii-V": [1, 6, 2, 5],
    "I-V-vi-iii-IV-I-IV-V": [1, 5, 6, 3, 4, 1, 4, 5],  # Canon progression
}

# Chord quality for each scale degree in major scale
MAJOR_SCALE_CHORD_QUALITIES = {
    1: "major",
    2: "minor",
    3: "minor",
    4: "major",
    5: "major",
    6: "minor",
    7: "diminished",
}

# Chord quality for each scale degree in minor scale
MINOR_SCALE_CHORD_QUALITIES = {
    1: "minor",
    2: "diminished",
    3: "major",
    4: "minor",
    5: "minor",  # or major in harmonic minor
    6: "major",
    7: "major",
}

# Octave ranges for different generation types
OCTAVE_RANGES = {
    "lead": (4, 6),    # C4 to C6
    "pad": (3, 5),     # C3 to C5
    "bass": (1, 3),    # C1 to C3
    "hook": (4, 5),    # C4 to C5 (singable range)
}

# Velocity ranges
VELOCITY_RANGES = {
    "lead": (80, 110),
    "pad": (60, 90),
    "bass": (90, 120),
    "hook": (90, 115),  # Slightly louder for emphasis
}

# Moods with their generation parameters
MOODS = {
    "happy": {
        "velocity_mod": 10,
        "leap_chance": 0.4,
        "prefer_major": True,
        "prefer_high": True,
        "density": 1.0,
        "staccato": False,
    },
    "sad": {
        "velocity_mod": -15,
        "leap_chance": 0.2,
        "prefer_minor": True,
        "prefer_low": True,
        "density": 0.7,
        "staccato": False,
    },
    "dark": {
        "velocity_mod": -10,
        "prefer_minor": True,
        "prefer_low": True,
        "density": 0.8,
        "use_chromatics": True,
    },
    "energetic": {
        "velocity_mod": 20,
        "leap_chance": 0.5,
        "density": 1.5,
        "prefer_short_notes": True,
        "staccato": True,
    },
    "calm": {
        "velocity_mod": -20,
        "leap_chance": 0.1,
        "density": 0.5,
        "prefer_long_notes": True,
        "legato": True,
    },
    "aggressive": {
        "velocity_mod": 30,
        "density": 2.0,
        "staccato": True,
        "prefer_low": True,
        "accents": True,
    },
    "dreamy": {
        "velocity_mod": -10,
        "density": 0.6,
        "legato": True,
        "prefer_high": True,
        "use_suspensions": True,
    },
    "mysterious": {
        "velocity_mod": -5,
        "use_chromatics": True,
        "unpredictable": True,
        "prefer_minor": True,
    },
    "epic": {
        "velocity_mod": 15,
        "prefer_wide_range": True,
        "density": 1.2,
        "use_octaves": True,
    },
    "romantic": {
        "velocity_mod": 0,
        "legato": True,
        "prefer_major": True,
        "density": 0.8,
    },
}

# Styles with their progression and rhythm preferences
STYLES = {
    "pop": {
        "progressions": ["I-V-vi-IV", "I-IV-V-I", "vi-IV-I-V"],
        "note_length": "Eighth",
        "density": 1.0,
        "swing": 0.0,
    },
    "rock": {
        "progressions": ["I-IV-V-I", "I-V-IV-I", "I-vi-IV-V"],
        "note_length": "Eighth",
        "heavy_bass": True,
        "power_chords": True,
    },
    "synthwave": {
        "progressions": ["vi-IV-I-V", "I-V-vi-IV"],
        "note_length": "Sixteenth",
        "arpeggios": True,
        "pad_heavy": True,
    },
    "jazz": {
        "progressions": ["ii-V-I", "I-vi-ii-V"],
        "note_length": "Eighth",
        "extensions": True,
        "swing": 0.3,
        "walking_bass": True,
    },
    "classical": {
        "progressions": ["I-IV-V-I", "I-V-vi-iii-IV-I-IV-V"],
        "note_length": "Quarter",
        "voice_leading": True,
        "counterpoint": True,
    },
    "edm": {
        "progressions": ["vi-IV-I-V", "I-V-vi-IV"],
        "note_length": "Sixteenth",
        "density": 1.5,
        "arpeggios": True,
        "sidechain_hint": True,
    },
    "lofi": {
        "progressions": ["ii-V-I", "I-vi-IV-V"],
        "note_length": "Eighth",
        "swing": 0.2,
        "muted": True,
        "density": 0.7,
    },
    "ambient": {
        "progressions": ["I-IV", "I-V"],
        "note_length": "Whole",
        "density": 0.3,
        "pad_heavy": True,
        "long_release": True,
    },
    "funk": {
        "progressions": ["I-IV", "I-V-IV-I"],
        "note_length": "Sixteenth",
        "syncopation": True,
        "groove": True,
    },
    "metal": {
        "progressions": ["I-IV-V-I", "vi-IV-I-V"],
        "note_length": "Sixteenth",
        "heavy_bass": True,
        "aggressive": True,
        "power_chords": True,
    },
}

# Melody generation algorithms
ALGORITHMS = {
    "simple": "Simple (fast, basic patterns)",
    "markov": "Markov Chain (learned patterns, more musical)",
}

# Operation modes for the generator
OPERATION_MODES = {
    "create": "Create from scratch",
    "analyze": "Analyze imported MIDI (detect key, mode, progression)",
    "harmonize": "Harmonize imported chords (add lead, bass, pad)",
    "continue": "Continue/extend imported MIDI with new bars",
}

# MIDI note names for display
NOTE_NAMES = ["C", "C#", "D", "D#", "E", "F", "F#", "G", "G#", "A", "A#", "B"]


def midi_note_to_name(midi_note: int) -> str:
    """Convert MIDI note number to note name with octave."""
    octave = (midi_note // 12) - 1
    note_name = NOTE_NAMES[midi_note % 12]
    return f"{note_name}{octave}"


def name_to_midi_note(note_name: str, octave: int = 4) -> int:
    """Convert note name and octave to MIDI note number."""
    base_notes = {
        "C": 0, "C#": 1, "Db": 1,
        "D": 2, "D#": 3, "Eb": 3,
        "E": 4, "F": 5, "F#": 6, "Gb": 6,
        "G": 7, "G#": 8, "Ab": 8,
        "A": 9, "A#": 10, "Bb": 10,
        "B": 11
    }
    return base_notes[note_name] + (octave + 1) * 12
