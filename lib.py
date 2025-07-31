from soundcard import get_microphone, default_speaker, SoundcardRuntimeWarning, default_microphone
import numpy as np
#from time import sleep
from warnings import filterwarnings

filterwarnings("ignore", category=SoundcardRuntimeWarning)

def init(bands_count, min=50, max=16000):
    """init lib (calc bands)"""
    global bands
    freq_edges = np.logspace(np.log10(min), np.log10(max), bands_count + 1)
    bands = [(freq_edges[i], freq_edges[i + 1]) for i in range(bands_count)]
    # for i, (fmin, fmax) in enumerate(bands):
    #     print(f"Band {i+1}: {fmin:.0f}-{fmax:.0f} Hz")
    # sleep(3)

def band_volume(freqs, mags, fmin, fmax):
    """Calculate the mean magnitude in the given frequency band."""
    idx = np.where((freqs >= fmin) & (freqs <= fmax))[0]
    return np.mean(mags[idx]) if len(idx) > 0 else 0

def get_device(speaker=True):
    return get_microphone(id=str(default_speaker().name if speaker else default_microphone().name), include_loopback=True)

def get_recorder(mic, samplerate=44100, block_size=4096):
    return mic.recorder(samplerate=samplerate, blocksize=block_size)

def record(device, samplerate=44100, block_size=4096):
    data = device.record(numframes=block_size)
    data = data.mean(axis=1)

    windowed = data * np.hanning(len(data))
    fft = np.fft.rfft(windowed)
    freqs = np.fft.rfftfreq(len(data), 1 / samplerate)
    mags = np.abs(fft)
    return [band_volume(freqs, mags, fmin, fmax) for fmin, fmax in bands]