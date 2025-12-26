#!/usr/bin/env python3
"""
Melody & Harmony Generator v2
Main entry point for the application.

Features:
- Four operation modes: Create, Analyze, Harmonize, Continue
- Mood and style modifiers
- MIDI import and export

Usage:
    python main.py                      # Interactive CLI mode
    python main.py --quick              # Quick generation with defaults
    python main.py --mode analyze -i file.mid
    python main.py --help               # Show all options
"""

import argparse
import sys
import os

# Add project root to path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from config.music_config import (
    KEY_NAMES, MODES, NOTE_LENGTHS, BAR_OPTIONS,
    GENERATION_TYPES, CHORD_PROGRESSIONS, DEFAULT_TEMPO,
    MOODS, STYLES, OPERATION_MODES
)
from core.melody_generator import MelodyGenerator
from core.harmony_generator import HarmonyGenerator
from core.midi_exporter import MidiExporter, generate_filename
from cli import (run_cli, print_banner, handle_analyze_mode, 
                 handle_harmonize_mode, handle_continue_mode, handle_create_mode)


def quick_generate(args):
    """Quick generation with command line arguments."""
    config = {
        'operation_mode': args.mode,
        'input_file': args.input,
        'key': args.key,
        'mode': args.scale,
        'bars': args.bars,
        'note_length': args.note_length,
        'time_signature': '4/4',
        'time_sig_tuple': (4, 4),
        'gen_type': args.type,
        'progression': args.progression if args.progression != 'random' else None,
        'tempo': args.tempo,
        'mood': args.mood if args.mood != 'none' else None,
        'style': args.style if args.style != 'none' else None,
    }
    
    print_banner()
    
    try:
        if args.mode == 'analyze':
            if not args.input:
                print("❌ Error: --input required for analyze mode")
                return
            handle_analyze_mode(args.input)
            
        elif args.mode == 'harmonize':
            if not args.input:
                print("❌ Error: --input required for harmonize mode")
                return
            path = handle_harmonize_mode(config)
            if path:
                print(f"\n✅ Exported to: {path}")
                
        elif args.mode == 'continue':
            if not args.input:
                print("❌ Error: --input required for continue mode")
                return
            path = handle_continue_mode(config)
            if path:
                print(f"\n✅ Exported to: {path}")
                
        else:  # create
            path = handle_create_mode(config)
            if path:
                print(f"\n✅ Exported to: {path}")
                
    except Exception as e:
        print(f"\n❌ Error: {e}")
        import traceback
        traceback.print_exc()


def test_mode():
    """Run comprehensive tests."""
    print_banner()
    print("Running test mode...\n")
    
    # Test create mode with different moods/styles
    test_configs = [
        {'mood': 'happy', 'style': 'pop', 'type': 'lead'},
        {'mood': 'dark', 'style': 'synthwave', 'type': 'lead'},
        {'mood': 'calm', 'style': 'ambient', 'type': 'pad'},
        {'mood': 'energetic', 'style': 'edm', 'type': 'harmony'},
    ]
    
    for cfg in test_configs:
        config = {
            'operation_mode': 'create',
            'key': 'C',
            'mode': 'Aeolian (Minor)' if cfg['mood'] in ['dark', 'sad'] else 'Ionian (Major)',
            'bars': 4,
            'note_length': 'Eighth',
            'time_signature': '4/4',
            'time_sig_tuple': (4, 4),
            'gen_type': cfg['type'],
            'progression': None,
            'tempo': 120,
            'mood': cfg['mood'],
            'style': cfg['style'],
        }
        
        print(f"\n{'='*60}")
        print(f"Testing: {cfg['mood']} {cfg['style']} {cfg['type']}")
        print(f"{'='*60}")
        
        try:
            path = handle_create_mode(config)
            print(f"✅ {path}")
        except Exception as e:
            print(f"❌ Error: {e}")
    
    print("\n✅ Test mode complete!")


def main():
    """Main entry point."""
    parser = argparse.ArgumentParser(
        description="Generate melodies and harmonies based on music theory",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Interactive mode
  python main.py
  
  # Quick create with mood and style
  python main.py --quick -k G -s Dorian -b 8 --mood happy --style pop
  
  # Analyze a MIDI file
  python main.py --mode analyze -i song.mid
  
  # Harmonize imported chords
  python main.py --mode harmonize -i chords.mid --mood dreamy --style ambient
  
  # Continue an existing melody
  python main.py --mode continue -i melody.mid -b 4 --mood energetic
  
  # Full harmony with specific progression
  python main.py --quick -t harmony -p I-V-vi-IV --style synthwave
        """
    )
    
    parser.add_argument('--quick', '-q', action='store_true',
                       help='Quick generate (non-interactive)')
    parser.add_argument('--mode', '-m', type=str, default='create',
                       choices=list(OPERATION_MODES.keys()),
                       help='Operation mode (default: create)')
    parser.add_argument('--input', '-i', type=str,
                       help='Input MIDI file (for analyze/harmonize/continue)')
    parser.add_argument('--key', '-k', type=str, default='C',
                       choices=KEY_NAMES,
                       help='Musical key (default: C)')
    parser.add_argument('--scale', '-s', type=str, default='Ionian (Major)',
                       choices=list(MODES.keys()),
                       help='Scale mode (default: Ionian)')
    parser.add_argument('--bars', '-b', type=int, default=8,
                       choices=BAR_OPTIONS,
                       help='Number of bars (default: 8)')
    parser.add_argument('--note-length', '-n', type=str, default='Eighth',
                       choices=list(NOTE_LENGTHS.keys()),
                       help='Base note length (default: Eighth)')
    parser.add_argument('--type', '-t', type=str, default='lead',
                       choices=list(GENERATION_TYPES.keys()),
                       help='Generation type (default: lead)')
    parser.add_argument('--tempo', type=int, default=DEFAULT_TEMPO,
                       help=f'Tempo in BPM (default: {DEFAULT_TEMPO})')
    parser.add_argument('--progression', '-p', type=str, default='random',
                       choices=['random'] + list(CHORD_PROGRESSIONS.keys()),
                       help='Chord progression (default: random)')
    parser.add_argument('--mood', type=str, default='none',
                       choices=['none'] + list(MOODS.keys()),
                       help='Mood modifier (default: none)')
    parser.add_argument('--style', type=str, default='none',
                       choices=['none'] + list(STYLES.keys()),
                       help='Style modifier (default: none)')
    parser.add_argument('--test-mode', action='store_true',
                       help='Run comprehensive tests')
    
    args = parser.parse_args()
    
    if args.test_mode:
        test_mode()
    elif args.quick or args.mode != 'create' or args.input:
        quick_generate(args)
    else:
        run_cli()


if __name__ == "__main__":
    main()
