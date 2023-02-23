#!/usr/bin/env python3

import pygame
import pygame.freetype

import io
import sys


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


max_line_height = 0

class Line:
   text: str
   row: int
   color: Tuple[int, int, int]
   surface: pygame.Surface
   rect: pygame.Rect

   def __init__(self, text: str, row: int, color: Tuple[int, int, int]):
       global max_line_height
       self.text = text
       self.row = row
       self.color = color
       self.surface, self.rect = font.render(text, color)
       max_line_height = max(max_line_height, self.rect.height)

@dataclass
class Slide:
    lines: List[Line]

    def shown(self, slide_index: int):
        pass

    def render(self):
        for line in self.lines:
            display.blit(line.surface, (100, 100 + max_line_height * line.row))


@dataclass
class LineTransition:
    start_line_index: int
    end_line_index: int

@dataclass
class SlideTransition:
    line_transitions: List[LineTransition]

    def shown(self, slide_index: int):
        global slide_deck
        self.index = slide_index
        self.start_time = pygame.time.get_ticks()
        self.start_slide: Slide = slide_deck[slide_index - 1]
        self.end_slide: Slide = slide_deck[slide_index + 1]

    def render(self):
        now = pygame.time.get_ticks()
        for transition in self.line_transitions:
            start_height = 100 + max_line_height * transition.start_line_index
            end_height = 100 + max_line_height * transition.end_line_index
            t = max(0.0, min(1.0, (now - self.start_time) / 1000))
            height = start_height + t * (end_height - start_height)
            display.blit(self.start_slide.lines[transition.start_line_index].surface, (100, height))
        if now >= self.start_time + 1000:
            change_slide(self.index + 1)

white = (255, 255, 255)

def parse_slide(lines, i, slide_deck):
    line = lines[i]
    assert line.startswith("#s ")
    title = line[3:]  # TODO: Use title.
    slide: Slide = Slide([])
    row: int = 0
    for l in range(i+1, len(lines)):
        line = lines[l]
        if line.startswith("#s ") or line.startswith("#t "):
            slide_deck.append(slide)
            return l
        slide.lines.append(Line(line, row, white))
        row += 1
    slide_deck.append(slide)
    return l + 1

def parse_transition(lines, i, slide_deck):
    line = lines[i]
    assert line.startswith("#t ")
    line = line[3:]
    pairs = line.split(" ")
    transition: SlideTransition = SlideTransition([])
    for pair in pairs:
        start_end = pair.split(",")
        start = int(start_end[0])
        end = int(start_end[1])
        transition.line_transitions.append(LineTransition(start, end))
    slide_deck.append(transition)
    return i + 1

def parse(lines):
    slide_deck = []
    i = 0
    while i < len(lines):
        line = lines[i]
        if line.startswith("#s "):
            i = parse_slide(lines, i, slide_deck)
        elif line.startswith("#t "):
            i = parse_transition(lines, i, slide_deck)
        elif line.strip() == "":
            i = i + 1
        else:
            raise ValueError(f"Anim Text Slides: Parse error at line {i}: Expected a new slide or transition, got '{line}'.")
    return slide_deck


with io.open(sys.argv[1]) as f:
    slide_deck = parse(f.read().splitlines())


current_slide: int = 0
def change_slide(new_slide: int):
    global current_slide
    current_slide = new_slide
    slide_deck[current_slide].shown(current_slide)

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
               change_slide((current_slide + 1) % len(slide_deck))
            elif event.key == pygame.K_BACKSPACE or event.key == pygame.K_LEFT:
                change_slide((current_slide - 1) if current_slide > 0 else len(slide_deck) - 1)

    # Update game state.
    # now = pygame.time.get_ticks()
    # seconds = now / 1000

    # text_t = max(0.0, min(1.0, (now - text_start_time) / text_duration))
    # text_location = tuple(map(lambda start, end: int(start + (text_t * (end - start))), text_start, text_end))

    # Render.
    # display.fill(((seconds * 10) % 255, 0, 0))
    display.fill((0, 0, 0))
    slide = slide_deck[current_slide]
    slide.render()

    #display.blit(text_surface, text_location)
    pygame.display.flip()

    # Wait for next frame.
    clock.tick(30)

# Done.
pygame.quit()

