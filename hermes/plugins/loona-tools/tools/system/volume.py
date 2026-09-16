import json
import os
import subprocess
import tempfile


CSHARP = r'''
using System;
using System.Runtime.InteropServices;

[ComImport, Guid("BCDE0395-E52F-467C-8E3D-C4579291692E")]
class MMDeviceEnumerator { }

[Guid("A95664D2-9614-4F35-A746-DE8DB63617E6")]
[InterfaceType(ComInterfaceType.InterfaceIsIUnknown)]
interface IMMDeviceEnumerator
{
    int EnumAudioEndpoints(int dataFlow, int stateMask, out IntPtr devices);
    int GetDefaultAudioEndpoint(int dataFlow, int role, out IMMDevice endpoint);
    int GetDevice(string id, out IMMDevice device);
}

[Guid("D666063F-1587-4E43-81F1-B948E807363F")]
[InterfaceType(ComInterfaceType.InterfaceIsIUnknown)]
interface IMMDevice
{
    int Activate(ref Guid id, int clsCtx, IntPtr activationParams,
                 out IAudioEndpointVolume endpoint);
}

[Guid("5CDF2C82-841E-4546-9722-0CF74078229A")]
[InterfaceType(ComInterfaceType.InterfaceIsIUnknown)]
interface IAudioEndpointVolume
{
    int RegisterControlChangeNotify(IntPtr notify);
    int UnregisterControlChangeNotify(IntPtr notify);
    int GetChannelCount(out uint count);
    int SetMasterVolumeLevel(float level, Guid context);
    int SetMasterVolumeLevelScalar(float level, Guid context);
    int GetMasterVolumeLevel(out float level);
    int GetMasterVolumeLevelScalar(out float level);
    int SetChannelVolumeLevel(uint channel, float level, Guid context);
    int SetChannelVolumeLevelScalar(uint channel, float level, Guid context);
    int GetChannelVolumeLevel(uint channel, out float level);
    int GetChannelVolumeLevelScalar(uint channel, out float level);
    int SetMute(bool mute, Guid context);
    int GetMute(out bool mute);
}

public static class AudioVolume
{
    public static float Set(float volume)
    {
        var enumerator = (IMMDeviceEnumerator)new MMDeviceEnumerator();

        IMMDevice device;
        int hr = enumerator.GetDefaultAudioEndpoint(0, 0, out device);
        if (hr != 0) Marshal.ThrowExceptionForHR(hr);
        if (device == null) throw new Exception("No default audio device found.");

        Guid iid = new Guid("5CDF2C82-841E-4546-9722-0CF74078229A");

        IAudioEndpointVolume endpoint;
        hr = device.Activate(ref iid, 23, IntPtr.Zero, out endpoint);
        if (hr != 0) Marshal.ThrowExceptionForHR(hr);
        if (endpoint == null) throw new Exception("No audio volume endpoint found.");

        hr = endpoint.SetMasterVolumeLevelScalar(volume, Guid.Empty);
        if (hr != 0) Marshal.ThrowExceptionForHR(hr);

        float actual;
        hr = endpoint.GetMasterVolumeLevelScalar(out actual);
        if (hr != 0) Marshal.ThrowExceptionForHR(hr);

        return actual;
    }
}
'''


def loona_set_volume(args: dict, **kwargs) -> str:
    """Set and verify Windows master volume."""

    try:
        volume = float(args.get("volume", -1))

        if not 0 <= volume <= 100:
            return json.dumps({
                "success": False,
                "action": "volume_change_failed",
                "error": "Volume must be between 0 and 100.",
            })

        scalar = volume / 100

        script = f'''
Add-Type @"
{CSHARP}
"@

$actual = [AudioVolume]::Set([float]{scalar})
Write-Output $actual.ToString("F4")
'''

        with tempfile.NamedTemporaryFile(
            mode="w", suffix=".ps1", delete=False, encoding="utf-8"
        ) as file:
            file.write(script)
            path = file.name

        try:
            result = subprocess.run(
                [
                    "powershell.exe",
                    "-NoProfile",
                    "-NonInteractive",
                    "-ExecutionPolicy", "Bypass",
                    "-File", path,
                ],
                capture_output=True,
                text=True,
                shell=False,
                timeout=15,
            )
        finally:
            os.remove(path)

        if result.returncode != 0:
            raise RuntimeError(
                result.stderr.strip() or "Windows could not change the volume."
            )

        output = result.stdout.strip().splitlines()

        if not output:
            raise RuntimeError("PowerShell produced no verification output.")

        actual = float(output[-1])
        actual_volume = round(actual * 100, 1)

        if abs(actual - scalar) > 0.01:
            return json.dumps({
                "success": False,
                "action": "volume_change_failed",
                "error": f"Verification failed: target {volume}%, actual {actual_volume}%.",
                "target_volume": volume,
                "actual_volume": actual_volume,
            })

        return json.dumps({
            "success": True,
            "action": "volume_changed",
            "volume": actual_volume,
        })

    except Exception as error:
        return json.dumps({
            "success": False,
            "action": "volume_change_failed",
            "error": str(error),
        })