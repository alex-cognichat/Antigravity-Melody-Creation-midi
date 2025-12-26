"""
Harmony Generator Module
Generates complete harmonies with chord progressions and multi-part arrangements.
"""

import random
from typing import List, Dict, Tuple, Optional
from dataclasses import dataclass
import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from core.scale_generator import ScaleGenerator
from core.melody_generator import MelodyGenerator, Note
from config.music_config import (
    CHORD_PROGRESSIONS, CHORD_TYPES,
    midi_note_to_name
)


class HarmonyGenerator:
    """Generates complete harmonies with multiple parts."""
    
    def __init__(self, key: str, mode: str, tempo: int = 120):
        """
        Initialize the harmony generator.
        
        Args:
            key: Root note (e.g., "C", "F#")
            mode: Scale mode (e.g., "Ionian (Major)", "Dorian")
            tempo: Tempo in BPM
        """
        self.key = key
        self.mode = mode
        self.tempo = tempo
        self.scale_gen = ScaleGenerator(key, mode)
        self.melody_gen = MelodyGenerator(key, mode, tempo)
        
    def generate_chord_progression(self, bars: int, 
                                    progression_name: str = None) -> List[int]:
        """
        Generate or select a chord progression.
        
        Args:
            bars: Number of bars
            progression_name: Optional specific progression name
            
        Returns:
            List of scale degrees for the progression
        """
        if progression_name and progression_name in CHORD_PROGRESSIONS:
            base_prog = CHORD_PROGRESSIONS[progression_name]
        else:
            # Select random progression
            prog_name = random.choice(list(CHORD_PROGRESSIONS.keys()))
            base_prog = CHORD_PROGRESSIONS[prog_name]
            
        # Extend or trim progression to match bars
        progression = []
        while len(progression) < bars:
            progression.extend(base_prog)
        return progression[:bars]
    
    def generate_full_harmony(self, bars: int,
                             note_length: str = "Eighth",
                             time_signature: Tuple[int, int] = (4, 4),
                             progression_name: str = None) -> Dict[str, List[Note]]:
        """
        Generate a complete harmony with lead, pad, and bass.
        
        Args:
            bars: Number of bars to generate
            note_length: Base note length for lead
            time_signature: Time signature
            progression_name: Optional chord progression name
            
        Returns:
            Dictionary with 'lead', 'pad', 'bass' keys containing note lists
        """
        # Generate chord progression
        progression = self.generate_chord_progression(bars, progression_name)
        
        # Generate each part
        harmony = {
            "lead": self.melody_gen.generate_lead(
                bars=bars,
                note_length=note_length,
                time_signature=time_signature
            ),
            "pad": self.melody_gen.generate_pad(
                bars=bars,
                note_length="Whole",
                time_signature=time_signature,
                chord_progression=progression
            ),
            "bass": self.melody_gen.generate_bass(
                bars=bars,
                note_length="Quarter",
                time_signature=time_signature,
                chord_progression=progression
            )
        }
        
        return harmony
    
    def generate_arpeggiated_harmony(self, bars: int,
                                     note_length: str = "Sixteenth",
                                     time_signature: Tuple[int, int] = (4, 4),
                                     progression_name: str = None) -> List[Note]:
        """
        Generate an arpeggiated harmony pattern.
        
        Args:
            bars: Number of bars to generate
            note_length: Note length for arpeggiation
            time_signature: Time signature
            progression_name: Optional chord progression name
            
        Returns:
            List of Note objects forming the arpeggio pattern
        """
        notes = []
        beats_per_bar = time_signature[0]
        
        progression = self.generate_chord_progression(bars, progression_name)
        
        from config.music_config import NOTE_LENGTHS, VELOCITY_RANGES
        duration = NOTE_LENGTHS.get(note_length, 0.25)
        vel_range = VELOCITY_RANGES["lead"]
        
        current_time = 0.0
        
        for bar_idx, degree in enumerate(progression):
            # Get chord for this bar
            chord = self.scale_gen.get_chord_at_octave(degree, octave=4)
            
            bar_start = bar_idx * beats_per_bar
            bar_end = bar_start + beats_per_bar
            
            # Create arpeggio pattern
            pattern = self._create_arpeggio_pattern(chord)
            pattern_idx = 0
            
            current_time = bar_start
            while current_time < bar_end:
                pitch = pattern[pattern_idx % len(pattern)]
                
                notes.append(Note(
                    pitch=pitch,
                    start_time=current_time,
                    duration=duration * 0.9,
                    velocity=random.randint(*vel_range)
                ))
                
                current_time += duration
                pattern_idx += 1
                
        return notes
    
    def _create_arpeggio_pattern(self, chord: List[int]) -> List[int]:
        """
        Create an arpeggio pattern from chord notes.
        
        Uses various arpeggio patterns:
        - Up: 1-2-3
        - Down: 3-2-1
        - Up-Down: 1-2-3-2
        - Random: shuffled notes
        """
        pattern_type = random.choice(["up", "down", "up-down", "up-down-up"])
        
        if pattern_type == "up":
            return chord
        elif pattern_type == "down":
            return list(reversed(chord))
        elif pattern_type == "up-down":
            return chord + list(reversed(chord[:-1]))
        else:  # up-down-up
            return chord + list(reversed(chord[1:-1])) + chord
    
    def generate_counterpoint(self, melody: List[Note],
                             interval: int = 3) -> List[Note]:
        """
        Generate a counterpoint melody based on an existing melody.
        
        Args:
            melody: Original melody
            interval: Interval for counterpoint (3 = thirds, 6 = sixths)
            
        Returns:
            Counterpoint melody as list of Notes
        """
        notes = []
        
        for note in melody:
            # Find counterpoint pitch
            counter_pitch = self._get_counterpoint_pitch(note.pitch, interval)
            
            notes.append(Note(
                pitch=counter_pitch,
                start_time=note.start_time,
                duration=note.duration,
                velocity=int(note.velocity * 0.85)  # Slightly softer
            ))
            
        return notes
    
    def _get_counterpoint_pitch(self, pitch: int, interval: int) -> int:
        """Get a counterpoint pitch at the specified interval."""
        scale_notes = self.scale_gen.get_scale_in_range(pitch - 12, pitch + 24)
        
        # Find current note's position in scale
        current_idx = None
        for i, note in enumerate(scale_notes):
            if note == pitch:
                current_idx = i
                break
                
        if current_idx is None:
            # Note not in scale, quantize first
            pitch = self.scale_gen.get_nearest_scale_note(pitch)
            for i, note in enumerate(scale_notes):
                if note == pitch:
                    current_idx = i
                    break
                    
        if current_idx is None:
            return pitch + interval  # Fallback
            
        # Get note at interval
        counter_idx = current_idx + interval - 1  # -1 because intervals are 1-indexed
        
        if 0 <= counter_idx < len(scale_notes):
            return scale_notes[counter_idx]
        else:
            return pitch + interval * 2  # Approximate
    
    def print_harmony_info(self, harmony: Dict[str, List[Note]]):
        """Print information about generated harmony."""
        print(f"\n{'='*60}")
        print(f"Harmony in {self.key} {self.mode}")
        print(f"{'='*60}")
        
        for part_name, notes in harmony.items():
            print(f"\n{part_name.upper()} ({len(notes)} notes):")
            print("-" * 40)
            
            for note in notes[:8]:  # Show first 8 notes
                info = note.to_dict()
                print(f"  {info['note_name']:5} | "
                      f"t={info['start_time']:6.2f} | "
                      f"dur={info['duration']:5.2f} | "
                      f"vel={info['velocity']}")
                      
            if len(notes) > 8:
                print(f"  ... and {len(notes) - 8} more notes")


if __name__ == "__main__":
    # Test harmony generator
    gen = HarmonyGenerator("C", "Ionian (Major)", tempo=120)
    
    print("Available chord progressions:")
    for name in CHORD_PROGRESSIONS.keys():
        print(f"  - {name}")
    
    harmony = gen.generate_full_harmony(
        bars=4,
        note_length="Eighth",
        progression_name="I-V-vi-IV"
    )
    
    gen.print_harmony_info(harmony)
    
    print("\n=== Arpeggiated Harmony ===")
    arpeggio = gen.generate_arpeggiated_harmony(
        bars=2,
        note_length="Sixteenth",
        progression_name="I-IV-V-I"
    )
    print(f"Generated {len(arpeggio)} arpeggio notes")
