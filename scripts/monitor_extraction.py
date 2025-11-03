"""
Live progress monitor for BIA extraction.
Shows real-time progress bar and statistics.
"""

import time
import os
from pathlib import Path
import re
from datetime import datetime, timedelta

LOG_FILE = Path("bia_extraction_FINAL.log")
PID = 56072

def clear_screen():
    """Clear terminal screen."""
    os.system('clear' if os.name == 'posix' else 'cls')

def check_process(pid):
    """Check if process is running."""
    try:
        os.kill(pid, 0)
        return True
    except OSError:
        return False

def parse_log():
    """Parse extraction log for progress."""
    if not LOG_FILE.exists():
        return None

    with open(LOG_FILE, 'r') as f:
        log_content = f.read()

    # Find chunks started and completed
    chunks_started = re.findall(r'Chunk (\d+)/8:', log_content)
    completions = re.findall(r'✓ Extracted\s+(\d+)\s+entities', log_content)
    errors = re.findall(r'✗ Error', log_content)
    categories = re.findall(r'CATEGORY \d+/3: (\w+)', log_content)

    return {
        'chunks_started': len(set(chunks_started)),
        'chunks_completed': len(completions),
        'total_entities': sum(int(c) for c in completions),
        'errors': len(errors),
        'current_category': categories[-1] if categories else 'Unknown',
        'last_chunk_entities': int(completions[-1]) if completions else 0
    }

def draw_progress_bar(current, total, width=40):
    """Draw a progress bar."""
    filled = int(width * current / total)
    bar = '█' * filled + '░' * (width - filled)
    percent = 100 * current / total
    return f'[{bar}] {percent:.1f}% ({current}/{total})'

def monitor():
    """Monitor extraction with live updates."""
    start_time = datetime.now()

    while True:
        clear_screen()

        # Header
        print('='*70)
        print('BIA EXTRACTION - LIVE PROGRESS MONITOR')
        print('='*70)
        print(f'Started: {start_time.strftime("%H:%M:%S")}')
        print(f'Current: {datetime.now().strftime("%H:%M:%S")}')
        print(f'Elapsed: {str(timedelta(seconds=int((datetime.now() - start_time).total_seconds())))}')
        print()

        # Check process
        is_running = check_process(PID)
        status_icon = '🟢' if is_running else '🔴'
        print(f'Process: {status_icon} {"RUNNING" if is_running else "STOPPED"} (PID {PID})')
        print()

        # Parse progress
        stats = parse_log()
        if stats:
            # Category progress
            print(f'Category: {stats["current_category"].upper()}')
            print()

            # Chunk progress
            print('Chunk Progress (Concepts):')
            print(draw_progress_bar(stats['chunks_completed'], 8))
            print(f'  Started: {stats["chunks_started"]}/8')
            print(f'  Completed: {stats["chunks_completed"]}/8')
            print()

            # Overall progress (3 categories × 8 chunks = 24 total)
            total_chunks = 24  # 8 chunks × 3 categories
            print('Overall Progress (All 3 Categories):')
            print(draw_progress_bar(stats['chunks_completed'], total_chunks))
            print()

            # Statistics
            print('Statistics:')
            print(f'  Total entities: {stats["total_entities"]:,}')
            print(f'  Last chunk: {stats["last_chunk_entities"]} entities')
            print(f'  Errors: {stats["errors"]}')
            print()

            # Estimates
            if stats['chunks_completed'] > 0:
                elapsed_sec = (datetime.now() - start_time).total_seconds()
                time_per_chunk = elapsed_sec / stats['chunks_completed']
                remaining_chunks = total_chunks - stats['chunks_completed']
                eta_sec = time_per_chunk * remaining_chunks
                eta = datetime.now() + timedelta(seconds=eta_sec)

                print('Estimates:')
                print(f'  Time per chunk: {int(time_per_chunk/60)} min {int(time_per_chunk%60)} sec')
                print(f'  Remaining time: {str(timedelta(seconds=int(eta_sec)))}')
                print(f'  ETA: {eta.strftime("%H:%M:%S")}')
        else:
            print('Waiting for log data...')

        print()
        print('='*70)
        print('Press Ctrl+C to exit monitor (extraction continues in background)')
        print('='*70)

        if not is_running:
            print('\n⚠️  Process stopped! Check log for errors.')
            break

        time.sleep(10)  # Update every 10 seconds

if __name__ == '__main__':
    try:
        monitor()
    except KeyboardInterrupt:
        print('\n\nMonitor stopped. Extraction continues in background.')
        print(f'To check status: tail -f {LOG_FILE}')
