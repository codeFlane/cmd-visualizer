from time import sleep
from click import command, option
import sys

from lib import *

def draw_bar(volume, width):
    """Return a string representation of the volume as a bar."""
    return '#' * min(round(volume), width) + '-' * round(width - volume)

@command()
@option('-s', '--size', default='150:10', help='Visual size of bars in WIDTH:HEIGHT format.')
@option('-d', '--delay', default=0.005, help='Delay between screen updates (in seconds).')
@option('-m', '--multiplier', default=1, help='Multiplier applied to raw volume levels before drawing.\nHelps boost weak signals or fine-tune bar height.')
@option('-b', '--block-size', default=4096, help='''Size of audio data block (in samples) used for FFT analysis.\n
Controls frequency resolution and processing delay.\n
- Lower (1024–2048): faster updates but may cause dead bands.\n
- Higher (4096–8192): better accuracy but higher latency.\n
Recommended: 8192 — best balance of precision and responsiveness.''')
@option('--samplerate', default=44100, help='''Audio sampling rate in Hz. Determines max detectable frequency and frequency resolution.\n
- Lower (16000–22050): less CPU load, but reduced high-frequency detail.\n
- Higher (48000+): better precision, but increased latency and processing load.\n
Recommended: 44100 for general use, 22050 for low-frequency focus.''')
def main(size, delay, multiplier, block_size, samplerate):
    width = int(size.split(':')[0])
    height = int(size.split(':')[1])
    # print(width, height)
    # sleep(3)
    init(height)
    print('\n' * height) #clear terminal

    rec = get_device()
    with get_recorder(rec, samplerate, block_size) as device:
        while True:
            rec_data = record(device, samplerate, block_size)
            sys.stdout.write(
                f"\033[{height}A" +
                ''.join([f"\033[K[{draw_bar(v * multiplier, width)}]\n" for v in rec_data])
            )
            sleep(delay)

if __name__ == '__main__':
    main()