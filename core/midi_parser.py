"""
MIDI Parser Module
Imports and parses MIDI files for analysis and continuation.
"""

import os
from typing import List, Dict, Tuple, Optional
from dataclasses import dataclass

try:
    from mido import MidiFile, tempo2bpm
except ImportError:
    print("Warning: mido library not installed. Install with: pip install mido")
    raise

import sys
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from core.melody_generator import Note
from config.music_config import midi_note_to_name, NOTE_NAMES


class MidiParser:
    """Parses MIDI files and extracts musical information."""
    
    def __init__(self, filepath: str):
        """
        Initialize the MIDI parser.
        
        Args:
            filepath: Path to the MIDI file
        """
        if not os.path.exists(filepath):
            raise FileNotFoundError(f"MIDI file not found: {filepath}")
            
        self.filepath = filepath
        self.midi = MidiFile(filepath)
        self.ticks_per_beat = self.midi.ticks_per_beat
        self._tempo = 120  # Default
        self._time_signature = (4, 4)
        self._parse_meta_info()
        
    def _parse_meta_info(self):
        """Extract tempo and time signature from MIDI."""
        for track in self.midi.tracks:
            for msg in track:
                if msg.type == 'set_tempo':
                    self._tempo = int(tempo2bpm(msg.tempo))
                elif msg.type == 'time_signature':
                    self._time_signature = (msg.numerator, msg.denominator)
                    
    @property
    def tempo(self) -> int:
        return self._tempo
    
    @property
    def time_signature(self) -> Tuple[int, int]:
        return self._time_signature
    
    def get_notes(self, track_index: int = None) -> List[Note]:
        """
        Extract all notes from the MIDI file.
        
        Args:
            track_index: Optional specific track to extract (None = all tracks)
            
        Returns:
            List of Note objects
        """
        notes = []
        tracks = [self.midi.tracks[track_index]] if track_index else self.midi.tracks
        
        for track in tracks:
            current_time = 0
            active_notes = {}  # pitch -> (start_time, velocity)
            
            for msg in track:
                current_time += msg.time
                current_beats = current_time / self.ticks_per_beat
                
                if msg.type == 'note_on' and msg.velocity > 0:
                    active_notes[msg.note] = (current_beats, msg.velocity)
                    
                elif msg.type == 'note_off' or (msg.type == 'note_on' and msg.velocity == 0):
                    if msg.note in active_notes:
                        start_time, velocity = active_notes.pop(msg.note)
                        duration = current_beats - start_time
                        
                        notes.append(Note(
                            pitch=msg.note,
                            start_time=start_time,
                            duration=duration,
                            velocity=velocity
                        ))
                        
        # Sort by start time
        notes.sort(key=lambda n: (n.start_time, n.pitch))
        return notes
    
    def get_notes_at_time(self, time: float, tolerance: float = 0.1) -> List[Note]:
        """Get all notes sounding at a specific time."""
        all_notes = self.get_notes()
        return [n for n in all_notes 
                if n.start_time <= time + tolerance 
                and n.start_time + n.duration > time - tolerance]
    
    def get_chords_by_bar(self, beats_per_bar: int = 4) -> List[List[int]]:
        """
        Extract chord pitches grouped by bar.
        
        Returns:
            List of lists, where each inner list contains pitch classes for that bar
        """
        notes = self.get_notes()
        if not notes:
            return []
            
        # Find total duration
        max_time = max(n.start_time + n.duration for n in notes)
        num_bars = int(max_time / beats_per_bar) + 1
        
        chords = [set() for _ in range(num_bars)]
        
        for note in notes:
            bar_idx = int(note.start_time / beats_per_bar)
            if bar_idx < num_bars:
                pitch_class = note.pitch % 12
                chords[bar_idx].add(pitch_class)
                
        return [sorted(list(c)) for c in chords]
    
    def get_duration_in_bars(self, beats_per_bar: int = 4) -> float:
        """Get the total duration of the MIDI in bars."""
        notes = self.get_notes()
        if not notes:
            return 0
        max_time = max(n.start_time + n.duration for n in notes)
        return max_time / beats_per_bar
    
    def get_track_names(self) -> List[str]:
        """Get names of all tracks in the MIDI file."""
        names = []
        for i, track in enumerate(self.midi.tracks):
            name = f"Track {i}"
            for msg in track:
                if msg.type == 'track_name':
                    name = msg.name
                    break
            names.append(name)
        return names
    
    def get_pitch_histogram(self) -> Dict[int, int]:
        """Get histogram of pitch classes (0-11)."""
        notes = self.get_notes()
        histogram = {i: 0 for i in range(12)}
        
        for note in notes:
            pitch_class = note.pitch % 12
            # Weight by duration
            histogram[pitch_class] += note.duration
            
        return histogram
    
    def get_average_note_length(self) -> float:
        """Get the average note length in beats."""
        notes = self.get_notes()
        if not notes:
            return 1.0
        return sum(n.duration for n in notes) / len(notes)
    
    def print_info(self):
        """Print information about the parsed MIDI file."""
        notes = self.get_notes()
        
        print(f"\n{'='*50}")
        print(f"MIDI File: {os.path.basename(self.filepath)}")
        print(f"{'='*50}")
        print(f"Tempo: {self.tempo} BPM")
        print(f"Time Signature: {self.time_signature[0]}/{self.time_signature[1]}")
        print(f"Ticks per beat: {self.ticks_per_beat}")
        print(f"Tracks: {len(self.midi.tracks)}")
        print(f"Total notes: {len(notes)}")
        
        if notes:
            print(f"Duration: {self.get_duration_in_bars():.1f} bars")
            print(f"Pitch range: {midi_note_to_name(min(n.pitch for n in notes))} - "
                  f"{midi_note_to_name(max(n.pitch for n in notes))}")
            print(f"Average note length: {self.get_average_note_length():.2f} beats")
            
        print(f"\nTracks:")
        for i, name in enumerate(self.get_track_names()):
            print(f"  {i}: {name}")


if __name__ == "__main__":
    import sys
    if len(sys.argv) > 1:
        parser = MidiParser(sys.argv[1])
        parser.print_info()
    else:
        print("Usage: python midi_parser.py <midi_file>")
