from __future__ import annotations

from threading import Thread
from typing import TYPE_CHECKING, List, Tuple

Pos = Size = Tuple[int, int]

if TYPE_CHECKING:
    import pygame
else:
    pygame = None


class PygameMainloop:
    pygame = None
    if TYPE_CHECKING:
        pygame = pygame
    screen: pygame.Surface
    clock: pygame.time.Clock
    running: bool
    thread: Thread = None

    def __init__(self, renderers: List[PygameSurfaceRenderer], handlers: List[PygameEventHandler], screen_size: Size, fps: int):
        self.handlers = handlers
        self.renderers = renderers
        self.fps = fps
        self.screen_size = screen_size

    def run(self):
        import pygame
        pygame.init()
        self.pygame = pygame
        for r in self.renderers:
            r.pygame = pygame
        for h in self.handlers:
            h.pygame = pygame
        self.screen = pygame.display.set_mode(self.screen_size)
        self.clock = pygame.time.Clock()
        self.running = True
        while self.running:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    self.running = False
                for handler in self.handlers:
                    handler.handle(event)
            for r in self.renderers:
                r.render(self.screen, self.clock)
            self.clock.tick(self.fps)
            self.pygame.display.update()

    def start_background(self, daemon=False):
        assert self.thread is None
        self.thread = Thread(target=self.run, daemon=daemon)
        self.thread.start()


class PygameSurfaceRenderer:
    if TYPE_CHECKING:
        pygame = pygame

    def render(self, screen: pygame.Surface, clock: pygame.time.Clock):
        raise NotImplementedError


class PygameEventHandler:
    if TYPE_CHECKING:
        pygame = pygame

    def handle(self, event: pygame.event.EventType):
        raise NotImplementedError
