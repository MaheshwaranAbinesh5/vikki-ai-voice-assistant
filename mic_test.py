import sounddevice as sd
import numpy as np
 
print("Testing every input device. KEEP TALKING OUT LOUD the whole time (count 1 2 3 ...).\n")
 
results = []
for i, d in enumerate(sd.query_devices()):
    if d["max_input_channels"] < 1:
        continue
    name = d["name"]
    try:
        rate = int(d["default_samplerate"])
        audio = sd.rec(int(2 * rate), samplerate=rate, channels=1, dtype="float32", device=i)
        sd.wait()
        peak = float(np.max(np.abs(audio)))
        results.append((i, name, peak))
        status = "HEARS YOU" if peak >= 0.01 else "silent"
        print(f"  device {i:>2}: {peak:.4f}  {status}  - {name}")
    except Exception as e:
        print(f"  device {i:>2}: could not open  - {name} ({str(e)[:60]})")
 
working = [r for r in results if r[2] >= 0.01]
print()
if working:
    best = max(working, key=lambda r: r[2])
    print(f"Best device: {best[0]} ({best[1]})")
    print(f"Run the assistant with:  python agent.py console --input-device {best[0]}")
else:
    print("Every device was silent. Windows is blocking or muting the microphone.")
    print("Fix in Windows Settings > Privacy & security > Microphone, then run this again.")
 







