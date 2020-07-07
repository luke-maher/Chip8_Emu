import pygame
import cpu
import screen

screen = screen.Screen()
cpu = cpu.Cpu(screen)
cpu.load_rom()

OPCODE_TIMER = pygame.USEREVENT + 1
TIMER_TIMER = pygame.USEREVENT + 2
pygame.time.set_timer(OPCODE_TIMER, 1)
pygame.time.set_timer(TIMER_TIMER, 17)

while True:
    for event in pygame.event.get():
        if event.type == OPCODE_TIMER:
            cpu.execute_opcode()
        elif event.type == TIMER_TIMER:
            cpu.decrease_timers()
        elif event.type == pygame.QUIT:
            pygame.quit()
            exit()
