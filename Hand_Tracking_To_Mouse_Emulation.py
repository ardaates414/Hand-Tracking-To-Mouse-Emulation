import cv2
import mediapipe as mp
import pyautogui
import time
import threading
import tkinter as tk
from PIL import Image, ImageDraw, ImageTk
import screeninfo
import math

class CursorOverlay:
    def __init__(self):
        self.root = tk.Tk()
        self.root.overrideredirect(True)
        self.root.attributes('-topmost', True)
        self.root.attributes('-transparentcolor', 'black')
        self.root.configure(bg='black')
        
        screen = screeninfo.get_monitors()[0]
        self.screen_width = screen.width
        self.screen_height = screen.height
        
        self.canvas = tk.Canvas(self.root, width=100, height=100, bg='black', highlightthickness=0)
        self.canvas.pack()
        
        self.current_x = self.screen_width // 2
        self.current_y = self.screen_height // 2
        self.root.geometry(f"100x100+{self.current_x-50}+{self.current_y-50}")
        self.create_cursor_icon()
    
    def create_cursor_icon(self):
        img = Image.new('RGBA', (100, 100), (0, 0, 0, 0))
        draw = ImageDraw.Draw(img)
        center = (50, 50)
        
        # Draw outer circle with glow
        for r in range(20, 30):
            alpha = int(200 - (r - 20) * 20)
            draw.ellipse([center[0]-r, center[1]-r, center[0]+r, center[1]+r],
                        outline=(255, 0, 255, alpha), width=2)
        
        # Draw center dot
        draw.ellipse([center[0]-5, center[1]-5, center[0]+5, center[1]+5],
                    fill=(255, 0, 255, 255))
        
        self.cursor_image = ImageTk.PhotoImage(img)
        self.canvas.delete("all")
        self.canvas.create_image(50, 50, image=self.cursor_image)
    
    def update_position(self, x, y):
        self.current_x = max(0, min(self.screen_width - 100, x - 50))
        self.current_y = max(0, min(self.screen_height - 100, y - 50))
        self.root.geometry(f"100x100+{int(self.current_x)}+{int(self.current_y)}")
    
    def show_click_effect(self):
        self.canvas.delete("all")
        img = Image.new('RGBA', (120, 120), (0, 0, 0, 0))
        draw = ImageDraw.Draw(img)
        center = (60, 60)
        
        # Draw click effect
        for r in range(30, 40):
            alpha = int(150 - (r - 30) * 15)
            draw.ellipse([center[0]-r, center[1]-r, center[0]+r, center[1]+r],
                        outline=(255, 0, 255, alpha), width=3)
        
        self.click_img = ImageTk.PhotoImage(img)
        self.canvas.create_image(60, 60, image=self.click_img)
        
        # Reset after animation
        threading.Timer(0.1, self.create_cursor_icon).start()
    
    def run(self):
        self.root.mainloop()

class HandController:
    def __init__(self):
        self.mp_hands = mp.solutions.hands
        self.hands = self.mp_hands.Hands(
            min_detection_confidence=0.7,
            min_tracking_confidence=0.5,
            max_num_hands=1
        )
        
        # Initialize webcam
        self.cap = cv2.VideoCapture(0)
        self.cap.set(cv2.CAP_PROP_FRAME_WIDTH, 1280)
        self.cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 720)
        
        # Mouse control
        pyautogui.FAILSAFE = False
        pyautogui.PAUSE = 0
        
        # Screen info
        screen = screeninfo.get_monitors()[0]
        self.screen_width = screen.width
        self.screen_height = screen.height
        
        # Cursor smoothing (lower value = faster response)
        self.smoothed_x = self.screen_width // 2
        self.smoothed_y = self.screen_height // 2
        self.smoothing = 0.2  # Further reduced from 0.3 for even faster movement
        
        # Click and drag detection
        self.pinched = False
        self.is_dragging = False
        self.pinch_start_time = 0
        self.last_click_time = 0
        self.click_cooldown = 0.1  # 100ms cooldown between clicks
        
        # Start cursor overlay
        self.cursor = CursorOverlay()
        self.overlay_thread = threading.Thread(target=self.cursor.run, daemon=True)
        self.overlay_thread.start()
        time.sleep(0.5)  # Give overlay time to initialize
    
    def calculate_distance(self, p1, p2):
        return ((p1.x - p2.x)**2 + (p1.y - p2.y)**2) ** 0.5
    
    def is_pinching(self, landmarks):
        # Check distance between thumb tip and index tip
        thumb_tip = landmarks[4]
        index_tip = landmarks[8]
        distance = self.calculate_distance(thumb_tip, index_tip)
        
        # Also check if thumb is bent towards the hand (like a pinch)
        thumb_ip = landmarks[3]  # Thumb IP joint
        thumb_mcp = landmarks[2]  # Thumb MCP joint
        thumb_bend = self.calculate_distance(thumb_tip, thumb_mcp) / max(0.001, self.calculate_distance(thumb_ip, thumb_mcp))
        
        # More reliable pinch detection that requires thumb to be bent
        return distance < 0.07 and thumb_bend > 1.2
    
    def run(self):
        print("Absolute Solver - Improved Version")
        print("Press 'q' to quit")
        
        while True:
            ret, frame = self.cap.read()
            if not ret:
                print("Failed to get frame from camera")
                break
                
            frame = cv2.flip(frame, 1)
            rgb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
            results = self.hands.process(rgb_frame)
            
            if results.multi_hand_landmarks:
                hand_landmarks = results.multi_hand_landmarks[0]
                landmarks = hand_landmarks.landmark
                
                # Get hand landmarks
                index_tip = landmarks[8]  # For pinch detection
                
                # Calculate palm center (average of wrist and base of fingers)
                wrist = landmarks[0]
                index_mcp = landmarks[5]
                pinky_mcp = landmarks[17]
                
                # Calculate center of the palm
                palm_center_x = (wrist.x + index_mcp.x + pinky_mcp.x) / 3
                palm_center_y = (wrist.y + index_mcp.y + pinky_mcp.y) / 3
                
                # Convert to screen coordinates
                screen_x = int(palm_center_x * self.screen_width)
                screen_y = int(palm_center_y * self.screen_height)
                
                # Smooth cursor movement
                self.smoothed_x = self.smoothed_x * self.smoothing + screen_x * (1 - self.smoothing)
                self.smoothed_y = self.smoothed_y * self.smoothing + screen_y * (1 - self.smoothing)
                
                # Move cursor
                pyautogui.moveTo(int(self.smoothed_x), int(self.smoothed_y))
                self.cursor.update_position(self.smoothed_x, self.smoothed_y)
                
                # Check for pinch gesture and handle timing
                is_pinching = self.is_pinching(landmarks)
                current_time = time.time()
                
                if is_pinching and not self.pinched:
                    # Start of pinch - just record the time, don't click yet
                    self.pinch_start_time = current_time
                    self.pinched = True
                    print("Pinch started - waiting to see if it's a click or drag")
                
                # If we've been pinching for more than 300ms, start dragging
                if self.pinched and not self.is_dragging and (current_time - self.pinch_start_time) > 0.3:
                    self.is_dragging = True
                    self.cursor.show_click_effect()
                    pyautogui.mouseDown()
                    print("Drag started")
                
                # If we're dragging, keep updating the mouse position
                if self.is_dragging:
                    pyautogui.moveTo(int(self.smoothed_x), int(self.smoothed_y))
                
                # Handle pinch release
                if not is_pinching and self.pinched:
                    if self.is_dragging:
                        # If we were dragging, just release
                        pyautogui.mouseUp()
                        self.is_dragging = False
                        print("Drag ended")
                    else:
                        # If it was a short pinch, do a click
                        self.cursor.show_click_effect()
                        pyautogui.click()
                        print("Click")
                    
                    self.pinched = False
            
            # Show the frame (optional, can be disabled for better performance)
            cv2.imshow('Hand Tracking', frame)
            
            # Exit on 'q' press
            if cv2.waitKey(1) & 0xFF == ord('q'):
                break
        
        # Cleanup
        self.cap.release()
        cv2.destroyAllWindows()
        self.hands.close()

if __name__ == "__main__":
    # Ensure mouse button is released when starting
    try:
        pyautogui.mouseUp()
    except:
        pass
    
    controller = HandController()
    controller.run()
