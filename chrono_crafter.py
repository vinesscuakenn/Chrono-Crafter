import pygame
import asyncio
import platform
from typing import List, Tuple
from collections import deque

# Initialize Pygame
pygame.init()

# Screen settings
WIDTH, HEIGHT = 800, 600
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Chrono Crafter")

# Colors
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
BROWN = (139, 69, 19)
GOLD = (255, 215, 0)
GRAY = (169, 169, 169)

# Game settings
TILE_SIZE = 40
PLAYER_SIZE = 30
GEAR_SIZE = 15
FPS = 60
MAX_TIME_STATES = 100
REWIND_DURATION = 2000  # milliseconds

class Player:
    def __init__(self, x: int, y: int):
        self.x = x * TILE_SIZE + TILE_SIZE // 2
        self.y = y * TILE_SIZE + TILE_SIZE // 2
        self.vx = 0
        self.vy = 0
        self.history: deque = deque(maxlen=MAX_TIME_STATES)

    def move(self, maze: List[List[int]]) -> bool:
        new_x, new_y = self.x + self.vx, self.y + self.vy
        player_rect = pygame.Rect(new_x - PLAYER_SIZE // 2, new_y - PLAYER_SIZE // 2, PLAYER_SIZE, PLAYER_SIZE)
        for i in range(len(maze)):
            for j in range(len(maze[0])):
                if maze[i][j] == 1:
                    wall_rect = pygame.Rect(j * TILE_SIZE, i * TILE_SIZE, TILE_SIZE, TILE_SIZE)
                    if player_rect.colliderect(wall_rect):
                        return False
        self.x, self.y = new_x, new_y
        self.history.append((self.x, self.y))
        return True

    def rewind(self):
        if self.history:
            self.x, self.y = self.history.pop()
            return True
        return False

    def draw(self):
        pygame.draw.circle(screen, BROWN, (int(self.x), int(self.y)), PLAYER_SIZE // 2)

class Game:
    def __init__(self):
        self.maze = [
            [1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1],
            [1, 2, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 1],
            [1, 0, 1, 1, 1, 0, 1, 1, 1, 0, 1, 1, 1, 0, 1, 1, 1, 0, 0, 1],
            [1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 1],
            [1, 0, 1, 1, 1, 0, 1, 1, 1, 0, 1, 3, 1, 0, 1, 1, 1, 0, 0, 1],
            [1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 1],
            [1, 0, 1, 1, 1, 0, 1, 1, 1, 0, 1, 1, 1, 0, 1, 1, 1, 0, 0, 1],
            [1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 1],
            [1, 0, 1, 1, 1, 0, 1, 1, 1, 0, 1, 3, 1, 0, 1, 1, 1, 0, 0, 1],
            [1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 1],
            [1, 0, 1, 1, 1, 0, 1, 1, 1, 0, 1, 1, 1, 0, 1, 1, 1, 0, 0, 1],
            [1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 4, 1],
            [1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1]
        ]
        self.player = None
        self.gears = []
        self.exit_pos = (0, 0)
        self.gear_count = 0
        self.collected_gears = 0
        self.rewinding = False
        self.rewind_start = 0
        self.font = pygame.font.SysFont("arial", 24)
        self.clock = pygame.time.Clock()
        self.setup_level()

    def setup_level(self):
        for i in range(len(self.maze)):
            for j in range(len(self.maze[0])):
                if self.maze[i][j] == 2:
                    self.player = Player(j, i)
                elif self.maze[i][j] == 3:
                    self.gears.append((j * TILE_SIZE + TILE_SIZE // 2, i * TILE_SIZE + TILE_SIZE // 2))
                    self.gear_count += 1
                elif self.maze[i][j] == 4:
                    self.exit_pos = (j * TILE_SIZE + TILE_SIZE // 2, i * TILE_SIZE + TILE_SIZE // 2)

    def draw(self):
        screen.fill(BLACK)
        for i in range(len(self.maze)):
            for j in range(len(self.maze[0])):
                if self.maze[i][j] == 1:
                    pygame.draw.rect(screen, GRAY, (j * TILE_SIZE, i * TILE_SIZE, TILE_SIZE, TILE_SIZE))
                elif self.maze[i][j] == 3:
                    pygame.draw.circle(screen, GOLD, (j * TILE_SIZE + TILE_SIZE // 2, i * TILE_SIZE + TILE_SIZE // 2), GEAR_SIZE)
                elif self.maze[i][j] == 4:
                    pygame.draw.rect(screen, BROWN, (j * TILE_SIZE, i * TILE_SIZE, TILE_SIZE, TILE_SIZE))
        self.player.draw()
        for gear in self.gears:
            pygame.draw.circle(screen, GOLD, gear, GEAR_SIZE)
        gear_text = self.font.render(f"Gears: {self.collected_gears}/{self.gear_count}", True, WHITE)
        screen.blit(gear_text, (10, 10))
        if self.rewinding:
            rewind_text = self.font.render("Rewinding...", True, WHITE)
            screen.blit(rewind_text, (10, 40))

async def main():
    game = Game()
    running = True
    while running:
        current_time = pygame.time.get_ticks()
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_SPACE and not game.rewinding:
                    game.rewinding = True
                    game.rewind_start = current_time
                elif event.key in [pygame.K_LEFT, pygame.K_RIGHT, pygame.K_UP, pygame.K_DOWN]:
                    game.player.vx = 0
                    game.player.vy = 0
                    if event.key == pygame.K_LEFT:
                        game.player.vx = -5
                    elif event.key == pygame.K_RIGHT:
                        game.player.vx = 5
                    elif event.key == pygame.K_UP:
                        game.player.vy = -5
                    elif event.key == pygame.K_DOWN:
                        game.player.vy = 5
            elif event.type == pygame.KEYUP:
                if event.key in [pygame.K_LEFT, pygame.K_RIGHT]:
                    game.player.vx = 0
                elif event.key in [pygame.K_UP, pygame.K_DOWN]:
                    game.player.vy = 0

        if not game.rewinding:
            game.player.move(game.maze)
        elif current_time - game.rewind_start < REWIND_DURATION:
            game.player.rewind()
        else:
            game.rewinding = False

        player_rect = pygame.Rect(game.player.x - PLAYER_SIZE // 2, game.player.y - PLAYER_SIZE // 2, PLAYER_SIZE, PLAYER_SIZE)
        for gear in game.gears[:]:
            gear_rect = pygame.Rect(gear[0] - GEAR_SIZE, gear[1] - GEAR_SIZE, GEAR_SIZE * 2, GEAR_SIZE * 2)
            if player_rect.colliderect(gear_rect):
                game.gears.remove(gear)
                game.collected_gears += 1
                game.maze[gear[1] // TILE_SIZE][gear[0] // TILE_SIZE] = 0

        if game.collected_gears == game.gear_count:
            exit_rect = pygame.Rect(game.exit_pos[0] - TILE_SIZE // 2, game.exit_pos[1] - TILE_SIZE // 2, TILE_SIZE, TILE_SIZE)
            if player_rect.colliderect(exit_rect):
                running = False  # Win condition

        game.draw()
        pygame.display.flip()
        game.clock.tick(FPS)
        await asyncio.sleep(1.0 / FPS)

    pygame.quit()

if platform.system() == "Emscripten":
    asyncio.ensure_future(main())
else:
    if __name__ == "__main__":
        asyncio.run(main())
