import pyaudio

def get_microphone_device_index(device_name, host_api_index=0):
    audio = pyaudio.PyAudio()
    info = audio.get_host_api_info_by_index(host_api_index)
    num_devices = info.get('deviceCount')

    for i in range(num_devices):
        device_info = audio.get_device_info_by_host_api_device_index(host_api_index, i)
        if device_info['name'] == device_name:
            return i
    return None
