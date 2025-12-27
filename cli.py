"""
Interactive CLI for Melody & Harmony Generator v2
Supports four operation modes: Create, Analyze, Harmonize, Continue
"""

import os
import sys

# Handle inquirer import with fallback
try:
    import inquirer
    from inquirer.themes import GreenPassion
    HAS_INQUIRER = True
except ImportError:
    HAS_INQUIRER = False
    print("Note: inquirer library not installed. Using simple input mode.")
    print("For better experience, install with: pip install inquirer\n")

# Add project root to path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from config.music_config import (
    KEY_NAMES, MODES, NOTE_LENGTHS, BAR_OPTIONS,
    TIME_SIGNATURES, GENERATION_TYPES, CHORD_PROGRESSIONS,
    DEFAULT_TEMPO, TEMPO_RANGE, MOODS, STYLES, OPERATION_MODES, ALGORITHMS
)
from core.scale_generator import ScaleGenerator
from core.melody_generator import MelodyGenerator
from core.harmony_generator import HarmonyGenerator
from core.midi_exporter import MidiExporter, generate_filename


def print_banner():
    """Print the application banner."""
    banner = """
╔══════════════════════════════════════════════════════════════════╗
║                                                                  ║
║     🎵  MELODY & HARMONY GENERATOR v2  🎵                       ║
║                                                                  ║
║     Generate melodies, bass lines, pads, and harmonies          ║
║     with mood, style, and multiple operation modes              ║
║                                                                  ║
╚══════════════════════════════════════════════════════════════════╝
"""
    print(banner)


def get_user_input_inquirer() -> dict:
    """Get user input using inquirer selectors."""
    
    # First ask for operation mode
    mode_question = [
        inquirer.List(
            'operation_mode',
            message="Operation Mode",
            choices=[f"{k}: {v}" for k, v in OPERATION_MODES.items()],
            default='create: Create from scratch'
        ),
    ]
    mode_answer = inquirer.prompt(mode_question, theme=GreenPassion())
    if not mode_answer:
        return None
        
    operation_mode = mode_answer['operation_mode'].split(':')[0].strip()
    
    # If import modes, ask for file
    input_file = None
    if operation_mode in ['analyze', 'harmonize', 'continue']:
        file_question = [
            inquirer.Path(
                'input_file',
                message="Path to MIDI file to import",
                path_type=inquirer.Path.FILE,
                exists=True
            ),
        ]
        file_answer = inquirer.prompt(file_question, theme=GreenPassion())
        if not file_answer:
            return None
        input_file = file_answer['input_file']
        
        # For analyze mode, we don't need other params
        if operation_mode == 'analyze':
            return {
                'operation_mode': operation_mode,
                'input_file': input_file,
            }
    
    questions = [
        inquirer.List(
            'algorithm',
            message="Melody Algorithm",
            choices=[f"{k}: {v}" for k, v in ALGORITHMS.items()],
            default='markov: Markov Chain (learned patterns, more musical)'
        ),
        inquirer.List(
            'mood',
            message="Select Mood",
            choices=['None'] + list(MOODS.keys()),
            default='None'
        ),
        inquirer.List(
            'style',
            message="Select Style",
            choices=['None'] + list(STYLES.keys()),
            default='None'
        ),
    ]
    
    # Only ask for key/mode if creating from scratch
    if operation_mode == 'create':
        questions.extend([
            inquirer.List(
                'key',
                message="Select Key",
                choices=KEY_NAMES,
                default='C'
            ),
            inquirer.List(
                'mode',
                message="Select Mode/Scale",
                choices=list(MODES.keys()),
                default='Ionian (Major)'
            ),
        ])
    
    questions.extend([
        inquirer.List(
            'bars',
            message="Number of Bars" + (" to add" if operation_mode == 'continue' else ""),
            choices=BAR_OPTIONS,
            default=8 if operation_mode == 'create' else 4
        ),
        inquirer.List(
            'note_length',
            message="Base Note Length",
            choices=list(NOTE_LENGTHS.keys()),
            default='Eighth'
        ),
        inquirer.List(
            'time_signature',
            message="Time Signature",
            choices=list(TIME_SIGNATURES.keys()),
            default='4/4'
        ),
        inquirer.List(
            'gen_type',
            message="Generation Type",
            choices=[f"{k}: {v}" for k, v in GENERATION_TYPES.items()],
            default='lead: Lead Melody'
        ),
        inquirer.List(
            'progression',
            message="Chord Progression",
            choices=['Auto/Random'] + list(CHORD_PROGRESSIONS.keys()),
            default='Auto/Random' if operation_mode != 'create' else 'I-V-vi-IV'
        ),
        inquirer.Text(
            'tempo',
            message=f"Tempo (BPM, {TEMPO_RANGE[0]}-{TEMPO_RANGE[1]})",
            default=str(DEFAULT_TEMPO),
            validate=lambda _, x: x.isdigit() and TEMPO_RANGE[0] <= int(x) <= TEMPO_RANGE[1]
        ),
    ])
    
    answers = inquirer.prompt(questions, theme=GreenPassion())
    
    if answers is None:
        return None
        
    # Parse and combine answers
    answers['operation_mode'] = operation_mode
    answers['input_file'] = input_file
    answers['gen_type'] = answers['gen_type'].split(':')[0].strip()
    answers['tempo'] = int(answers['tempo'])
    answers['time_sig_tuple'] = TIME_SIGNATURES[answers['time_signature']]
    
    if answers['progression'] == 'Auto/Random':
        answers['progression'] = None
    if answers['mood'] == 'None':
        answers['mood'] = None
    if answers['style'] == 'None':
        answers['style'] = None
    answers['algorithm'] = answers.get('algorithm', 'markov: Markov').split(':')[0].strip()
        
    return answers


def get_user_input_simple() -> dict:
    """Get user input using simple text prompts as fallback."""
    print("\n--- Configuration ---\n")
    
    # Operation mode
    op_modes = list(OPERATION_MODES.items())
    print("Operation Modes:")
    for i, (key, desc) in enumerate(op_modes, 1):
        print(f"  {i}. {key}: {desc}")
    op_idx = input("Select mode [1]: ").strip() or '1'
    try:
        operation_mode = op_modes[int(op_idx) - 1][0]
    except (ValueError, IndexError):
        operation_mode = 'create'
    
    input_file = None
    if operation_mode in ['analyze', 'harmonize', 'continue']:
        input_file = input("Path to MIDI file: ").strip()
        if not os.path.exists(input_file):
            print(f"File not found: {input_file}")
            return None
            
        if operation_mode == 'analyze':
            return {'operation_mode': operation_mode, 'input_file': input_file}
    
    # Mood
    mood_list = ['None'] + list(MOODS.keys())
    print(f"\nMoods:")
    for i, m in enumerate(mood_list, 1):
        print(f"  {i}. {m}")
    mood_idx = input("Select Mood [1]: ").strip() or '1'
    try:
        mood = mood_list[int(mood_idx) - 1]
        if mood == 'None':
            mood = None
    except (ValueError, IndexError):
        mood = None
    
    # Style
    style_list = ['None'] + list(STYLES.keys())
    print(f"\nStyles:")
    for i, s in enumerate(style_list, 1):
        print(f"  {i}. {s}")
    style_idx = input("Select Style [1]: ").strip() or '1'
    try:
        style = style_list[int(style_idx) - 1]
        if style == 'None':
            style = None
    except (ValueError, IndexError):
        style = None
    
    # Key and mode (only for create)
    if operation_mode == 'create':
        print(f"\nAvailable keys: {', '.join(KEY_NAMES)}")
        key = input("Select Key [C]: ").strip().upper() or 'C'
        if key not in KEY_NAMES:
            key = 'C'
        
        mode_list = list(MODES.keys())
        print(f"\nModes:")
        for i, mode in enumerate(mode_list, 1):
            print(f"  {i}. {mode}")
        mode_idx = input("Select Mode [1]: ").strip() or '1'
        try:
            mode = mode_list[int(mode_idx) - 1]
        except (ValueError, IndexError):
            mode = mode_list[0]
    else:
        key = 'C'
        mode = 'Ionian (Major)'
    
    # Bars
    print(f"\nBar options: {BAR_OPTIONS}")
    bars = input("Number of Bars [8]: ").strip() or '8'
    bars = int(bars) if bars.isdigit() and int(bars) in BAR_OPTIONS else 8
    
    # Note length
    note_lengths = list(NOTE_LENGTHS.keys())
    print(f"\nNote lengths:")
    for i, nl in enumerate(note_lengths, 1):
        print(f"  {i}. {nl}")
    nl_idx = input("Select Note Length [6]: ").strip() or '6'
    try:
        note_length = note_lengths[int(nl_idx) - 1]
    except (ValueError, IndexError):
        note_length = 'Eighth'
    
    # Time signature
    time_sigs = list(TIME_SIGNATURES.keys())
    print(f"\nTime signatures: {time_sigs}")
    time_sig = input("Time Signature [4/4]: ").strip() or '4/4'
    if time_sig not in TIME_SIGNATURES:
        time_sig = '4/4'
    
    # Generation type
    gen_types = list(GENERATION_TYPES.items())
    print(f"\nGeneration types:")
    for i, (k, name) in enumerate(gen_types, 1):
        print(f"  {i}. {k}: {name}")
    gt_idx = input("Select Generation Type [1]: ").strip() or '1'
    try:
        gen_type = gen_types[int(gt_idx) - 1][0]
    except (ValueError, IndexError):
        gen_type = 'lead'
    
    # Chord progression
    prog_list = ['Auto/Random'] + list(CHORD_PROGRESSIONS.keys())
    print(f"\nChord progressions:")
    for i, prog in enumerate(prog_list, 1):
        print(f"  {i}. {prog}")
    prog_idx = input("Select Progression [1]: ").strip() or '1'
    try:
        progression = prog_list[int(prog_idx) - 1]
        if progression == 'Auto/Random':
            progression = None
    except (ValueError, IndexError):
        progression = None
    
    # Tempo
    tempo = input(f"\nTempo [{DEFAULT_TEMPO}]: ").strip()
    try:
        tempo = int(tempo)
        if not TEMPO_RANGE[0] <= tempo <= TEMPO_RANGE[1]:
            tempo = DEFAULT_TEMPO
    except ValueError:
        tempo = DEFAULT_TEMPO
    
    return {
        'operation_mode': operation_mode,
        'input_file': input_file,
        'key': key,
        'mode': mode,
        'bars': bars,
        'note_length': note_length,
        'time_signature': time_sig,
        'time_sig_tuple': TIME_SIGNATURES[time_sig],
        'gen_type': gen_type,
        'progression': progression,
        'tempo': tempo,
        'mood': mood,
        'style': style,
        'algorithm': 'markov',
    }


def handle_analyze_mode(input_file: str) -> dict:
    """Analyze a MIDI file and return detected parameters."""
    from core.midi_parser import MidiParser
    from core.chord_analyzer import ChordAnalyzer
    
    print(f"\n⏳ Analyzing {input_file}...")
    
    parser = MidiParser(input_file)
    notes = parser.get_notes()
    
    if not notes:
        print("❌ No notes found in MIDI file")
        return None
    
    # Run full analysis
    result = ChordAnalyzer.full_analysis(notes, print_results=True)
    
    # Print additional info
    parser.print_info()
    
    return result


def handle_harmonize_mode(config: dict) -> str:
    """Add harmony parts to an imported chord progression."""
    from core.midi_parser import MidiParser
    from core.chord_analyzer import ChordAnalyzer
    
    input_file = config['input_file']
    print(f"\n⏳ Harmonizing {input_file}...")
    
    parser = MidiParser(input_file)
    notes = parser.get_notes()
    
    if not notes:
        print("❌ No notes found in MIDI file")
        return None
    
    # Detect key and mode
    histogram = {i: 0 for i in range(12)}
    for note in notes:
        histogram[note.pitch % 12] += note.duration
    
    detected_key, detected_mode, _ = ChordAnalyzer.detect_key(histogram)
    print(f"Detected: {detected_key} {detected_mode}")
    
    # Use detected key/mode or override from config
    key = config.get('key', detected_key)
    mode = config.get('mode', detected_mode)
    
    # Create generators
    melody_gen = MelodyGenerator(key, mode, config['tempo'])
    harmony_gen = HarmonyGenerator(key, mode, config['tempo'])
    exporter = MidiExporter(config['tempo'], config['time_sig_tuple'])
    
    # Calculate bars from imported notes
    bars = int(parser.get_duration_in_bars()) or 4
    
    # Generate harmony parts
    harmony = harmony_gen.generate_full_harmony(
        bars=bars,
        note_length=config['note_length'],
        time_signature=config['time_sig_tuple'],
        progression_name=config['progression']
    )
    
    # Print and export
    title = f"Harmonized: {key} {mode} ({bars} bars)"
    exporter.print_notes_to_terminal(harmony, title)
    
    output_path = generate_filename('harmonized', key, mode, bars)
    path = exporter.export_multi_track(harmony, output_path)
    
    return path


def handle_continue_mode(config: dict) -> str:
    """Continue/extend an existing MIDI file."""
    from core.midi_parser import MidiParser
    from core.chord_analyzer import ChordAnalyzer
    
    input_file = config['input_file']
    print(f"\n⏳ Continuing {input_file} with {config['bars']} more bars...")
    
    parser = MidiParser(input_file)
    existing_notes = parser.get_notes()
    
    if not existing_notes:
        print("❌ No notes found in MIDI file")
        return None
    
    # Detect key and mode
    histogram = parser.get_pitch_histogram()
    detected_key, detected_mode, _ = ChordAnalyzer.detect_key(histogram)
    print(f"Detected: {detected_key} {detected_mode}")
    
    key = detected_key
    mode = detected_mode
    
    # Create generators
    melody_gen = MelodyGenerator(key, mode, config['tempo'])
    exporter = MidiExporter(config['tempo'], config['time_sig_tuple'])
    
    # Generate continuation
    new_notes = melody_gen.continue_melody(
        existing_notes=existing_notes,
        bars_to_add=config['bars'],
        note_length=config['note_length'],
        mood=config.get('mood'),
        style=config.get('style')
    )
    
    # Combine original and new notes
    all_notes = existing_notes + new_notes
    
    # Print new notes
    title = f"Continuation: {key} {mode} (+{config['bars']} bars)"
    exporter.print_notes_to_terminal({'new_notes': new_notes}, title)
    
    # Export combined
    total_bars = int(parser.get_duration_in_bars()) + config['bars']
    output_path = generate_filename('continued', key, mode, total_bars)
    path = exporter.export_single_track(all_notes, output_path, track_name="Continued Melody")
    
    return path


def handle_create_mode(config: dict) -> str:
    """Generate music from scratch (original behavior)."""
    key = config['key']
    mode = config['mode']
    bars = config['bars']
    note_length = config['note_length']
    time_sig = config['time_sig_tuple']
    gen_type = config['gen_type']
    progression = config['progression']
    tempo = config['tempo']
    mood = config.get('mood')
    style = config.get('style')
    
    # Create generators
    melody_gen = MelodyGenerator(key, mode, tempo)
    harmony_gen = HarmonyGenerator(key, mode, tempo)
    exporter = MidiExporter(tempo, time_sig)
    
    # Generate based on type
    mood_str = f" [{mood}]" if mood else ""
    style_str = f" [{style}]" if style else ""
    algo = config.get('algorithm', 'markov')
    algo_str = f" ({algo})" if algo else ""
    print(f"\n⏳ Generating {GENERATION_TYPES[gen_type]}{mood_str}{style_str}{algo_str}...")
    
    if gen_type == 'lead':
        if algo == 'markov':
            from core.markov_generator import MarkovMelodyGenerator
            markov_gen = MarkovMelodyGenerator(key, mode, tempo)
            notes = markov_gen.generate(bars, note_length, time_sig, 
                                        mood=mood, style=style)
        else:
            notes = melody_gen.generate_lead(bars, note_length, time_sig, 
                                             mood=mood, style=style)
        track_data = notes
        
    elif gen_type == 'bass':
        prog = CHORD_PROGRESSIONS.get(progression) if progression else None
        notes = melody_gen.generate_bass(bars, note_length, time_sig, prog)
        track_data = notes
        
    elif gen_type == 'pad':
        prog = CHORD_PROGRESSIONS.get(progression) if progression else None
        notes = melody_gen.generate_pad(bars, note_length, time_sig, prog)
        track_data = notes
        
    elif gen_type == 'hook':
        from core.hook_generator import HookGenerator
        hook_gen = HookGenerator(key, mode, tempo)
        notes = hook_gen.generate(bars, note_length, time_sig, 
                                  mood=mood, style=style)
        track_data = notes
        
    else:  # harmony
        harmony = harmony_gen.generate_full_harmony(
            bars, note_length, time_sig, progression
        )
        track_data = harmony
    
    # Print to terminal
    title = f"{key} {mode} - {GENERATION_TYPES[gen_type]} ({bars} bars)"
    
    if isinstance(track_data, dict):
        exporter.print_notes_to_terminal(track_data, title)
    else:
        exporter.print_notes_to_terminal({gen_type: track_data}, title)
    
    # Export to MIDI
    output_path = generate_filename(gen_type, key, mode, bars)
    
    if isinstance(track_data, dict):
        path = exporter.export_multi_track(track_data, output_path)
    else:
        path = exporter.export_single_track(track_data, output_path, 
                                           track_name=GENERATION_TYPES[gen_type])
    
    return path


def run_cli():
    """Main CLI loop."""
    print_banner()
    
    while True:
        # Get user input
        if HAS_INQUIRER:
            config = get_user_input_inquirer()
        else:
            config = get_user_input_simple()
            
        if config is None:
            print("\n👋 Goodbye!")
            break
            
        try:
            operation = config.get('operation_mode', 'create')
            
            if operation == 'analyze':
                handle_analyze_mode(config['input_file'])
                output_path = None
            elif operation == 'harmonize':
                output_path = handle_harmonize_mode(config)
            elif operation == 'continue':
                output_path = handle_continue_mode(config)
            else:  # create
                output_path = handle_create_mode(config)
            
            if output_path:
                print(f"\n✅ Successfully exported to:")
                print(f"   📁 {output_path}")
            
        except Exception as e:
            print(f"\n❌ Error: {e}")
            import traceback
            traceback.print_exc()
        
        # Ask to continue
        print()
        if HAS_INQUIRER:
            continue_q = [
                inquirer.Confirm('continue', 
                                message="Run again?", 
                                default=True)
            ]
            result = inquirer.prompt(continue_q)
            if not result or not result['continue']:
                print("\n👋 Goodbye!")
                break
        else:
            again = input("Run again? [Y/n]: ").strip().lower()
            if again == 'n':
                print("\n👋 Goodbye!")
                break


if __name__ == "__main__":
    run_cli()
