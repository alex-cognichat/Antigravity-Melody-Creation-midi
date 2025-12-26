"""
Scale Generator Module
Generates scales, modes, and chords based on music theory.
"""

from typing import List, Tuple, Dict
import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from config.music_config import (
    KEYS, MODES, CHORD_TYPES, 
    MAJOR_SCALE_CHORD_QUALITIES, MINOR_SCALE_CHORD_QUALITIES,
    midi_note_to_name
)


class ScaleGenerator:
    """Generates scales, modes, and chords based on music theory principles."""
    
    def __init__(self, key: str, mode: str):
        """
        Initialize the scale generator.
        
        Args:
            key: The root note (e.g., "C", "F#", "Bb")
            mode: The mode/scale type (e.g., "Ionian (Major)", "Dorian")
        """
        self.key = key
        self.mode = mode
        self.root_note = KEYS[key]
        self.intervals = MODES[mode]
        
    def get_scale(self, octave: int = 4, num_octaves: int = 1) -> List[int]:
        """
        Get all notes in the scale across specified octaves.
        
        Args:
            octave: Starting octave (default 4)
            num_octaves: Number of octaves to span
            
        Returns:
            List of MIDI note numbers in the scale
        """
        base_note = KEYS[self.key] + (octave - 4) * 12
        notes = []
        
        for oct in range(num_octaves):
            for interval in self.intervals:
                note = base_note + interval + (oct * 12)
                if 0 <= note <= 127:  # Valid MIDI range
                    notes.append(note)
                    
        return notes
    
    def get_scale_in_range(self, low: int, high: int) -> List[int]:
        """
        Get all notes in the scale within a MIDI note range.
        
        Args:
            low: Lowest MIDI note number
            high: Highest MIDI note number
            
        Returns:
            List of MIDI note numbers in the scale within the range
        """
        notes = []
        # Calculate the base note at the lowest possible octave
        root_pitch_class = KEYS[self.key] % 12
        
        # Start from the lowest octave that could contain notes in range
        start_octave = (low // 12) - 1
        end_octave = (high // 12) + 1
        
        for octave in range(start_octave, end_octave + 1):
            base_note = root_pitch_class + (octave * 12)
            for interval in self.intervals:
                note = base_note + interval
                if low <= note <= high:
                    notes.append(note)
                    
        return sorted(list(set(notes)))
    
    def get_chord(self, degree: int, chord_type: str = None) -> List[int]:
        """
        Get a chord built on a specific scale degree.
        
        Args:
            degree: Scale degree (1-7)
            chord_type: Optional specific chord type, otherwise uses diatonic chord
            
        Returns:
            List of MIDI note numbers forming the chord
        """
        if degree < 1 or degree > len(self.intervals):
            raise ValueError(f"Invalid scale degree: {degree}")
            
        # Get the root note of the chord (scale degree)
        root_interval = self.intervals[degree - 1]
        root = self.root_note + root_interval
        
        if chord_type:
            # Use specified chord type
            intervals = CHORD_TYPES[chord_type]
        else:
            # Determine chord quality based on mode
            if "Minor" in self.mode or "Aeolian" in self.mode or "Dorian" in self.mode:
                quality = MINOR_SCALE_CHORD_QUALITIES.get(degree, "major")
            else:
                quality = MAJOR_SCALE_CHORD_QUALITIES.get(degree, "major")
            intervals = CHORD_TYPES[quality]
            
        return [root + interval for interval in intervals]
    
    def get_chord_at_octave(self, degree: int, octave: int = 4, 
                            chord_type: str = None) -> List[int]:
        """
        Get a chord at a specific octave.
        
        Args:
            degree: Scale degree (1-7)
            octave: Desired octave
            chord_type: Optional specific chord type
            
        Returns:
            List of MIDI note numbers forming the chord
        """
        chord = self.get_chord(degree, chord_type)
        # Transpose to desired octave
        base_octave = (chord[0] // 12) - 1
        octave_diff = octave - base_octave
        return [note + (octave_diff * 12) for note in chord]
    
    def get_all_diatonic_chords(self) -> Dict[int, List[int]]:
        """
        Get all diatonic chords for the scale.
        
        Returns:
            Dictionary mapping scale degrees to chord notes
        """
        return {degree: self.get_chord(degree) 
                for degree in range(1, len(self.intervals) + 1)}
    
    def is_note_in_scale(self, midi_note: int) -> bool:
        """Check if a MIDI note is in the current scale."""
        note_pitch_class = midi_note % 12
        root_pitch_class = KEYS[self.key] % 12
        relative_pitch = (note_pitch_class - root_pitch_class) % 12
        return relative_pitch in self.intervals
    
    def get_nearest_scale_note(self, midi_note: int) -> int:
        """
        Get the nearest note in the scale to a given MIDI note.
        
        Args:
            midi_note: Input MIDI note number
            
        Returns:
            Nearest MIDI note that is in the scale
        """
        if self.is_note_in_scale(midi_note):
            return midi_note
            
        # Check notes above and below
        for offset in range(1, 7):
            if self.is_note_in_scale(midi_note + offset):
                return midi_note + offset
            if self.is_note_in_scale(midi_note - offset):
                return midi_note - offset
                
        return midi_note  # Fallback
    
    def get_scale_degree(self, midi_note: int) -> int:
        """
        Get the scale degree of a MIDI note.
        
        Args:
            midi_note: MIDI note number
            
        Returns:
            Scale degree (1-indexed), or 0 if not in scale
        """
        note_pitch_class = midi_note % 12
        root_pitch_class = KEYS[self.key] % 12
        relative_pitch = (note_pitch_class - root_pitch_class) % 12
        
        try:
            return self.intervals.index(relative_pitch) + 1
        except ValueError:
            return 0
    
    def get_chord_tones(self, degree: int = 1) -> List[int]:
        """
        Get the pitch classes (0-11) of chord tones for a scale degree.
        
        Args:
            degree: Scale degree (1-7)
            
        Returns:
            List of pitch classes that are chord tones
        """
        chord = self.get_chord(degree)
        return [note % 12 for note in chord]
    
    def print_scale_info(self):
        """Print information about the current scale."""
        print(f"\n{'='*50}")
        print(f"Scale: {self.key} {self.mode}")
        print(f"{'='*50}")
        
        scale_notes = self.get_scale()
        note_names = [midi_note_to_name(n) for n in scale_notes]
        print(f"Notes: {' - '.join(note_names)}")
        
        print(f"\nDiatonic Chords:")
        for degree in range(1, len(self.intervals) + 1):
            chord = self.get_chord(degree)
            chord_names = [midi_note_to_name(n) for n in chord]
            print(f"  {degree}: {' - '.join(chord_names)}")


if __name__ == "__main__":
    # Test the scale generator
    sg = ScaleGenerator("C", "Ionian (Major)")
    sg.print_scale_info()
    
    sg2 = ScaleGenerator("A", "Aeolian (Minor)")
    sg2.print_scale_info()
    
    sg3 = ScaleGenerator("D", "Dorian")
    sg3.print_scale_info()
