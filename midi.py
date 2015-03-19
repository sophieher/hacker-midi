#!/usr/bin/env python

import mido


def pitch_to_midi(pitch, amplitude):
    note = max(int(pitch % 127), 50)
    on = mido.Message('note_on', note=note, velocity=64)
    return on
