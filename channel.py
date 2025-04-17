import pygame
import time

pygame.init()
pygame.mixer.init()

sound = pygame.mixer.Sound('your_sound_file.wav')
channel = pygame.mixer.Channel(1)  # channel 1

channel.play(sound)

# Wait a bit and check if it's still busy
time.sleep(0.5)
if channel.get_busy():
    print("Still playing...")
else:
    print("Done playing.")
