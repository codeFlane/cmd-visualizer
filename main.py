from time import sleep, time
from click import command, option
import sys

from lib import *

def draw_bar(volume, width):
    """Return a string representation of the volume as a bar."""
    return '#' * min(round(volume), width) + '-' * round(width - volume)

@command()
@option('--reverse', is_flag=True, help='Reverse bands')
@option('--show-stats', is_flag=True, help='Show statistics (delay/min/avg/max)')
@option('--disable-fill-dead', is_flag=True, help='Disable fill dead bands funcion')
@option('--highlight-dead', is_flag=True, help='Highlight dead bands')
@option('-s', '--size', default='150:10', help='Visual size of bars in WIDTH:HEIGHT format.')
@option('-d', '--delay', default=0.005, help='Delay between screen updates (in seconds).')
@option('-m', '--multiplier', default=1, help='Multiplier applied to raw volume levels before drawing.')
@option('-b', '--block-size', default=2048, help='Block size for FFT.')
@option('--samplerate', default=44100, help='Sampling rate in Hz.')
def main(reverse, show_stats, disable_fill_dead, highlight_dead, size, delay, multiplier, block_size, samplerate):
    width = int(size.split(':')[0])
    height = int(size.split(':')[1])
    init(height)
    print('\n' * (height)) #clear terminal

    rec = get_device()
    with get_recorder(rec, samplerate, block_size) as device:
        while True:
            start = time()
            rec_data = record(device, samplerate, block_size)
            if disable_fill_dead:
                _, filled = fill_dead_bands(rec_data)
            else:
                rec_data, filled = fill_dead_bands(rec_data)
            if reverse:
                rec_data.reverse()
            end = time()
            bars = []

            for i, volume in enumerate(rec_data):
                is_filled = i in filled
                bar = draw_bar(volume * multiplier, width)
                if is_filled and highlight_dead:
                    bars.append(f"\033[K\033[1m[{bar}]\033[0m\n")
                else:
                    bars.append(f"\033[K[{bar}]\n")
            bars = ''.join(bars)
            stats = (
                f'\033[KDelay: {end - start:.3f}s | '
                f'Min: {to_db(min([rec for rec in rec_data if rec > 0.0]) if [rec for rec in rec_data if rec > 0.0] else '-inf'):.3f}dB | '
                f'Avg: {to_db(sum(rec_data) / len(rec_data)):.3f}dB | '
                f'Max: {to_db(max(rec_data)):.3f}dB\n'
            )
            sys.stdout.write(f'\033[{height + int(show_stats)}A{bars}{stats if show_stats else ''}')
            # sys.stdout.flush()
            if end - start - delay > 0:
                sleep(end - start - delay)

if __name__ == '__main__':
    main()