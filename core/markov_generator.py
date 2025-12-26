"""
Advanced Markov Chain Melody Generator

Implements a higher-order Markov chain for melody generation.
Based on research from:
- SpackiGabriel/procedural-melody-generation-markov-chain
- musikalkemist/generativemusicaicourse
- arxiv.org research on Markov vs RNN for music generation

Features:
- Higher-order transitions (considers previous N notes)
- Weighted by rhythm and beat position
- Learns patterns from existing melodies
- Built-in musical patterns for each mood/style
"""

import random
from typing import List, Dict, Tuple, Optional
from collections import defaultdict
from dataclasses import dataclass
import sys
import os

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from core.melody_generator import Note
from core.scale_generator import ScaleGenerator
from config.music_config import (
    OCTAVE_RANGES, VELOCITY_RANGES, NOTE_LENGTHS, MOODS, STYLES,
    midi_note_to_name, CHORD_PROGRESSIONS
)


# Pre-defined melodic patterns based on music theory
# Intervals represented as scale degrees (0 = same, 1 = step up, -1 = step down, etc.)
MELODIC_PATTERNS = {
    # Common melodic motifs
    "ascending_scale": [0, 1, 2, 3],
    "descending_scale": [0, -1, -2, -3],
    "arpeggio_up": [0, 2, 4],
    "arpeggio_down": [0, -2, -4],
    "neighbor_tone": [0, 1, 0],
    "neighbor_below": [0, -1, 0],
    "mordent": [0, 1, 0, -1, 0],
    "turn": [0, 1, 0, -1, 0],
    "leap_step_back": [0, 3, 2],
    "step_leap_back": [0, 1, -2],
    "pendulum": [0, 2, -1, 1],
    "wave": [0, 1, 2, 1, 0, -1, -2, -1],
    "trill": [0, 1, 0, 1],
    "alberti": [0, 2, 1, 2],
}

# Mood-specific pattern weights
MOOD_PATTERNS = {
    "happy": {
        "ascending_scale": 2.0,
        "arpeggio_up": 2.0,
        "wave": 1.5,
        "neighbor_tone": 1.0,
    },
    "sad": {
        "descending_scale": 2.0,
        "neighbor_below": 2.0,
        "step_leap_back": 1.5,
    },
    "energetic": {
        "arpeggio_up": 2.0,
        "arpeggio_down": 2.0,
        "leap_step_back": 1.5,
        "trill": 1.5,
    },
    "calm": {
        "neighbor_tone": 2.0,
        "neighbor_below": 2.0,
        "wave": 1.0,
    },
    "dark": {
        "descending_scale": 2.0,
        "neighbor_below": 2.0,
        "step_leap_back": 1.5,
    },
    "dreamy": {
        "wave": 2.0,
        "neighbor_tone": 1.5,
        "pendulum": 1.5,
    },
    "aggressive": {
        "arpeggio_up": 2.0,
        "arpeggio_down": 2.0,
        "leap_step_back": 2.0,
    },
    "mysterious": {
        "pendulum": 2.0,
        "turn": 1.5,
        "step_leap_back": 1.5,
    },
}


class MarkovChain:
    """
    Higher-order Markov chain for melodic interval transitions.
    """
    
    def __init__(self, order: int = 2):
        """
        Initialize the Markov chain.
        
        Args:
            order: Number of previous states to consider (higher = more coherent)
        """
        self.order = order
        self.transitions: Dict[Tuple, Dict[int, float]] = defaultdict(lambda: defaultdict(float))
        self.total_counts: Dict[Tuple, float] = defaultdict(float)
        
    def train(self, sequences: List[List[int]]):
        """
        Train the Markov chain on sequences of intervals.
        
        Args:
            sequences: List of interval sequences (e.g., [[0, 2, -1, 1], ...])
        """
        for seq in sequences:
            if len(seq) <= self.order:
                continue
                
            for i in range(len(seq) - self.order):
                state = tuple(seq[i:i + self.order])
                next_interval = seq[i + self.order]
                
                self.transitions[state][next_interval] += 1.0
                self.total_counts[state] += 1.0
    
    def add_weighted_transition(self, state: Tuple[int, ...], 
                                next_interval: int, weight: float = 1.0):
        """Add a weighted transition to the chain."""
        self.transitions[state][next_interval] += weight
        self.total_counts[state] += weight
        
    def get_next(self, history: List[int], 
                 temperature: float = 1.0) -> int:
        """
        Get the next interval based on recent history.
        
        Args:
            history: Recent interval history
            temperature: Randomness (0 = deterministic, 1 = normal, >1 = more random)
            
        Returns:
            Next interval to use
        """
        if len(history) < self.order:
            # Not enough history, return random step
            return random.choice([-1, 0, 1, 2])
            
        state = tuple(history[-self.order:])
        
        if state not in self.transitions:
            # Unknown state, try with shorter history
            for i in range(1, self.order):
                shorter_state = state[i:]
                if shorter_state in self.transitions:
                    state = shorter_state
                    break
            else:
                # Still no match, return random musical interval
                return random.choices(
                    [-2, -1, 0, 1, 2],
                    weights=[0.15, 0.25, 0.2, 0.25, 0.15]
                )[0]
        
        candidates = self.transitions[state]
        total = self.total_counts.get(state, 1.0)
        
        # Apply temperature
        intervals = list(candidates.keys())
        weights = [candidates[i] / total for i in intervals]
        
        if temperature != 1.0:
            weights = [w ** (1.0 / temperature) for w in weights]
            total_w = sum(weights)
            weights = [w / total_w for w in weights]
        
        return random.choices(intervals, weights=weights)[0]


class MarkovMelodyGenerator:
    """
    Advanced melody generator using higher-order Markov chains.
    """
    
    def __init__(self, key: str, mode: str, tempo: int = 120):
        """
        Initialize the Markov melody generator.
        
        Args:
            key: Root note (e.g., "C", "F#")
            mode: Scale mode (e.g., "Ionian (Major)")
            tempo: Tempo in BPM
        """
        self.key = key
        self.mode = mode
        self.tempo = tempo
        self.scale_gen = ScaleGenerator(key, mode)
        
        # Initialize Markov chains for different aspects
        self.pitch_chain = MarkovChain(order=3)
        self.rhythm_chain = MarkovChain(order=2)
        
        # Train with built-in patterns
        self._init_patterns()
        
    def _init_patterns(self):
        """Initialize patterns into the Markov chains."""
        # Add all melodic patterns with base weight
        for pattern_name, intervals in MELODIC_PATTERNS.items():
            self._add_pattern(intervals, weight=1.0)
            
        # Add common interval progressions
        common_progressions = [
            [0, 1, 2, 3, 4],      # Ascending scale run
            [0, -1, -2, -3, -4],   # Descending scale run
            [0, 2, 4, 2, 0],       # Arpeggio and back
            [0, 1, 0, -1, 0],      # Neighbor motion
            [0, 4, 3, 2, 1, 0],    # Leap then step down
            [0, -4, -3, -2, -1, 0], # Leap then step up
            [0, 2, 1, 3, 2, 4],    # Zigzag up
            [0, -2, -1, -3, -2, -4], # Zigzag down
            [0, 0, 1, 1, 2, 2],    # Repeated steps
            [0, 2, 0, 2, 0],       # Pendulum thirds
        ]
        
        for prog in common_progressions:
            self._add_pattern(prog, weight=2.0)
            
        # Add rhythm patterns (as relative duration ratios)
        rhythm_patterns = [
            [1, 1, 1, 1],          # Even
            [2, 1, 1],             # Long-short-short
            [1, 1, 2],             # Short-short-long
            [1, 2, 1],             # Short-long-short
            [3, 1],                # Dotted
            [1, 1, 1, 1, 2, 2],    # Acceleration
        ]
        
        for pattern in rhythm_patterns:
            self.rhythm_chain.train([pattern])
    
    def _add_pattern(self, intervals: List[int], weight: float = 1.0):
        """Add a pattern to the pitch chain."""
        if len(intervals) <= self.pitch_chain.order:
            return
            
        # Train on the pattern
        self.pitch_chain.train([intervals])
        
        # Add explicit transitions with weight
        for i in range(len(intervals) - self.pitch_chain.order):
            state = tuple(intervals[i:i + self.pitch_chain.order])
            next_int = intervals[i + self.pitch_chain.order]
            self.pitch_chain.add_weighted_transition(state, next_int, weight)
    
    def apply_mood(self, mood: str):
        """Apply mood-specific pattern weighting."""
        if mood not in MOOD_PATTERNS:
            return
            
        for pattern_name, weight in MOOD_PATTERNS[mood].items():
            if pattern_name in MELODIC_PATTERNS:
                self._add_pattern(MELODIC_PATTERNS[pattern_name], weight=weight)
    
    def generate(self, bars: int, note_length: str = "Eighth",
                time_signature: Tuple[int, int] = (4, 4),
                mood: str = None, style: str = None,
                temperature: float = 0.9) -> List[Note]:
        """
        Generate a melody using Markov chains.
        
        Args:
            bars: Number of bars
            note_length: Base note length
            time_signature: Time signature
            mood: Optional mood modifier
            style: Optional style modifier
            temperature: Randomness (0.5 = focused, 1.0 = normal, 1.5 = creative)
            
        Returns:
            List of Note objects
        """
        # Apply mood
        if mood:
            self.apply_mood(mood)
        
        notes = []
        beats_per_bar = time_signature[0]
        total_beats = bars * beats_per_bar
        
        # Get scale notes
        low, high = OCTAVE_RANGES["lead"]
        low_midi = low * 12 + 12
        high_midi = high * 12 + 12
        scale_notes = self.scale_gen.get_scale_in_range(low_midi, high_midi)
        
        if not scale_notes:
            return notes
        
        # Get parameters from mood/style
        mood_params = MOODS.get(mood, {}) if mood else {}
        style_params = STYLES.get(style, {}) if style else {}
        
        base_duration = NOTE_LENGTHS.get(note_length, 0.5)
        density = mood_params.get("density", style_params.get("density", 1.0))
        velocity_mod = mood_params.get("velocity_mod", 0)
        vel_range = VELOCITY_RANGES["lead"]
        
        # Start in middle of scale
        current_note_idx = len(scale_notes) // 2
        interval_history = [0, 0, 0]  # Initialize history
        
        current_time = 0.0
        phrase_position = 0
        
        while current_time < total_beats:
            # Generate rhythm variation
            duration = self._get_rhythm_duration(
                base_duration, current_time, beats_per_bar, density
            )
            
            if current_time + duration > total_beats:
                duration = total_beats - current_time
            if duration <= 0:
                break
            
            # Get next interval from Markov chain
            interval = self.pitch_chain.get_next(interval_history, temperature)
            
            # Apply musical constraints
            interval = self._constrain_interval(
                current_note_idx, interval, scale_notes, 
                current_time, total_beats
            )
            
            # Move to new note
            current_note_idx = max(0, min(len(scale_notes) - 1, 
                                          current_note_idx + interval))
            
            # Update history
            interval_history.append(interval)
            if len(interval_history) > 6:
                interval_history.pop(0)
            
            # Create note
            pitch = scale_notes[current_note_idx]
            base_velocity = random.randint(*vel_range)
            velocity = max(1, min(127, base_velocity + velocity_mod))
            
            # Add accent on strong beats
            beat_in_bar = current_time % beats_per_bar
            if beat_in_bar == 0:
                velocity = min(127, velocity + 10)
            
            notes.append(Note(
                pitch=pitch,
                start_time=current_time,
                duration=duration * 0.9,
                velocity=velocity
            ))
            
            current_time += duration
            phrase_position += 1
        
        return notes
    
    def _get_rhythm_duration(self, base: float, time: float, 
                            beats_per_bar: float, density: float) -> float:
        """Generate rhythmic variation."""
        beat_in_bar = time % beats_per_bar
        
        # Strong beats tend to be longer
        if beat_in_bar == 0:
            multipliers = [1, 1, 2]
        elif beat_in_bar == beats_per_bar / 2:
            multipliers = [0.5, 1, 1, 2]
        else:
            multipliers = [0.5, 0.5, 1, 1]
        
        duration = base * random.choice(multipliers)
        return duration / density
    
    def _constrain_interval(self, current_idx: int, interval: int,
                           scale_notes: List[int], current_time: float,
                           total_beats: float) -> int:
        """Apply musical constraints to the interval."""
        max_idx = len(scale_notes) - 1
        new_idx = current_idx + interval
        
        # Constrain to scale range
        if new_idx < 0:
            interval = -current_idx  # Go to lowest
        elif new_idx > max_idx:
            interval = max_idx - current_idx  # Go to highest
        
        # At end, tend toward tonic
        if current_time > total_beats * 0.85:
            tonic_idx = 0  # First note is tonic
            distance_to_tonic = tonic_idx - current_idx
            
            # Bias toward tonic
            if abs(distance_to_tonic) > 4:
                if distance_to_tonic > 0:
                    interval = min(interval + 1, 2)
                else:
                    interval = max(interval - 1, -2)
            elif abs(distance_to_tonic) <= 2:
                interval = distance_to_tonic
        
        # Avoid too many large leaps
        if abs(interval) > 4:
            interval = 4 if interval > 0 else -4
        
        return interval
    
    def train_from_notes(self, notes: List[Note]):
        """
        Train the Markov chain from existing notes.
        
        Args:
            notes: List of Note objects to learn from
        """
        if len(notes) < 4:
            return
        
        # Sort by start time
        sorted_notes = sorted(notes, key=lambda n: n.start_time)
        
        # Extract intervals
        intervals = []
        for i in range(1, len(sorted_notes)):
            interval = sorted_notes[i].pitch - sorted_notes[i-1].pitch
            # Convert to scale degrees approximately
            interval = max(-7, min(7, interval // 2))
            intervals.append(interval)
        
        if intervals:
            self.pitch_chain.train([intervals])
    
    def continue_melody(self, existing_notes: List[Note], 
                       bars_to_add: int,
                       mood: str = None,
                       style: str = None) -> List[Note]:
        """
        Continue an existing melody.
        
        Args:
            existing_notes: Existing melody notes
            bars_to_add: Bars to add
            mood: Optional mood
            style: Optional style
            
        Returns:
            List of new notes to append
        """
        # Train from existing notes
        self.train_from_notes(existing_notes)
        
        # Get last note info
        if existing_notes:
            last_note = max(existing_notes, key=lambda n: n.start_time)
            
            # Get average note length
            avg_duration = sum(n.duration for n in existing_notes) / len(existing_notes)
            if avg_duration >= 1.5:
                note_length = "Half"
            elif avg_duration >= 0.75:
                note_length = "Quarter"
            elif avg_duration >= 0.35:
                note_length = "Eighth"
            else:
                note_length = "Sixteenth"
        else:
            note_length = "Eighth"
        
        # Generate continuation
        new_notes = self.generate(
            bars=bars_to_add,
            note_length=note_length,
            mood=mood,
            style=style,
            temperature=0.85  # Slightly more focused for continuation
        )
        
        # Adjust start times
        if existing_notes:
            offset = last_note.start_time + last_note.duration
            for note in new_notes:
                note.start_time += offset
        
        return new_notes


if __name__ == "__main__":
    # Test the Markov melody generator
    gen = MarkovMelodyGenerator("C", "Ionian (Major)", tempo=120)
    
    print("\n=== Markov Chain Melody (No Mood) ===")
    melody = gen.generate(bars=4, note_length="Eighth")
    for note in melody[:12]:
        print(f"  {note.to_dict()}")
    print(f"  Total: {len(melody)} notes")
    
    print("\n=== Markov Chain Melody (Happy) ===")
    gen2 = MarkovMelodyGenerator("G", "Ionian (Major)", tempo=130)
    melody_happy = gen2.generate(bars=4, note_length="Eighth", mood="happy")
    for note in melody_happy[:12]:
        print(f"  {note.to_dict()}")
    print(f"  Total: {len(melody_happy)} notes")
    
    print("\n=== Markov Chain Melody (Dark) ===")
    gen3 = MarkovMelodyGenerator("A", "Aeolian (Minor)", tempo=90)
    melody_dark = gen3.generate(bars=4, note_length="Quarter", mood="dark")
    for note in melody_dark[:8]:
        print(f"  {note.to_dict()}")
    print(f"  Total: {len(melody_dark)} notes")
