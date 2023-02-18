import pygame

pygame.init()
pygame.display.set_mode((1920, 1080))
clock = pygame.time.Clock()
pygame.display.set_caption("Animated Text Slides")
display = pygame.display.get_surface()
request_quit = False
while not request_quit:
    seconds = pygame.time.get_ticks() / 1000
    display.fill(((seconds * 10) % 255, 0, 0))
    events = pygame.event.get()
    for event in events:
        if event.type == pygame.QUIT:
            request_quit = True
        elif event.type == pygame.KEYDOWN:
            if event.key == pygame.K_ESCAPE:
                request_quit = True
    pygame.display.flip()
    clock.tick(30)
pygame.quit()
