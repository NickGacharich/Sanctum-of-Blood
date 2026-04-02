import wave, struct, math, random

sample_rate = 44100
duration = 14
num_samples = int(sample_rate * duration)


def clamp(x): return max(-1.0, min(1.0, x))

# fake reverb (echo)
delay_samples = int(0.03 * sample_rate)  # 30ms delay

samples = []
freqs = [82.41, 73.42, 65.41, 61.74]

for i in range(num_samples):

    t = i / sample_rate
    base = freqs[int((t // 3.5) % len(freqs))]

    guitar = sum(math.sin(2 * math.pi * base * m * t) for m in [1, 2, 3, 4])
    guitar = math.tanh(4 * guitar)
    guitar *= 0.6 if math.sin(2 * math.pi * 8 * t) > 0 else 1.0

    # --- CHANTING CHOIR LAYER ---
    root = base / 2
    minor_third = root * 1.2
    fifth = root * 1.5

    # Build layered voices
    chant = 0
    for freq in [root, minor_third, fifth]:
        chant += math.sin(2 * math.pi * freq * t)
        chant += 0.4 * math.sin(2 * math.pi * freq * 0.5 * t)  # deeper voice

    # Normalize
    chant *= 0.5

    # --- RHYTHMIC CHANTING (syllables like "OH... AH...") ---
    bpm = 90
    beat = (t * bpm / 60) % 1  # 0 → 1 each beat

    # Create chant pattern (on/off envelope)
    if beat < 0.3:
        envelope = math.sin(math.pi * (beat / 0.3))  # smooth attack/decay
    else:
        envelope = 0

    # Add slower phrase cycle (like chanting phrases)
    phrase = (t % 4.0) / 4.0
    phrase_env = 0.5 + 0.5 * math.sin(2 * math.pi * phrase)

    chant *= envelope * phrase_env

    # Fade in at start
    attack = 1 - math.exp(-0.5 * t)

    chant *= attack * 0.4

    kick = math.sin(2 * math.pi * 55 * t) * math.exp(-6 * (t % 0.5))
    noise = (random.random() * 2 - 1) * 0.1 * math.exp(-10 * (t % 0.25))

    val = clamp(0.55 * guitar + 0.35 * chant + 0.25 * kick + noise)

    samples.append(int(val * 32767))

with wave.open("doom_metal_choir_loop.wav", "w") as f:
    f.setnchannels(1)
    f.setsampwidth(2)
    f.setframerate(sample_rate)
    for s in samples:
        f.writeframes(struct.pack("<h", s))