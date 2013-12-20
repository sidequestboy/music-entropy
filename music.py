#!/usr/bin/env python3

import wave
import struct
from numpy.fft import fft
from numpy import array
import math

import sys
from functools import wraps
from pylab import *


def command(func, _funcs={}):
    """Decorate functions with this to register them as commands"""

    # register the command
    func_name = func.__name__.lower()
    if func_name in _funcs:
        raise Exception('Duplicate definition for command {}'.format(func_name))
    _funcs[func_name] = func

    # play nice and leave the command where it was in this script
    @wraps(func)
    def wrapped(*args):
        return func(*args)
    return wrapped

@command
def get_shannon_rel_entropy(file_name):
    wr = wave.open(file_name, 'r')

    song = time_data(wr)

    print("ffting")

    song_fft = fft(song)

    print(shannon_rel_entropy(song_fft))

@command
def get_mutual_info(file_1, file_2):
    wr_1 = wave.open(file_1, 'r')
    wr_2 = wave.open(file_2, 'r')
    # num_frames = min(wr_1.getframerate()*wr_1.getnframes(), 
    #                  wr_2.getframerate()*wr_2.getnframes())

    # for i in range(num_frames):
    #     wave_data_1 = wr_1.readframes(1)
    #     wave_data_2 = wr_2.readframes(1)

    #     data_1 = struct.unpack("<hh", wave_data_1)
    #     data_2 = struct.unpack("<hh", wave_data_2)

    #     song_1.append(data_1)
    #     song_2.append(data_2)

    song_1_fft = fft(time_data(wr_1))
    song_2_fft = fft(time_data(wr_2))

    mutual_info(song_1_fft, song_2_fft)



@command 
def plot_time(file_name, down_sample = 1):

    try:
        down_sample = int(down_sample)
    except Exception as e:
        raise SystemExit
    wr = wave.open(file_name, 'r')
    song = time_data(wr, down_sample=down_sample)
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

@command
def plot_frequencies(file_name, down_sample = 1):
    try:
        down_sample = int(down_sample)
    except Exception as e:
        raise SystemExit

    wr = wave.open(file_name, 'r')
    song = time_data(wr, down_sample=down_sample)
    num_frames = wr.getnframes()
    frame_rate = wr.getframerate()

    t = arange(0.0, num_frames / frame_rate, down_sample / frame_rate)
    
    plot(t, fft(song))

    xlabel('frequency (Hz)')
    ylabel('amplitude')
    title('Amplitude of track {} over time'.format(file_name))
    grid(True)
    # savefig("{}.png".format(file_name[:-4]))
    show()

@command
def get_wav_info(file_name):
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


def time_data(wr, down_sample=1, max_frames=None):
    # expects wav file object opened for reading

    sample_width = wr.getsampwidth()
    frame_rate = wr.getframerate()
    n_frames = wr.getnframes()
    n_channels = wr.getnchannels()
    if n_channels != 2 or sample_width != 2 or frame_rate != 44100:
        print("Wrong sample width or frame rate")
        get_wav_info(wr)
        raise SystemExit

    song = []

    for i in range(n_frames):
        wave_data = wr.readframes(1)
        if i % down_sample != 0:
            continue

        data = struct.unpack("<hh", wave_data)

        song.append((data[0] + data[1]) / 2)

    return song


def mutual_info(song_1_fft, song_2_fft):
    total_weight_1 = sum([abs(z) for z in song_1_fft])
    total_weight_2 = sum([abs(z) for z in song_2_fft])

    m_info = 0

    for z in song_1_fft:
        p_x = (abs(z)/total_weight)
        

def shannon_rel_entropy(song_fft):
    # normalize the fft
    total_weight = sum([abs(z) for z in song_fft])
    song_entropy = 0
    p_x_sum = 0
    for z in song_fft:
        p_x = (abs(z)/total_weight)
        p_x_sum += p_x
        song_entropy += p_x * math.log(1/p_x, 2)
    print(p_x_sum)

    return song_entropy / math.log(len(song_fft), 2)


"""
struct MyStruct {
    int Thing;
};
"""


@command
def help():
    """Get usage information about this script"""
    print('\nUsage: {} [command]\n'.format(sys.argv[0]))
    print('Available commands:')
    for name, func in command.__defaults__[0].items():  # _funcs={}
        print(' * {:16s} {}'.format(name, func.__doc__ or ''))
    raise SystemExit(1)

if __name__ == '__main__':

    # Get the command, or run 'help' if no command is provided
    if len(sys.argv) < 2:
        cmd, args = 'help', []
    else:
        cmd, args = sys.argv[1].lower(), sys.argv[2:]

    # Map the command to a function, falling back to 'help' if it's not found
    funcs = command.__defaults__[0]  # _funcs={}
    if cmd not in funcs:
        print('Command "{}" not found :('.format(cmd))
        cmd, args = 'help', []

    # do it!
    funcs[cmd](*args)