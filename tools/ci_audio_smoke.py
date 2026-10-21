"""Create a non-silent CI fixture and reject silently skipped extraction stages."""

import sys
import wave
from pathlib import Path

import numpy as np


def prepare():
    directory = Path("logs/ci-input")
    directory.mkdir(parents=True, exist_ok=True)
    sample_rate = 48000
    time = np.arange(sample_rate * 8) / sample_rate
    samples = (0.25 * np.sin(2 * np.pi * 220 * time) * 32767).astype("<i2")
    with wave.open(str(directory / "tone.wav"), "wb") as stream:
        stream.setnchannels(1)
        stream.setsampwidth(2)
        stream.setframerate(sample_rate)
        stream.writeframes(samples.tobytes())


def verify():
    directory = Path("logs/mi-test")
    waves = sorted((directory / "1_16k_wavs").glob("*.wav"))
    if not waves:
        raise RuntimeError("Preprocessing produced no audio clips")
    for source in waves:
        for folder, filename in [
            ("2a_f0", source.name + ".npy"),
            ("2b-f0nsf", source.name + ".npy"),
            ("3_feature256", source.stem + ".npy"),
        ]:
            output = directory / folder / filename
            if not output.is_file():
                raise RuntimeError("Extraction output missing: {}".format(output))
            values = np.load(output, allow_pickle=False)
            if not values.size or not np.isfinite(values).all():
                raise RuntimeError("Empty or non-finite extraction: {}".format(output))
            if folder == "3_feature256" and (values.ndim != 2 or values.shape[1] != 256):
                raise RuntimeError("Unexpected feature shape: {}".format(values.shape))
    print("Verified preprocessing, pitch and HuBERT features for {} clips".format(len(waves)))


if __name__ == "__main__":
    if sys.argv[1:] == ["prepare"]:
        prepare()
    elif sys.argv[1:] == ["verify"]:
        verify()
    else:
        raise SystemExit("Usage: ci_audio_smoke.py prepare|verify")
