import pygame
import pygame.freetype

# Initialize pygame.
pygame.init()
pygame.display.set_mode((1920, 1080))
clock = pygame.time.Clock()
pygame.display.set_caption("Animated Text Slides")
display = pygame.display.get_surface()

# Load font.
wanted_fonts = [
    "dejavusansmono",
    "ubuntumono",
    "liberationmono",
    "bitstreamverasansmono",
    "nimbusmonops",
    "notosansmono",
    "freemono",
    "tlwgmono",
    "mitramono",
    "notosansmonocjktc",
    "notosansmonocjksc",
    "notosansmonocjkkr",
    "notosansmonocjkhk",
    "notosansmonocjkjp",
    "notomono"]

fonts = [f for f in pygame.font.get_fonts() if f in wanted_fonts]
font_name = fonts[0] if fonts else None
font = pygame.freetype.SysFont(font_name, 20)
text_surface, text_rect = font.render("Hello World!", (180, 180, 180))

text_start = (1000, 200)  # px
text_end = (500, 500)  # px
text_duration = 5000.0  # ms
text_start_time = pygame.time.get_ticks() + 2000  # ms

# Main loop.
request_quit = False
while not request_quit:
    # Process input.
    events = pygame.event.get()
    for event in events:
        if event.type == pygame.QUIT:
            request_quit = True
        elif event.type == pygame.KEYDOWN:
            if event.key == pygame.K_ESCAPE:
                request_quit = True

    # Update game state.
    now = pygame.time.get_ticks()
    seconds = now / 1000

    text_t = max(0.0, min(1.0, (now - text_start_time) / text_duration))
    text_location = tuple(map(lambda start, end: int(start + (text_t * (end - start))), text_start, text_end))

    # Render.
    display.fill(((seconds * 10) % 255, 0, 0))
    display.blit(text_surface, text_location)
    pygame.display.flip()

    # Wait for next frame.
    clock.tick(30)

# Done.
pygame.quit()
