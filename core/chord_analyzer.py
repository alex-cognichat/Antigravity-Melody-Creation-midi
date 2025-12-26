"""
Chord Analyzer Module
Analyzes chord progressions to detect key, mode, and suggest continuations.
"""

from typing import List, Dict, Tuple, Optional
from collections import Counter
import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from config.music_config import (
    KEYS, KEY_NAMES, MODES, CHORD_TYPES, CHORD_PROGRESSIONS,
    MAJOR_SCALE_CHORD_QUALITIES, MINOR_SCALE_CHORD_QUALITIES,
    midi_note_to_name, NOTE_NAMES
)


# Chord templates for recognition (pitch class sets)
CHORD_TEMPLATES = {
    "major": {0, 4, 7},
    "minor": {0, 3, 7},
    "diminished": {0, 3, 6},
    "augmented": {0, 4, 8},
    "sus2": {0, 2, 7},
    "sus4": {0, 5, 7},
    "dom7": {0, 4, 7, 10},
    "maj7": {0, 4, 7, 11},
    "min7": {0, 3, 7, 10},
}


class ChordAnalyzer:
    """Analyzes chord progressions and detects musical keys/modes."""
    
    @staticmethod
    def identify_chord(pitch_classes: List[int]) -> Tuple[str, str]:
        """
        Identify a chord from its pitch classes.
        
        Args:
            pitch_classes: List of pitch classes (0-11)
            
        Returns:
            Tuple of (root_note_name, chord_type)
        """
        if not pitch_classes:
            return ("", "unknown")
            
        pitch_set = set(pitch_classes)
        best_match = None
        best_score = 0
        
        # Try each possible root
        for root in range(12):
            # Transpose chord to have root at 0
            transposed = {(p - root) % 12 for p in pitch_set}
            
            # Match against templates
            for chord_type, template in CHORD_TEMPLATES.items():
                # Calculate overlap score
                overlap = len(transposed & template)
                total = len(transposed | template)
                score = overlap / total if total > 0 else 0
                
                if score > best_score:
                    best_score = score
                    best_match = (NOTE_NAMES[root], chord_type)
                    
        if best_match and best_score > 0.5:
            return best_match
        else:
            # Return just the bass note if no good match
            return (NOTE_NAMES[min(pitch_classes)], "unknown")
    
    @staticmethod
    def detect_key(pitch_histogram: Dict[int, float]) -> Tuple[str, str, float]:
        """
        Detect the key from a pitch histogram using the Krumhansl-Schmuckler algorithm.
        
        Args:
            pitch_histogram: Dictionary mapping pitch class (0-11) to weight
            
        Returns:
            Tuple of (key_name, mode, confidence_score)
        """
        # Major key profile (Krumhansl-Kessler)
        major_profile = [6.35, 2.23, 3.48, 2.33, 4.38, 4.09, 2.52, 5.19, 2.39, 3.66, 2.29, 2.88]
        # Minor key profile
        minor_profile = [6.33, 2.68, 3.52, 5.38, 2.60, 3.53, 2.54, 4.75, 3.98, 2.69, 3.34, 3.17]
        
        best_key = "C"
        best_mode = "Ionian (Major)"
        best_corr = -1
        
        # Normalize histogram
        total = sum(pitch_histogram.values())
        if total == 0:
            return (best_key, best_mode, 0.0)
            
        hist_values = [pitch_histogram.get(i, 0) / total for i in range(12)]
        
        for key_idx in range(12):
            # Rotate histogram to match key
            rotated = hist_values[key_idx:] + hist_values[:key_idx]
            
            # Correlate with major profile
            major_corr = ChordAnalyzer._correlation(rotated, major_profile)
            if major_corr > best_corr:
                best_corr = major_corr
                best_key = KEY_NAMES[key_idx]
                best_mode = "Ionian (Major)"
                
            # Correlate with minor profile
            minor_corr = ChordAnalyzer._correlation(rotated, minor_profile)
            if minor_corr > best_corr:
                best_corr = minor_corr
                best_key = KEY_NAMES[key_idx]
                best_mode = "Aeolian (Minor)"
                
        return (best_key, best_mode, best_corr)
    
    @staticmethod
    def _correlation(a: List[float], b: List[float]) -> float:
        """Calculate Pearson correlation coefficient."""
        n = len(a)
        if n == 0:
            return 0
            
        mean_a = sum(a) / n
        mean_b = sum(b) / n
        
        numerator = sum((a[i] - mean_a) * (b[i] - mean_b) for i in range(n))
        denom_a = sum((a[i] - mean_a) ** 2 for i in range(n)) ** 0.5
        denom_b = sum((b[i] - mean_b) ** 2 for i in range(n)) ** 0.5
        
        if denom_a * denom_b == 0:
            return 0
            
        return numerator / (denom_a * denom_b)
    
    @staticmethod
    def analyze_progression(chords: List[Tuple[str, str]], key: str) -> List[str]:
        """
        Convert chord sequence to Roman numeral notation.
        
        Args:
            chords: List of (root, quality) tuples
            key: The key to analyze in
            
        Returns:
            List of Roman numeral representations
        """
        key_idx = KEY_NAMES.index(key) if key in KEY_NAMES else 0
        roman_numerals = ["I", "bII", "II", "bIII", "III", "IV", "#IV", "V", "bVI", "VI", "bVII", "VII"]
        
        result = []
        for root, quality in chords:
            if not root:
                result.append("?")
                continue
                
            root_idx = KEY_NAMES.index(root) if root in KEY_NAMES else 0
            degree = (root_idx - key_idx) % 12
            
            numeral = roman_numerals[degree]
            
            # Lowercase for minor
            if quality in ["minor", "min7", "diminished"]:
                numeral = numeral.lower()
            if quality == "diminished":
                numeral += "°"
            elif quality == "augmented":
                numeral += "+"
            elif quality in ["dom7", "maj7", "min7"]:
                numeral += "7"
                
            result.append(numeral)
            
        return result
    
    @staticmethod
    def suggest_next_chords(progression: List[str], num_suggestions: int = 4) -> List[List[int]]:
        """
        Suggest probable next chords based on the current progression.
        Uses common progression patterns.
        
        Args:
            progression: Current progression as Roman numerals or scale degrees
            num_suggestions: Number of chord suggestions
            
        Returns:
            List of suggested scale degrees
        """
        # Common chord transitions (from -> likely next)
        transitions = {
            1: [4, 5, 6, 2],     # I often goes to IV, V, vi, ii
            2: [5, 4, 1],        # ii often goes to V, IV, I
            3: [4, 6, 2],        # iii often goes to IV, vi, ii
            4: [5, 1, 2],        # IV often goes to V, I, ii
            5: [1, 6, 4],        # V often goes to I, vi, IV
            6: [4, 2, 5],        # vi often goes to IV, ii, V
            7: [1, 3],           # vii° often goes to I, iii
        }
        
        if not progression:
            return [[1], [4], [5], [6]][:num_suggestions]
            
        # Get last chord degree
        last = progression[-1] if isinstance(progression[-1], int) else 1
        
        suggestions = transitions.get(last, [1, 4, 5, 6])
        return [[s] for s in suggestions[:num_suggestions]]
    
    @staticmethod
    def detect_note_length(notes) -> str:
        """
        Detect the most common note length.
        
        Args:
            notes: List of Note objects
            
        Returns:
            Note length name
        """
        if not notes:
            return "Eighth"
            
        durations = [n.duration for n in notes]
        avg_duration = sum(durations) / len(durations)
        
        # Map to note length names
        if avg_duration >= 3.0:
            return "Whole"
        elif avg_duration >= 1.5:
            return "Half"
        elif avg_duration >= 0.75:
            return "Quarter"
        elif avg_duration >= 0.375:
            return "Eighth"
        else:
            return "Sixteenth"
    
    @staticmethod
    def full_analysis(notes, print_results: bool = True) -> Dict:
        """
        Perform complete analysis of notes.
        
        Args:
            notes: List of Note objects
            print_results: Whether to print the results
            
        Returns:
            Dictionary with all analysis results
        """
        from core.midi_parser import MidiParser
        
        # Build pitch histogram
        histogram = {i: 0 for i in range(12)}
        for note in notes:
            histogram[note.pitch % 12] += note.duration
            
        # Detect key
        key, mode, confidence = ChordAnalyzer.detect_key(histogram)
        
        # Detect note length
        note_length = ChordAnalyzer.detect_note_length(notes)
        
        # Get pitch range
        if notes:
            lowest = min(n.pitch for n in notes)
            highest = max(n.pitch for n in notes)
        else:
            lowest = highest = 60
            
        # Calculate duration
        if notes:
            total_duration = max(n.start_time + n.duration for n in notes)
            bars = total_duration / 4  # Assuming 4/4
        else:
            bars = 0
            
        result = {
            "key": key,
            "mode": mode,
            "confidence": confidence,
            "note_length": note_length,
            "lowest_note": midi_note_to_name(lowest),
            "highest_note": midi_note_to_name(highest),
            "num_notes": len(notes),
            "bars": bars,
            "pitch_histogram": histogram,
        }
        
        if print_results:
            print(f"\n{'='*50}")
            print("Analysis Results")
            print(f"{'='*50}")
            print(f"Detected Key: {key} {mode}")
            print(f"Confidence: {confidence:.2%}")
            print(f"Note Length: {note_length}")
            print(f"Bars: {bars:.1f}")
            print(f"Pitch Range: {result['lowest_note']} - {result['highest_note']}")
            print(f"Total Notes: {len(notes)}")
            print(f"{'='*50}")
            
        return result


if __name__ == "__main__":
    # Test with a simple example
    from core.melody_generator import Note
    
    # Create some test notes in C major
    test_notes = [
        Note(pitch=60, start_time=0, duration=1, velocity=100),  # C
        Note(pitch=64, start_time=1, duration=1, velocity=100),  # E
        Note(pitch=67, start_time=2, duration=1, velocity=100),  # G
        Note(pitch=65, start_time=3, duration=1, velocity=100),  # F
    ]
    
    result = ChordAnalyzer.full_analysis(test_notes)
    print(f"\nDetected: {result['key']} {result['mode']}")
