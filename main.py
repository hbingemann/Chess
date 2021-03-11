# ---------------------------------------------------
# |                    CHESS                        |
# ---------------------------------------------------

import pygame

SIZE = WIDTH, HEIGHT = 800, 800
FPS = 60


def draw_board(surface):
    col = None
    for x in range(8):
        for y in range(8):
            if (x + y) % 2 == 0:  # to make checkered pattern
                col = "#61a055"
            else:
                col = "#ebf2d2"
            pygame.draw.rect(surface, col, (x * WIDTH // 8, y * WIDTH // 8, WIDTH, HEIGHT))


if __name__ == '__main__':  # running the game
    # setting some values that will be useful
    screen = pygame.display.set_mode(SIZE)
    pygame.display.set_caption('CHESS')

    draw_board(screen)

    # game loop
    run = True
    clock = pygame.time.Clock()
    while run:
        # regulate game speed and calculate some elapsed time for inputs
        clock.tick(FPS)

        # check events
        for event in pygame.event.get():

            # close window
            if event.type == pygame.QUIT:
                run = False

        pygame.display.update()

    pygame.quit()
