"""
FFmpeg filter definitions for motion (Ken Burns), audio mixing, and transitions.
"""

# Target resolution for shorts
WIDTH = 1080
HEIGHT = 1920
FPS = 30
SCENE_DURATION = 5  # seconds

# Mapping of camera movements to FFmpeg zoompan filters
MOTION_FILTERS = {
    "dolly-in": (
        f"zoompan=z='min(zoom+0.0015,1.5)':x='iw/2-(iw/zoom/2)':y='ih/2-(ih/zoom/2)':"
        f"d={SCENE_DURATION * FPS}:s={WIDTH}x{HEIGHT}:fps={FPS}"
    ),
    "pan-left": (
        f"zoompan=z='1.3':x='iw*0.3-(iw*0.3/zoom)*on/{SCENE_DURATION * FPS}':y='ih/2-(ih/zoom/2)':"
        f"d={SCENE_DURATION * FPS}:s={WIDTH}x{HEIGHT}:fps={FPS}"
    ),
    "tilt-up": (
        f"zoompan=z='1.2':x='iw/2-(iw/zoom/2)':y='ih*0.4-(ih*0.4/zoom)*on/{SCENE_DURATION * FPS}':"
        f"d={SCENE_DURATION * FPS}:s={WIDTH}x{HEIGHT}:fps={FPS}"
    ),
    "handheld": (
        f"zoompan=z='1.1+0.0005*sin(on/5)':x='iw/2-(iw/zoom/2)+5*sin(on/3)':y='ih/2-(ih/zoom/2)+3*cos(on/4)':"
        f"d={SCENE_DURATION * FPS}:s={WIDTH}x{HEIGHT}:fps={FPS}"
    ),
    "static-wide": (
        f"zoompan=z='1.05':x='iw/2-(iw/zoom/2)':y='ih/2-(ih/zoom/2)':"
        f"d={SCENE_DURATION * FPS}:s={WIDTH}x{HEIGHT}:fps={FPS}"
    )
}

TRANSITION_DURATION = 0.3  # seconds

# Audio mixing parameters
AUDIO_REVERB = "aecho=0.8:0.9:40:0.3"  
AUDIO_COMPRESSOR = "acompressor=threshold=-20dB:ratio=3:1"
AUDIO_HIGHPASS = "highpass=f=80"
AUDIO_NORMALIZE = "loudnorm=I=-14:LRA=11:TP=-1.0"  

# Music volume ducking timeline (assuming 30s total)
MUSIC_VOLUME_FILTER = (
    "volume=eval=frame:volume='if(between(t,2,28),0.079,0.25)'" # -22dB mid, -12dB otherwise
)

# Caption styles (ASS format)
ASS_HEADER = f"""[Script Info]
ScriptType: v4.00+
PlayResX: {WIDTH}
PlayResY: {HEIGHT}
WrapStyle: 1

[V4+ Styles]
Format: Name, Fontname, Fontsize, PrimaryColour, SecondaryColour, OutlineColour, BackColour, Bold, Italic, Underline, StrikeOut, ScaleX, ScaleY, Spacing, Angle, BorderStyle, Outline, Shadow, Alignment, MarginL, MarginR, MarginV, Encoding
Style: Default,Montserrat ExtraBold,88,&H00FFFFFF,&H000000FF,&H00000000,&H00000000,-1,0,0,0,100,100,0,0,1,4,0,2,10,10,160,1
Style: Highlight,Montserrat ExtraBold,92,&H0000E5FF,&H000000FF,&H00000000,&H00000000,-1,0,0,0,105,105,0,0,1,4,0,2,10,10,160,1

[Events]
Format: Layer, Start, End, Style, Name, MarginL, MarginR, MarginV, Effect, Text
"""
