#!/usr/bin/env python3
"""Play a sine signal."""
import argparse
import sys

import numpy as np
import sounddevice as sd
import soundfile as sf

def int_or_str(text):
    """Helper function for argument parsing."""
    try:
        return int(text)
    except ValueError:
        return text


parser = argparse.ArgumentParser(add_help=False)
parser.add_argument(
    '-l', '--list-devices', action='store_true',
    help='show list of audio devices and exit')
args, remaining = parser.parse_known_args()
if args.list_devices:
    print(sd.query_devices())
    parser.exit(0)
parser = argparse.ArgumentParser(
    description=__doc__,
    formatter_class=argparse.RawDescriptionHelpFormatter,
    parents=[parser])
parser.add_argument(
    'frequency', nargs='?', metavar='FREQUENCY', type=float, default=500,
    help='frequency in Hz (default: %(default)s)')
parser.add_argument(
    '-d', '--device', type=int_or_str,
    help='output device (numeric ID or substring)')
parser.add_argument(
    '-a', '--amplitude', type=float, default=0.2,
    help='amplitude (default: %(default)s)')
parser.add_argument(
    '-f', '--filename', type=str, default="recording_352.wav",
    help='filename (default: %(default)s)')
parser.add_argument(
    '-t','--time_duration', type=float, default=10.0,
    help='time duration (default: %(default)s)'
)

args = parser.parse_args(remaining)

start_idx = 0

volume = 1    # range [0.0, 1.0]
fs = 96000      # sampling rate, Hz, must be integer
duration = args.time_duration   # in seconds, may be float
f = args.frequency        # sine frequency, Hz, may be float

# generate samples, note conversion to float32 array
samples = volume*(np.sin(2*np.pi*np.arange(fs*duration)*f/fs)).astype(np.float32)

print("Recording\n")
# Simultaneously play the driving signal and record the sound 
recorded_sound = sd.playrec(samples,fs,channels=2)

sd.wait()
print("Finished Recording")

sf.write(args.filename,recorded_sound,fs)

