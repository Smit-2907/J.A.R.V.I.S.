import pyaudio
p = pyaudio.PyAudio()
print(f"Default Input Device: {p.get_default_input_device_info()}")
print(f"Default Output Device: {p.get_default_output_device_info()}")

for i in range(p.get_device_count()):
    info = p.get_device_info_by_index(i)
    print(f"Device {i}: {info['name']} (Input: {info['maxInputChannels']}, Output: {info['maxOutputChannels']})")
p.terminate()
