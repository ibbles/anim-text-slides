#!/usr/bin/env python3

"""Animated Text Slides

A code presentation tool.

Uses pygame.
Install using
    python3 -m pip install -U pygame
or some variant thereof.
"""

import pygame
import pygame.freetype

import io
import sys


from dataclasses import dataclass
from typing import List, Tuple

# Initialize pygame.
pygame.init()
pygame.display.set_mode((1920, 1080), pygame.RESIZABLE)
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
    "notomono",
]

fonts = [f for f in pygame.font.get_fonts() if f in wanted_fonts]
font_name = fonts[0] if fonts else None
font = pygame.freetype.SysFont(font_name, 20)
title_font = pygame.freetype.SysFont(font_name, 50)
text_surface, text_rect = font.render("Hello World!", (180, 180, 180))

text_start = (1000, 200)  # px
text_end = (500, 500)  # px
text_duration = 5000.0  # ms
text_start_time = pygame.time.get_ticks() + 2000  # ms

animation_duration = 500  # ms

max_line_height = 0


class Title:
    text: str
    color: Tuple[int, int, int]
    surface: pygame.Surface
    rect: pygame.Rect

    def __init__(self, text: str, color: Tuple[int, int, int]):
        self.text = text
        self.color = color
        self.surface, self.rect = title_font.render(text, color)


class Line:
    text: str
    color: Tuple[int, int, int]
    fade_in: bool
    surface: pygame.Surface
    rect: pygame.Rect

    def __init__(self, text: str, color: Tuple[int, int, int]):
        global max_line_height
        self.text = text
        self.color = color
        self.fade_in = False
        self.surface, self.rect = font.render(text, color)
        max_line_height = max(max_line_height, self.rect.height)

    def set_color(self, color: Tuple[int, int, int]):
        self.color = color
        self.surface, self.rect = font.render(self.text, color)


@dataclass
class Slide:
    title: Title
    lines: List[Line]

    def shown(self, slide_index: int, direction: int):
        self.start_time = pygame.time.get_ticks()
        if direction != 1:
            # Only run animations when stepping forward.
            for line in self.lines:
                line.fade_in = False
            return

    def render(self):
        display.blit(self.title.surface, (10, 10))
        now = pygame.time.get_ticks()
        alpha = 255 * max(0.0, min(1.0, (now - self.start_time) / 500))
        for row, line in enumerate(self.lines):
            if line.fade_in:
                line.surface.set_alpha(alpha)
            display.blit(line.surface, (100, 100 + max_line_height * row))


@dataclass
class LineTransition:
    start_line_index: int
    end_line_index: int


@dataclass
class SlideTransition:
    line_transitions: List[LineTransition]

    def shown(self, slide_index: int, direction: int):
        global slide_deck
        if direction != 1:
            # Only run animations when stepping forward.
            if direction == -1:
                change_slide(slide_index - 1, direction)
            if direction == 0:
                change_slide(slide_index + 1, direction)
            return
        self.index = slide_index
        self.start_time = pygame.time.get_ticks()
        self.start_slide: Slide = slide_deck[slide_index - 1]
        self.end_slide: Slide = slide_deck[slide_index + 1]
        any_new: bool = False
        for row in range(len(self.end_slide.lines)):
            if (
                any(t.end_line_index == row for t in self.line_transitions)
                or len(self.end_slide.lines[row].text) == 0
            ):
                self.end_slide.lines[row].set_color(gray)
            else:
                any_new = True
                self.end_slide.lines[row].set_color(white)
                self.end_slide.lines[row].fade_in = True
        if not any_new:
            for line in self.end_slide.lines:
                line.set_color(white)

    def render(self):
        display.blit(self.end_slide.title.surface, (10, 10))
        now = pygame.time.get_ticks()
        for transition in self.line_transitions:
            start_height = 100 + max_line_height * transition.start_line_index
            end_height = 100 + max_line_height * transition.end_line_index
            t = max(0.0, min(1.0, (now - self.start_time) / animation_duration))
            height = start_height + t * (end_height - start_height)
            display.blit(
                self.start_slide.lines[transition.start_line_index].surface,
                (100, height),
            )
        if now >= self.start_time + animation_duration:
            change_slide(self.index + 1, 1)


white = (255, 255, 255)
gray = (128, 128, 128)


def parse_slide(lines, i, slide_deck):
    line = lines[i]
    assert line.startswith("#s ")
    title = line[3:]
    slides: List[Slide] = [Slide(Title(title, white), [])]

    def ensure_size(n: int):
        assert len(slides) > 0  # Must have at least one slide to copy lines from.
        for i in range(len(slides), n + 1):
            slides.append(Slide(Title(title, white), slides[-1].lines[:]))

    for l in range(i + 1, len(lines)):
        line = lines[l]
        if line.startswith("#sl,"):
            separator = line.find(" ")
            separator = separator if separator >= 0 else len(line)
            properties = line[4:separator].split(",")
            text = line[separator + 1 :]
            slide_nr = int(properties[0])
            ensure_size(slide_nr)
            for i in range(slide_nr, len(slides)):
                slides[i].lines.append(Line(text, white))
        elif line.startswith("#s ") or line.startswith("#t "):
            l -= 1  # So that the +1 at the return gets us back to this line.
            break
        else:
            # slide_nr = 0 implicitly, i.e. add this line to all slides.
            for slide in slides:
                slide.lines.append(Line(line, white))
    slide_deck.extend(slides)
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
            raise ValueError(
                f"Anim Text Slides: Parse error at line {i}: Expected a new slide or"
                f" transition, got '{line}'."
            )
    return slide_deck


file: str = sys.argv[1] if len(sys.argv) == 2 else "./test_file.ats"
with io.open(file) as f:
    slide_deck = parse(f.read().splitlines())


current_slide: int = 0


def change_slide(new_slide: int, direction: int):
    """Change to a new slide.

    The new slide has its shown method called and will receive render calls
    every frame until another slide is changed to.

    new_slide: Index into slide_deck.
    direction: 1 for moving forward, -1 for moving backwards, 0 for jump.
    """
    global current_slide
    current_slide = new_slide
    slide_deck[current_slide].shown(current_slide, direction)


change_slide(0, 0)

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
                change_slide((current_slide + 1) % len(slide_deck), 1)
            elif event.key == pygame.K_BACKSPACE or event.key == pygame.K_LEFT:
                change_slide(
                    (current_slide - 1) if current_slide > 0 else len(slide_deck) - 1,
                    -1,
                )

    # Update game state.
    # Do we have any game state?

    # Render.
    display.fill((0, 0, 0))
    slide = slide_deck[current_slide]
    slide.render()
    pygame.display.flip()

    # Wait for next frame.
    clock.tick(30)

# Done.
pygame.quit()
