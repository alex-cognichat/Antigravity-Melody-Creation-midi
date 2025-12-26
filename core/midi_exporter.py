"""
MIDI Exporter Module
Exports generated notes to MIDI files and prints to terminal.
"""

from typing import List, Dict, Union
import os
from datetime import datetime

try:
    from mido import MidiFile, MidiTrack, Message, MetaMessage, bpm2tempo
except ImportError:
    print("Warning: mido library not installed. Install with: pip install mido")
    raise

import sys
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from core.melody_generator import Note
from config.music_config import midi_note_to_name


class MidiExporter:
    """Exports notes to MIDI files."""
    
    TICKS_PER_BEAT = 480  # Standard MIDI resolution
    
    def __init__(self, tempo: int = 120, time_signature: tuple = (4, 4)):
        """
        Initialize the MIDI exporter.
        
        Args:
            tempo: Tempo in BPM
            time_signature: Time signature as (numerator, denominator)
        """
        self.tempo = tempo
        self.time_signature = time_signature
        
    def export_single_track(self, notes: List[Note], filename: str,
                            track_name: str = "Generated Melody") -> str:
        """
        Export a single track of notes to a MIDI file.
        
        Args:
            notes: List of Note objects
            filename: Output filename (with or without .mid extension)
            track_name: Name for the MIDI track
            
        Returns:
            Full path to the created file
        """
        if not filename.endswith('.mid'):
            filename += '.mid'
            
        # Ensure output directory exists
        output_dir = os.path.dirname(filename)
        if output_dir and not os.path.exists(output_dir):
            os.makedirs(output_dir)
            
        mid = MidiFile(ticks_per_beat=self.TICKS_PER_BEAT)
        track = MidiTrack()
        mid.tracks.append(track)
        
        # Add track name and tempo
        track.append(MetaMessage('track_name', name=track_name, time=0))
        track.append(MetaMessage('set_tempo', tempo=bpm2tempo(self.tempo), time=0))
        
        # Add time signature
        track.append(MetaMessage('time_signature',
                                 numerator=self.time_signature[0],
                                 denominator=self.time_signature[1],
                                 time=0))
        
        # Convert notes to MIDI messages
        self._add_notes_to_track(track, notes)
        
        # Add end of track
        track.append(MetaMessage('end_of_track', time=0))
        
        mid.save(filename)
        return os.path.abspath(filename)
    
    def export_multi_track(self, tracks: Dict[str, List[Note]], 
                          filename: str) -> str:
        """
        Export multiple tracks to a single MIDI file.
        
        Args:
            tracks: Dictionary mapping track names to note lists
            filename: Output filename
            
        Returns:
            Full path to the created file
        """
        if not filename.endswith('.mid'):
            filename += '.mid'
            
        # Ensure output directory exists
        output_dir = os.path.dirname(filename)
        if output_dir and not os.path.exists(output_dir):
            os.makedirs(output_dir)
            
        mid = MidiFile(type=1, ticks_per_beat=self.TICKS_PER_BEAT)
        
        # Add tempo track (track 0)
        tempo_track = MidiTrack()
        mid.tracks.append(tempo_track)
        tempo_track.append(MetaMessage('set_tempo', tempo=bpm2tempo(self.tempo), time=0))
        tempo_track.append(MetaMessage('time_signature',
                                       numerator=self.time_signature[0],
                                       denominator=self.time_signature[1],
                                       time=0))
        tempo_track.append(MetaMessage('end_of_track', time=0))
        
        # Add each track
        for channel, (track_name, notes) in enumerate(tracks.items()):
            track = MidiTrack()
            mid.tracks.append(track)
            
            track.append(MetaMessage('track_name', name=track_name, time=0))
            self._add_notes_to_track(track, notes, channel=channel)
            track.append(MetaMessage('end_of_track', time=0))
            
        mid.save(filename)
        return os.path.abspath(filename)
    
    def _add_notes_to_track(self, track: MidiTrack, notes: List[Note],
                            channel: int = 0):
        """
        Add notes to a MIDI track.
        
        Converts Note objects to MIDI note_on/note_off messages with proper
        delta times.
        """
        if not notes:
            return
            
        # Create list of events (note_on and note_off)
        events = []
        for note in notes:
            start_tick = int(note.start_time * self.TICKS_PER_BEAT)
            end_tick = int((note.start_time + note.duration) * self.TICKS_PER_BEAT)
            
            events.append({
                'type': 'note_on',
                'tick': start_tick,
                'note': note.pitch,
                'velocity': note.velocity,
                'channel': channel
            })
            events.append({
                'type': 'note_off',
                'tick': end_tick,
                'note': note.pitch,
                'velocity': 0,
                'channel': channel
            })
            
        # Sort by tick, with note_off before note_on for same tick
        events.sort(key=lambda e: (e['tick'], e['type'] != 'note_off'))
        
        # Convert to MIDI messages with delta times
        current_tick = 0
        for event in events:
            delta = event['tick'] - current_tick
            current_tick = event['tick']
            
            track.append(Message(
                event['type'],
                note=event['note'],
                velocity=event['velocity'],
                channel=event['channel'],
                time=delta
            ))
    
    def print_notes_to_terminal(self, notes: Union[List[Note], Dict[str, List[Note]]],
                                title: str = "Generated Notes"):
        """
        Print notes to terminal in a formatted table.
        
        Args:
            notes: List of notes or dictionary of track -> notes
            title: Title for the output
        """
        print(f"\n{'='*70}")
        print(f" {title}")
        print(f"{'='*70}")
        print(f" Key: N/A  |  Tempo: {self.tempo} BPM  |  Time: {self.time_signature[0]}/{self.time_signature[1]}")
        print(f"{'='*70}")
        
        if isinstance(notes, dict):
            # Multiple tracks
            for track_name, track_notes in notes.items():
                self._print_track(track_name, track_notes)
        else:
            # Single track
            self._print_track("Main", notes)
            
        print(f"{'='*70}\n")
    
    def _print_track(self, track_name: str, notes: List[Note]):
        """Print a single track's notes."""
        print(f"\n  ▸ {track_name.upper()} ({len(notes)} notes)")
        print(f"  {'-'*64}")
        print(f"  {'Note':^8} | {'Start':^10} | {'Duration':^10} | {'Velocity':^8} | {'Bar':^6}")
        print(f"  {'-'*64}")
        
        for note in notes:
            bar = int(note.start_time / 4) + 1
            beat = (note.start_time % 4) + 1
            note_name = midi_note_to_name(note.pitch)
            
            print(f"  {note_name:^8} | {note.start_time:^10.2f} | "
                  f"{note.duration:^10.2f} | {note.velocity:^8} | {bar}.{beat:.1f}")
            
        if not notes:
            print(f"  {'(no notes)':^64}")


def generate_filename(gen_type: str, key: str, mode: str, bars: int,
                     output_dir: str = "output") -> str:
    """
    Generate a filename for the MIDI export.
    
    Args:
        gen_type: Generation type (lead, bass, pad, harmony)
        key: Musical key
        mode: Scale mode
        bars: Number of bars
        output_dir: Output directory
        
    Returns:
        Full path for the MIDI file
    """
    # Clean mode name for filename
    mode_clean = mode.split()[0].lower()
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    
    filename = f"{gen_type}_{key}_{mode_clean}_{bars}bars_{timestamp}.mid"
    return os.path.join(output_dir, filename)


if __name__ == "__main__":
    # Test the MIDI exporter
    from core.melody_generator import MelodyGenerator
    
    # Generate some test notes
    gen = MelodyGenerator("C", "Ionian (Major)", tempo=120)
    lead_notes = gen.generate_lead(bars=4, note_length="Eighth")
    bass_notes = gen.generate_bass(bars=4, note_length="Quarter")
    
    # Create exporter
    exporter = MidiExporter(tempo=120, time_signature=(4, 4))
    
    # Print to terminal
    exporter.print_notes_to_terminal(
        {"Lead": lead_notes, "Bass": bass_notes},
        title="Test Generation - C Major"
    )
    
    # Export single track
    output_path = exporter.export_single_track(
        lead_notes,
        "output/test_lead.mid",
        track_name="Lead Melody"
    )
    print(f"Exported single track to: {output_path}")
    
    # Export multi-track
    output_path = exporter.export_multi_track(
        {"Lead": lead_notes, "Bass": bass_notes},
        "output/test_multi.mid"
    )
    print(f"Exported multi-track to: {output_path}")
