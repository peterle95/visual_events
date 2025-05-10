import pygame
import math
import random

# --- Constants ---
WIDTH, HEIGHT = 800, 800
FPS = 60
CENTER_X, CENTER_Y = WIDTH // 2, HEIGHT // 2

# --- Initialization ---
pygame.init()
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Abstract Psychedelic Flow")
clock = pygame.time.Clock()

# --- Main Time Variable ---
t = 0  # Time in frames

# --- Parameters for the visual (TWEAK THESE!) ---

# Tunnel parameters
TUNNEL_LAYERS = 12
TUNNEL_SHRINK_FACTOR = 0.85  # How much smaller each successive layer is
TUNNEL_BASE_ROTATION_SPEED = 0.002
TUNNEL_HUE_SHIFT_PER_LAYER = 8
TUNNEL_POLYGON_SIDES_BASE = 5 # Base number of sides for tunnel polygons
TUNNEL_SIDE_OSCILLATION = 2   # e.g., 5 sides +/- 2 = 3 to 7 sides
TUNNEL_POINT_WOBBLE_AMOUNT = 0.15 # How much individual points of polygon wobble

# Radiating Beams / Flares
NUM_BEAMS = 10
BEAM_BASE_LENGTH = WIDTH * 0.6
BEAM_LENGTH_OSCILLATION = WIDTH * 0.2
BEAM_ROTATION_SPEED = 0.004
BEAM_THICKNESS_BASE = 15
BEAM_THICKNESS_OSCILLATION = 10
BEAM_HUE_SPREAD = 120 # Hue difference across beams

# Color & Effect parameters
HUE_BASE_OFFSET = 0  # Start with red/orange hues (0), blues (240), greens (120) etc.
HUE_CYCLE_SPEED = 0.15
SATURATION_BASE = 95
VALUE_BASE = 85
TRAIL_EFFECT_ALPHA = 15 # Lower for longer trails (5-25), 255 for no trail (sharper)

# --- Helper Functions ---
def hsva_to_rgb(h, s, v, a=100):
    color = pygame.Color(0)
    color.hsva = (h % 360,
                  max(0, min(100, s)),
                  max(0, min(100, v)),
                  max(0, min(100, a)))
    return color

# --- Main Loop ---
running = True
while running:
    # --- Event Handling ---
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_ESCAPE:
                running = False

    # --- Update Logic ---
    t += 1

    # --- Drawing ---
    # Trail effect or solid background
    if TRAIL_EFFECT_ALPHA < 255:
        trail_surface = pygame.Surface((WIDTH, HEIGHT), pygame.SRCALPHA)
        # Background color for trail can also shift
        # bg_trail_hue = (HUE_BASE_OFFSET + t * HUE_CYCLE_SPEED * 0.1) % 360
        # trail_surface.fill(hsva_to_rgb(bg_trail_hue, 20, 10, TRAIL_EFFECT_ALPHA))
        trail_surface.fill((0, 0, 0, TRAIL_EFFECT_ALPHA)) # Classic black trail
        screen.blit(trail_surface, (0, 0))
    else:
        bg_hue = (HUE_BASE_OFFSET + t * HUE_CYCLE_SPEED * 0.2) % 360
        screen.fill(hsva_to_rgb(bg_hue, 30, 15)) # Dark, desaturated, shifting background

    # Calculate current global hue for this frame
    current_global_hue = (HUE_BASE_OFFSET + t * HUE_CYCLE_SPEED) % 360

    # 1. Central Tunnel/Portal
    for i in range(TUNNEL_LAYERS, 0, -1): # Draw from back to front
        layer_progress = (TUNNEL_LAYERS - i) / TUNNEL_LAYERS
        
        # Size pulsates and shrinks with depth
        size = (WIDTH * 0.9) * (TUNNEL_SHRINK_FACTOR ** (TUNNEL_LAYERS - i))
        size *= (1 + 0.08 * math.sin(t * 0.015 + i * 0.5))

        # Rotation speed can vary per layer, or a general rotation
        layer_rotation_offset = t * TUNNEL_BASE_ROTATION_SPEED * (i * 0.1 + 1) * ((-1)**i) # Alternating direction

        tunnel_hue = (current_global_hue + i * TUNNEL_HUE_SHIFT_PER_LAYER) % 360
        tunnel_sat = SATURATION_BASE - i * 2 - layer_progress * 10
        tunnel_val = VALUE_BASE - i * 3 - layer_progress * 15
        
        # Number of sides for the polygon can oscillate
        num_points = TUNNEL_POLYGON_SIDES_BASE + int(TUNNEL_SIDE_OSCILLATION * math.sin(t * 0.01 + i * 0.3))
        num_points = max(3, num_points) # Ensure at least 3 sides

        points = []
        for p_idx in range(num_points):
            angle = (2 * math.pi / num_points) * p_idx + layer_rotation_offset
            
            # Individual point wobble for more organic shape
            radius_mod_p = 1 + TUNNEL_POINT_WOBBLE_AMOUNT * math.sin(t * 0.025 + i * 0.4 + p_idx * 0.8 + layer_progress * math.pi)
            
            px = CENTER_X + size * 0.5 * math.cos(angle) * radius_mod_p
            py = CENTER_Y + size * 0.5 * math.sin(angle) * radius_mod_p
            points.append((px, py))
        
        if len(points) >= 3:
            # Filled polygon
            pygame.draw.polygon(screen, hsva_to_rgb(tunnel_hue, tunnel_sat, tunnel_val), points, 0)
            # Outline (slightly brighter/more saturated)
            outline_thickness = max(1, int(4 - layer_progress * 3))
            pygame.draw.polygon(screen, hsva_to_rgb(tunnel_hue, tunnel_sat + 5, tunnel_val + 10), points, outline_thickness)


    # 2. Radiating Beams / Energy Flares
    overall_beam_rotation = t * BEAM_ROTATION_SPEED
    for b in range(NUM_BEAMS):
        beam_angle = (2 * math.pi / NUM_BEAMS) * b + overall_beam_rotation

        # Length pulsation
        current_beam_length = BEAM_BASE_LENGTH + \
                              BEAM_LENGTH_OSCILLATION * math.sin(t * 0.02 + b * (2 * math.pi / NUM_BEAMS) * 2) # Phase shift per beam

        # Thickness pulsation
        current_beam_thickness = BEAM_THICKNESS_BASE + \
                                 BEAM_THICKNESS_OSCILLATION * math.cos(t * 0.025 + b * (2 * math.pi / NUM_BEAMS) * 1.5)
        current_beam_thickness = max(1, int(current_beam_thickness))

        # Color - hue spread across beams, cycles with global hue
        beam_hue_offset = (b / NUM_BEAMS) * BEAM_HUE_SPREAD
        beam_hue = (current_global_hue + beam_hue_offset + 180) % 360 # +180 to contrast with tunnel
        beam_sat = SATURATION_BASE - 10 + 10 * math.sin(t * 0.01 + b * 0.3)
        beam_val = VALUE_BASE - 5 + 5 * math.cos(t * 0.012 + b * 0.4)
        
        beam_color = hsva_to_rgb(beam_hue, beam_sat, beam_val, 70) # Semi-transparent beams

        # Beam as a tapered polygon (triangle pointing outwards)
        # To make it tapered, we define 3 points for a triangle:
        # Center, and two points at the end of the beam slightly offset perpendicularly
        
        end_x = CENTER_X + current_beam_length * math.cos(beam_angle)
        end_y = CENTER_Y + current_beam_length * math.sin(beam_angle)

        # Calculate perpendicular vector for thickness
        perp_angle = beam_angle + math.pi / 2
        dx_offset = (current_beam_thickness / 2) * math.cos(perp_angle)
        dy_offset = (current_beam_thickness / 2) * math.sin(perp_angle)

        p1 = (CENTER_X, CENTER_Y)
        p2 = (end_x + dx_offset, end_y + dy_offset)
        p3 = (end_x - dx_offset, end_y - dy_offset)
        
        pygame.draw.polygon(screen, beam_color, [p1, p2, p3])

        # Optional: Add a brighter "core" line to the beam
        # core_thickness = max(1, int(current_beam_thickness * 0.3))
        # core_color = hsva_to_rgb(beam_hue, beam_sat + 10, beam_val + 15, 90)
        # pygame.draw.line(screen, core_color, (CENTER_X, CENTER_Y), (end_x, end_y), core_thickness)


    # --- Display Update ---
    pygame.display.flip()

    # --- Cap FPS ---
    clock.tick(FPS)

pygame.quit()