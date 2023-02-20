import pygame
import pygame.freetype

from dataclasses import dataclass
from typing import List, Tuple

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


class Line:
   text: str
   row: int
   color: Tuple[int, int, int]
   surface: pygame.Surface
   rect: pygame.Rect

   def __init__(self, text: str, row: int, color: Tuple[int, int, int]):
       self.text = text
       self.row = row
       self.color = color
       self.surface, self.rect = font.render(text, color)

@dataclass
class Slide:
    lines: List[Line]

#@dataclass
#class SlideDeck:
#    slides: List[Slide]

@dataclass
class LineTransition:
    start_line_index: int
    end_line_index: int

@dataclass
class SlideTransition:
    start_slide: Slide
    end_slide: Slide
    line_transitions: List[LineTransition]

white = (255, 255, 255)

slide_1 = Slide([
    Line("First line", 0, white),
    Line("Second line", 1, white), 
    Line("Third line", 2, white)])
slide_2 = Slide([
    Line("Alpha line", 0, white),
    Line("Beta line", 1, white),
    Line("Gamma line", 2, white)])
slide_3 = Slide([
    Line("Line 1", 0, white),
    Line("Line 2", 1, white),
    Line("Line 3", 2, white)])

#slide_deck = SlideDeck([slide_1, slide_2, slide_3])
slide_deck = [slide_1, slide_2, slide_3]

current_slide: int = 0

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
            elif event.key == pygame.K_SPACE or event.key == pygame.K_RIGHT:
                current_slide = (current_slide + 1) % len(slide_deck)
            elif event.key == pygame.K_BACKSPACE or event.key == pygame.K_LEFT:
                current_slide = (current_slide - 1) if current_slide > 0 else len(slide_deck) - 1

    # Update game state.
    # now = pygame.time.get_ticks()
    # seconds = now / 1000

    # text_t = max(0.0, min(1.0, (now - text_start_time) / text_duration))
    # text_location = tuple(map(lambda start, end: int(start + (text_t * (end - start))), text_start, text_end))

    # Render.
    # display.fill(((seconds * 10) % 255, 0, 0))
    display.fill((0, 0, 0))
    slide = slide_deck[current_slide]
    y_offset = 0
    for line in slide.lines:
        display.blit(line.surface, (100, 100 + y_offset))
        y_offset += 1.3 * line.rect.height

    #display.blit(text_surface, text_location)
    pygame.display.flip()

    # Wait for next frame.
    clock.tick(30)

# Done.
pygame.quit()

