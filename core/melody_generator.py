"""
Melody Generator Module
Generates lead melodies, bass lines, and pads using music theory principles.
"""

import random
from typing import List, Dict, Tuple, Optional
from dataclasses import dataclass
import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from core.scale_generator import ScaleGenerator
from config.music_config import (
    OCTAVE_RANGES, VELOCITY_RANGES, NOTE_LENGTHS,
    MOODS, STYLES, midi_note_to_name
)


@dataclass
class Note:
    """Represents a single note with all MIDI properties."""
    pitch: int           # MIDI note number (0-127)
    start_time: float    # Start time in beats
    duration: float      # Duration in beats
    velocity: int        # Velocity (0-127)
    
    def to_dict(self) -> Dict:
        return {
            "pitch": self.pitch,
            "start_time": self.start_time,
            "duration": self.duration,
            "velocity": self.velocity,
            "note_name": midi_note_to_name(self.pitch)
        }


class MelodyGenerator:
    """Generates melodies based on music theory principles."""
    
    def __init__(self, key: str, mode: str, tempo: int = 120):
        """
        Initialize the melody generator.
        
        Args:
            key: Root note (e.g., "C", "F#")
            mode: Scale mode (e.g., "Ionian (Major)", "Dorian")
            tempo: Tempo in BPM
        """
        self.key = key
        self.mode = mode
        self.tempo = tempo
        self.scale_gen = ScaleGenerator(key, mode)
        
    def generate_lead(self, bars: int, note_length: str = "Eighth",
                     time_signature: Tuple[int, int] = (4, 4),
                     mood: str = None, style: str = None) -> List[Note]:
        """
        Generate a lead melody line.
        
        Uses music theory principles:
        - Mostly stepwise motion
        - Occasional leaps to chord tones
        - Ends on tonic or 5th
        - Rhythmic variation
        
        Args:
            bars: Number of bars to generate
            note_length: Base note length
            time_signature: Time signature as (beats, note value)
            
        Returns:
            List of Note objects
        """
        notes = []
        beats_per_bar = time_signature[0]
        total_beats = bars * beats_per_bar
        
        # Get scale notes in lead range
        low, high = OCTAVE_RANGES["lead"]
        low_midi = low * 12 + 12  # Convert octave to MIDI
        high_midi = high * 12 + 12
        scale_notes = self.scale_gen.get_scale_in_range(low_midi, high_midi)
        
        if not scale_notes:
            return notes
            
        base_duration = NOTE_LENGTHS.get(note_length, 0.5)
        vel_range = VELOCITY_RANGES["lead"]
        
        # Apply mood modifiers
        mood_params = MOODS.get(mood, {}) if mood else {}
        style_params = STYLES.get(style, {}) if style else {}
        
        velocity_mod = mood_params.get("velocity_mod", 0)
        density = mood_params.get("density", style_params.get("density", 1.0))
        leap_chance = mood_params.get("leap_chance", 0.25)
        
        current_time = 0.0
        current_note_idx = len(scale_notes) // 2  # Start in middle of range
        
        # Track phrase structure
        phrase_length = beats_per_bar * 2  # 2-bar phrases
        
        while current_time < total_beats:
            # Determine note duration with variation
            duration = self._get_varied_duration(base_duration, current_time, 
                                                  beats_per_bar)
            
            # Don't exceed total length
            if current_time + duration > total_beats:
                duration = total_beats - current_time
                
            if duration <= 0:
                break
                
            # Get next note using melodic motion rules
            current_note_idx = self._get_next_note_index(
                current_note_idx, scale_notes, current_time, 
                phrase_length, total_beats
            )
            
            pitch = scale_notes[current_note_idx]
            base_velocity = random.randint(*vel_range)
            velocity = max(1, min(127, base_velocity + velocity_mod))
            
            notes.append(Note(
                pitch=pitch,
                start_time=current_time,
                duration=duration * 0.9,  # Slight gap between notes
                velocity=velocity
            ))
            
            current_time += duration / density  # density affects note spacing
            
        return notes
    
    def continue_melody(self, existing_notes: List[Note], bars_to_add: int,
                       note_length: str = None, mood: str = None,
                       style: str = None) -> List[Note]:
        """
        Continue an existing melody with new bars that fit naturally.
        
        Args:
            existing_notes: List of existing Note objects
            bars_to_add: Number of new bars to generate
            note_length: Note length (auto-detected if None)
            mood: Optional mood
            style: Optional style
            
        Returns:
            List of new Note objects to append
        """
        if not existing_notes:
            return self.generate_lead(bars_to_add, note_length or "Eighth",
                                      mood=mood, style=style)
        
        # Analyze existing notes
        last_note = max(existing_notes, key=lambda n: n.start_time)
        start_time = last_note.start_time + last_note.duration
        
        # Detect average note length if not provided
        if note_length is None:
            avg_dur = sum(n.duration for n in existing_notes) / len(existing_notes)
            if avg_dur >= 2.0:
                note_length = "Half"
            elif avg_dur >= 1.0:
                note_length = "Quarter"
            elif avg_dur >= 0.4:
                note_length = "Eighth"
            else:
                note_length = "Sixteenth"
        
        # Generate continuation starting from last pitch
        new_notes = []
        beats_per_bar = 4
        total_beats = bars_to_add * beats_per_bar
        
        low, high = OCTAVE_RANGES["lead"]
        low_midi = low * 12 + 12
        high_midi = high * 12 + 12
        scale_notes = self.scale_gen.get_scale_in_range(low_midi, high_midi)
        
        if not scale_notes:
            return new_notes
        
        # Find closest scale note to last pitch
        current_note_idx = 0
        min_dist = float('inf')
        for i, note in enumerate(scale_notes):
            dist = abs(note - last_note.pitch)
            if dist < min_dist:
                min_dist = dist
                current_note_idx = i
        
        base_duration = NOTE_LENGTHS.get(note_length, 0.5)
        vel_range = VELOCITY_RANGES["lead"]
        mood_params = MOODS.get(mood, {}) if mood else {}
        velocity_mod = mood_params.get("velocity_mod", 0)
        
        current_time = start_time
        phrase_length = beats_per_bar * 2
        end_time = start_time + total_beats
        
        while current_time < end_time:
            duration = self._get_varied_duration(base_duration, current_time, beats_per_bar)
            if current_time + duration > end_time:
                duration = end_time - current_time
            if duration <= 0:
                break
            
            current_note_idx = self._get_next_note_index(
                current_note_idx, scale_notes, current_time - start_time,
                phrase_length, total_beats
            )
            
            pitch = scale_notes[current_note_idx]
            base_velocity = random.randint(*vel_range)
            velocity = max(1, min(127, base_velocity + velocity_mod))
            
            new_notes.append(Note(
                pitch=pitch,
                start_time=current_time,
                duration=duration * 0.9,
                velocity=velocity
            ))
            
            current_time += duration
            
        return new_notes
    
    def generate_bass(self, bars: int, note_length: str = "Quarter",
                     time_signature: Tuple[int, int] = (4, 4),
                     chord_progression: List[int] = None) -> List[Note]:
        """
        Generate a bass line.
        
        Uses music theory principles:
        - Emphasizes root notes of chords
        - Uses 5ths and octaves
        - Creates rhythmic foundation
        
        Args:
            bars: Number of bars to generate
            note_length: Base note length
            time_signature: Time signature
            chord_progression: Optional chord progression (scale degrees)
            
        Returns:
            List of Note objects
        """
        notes = []
        beats_per_bar = time_signature[0]
        total_beats = bars * beats_per_bar
        
        # Get scale notes in bass range
        low, high = OCTAVE_RANGES["bass"]
        low_midi = low * 12 + 12
        high_midi = high * 12 + 12
        scale_notes = self.scale_gen.get_scale_in_range(low_midi, high_midi)
        
        if not scale_notes:
            return notes
            
        base_duration = NOTE_LENGTHS.get(note_length, 1.0)
        vel_range = VELOCITY_RANGES["bass"]
        
        # Default progression if none provided
        if chord_progression is None:
            chord_progression = [1, 4, 5, 1]
            
        current_time = 0.0
        bar_idx = 0
        
        while current_time < total_beats:
            # Get current chord root
            chord_idx = bar_idx % len(chord_progression)
            degree = chord_progression[chord_idx]
            
            # Get bass notes for this bar
            bar_notes = self._generate_bass_bar(
                degree, base_duration, beats_per_bar,
                scale_notes, vel_range, current_time
            )
            
            notes.extend(bar_notes)
            current_time += beats_per_bar
            bar_idx += 1
            
        return notes
    
    def generate_pad(self, bars: int, note_length: str = "Whole",
                    time_signature: Tuple[int, int] = (4, 4),
                    chord_progression: List[int] = None) -> List[Note]:
        """
        Generate pad/chord voicings.
        
        Uses music theory principles:
        - Smooth voice leading
        - Sustained chords
        - Inversions for smooth transitions
        
        Args:
            bars: Number of bars to generate
            note_length: Base note length (typically whole or half)
            time_signature: Time signature
            chord_progression: Optional chord progression (scale degrees)
            
        Returns:
            List of Note objects (multiple notes per chord)
        """
        notes = []
        beats_per_bar = time_signature[0]
        total_beats = bars * beats_per_bar
        
        base_duration = NOTE_LENGTHS.get(note_length, 4.0)
        vel_range = VELOCITY_RANGES["pad"]
        
        # Default progression if none provided
        if chord_progression is None:
            chord_progression = [1, 5, 6, 4]
            
        current_time = 0.0
        prev_chord = None
        bar_idx = 0
        
        # Determine chord duration based on progression length and bars
        chords_per_bar = 1 if base_duration >= beats_per_bar else 2
        
        while current_time < total_beats:
            chord_idx = bar_idx % len(chord_progression)
            degree = chord_progression[chord_idx]
            
            # Get chord at appropriate octave
            low, high = OCTAVE_RANGES["pad"]
            octave = (low + high) // 2
            
            chord_notes = self.scale_gen.get_chord_at_octave(degree, octave)
            
            # Apply voice leading if we have a previous chord
            if prev_chord is not None:
                chord_notes = self._apply_voice_leading(prev_chord, chord_notes)
                
            # Duration for this chord
            duration = min(base_duration, total_beats - current_time)
            if duration <= 0:
                break
                
            # Add all chord notes
            for pitch in chord_notes:
                velocity = random.randint(*vel_range)
                notes.append(Note(
                    pitch=pitch,
                    start_time=current_time,
                    duration=duration * 0.95,
                    velocity=velocity
                ))
                
            prev_chord = chord_notes
            current_time += base_duration
            bar_idx += 1
            
        return notes
    
    def _get_varied_duration(self, base_duration: float, 
                             current_time: float,
                             beats_per_bar: float) -> float:
        """Add rhythmic variation to note durations."""
        beat_in_bar = current_time % beats_per_bar
        
        # Longer notes on strong beats
        if beat_in_bar == 0:
            return base_duration * random.choice([1, 2])
        elif beat_in_bar == beats_per_bar / 2:
            return base_duration * random.choice([1, 1, 2])
        else:
            return base_duration * random.choice([0.5, 1, 1])
    
    def _get_next_note_index(self, current_idx: int, scale_notes: List[int],
                             current_time: float, phrase_length: float,
                             total_beats: float) -> int:
        """
        Determine the next note using melodic motion rules.
        
        Rules applied:
        - Mostly stepwise motion (move by 1-2 scale degrees)
        - Occasional leaps (3-4 scale degrees)
        - Tendency to return to tonic at phrase ends
        - Stay within scale range
        """
        max_idx = len(scale_notes) - 1
        
        # Check if we're at phrase end
        beat_in_phrase = current_time % phrase_length
        near_phrase_end = beat_in_phrase > phrase_length * 0.75
        
        # At end of piece, move toward tonic
        near_end = current_time > total_beats * 0.9
        
        if near_end or near_phrase_end:
            # Move toward lower register (tonic area)
            target_idx = max(0, min(2, max_idx))
            step = -1 if current_idx > target_idx else 1
            return max(0, min(max_idx, current_idx + step))
        
        # Normal melodic motion
        motion_type = random.random()
        
        if motion_type < 0.5:
            # Stepwise motion (most common)
            step = random.choice([-1, 1])
        elif motion_type < 0.75:
            # Small leap (skip)
            step = random.choice([-2, 2])
        else:
            # Larger leap
            step = random.choice([-3, -4, 3, 4])
            
        new_idx = current_idx + step
        
        # Keep within range
        new_idx = max(0, min(max_idx, new_idx))
        
        return new_idx
    
    def _generate_bass_bar(self, degree: int, base_duration: float,
                          beats_per_bar: float, scale_notes: List[int],
                          vel_range: Tuple[int, int],
                          start_time: float) -> List[Note]:
        """Generate bass notes for a single bar."""
        notes = []
        
        # Get root note for this chord
        chord = self.scale_gen.get_chord(degree)
        root_pitch_class = chord[0] % 12
        fifth_pitch_class = chord[2] % 12 if len(chord) > 2 else root_pitch_class
        
        # Find root and fifth in bass range
        root_note = None
        fifth_note = None
        
        for note in scale_notes:
            if note % 12 == root_pitch_class and root_note is None:
                root_note = note
            if note % 12 == fifth_pitch_class and fifth_note is None:
                fifth_note = note
                
        if root_note is None:
            root_note = scale_notes[0]
        if fifth_note is None:
            fifth_note = root_note
            
        current_time = start_time
        end_time = start_time + beats_per_bar
        
        # Create bass pattern
        pattern_type = random.choice(["root", "root-fifth", "walking"])
        
        if pattern_type == "root":
            # Simple root notes
            while current_time < end_time:
                duration = min(base_duration, end_time - current_time)
                notes.append(Note(
                    pitch=root_note,
                    start_time=current_time,
                    duration=duration * 0.8,
                    velocity=random.randint(*vel_range)
                ))
                current_time += base_duration
                
        elif pattern_type == "root-fifth":
            # Alternating root and fifth
            is_root = True
            while current_time < end_time:
                pitch = root_note if is_root else fifth_note
                duration = min(base_duration, end_time - current_time)
                notes.append(Note(
                    pitch=pitch,
                    start_time=current_time,
                    duration=duration * 0.8,
                    velocity=random.randint(*vel_range)
                ))
                current_time += base_duration
                is_root = not is_root
                
        else:  # walking
            # Walking bass line
            current_note_idx = scale_notes.index(root_note) if root_note in scale_notes else 0
            while current_time < end_time:
                duration = min(base_duration, end_time - current_time)
                notes.append(Note(
                    pitch=scale_notes[current_note_idx],
                    start_time=current_time,
                    duration=duration * 0.8,
                    velocity=random.randint(*vel_range)
                ))
                current_time += base_duration
                # Move to adjacent note
                step = random.choice([-1, 1])
                current_note_idx = max(0, min(len(scale_notes) - 1, 
                                             current_note_idx + step))
                
        return notes
    
    def _apply_voice_leading(self, prev_chord: List[int], 
                             new_chord: List[int]) -> List[int]:
        """
        Apply voice leading principles to smooth chord transitions.
        
        Rules:
        - Keep common tones
        - Move other voices by smallest interval
        """
        if len(prev_chord) != len(new_chord):
            return new_chord
            
        result = []
        used_notes = set()
        
        for prev_note in prev_chord:
            # Find closest note in new chord
            best_note = None
            best_distance = float('inf')
            
            for new_note in new_chord:
                # Check all octave transpositions
                for octave_shift in [-12, 0, 12]:
                    candidate = new_note + octave_shift
                    if candidate in used_notes:
                        continue
                    distance = abs(prev_note - candidate)
                    if distance < best_distance and 0 <= candidate <= 127:
                        best_distance = distance
                        best_note = candidate
                        
            if best_note is not None:
                result.append(best_note)
                used_notes.add(best_note)
            else:
                # Fallback to original note
                result.append(new_chord[len(result)] if len(result) < len(new_chord) else prev_note)
                
        return sorted(result)


if __name__ == "__main__":
    # Test the melody generator
    gen = MelodyGenerator("C", "Ionian (Major)", tempo=120)
    
    print("\n=== Lead Melody ===")
    lead = gen.generate_lead(bars=4, note_length="Eighth")
    for note in lead[:10]:  # Print first 10 notes
        print(f"  {note.to_dict()}")
    print(f"  ... ({len(lead)} total notes)")
    
    print("\n=== Bass Line ===")
    bass = gen.generate_bass(bars=4, note_length="Quarter")
    for note in bass[:8]:
        print(f"  {note.to_dict()}")
    print(f"  ... ({len(bass)} total notes)")
    
    print("\n=== Pad Chords ===")
    pad = gen.generate_pad(bars=4, note_length="Whole")
    for note in pad[:12]:
        print(f"  {note.to_dict()}")
    print(f"  ... ({len(pad)} total notes)")
