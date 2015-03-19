#!/usr/bin/env python

# Mostly borrowed from PyAudio examples

import pyaudio
import struct
import math
import analyse
import numpy as np

SAMPLING_RATE = 44100

# Adjust as necessary
INPUT_BLOCK_TIME = 0.05
INITIAL_TAP_THRESHOLD = 0.010 # Default value is 0.010
INPUT_FRAMES_PER_BLOCK = int(SAMPLING_RATE*INPUT_BLOCK_TIME)

# if we get this many loud blocks in a row, raise the tap threshold
OVERSENSITIVE = 15.0/INPUT_BLOCK_TIME
# if we get this many quiet blocks in a row, decrease the tap threshold
UNDERSENSITIVE = 120.0/INPUT_BLOCK_TIME

# if the noise was longer than this many blocks, it's not a 'tap'
MAX_TAP_BLOCKS = 0.15/INPUT_BLOCK_TIME 


def get_rms(block):
    # From PyAudio examples
    # RMS amplitude is defined as the square root of the 
    # mean over time of the square of the amplitude.
    # so we need to convert this string of bytes into 
    # a string of 16-bit samples...
    SHORT_NORMALIZE = (1.0/32768.0)
    
    count = len(block)/2
    format = "%dh"%(count)
    shorts = struct.unpack(format, block)

    # iterate over the block.
    sum_squares = 0.0
    for sample in shorts:
    # sample is a signed short in +/- 32768. 
    # normalize it to 1.0
        n = sample * SHORT_NORMALIZE
        sum_squares += n*n

    return math.sqrt( sum_squares / count )


def get_mic_input():
    pa = pyaudio.PyAudio()
    input_stream = pa.open(format=pyaudio.paInt16, channels=2, rate=SAMPLING_RATE,  input=True, frames_per_buffer=INPUT_FRAMES_PER_BLOCK)
    return input_stream


def determine_pitch(raw_samples):
    # SoundAnalyse needs array of samples in 16-bit format for pitch detection
    samples = np.fromstring(raw_samples, dtype=np.int16)
    return analyse.detect_pitch(samples)


if __name__ == '__main__':
    tap_threshold = INITIAL_TAP_THRESHOLD                  
    noisy_count = MAX_TAP_BLOCKS+1                          
    quiet_count = 0
    tap_count = 0

    input_stream = get_mic_input()

    for i in range(1000):
        try:                
            samples = input_stream.read(INPUT_FRAMES_PER_BLOCK)         
        except IOError, e:                              
            print e
            noisy_count = 1
            continue

        amplitude = get_rms(samples)
        if amplitude > tap_threshold:
            # too loud to be a tap, adjust threshold if this keeps happening
            quiet_count = 0
            noisy_count += 1
            if noisy_count > OVERSENSITIVE:
                # raise sensitivity by 110%
                tap_threshold *= 1.1
        else:
            if 1 <= noisy_count <= MAX_TAP_BLOCKS:
                tap_count += 1
                pitch = determine_pitch(samples)
                print '{count}: TAP! @ {pitch} Hz'.format(count=tap_count, pitch=(pitch or 'no pitch'))
            # too quiet
            noisy_count = 0
            quiet_count += 1
            if quiet_count > UNDERSENSITIVE:
                # lower sensitivity by 90%
                tap_threshold *= 0.9
