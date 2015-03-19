#!/usr/bin/env python

import mido


def pitch_to_midi(note, amplitude):
    on = mido.Message('note_on', note=int(note), velocity=64)
    return on
