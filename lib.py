from soundcard import get_microphone, default_speaker, SoundcardRuntimeWarning, default_microphone
import numpy as np
from math import log10
from warnings import filterwarnings

filterwarnings("ignore", category=SoundcardRuntimeWarning)

def to_db(x):
    return 20 * log10(max(x, 1e-10))

def init(bands_count, min=50, max=16000):
    """Init lib (calc bands)"""
    global bands
    freq_edges = np.logspace(np.log10(min), np.log10(max), bands_count + 1)
    bands = [(freq_edges[i], freq_edges[i + 1]) for i in range(bands_count)]
    # for i, (fmin, fmax) in enumerate(bands):
    #     print(f"Band {i+1}: {fmin:.0f}-{fmax:.0f} Hz")
    # sleep(3)

def fill_dead_bands(data):
    filled_indices = []
    data = data[:]
    n = len(data)

# === 1. Leading dead bands ===
    i = 0
    while i < n and data[i] == 0:
        i += 1
    if i > 0 and i < n:
        target = data[i]
        if i == 1:
            data[0] = target / 2
            filled_indices.append(0)
        else:
            for j in range(i):
                data[j] = target * (j + 1) / i
                filled_indices.append(j)

    # === 2. Middle dead bands ===
    i = 0
    while i < n:
        if data[i] == 0:
            start = i
            while i < n and data[i] == 0:
                i += 1
            end = i
            if start > 0 and end < n:
                left = data[start - 1]
                right = data[end]
                for j, k in enumerate(range(start, end), 1):
                    data[k] = left + (right - left) * j / (end - start + 1)
                    filled_indices.append(k)
        else:
            i += 1

    # === 3. Trailing dead bands ===
    i = n - 1
    while i >= 0 and data[i] == 0:
        i -= 1
    if i < n - 1 and i >= 0:
        target = data[i]
        count = n - 1 - i
        for j in range(1, count + 1):
            data[i + j] = target * (count - j + 1) / count
            filled_indices.append(i + j)

    return data, filled_indices

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