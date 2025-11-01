# Hand Tracking Mouse Emulator

A Python application that turns your webcam into a hand gesture-controlled mouse using computer vision and hand tracking.
-------------------------------------------------------------------------------------------------------------------------

## Features

- 👆 Precise hand tracking for cursor movement
- 🤏 Intuitive pinch-to-click gesture
- 🖱️ Smooth cursor movement with adjustable sensitivity
- 🎮 Natural hand gestures for mouse control
- 🖥️ Custom cursor overlay with visual feedback
- ⚡ Optimized for performance

## Requirements

- Python 3.7+
- Webcam
- Windows OS (for mouse emulation)

## Installation

1. Install the required packages:
   ```
   pip install -r requirements.txt
   ```
   Or simply run `Install.bat`

2. Run the application:
   ```
   python Hand_Tracking_To_Mouse_Emulation.py
   ```
   Or double-click `Run.bat`

## How to Use

1. Position yourself in front of your webcam
2. Move your hand to control the cursor
3. Pinch your thumb and index finger together to click
4. Hold the pinch to drag items
5. Press 'Q' to quit the application

## Controls

- ✋ Open hand: Move cursor
- 🤏 Pinch: Left click
- 🤏 Pinch and hold: Drag
- 🖐️ Release pinch: Release click/drag
- Q: Quit application

## Customization

You can adjust the following settings in the code:
- `smoothing = 0.2` - Lower values make the cursor more responsive
- `pinch_threshold = 0.07` - Adjust pinch sensitivity
- `drag_delay = 0.3` - Time to hold before drag starts (in seconds)

## Troubleshooting

- Ensure good lighting for better hand tracking
- Keep your hand visible to the webcam
- Make sure no other application is using the webcam
- Run as administrator if mouse control doesn't work

## License

This project doesn't have a license do what ever you want to do with this just promote me please. ༼ つ ◕_◕ ༽つ
