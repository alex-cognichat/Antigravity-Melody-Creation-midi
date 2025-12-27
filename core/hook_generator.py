"""
Hook Generator Module

Generates extremely catchy, memorable hook melodies using advanced techniques:
- Call-and-response patterns
- Repetition with variation
- Strong rhythmic motifs
- Memorable intervals (3rds, 5ths, octaves)
- Singable range and contour
- Emphasis on strong beats
"""

import random
from typing import List, Tuple, Optional
from dataclasses import dataclass
import sys
import os

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from core.scale_generator import ScaleGenerator
from core.melody_generator import Note
from config.music_config import (
    OCTAVE_RANGES, VELOCITY_RANGES, NOTE_LENGTHS,
    MOODS, STYLES, midi_note_to_name
)


# Hook-specific melodic patterns - designed for maximum catchiness
CATCHY_PATTERNS = {
    # Repetitive motifs (creates earworm effect)
    "repeat_two": [0, 0],  # Same note twice
    "repeat_three": [0, 0, 0],  # Same note three times
    "call_response": [0, 2, 0, -2],  # Up then down - creates question/answer
    
    # Arpeggiated hooks (strong chord tones)
    "power_arpeggio": [0, 4, 7, 4],  # 1-3-5-3 (major feel)
    "minor_arpeggio": [0, 3, 7, 3],  # 1-b3-5-b3 (minor feel)
    "octave_jump": [0, 7, 0, 7],  # Root to 5th pattern
    
    # Stepwise catchy patterns
    "ascending_hook": [0, 1, 2, 0],  # Step up then reset
    "descending_hook": [0, -1, -2, 0],  # Step down then reset
    "zigzag": [0, 2, 1, 3],  # Creates interesting contour
    
    # Syncopated/rhythmic patterns (memorable timing)
    "anticipation": [0, 0, 2],  # Repeat then move
    "resolution": [2, 1, 0],  # Step down to tonic
    
    # Classic hook intervals
    "fourth_leap": [0, 3, 3, 0],  # Leap of a fourth
    "fifth_leap": [0, 4, 4, 0],  # Leap of a fifth
    "octave_drop": [7, 0, 0, 0],  # Dramatic octave drop
    
    # Pop hook patterns
    "pentatonic_hook": [0, 2, 4, 2, 0],  # Pentatonic friendly
    "millennial_whoop": [4, 2, 4, 2],  # The famous "oh-oh-oh" pattern
    "do_re_mi": [0, 1, 2, 4, 2],  # Classic ascending
}

# Style-specific hook preferences
HOOK_STYLES = {
    "pop": {
        "patterns": ["millennial_whoop", "pentatonic_hook", "repeat_two", "call_response"],
        "rhythmic_emphasis": True,
        "repetition_factor": 0.6,
        "velocity_accent": 15,
    },
    "rock": {
        "patterns": ["power_arpeggio", "octave_jump", "fourth_leap", "resolution"],
        "rhythmic_emphasis": True,
        "repetition_factor": 0.5,
        "velocity_accent": 20,
    },
    "edm": {
        "patterns": ["repeat_three", "zigzag", "anticipation", "ascending_hook"],
        "rhythmic_emphasis": True,
        "repetition_factor": 0.7,
        "velocity_accent": 10,
    },
    "synthwave": {
        "patterns": ["power_arpeggio", "octave_jump", "call_response", "millennial_whoop"],
        "rhythmic_emphasis": True,
        "repetition_factor": 0.5,
        "velocity_accent": 12,
    },
    "funk": {
        "patterns": ["anticipation", "zigzag", "repeat_two", "call_response"],
        "rhythmic_emphasis": True,
        "syncopation": True,
        "repetition_factor": 0.4,
        "velocity_accent": 18,
    },
    "metal": {
        "patterns": ["power_arpeggio", "octave_drop", "fifth_leap", "resolution"],
        "rhythmic_emphasis": True,
        "repetition_factor": 0.5,
        "velocity_accent": 25,
    },
    "jazz": {
        "patterns": ["call_response", "zigzag", "do_re_mi", "descending_hook"],
        "rhythmic_emphasis": False,
        "repetition_factor": 0.3,
        "velocity_accent": 8,
    },
    "lofi": {
        "patterns": ["pentatonic_hook", "repeat_two", "descending_hook", "call_response"],
        "rhythmic_emphasis": False,
        "repetition_factor": 0.5,
        "velocity_accent": 5,
    },
}

# Mood-based pattern adjustments
HOOK_MOODS = {
    "happy": {
        "prefer_patterns": ["ascending_hook", "power_arpeggio", "millennial_whoop"],
        "prefer_high": True,
        "velocity_boost": 10,
    },
    "sad": {
        "prefer_patterns": ["descending_hook", "minor_arpeggio", "resolution"],
        "prefer_high": False,
        "velocity_boost": -10,
    },
    "energetic": {
        "prefer_patterns": ["octave_jump", "repeat_three", "zigzag"],
        "prefer_high": True,
        "velocity_boost": 20,
    },
    "dark": {
        "prefer_patterns": ["minor_arpeggio", "octave_drop", "descending_hook"],
        "prefer_high": False,
        "velocity_boost": -5,
    },
    "aggressive": {
        "prefer_patterns": ["power_arpeggio", "octave_drop", "fifth_leap"],
        "prefer_high": False,
        "velocity_boost": 25,
    },
    "dreamy": {
        "prefer_patterns": ["pentatonic_hook", "call_response", "ascending_hook"],
        "prefer_high": True,
        "velocity_boost": -15,
    },
    "epic": {
        "prefer_patterns": ["octave_jump", "power_arpeggio", "fifth_leap"],
        "prefer_high": True,
        "velocity_boost": 15,
    },
}


class HookGenerator:
    """
    Generates extremely catchy hook melodies.
    
    Uses techniques proven to create memorable melodies:
    - Repetition: The most important element of catchiness
    - Contrast: After repetition, introduce variation
    - Strong beat emphasis: Hook falls on beats 1 and 3
    - Singable range: Limited to ~1 octave for memorability
    - Chord tone emphasis: Uses 1, 3, 5 of the scale
    """
    
    def __init__(self, key: str, mode: str, tempo: int = 120):
        """
        Initialize the hook generator.
        
        Args:
            key: Root note (e.g., "C", "F#")
            mode: Scale mode (e.g., "Ionian (Major)")
            tempo: Tempo in BPM
        """
        self.key = key
        self.mode = mode
        self.tempo = tempo
        self.scale_gen = ScaleGenerator(key, mode)
        
    def generate(self, bars: int = 1, note_length: str = "Eighth",
                 time_signature: Tuple[int, int] = (4, 4),
                 mood: str = None, style: str = None) -> List[Note]:
        """
        Generate a catchy hook melody.
        
        Args:
            bars: Number of bars (default 1 for short hook)
            note_length: Base note length
            time_signature: Time signature as (beats, note_value)
            mood: Optional mood modifier
            style: Optional style modifier
            
        Returns:
            List of Note objects forming the hook
        """
        notes = []
        beats_per_bar = time_signature[0]
        total_beats = bars * beats_per_bar
        
        # Hook uses a focused range for singability (1 octave centered on middle)
        low, high = OCTAVE_RANGES.get("hook", (4, 5))
        low_midi = low * 12 + 12
        high_midi = high * 12 + 12
        scale_notes = self.scale_gen.get_scale_in_range(low_midi, high_midi)
        
        if not scale_notes:
            return notes
        
        base_duration = NOTE_LENGTHS.get(note_length, 0.5)
        vel_range = VELOCITY_RANGES.get("hook", (90, 115))
        
        # Get style and mood parameters
        style_params = HOOK_STYLES.get(style, {})
        mood_params = HOOK_MOODS.get(mood, {})
        
        velocity_mod = mood_params.get("velocity_boost", 0) + style_params.get("velocity_accent", 0)
        repetition_factor = style_params.get("repetition_factor", 0.5)
        
        # Select patterns based on style and mood
        available_patterns = self._select_patterns(style, mood)
        
        # Generate hook structure
        current_time = 0.0
        phrase_notes = []
        
        # Calculate notes per bar to ensure we fill the bar properly
        notes_per_bar = int(beats_per_bar / base_duration)
        
        # Generate the hook using patterns
        for bar_num in range(bars):
            bar_start = bar_num * beats_per_bar
            bar_notes = self._generate_bar(
                bar_num=bar_num,
                total_bars=bars,
                scale_notes=scale_notes,
                beats_per_bar=beats_per_bar,
                base_duration=base_duration,
                bar_start=bar_start,
                patterns=available_patterns,
                vel_range=vel_range,
                velocity_mod=velocity_mod,
                repetition_factor=repetition_factor,
                style=style,
                mood=mood
            )
            notes.extend(bar_notes)
        
        return notes
    
    def _select_patterns(self, style: str = None, mood: str = None) -> List[str]:
        """Select patterns based on style and mood preferences."""
        patterns = list(CATCHY_PATTERNS.keys())
        
        # Weight patterns based on style
        if style and style in HOOK_STYLES:
            preferred = HOOK_STYLES[style].get("patterns", [])
            # Add preferred patterns multiple times to weight them
            patterns.extend(preferred * 3)
        
        # Weight patterns based on mood
        if mood and mood in HOOK_MOODS:
            preferred = HOOK_MOODS[mood].get("prefer_patterns", [])
            patterns.extend(preferred * 2)
        
        return patterns
    
    def _generate_bar(self, bar_num: int, total_bars: int,
                      scale_notes: List[int], beats_per_bar: float,
                      base_duration: float, bar_start: float,
                      patterns: List[str], vel_range: Tuple[int, int],
                      velocity_mod: int, repetition_factor: float,
                      style: str = None, mood: str = None) -> List[Note]:
        """Generate a single bar of the hook."""
        notes = []
        current_time = bar_start
        
        # For even bars, repeat with variation (key to catchiness)
        should_repeat = bar_num > 0 and random.random() < repetition_factor
        
        # Choose a primary pattern for this bar
        pattern_name = random.choice(patterns)
        pattern = CATCHY_PATTERNS.get(pattern_name, [0, 2, 0])
        
        # Find root position (middle of scale for singability)
        root_idx = len(scale_notes) // 2
        
        # Adjust starting position based on mood
        if mood:
            mood_params = HOOK_MOODS.get(mood, {})
            if mood_params.get("prefer_high"):
                root_idx = min(len(scale_notes) - 1, root_idx + 2)
            elif mood_params.get("prefer_high") == False:
                root_idx = max(0, root_idx - 2)
        
        # Generate notes following the pattern
        pattern_idx = 0
        notes_in_bar = 0
        max_notes = int(beats_per_bar / base_duration)
        
        while current_time < bar_start + beats_per_bar and notes_in_bar < max_notes:
            # Get interval from pattern
            if pattern_idx < len(pattern):
                interval = pattern[pattern_idx]
                pattern_idx += 1
            else:
                # Cycle through pattern or use simple step
                interval = pattern[pattern_idx % len(pattern)] if pattern else 0
                pattern_idx += 1
            
            # Calculate note index with bounds checking
            note_idx = root_idx + interval
            note_idx = max(0, min(len(scale_notes) - 1, note_idx))
            
            pitch = scale_notes[note_idx]
            
            # Calculate duration - hooks often use consistent rhythms
            duration = base_duration
            
            # Don't exceed bar boundary
            if current_time + duration > bar_start + beats_per_bar:
                duration = bar_start + beats_per_bar - current_time
            
            if duration <= 0:
                break
            
            # Calculate velocity with accents on strong beats
            is_strong_beat = (current_time - bar_start) % 1.0 < 0.01 or \
                           abs((current_time - bar_start) - 2.0) < 0.01
            
            accent = 15 if is_strong_beat else 0
            base_velocity = random.randint(*vel_range)
            velocity = max(1, min(127, base_velocity + velocity_mod + accent))
            
            # Create the note
            notes.append(Note(
                pitch=pitch,
                start_time=current_time,
                duration=duration * 0.85,  # Slight gap for definition
                velocity=velocity
            ))
            
            current_time += duration
            notes_in_bar += 1
            
            # Update root for next pattern iteration (creates movement)
            if pattern_idx >= len(pattern):
                pattern_idx = 0
                # Slight variation in root position
                if random.random() < 0.3:
                    root_idx = max(0, min(len(scale_notes) - 1, 
                                         root_idx + random.choice([-1, 0, 1])))
        
        return notes
    
    def generate_with_variation(self, bars: int = 2,
                                 note_length: str = "Eighth",
                                 time_signature: Tuple[int, int] = (4, 4),
                                 mood: str = None, style: str = None) -> List[Note]:
        """
        Generate a hook with call-and-response variation.
        
        Creates an A-A' pattern where the second half is a variation
        of the first, which is highly effective for memorability.
        """
        if bars < 2:
            return self.generate(bars, note_length, time_signature, mood, style)
        
        half_bars = bars // 2
        
        # Generate first half (call)
        first_half = self.generate(half_bars, note_length, time_signature, mood, style)
        
        # Generate second half as variation (response)
        second_half = self._generate_variation(first_half, half_bars, 
                                                time_signature, mood, style)
        
        return first_half + second_half
    
    def _generate_variation(self, original: List[Note], bars: int,
                            time_signature: Tuple[int, int],
                            mood: str = None, style: str = None) -> List[Note]:
        """Create a variation of the original phrase."""
        if not original:
            return self.generate(bars, time_signature=time_signature, 
                               mood=mood, style=style)
        
        beats_per_bar = time_signature[0]
        offset = bars * beats_per_bar
        
        varied = []
        for note in original:
            # Apply variation: transpose, shift timing, or change velocity
            variation_type = random.choice(["transpose", "same", "same", "rhythm"])
            
            if variation_type == "transpose":
                # Transpose up or down a step/third
                pitch_change = random.choice([-2, -1, 1, 2])
                new_pitch = note.pitch + pitch_change
            elif variation_type == "rhythm":
                # Keep pitch, vary rhythm slightly
                new_pitch = note.pitch
            else:
                new_pitch = note.pitch
            
            varied.append(Note(
                pitch=new_pitch,
                start_time=note.start_time + offset,
                duration=note.duration,
                velocity=min(127, max(1, note.velocity + random.randint(-5, 5)))
            ))
        
        return varied


# Test the hook generator
if __name__ == "__main__":
    gen = HookGenerator("C", "Ionian (Major)", tempo=120)
    
    print("\n=== 1-Bar Pop Hook ===")
    hook = gen.generate(bars=1, style="pop", mood="happy")
    for note in hook:
        print(f"  {midi_note_to_name(note.pitch)} @ {note.start_time:.2f}")
    
    print("\n=== 2-Bar Rock Hook ===")
    hook = gen.generate(bars=2, style="rock", mood="energetic")
    for note in hook:
        print(f"  {midi_note_to_name(note.pitch)} @ {note.start_time:.2f}")
    
    print("\n=== 4-Bar Hook with Variation ===")
    hook = gen.generate_with_variation(bars=4, style="edm", mood="epic")
    for note in hook:
        print(f"  {midi_note_to_name(note.pitch)} @ {note.start_time:.2f}")
