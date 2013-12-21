#!/usr/bin/env python3

"""Command line utility for evaluating song entropy"""

# file I/O
import wave
import struct

# math & plotting
from numpy.fft import fft, fftfreq
import math
from pylab import *

# documentation
from api_docs import command, parse_args, help


@command
def get_shannon_rel_entropy(file_name, down_sample=1, blah=2, foo='bar'):
    """Get ratio of the song's entropy to the entropy of the Uniform
    distribution
    """
    wr = wave.open(file_name, 'r')

    song = _time_data(wr)

    print("ffting")

    song_fft = fft(song)

    print(_shannon_rel_entropy(song_fft))

@command
def plot(domain, file_name, down_sample=1):
    """Plot .wav file over time or frequency.
    
    Parameters:
        <domain> can be 'time' or 'freq'. 'freq' plots the magnitudes of
        the Fast Fourier Transform of the .wav data.

    """
    if "time" in domain:
        _plot_time(file_name, down_sample=down_sample)
    if "freq" in domain:
        _plot_freq(file_name, down_sample=down_sample)

 
def _plot_time(file_name, down_sample=1):

    try:
        down_sample = int(down_sample)
    except TypeError:
        print("argument down_sample must be int")
        raise SystemExit
    wr = wave.open(file_name, 'r')
    song = _time_data(wr, down_sample=down_sample)
    num_frames = wr.getnframes()
    frame_rate = wr.getframerate()

    t = arange(0.0, num_frames / frame_rate, down_sample / frame_rate)
    
    plot(t, song)

    xlabel('time (s)')
    ylabel('amplitude (maximum 2^8, minimum -2^8)')
    title('Amplitude of track {} over time'.format(file_name))
    grid(True)
    # savefig("{}.png".format(file_name[:-4]))
    show()

def _plot_frequencies(file_name, down_sample=1):
    try:
        down_sample = int(down_sample)
    except TypeError:
        print("argument down_sample must be int")
        raise SystemExit

    wr = wave.open(file_name, 'r')
    song = _time_data(wr, down_sample=down_sample)
    frequencies = fftfreq(len(song), 1 / wr.getframerate())
    
    bar(frequencies, [abs(z) for z in fft(song)])
    title('Amplitudes of frequencies of track {}'.format(file_name))

    show()

@command
def get_wav_info(file_name):
    """Print meta-info about .wav file.

    Output:
        sample width (in bytes)
        frame rate (in Hz)
        num frames
        track length (in seconds)
        num channels
    """
    wr = wave.open(file_name, 'r')
    sample_width = wr.getsampwidth()
    frame_rate = wr.getframerate()
    num_frames = wr.getnframes()
    n_channels = wr.getnchannels()
    print("sample width: {} bytes".format(sample_width))
    print("frame rate: {} Hz".format(frame_rate))
    print("num frames: {}".format(num_frames))
    print("track length: {} s".format(num_frames / frame_rate))
    print("num channels: {}".format(n_channels))


def _time_data(wr, down_sample=1, max_frames=None):
    # expects wav file object opened for reading

    sample_width = wr.getsampwidth()
    frame_rate = wr.getframerate()
    n_frames = max_frames if max_frames else wr.getnframes()
    n_channels = wr.getnchannels()
    if n_channels != 2 or sample_width != 2 or frame_rate != 44100:
        print("Wrong sample width or frame rate")
        get_wav_info(wr)
        raise SystemExit

    song = []

    for i in range(int(n_frames / down_sample)):
        wave_data = wr.readframes(1)
        wr.setpos(down_sample * i)

        data = struct.unpack("<hh", wave_data)

        song.append((data[0] + data[1]) / 2)

    return song

def _shannon_rel_entropy(song_fft):
    return _entropy(song_fft) / math.log(len(song_fft), 2)

def _entropy(song_fft):
    # normalize the fft
    total_weight = sum([abs(z) for z in song_fft])
    song_entropy = 0
    p_x_sum = 0
    for z in song_fft:
        p_x = (abs(z)/total_weight)
        p_x_sum += p_x
        song_entropy += p_x * math.log(1/p_x, 2)

    return song_entropy

if __name__ == '__main__':
    parse_args()
