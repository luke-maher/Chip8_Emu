import random as r
import pygame


class Cpu:
    def __init__(self, screen):
        self.pc = 0x200
        self.current_operation = 0
        self.v = [0] * 16
        self.memory = [0] * 4096
        self.stack = [0] * 16
        self.sp = 0
        self.index = 0
        self.sound_timer = 0
        self.delay_timer = 0
        self.screen = screen

        fontset = [
            0xF0, 0x90, 0x90, 0x90, 0xF0,
            0x20, 0x60, 0x20, 0x20, 0x70,
            0xF0, 0x10, 0xF0, 0x80, 0xF0,
            0xF0, 0x10, 0xF0, 0x10, 0xF0,
            0x90, 0x90, 0xF0, 0x10, 0x10,
            0xF0, 0x80, 0xF0, 0x10, 0xF0,
            0xF0, 0x80, 0xF0, 0x90, 0xF0,
            0xF0, 0x10, 0x20, 0x40, 0x40,
            0xF0, 0x90, 0xF0, 0x90, 0xF0,
            0xF0, 0x90, 0xF0, 0x10, 0xF0,
            0xF0, 0x90, 0xF0, 0x90, 0x90,
            0xE0, 0x90, 0xE0, 0x90, 0xE0,
            0xF0, 0x80, 0x80, 0x80, 0xF0,
            0xE0, 0x90, 0x90, 0x90, 0xE0,
            0xF0, 0x80, 0xF0, 0x80, 0xF0,
            0xF0, 0x80, 0xF0, 0x80, 0x80
        ]

        self.memory[:len(fontset)] = fontset

        self.opcode_lookup = {
            0x0: self.get_0_operation,
            0x1: self.jump_to_address,
            0x2: self.jump_to_subroutine,
            0x3: self.skip_if_reg_equals_val,
            0x4: self.skip_if_reg_not_equals_val,
            0x5: self.skip_if_reg_equal_reg,
            0x6: self.move_value_to_reg,
            0x7: self.add_value_to_reg,
            0x8: self.get_8_operation,
            0x9: self.skip_if_reg_not_equal_reg,
            0xa: self.load_index_reg_with_value,
            0xb: self.jump_to_index_plus_value,
            0xc: self.generate_random_number,
            0xd: self.draw_sprite,
            0xe: self.get_e_operation,
            0xf: self.get_f_operation
        }

        self.zero_opcode_lookup = {
            0xe0: self.clear_screen,
            0xee: self.return_from_subroutine,
            0: self.nothing
        }

        self.eight_opcode_lookup = {
            0x0: self.move_reg_into_reg,
            0x1: self.logical_or,
            0x2: self.logical_and,
            0x3: self.exclusive_or,
            0x4: self.add_reg_to_reg,
            0x5: self.subtract_reg_from_reg,
            0x6: self.right_shift_reg,
            0x7: self.subtract_reg_from_reg1,
            0xe: self.left_shift_reg
        }

        self.f_opcode_lookup = {
            0x07: self.move_delay_timer_into_reg,
            0x0a: self.wait_for_keypress,
            0x15: self.move_reg_into_delay_timer,
            0x18: self.move_reg_into_sound_timer,
            0x1e: self.add_index_with_reg,
            0x29: self.set_index_to_sprite_reg,
            0x33: self.store_bcd_of_reg_in_memory_index,
            0x55: self.store_regs_in_rpl,
            0x65: self.read_regs_from_rpl
        }

        self.e_opcode_lookup = {
            0x9e: self.skip_if_key_press,
            0xa1: self.skip_if_key_not_press
        }

        self.key_mappings = {
            0x0: pygame.K_s,
            0x1: pygame.K_1,
            0x2: pygame.K_2,
            0x3: pygame.K_3,
            0x4: pygame.K_4,
            0x5: pygame.K_q,
            0x6: pygame.K_w,
            0x7: pygame.K_e,
            0x8: pygame.K_r,
            0x9: pygame.K_a,
            0xA: pygame.K_d,
            0xB: pygame.K_f,
            0xC: pygame.K_z,
            0xD: pygame.K_x,
            0xE: pygame.K_c,
            0xF: pygame.K_v,
        }

    def load_rom(self):
        rom_data = open("roms/c8_test", 'rb').read()
        for index, val in enumerate(rom_data):
            self.memory[index + 512] = val

    def execute_opcode(self):
        self.current_operation = self.memory[self.pc] << 8 | self.memory[self.pc + 1]
        self.pc += 2
        self.opcode_lookup.get((self.current_operation & 0xf000) >> 12, self.unknown_opcode)()

    def decrease_timers(self):
        if self.delay_timer != 0:
            self.delay_timer -= 1

        if self.sound_timer != 0:
            if self.sound_timer == 1:
                print("BEEEEEEEP")
            self.sound_timer -= 1

    def get_0_operation(self):
        self.zero_opcode_lookup.get(self.current_operation & 0xff, self.unknown_opcode)()

    def get_8_operation(self):
        self.eight_opcode_lookup.get(self.current_operation & 0xf, self.unknown_opcode)()

    def get_f_operation(self):
        self.f_opcode_lookup.get(self.current_operation & 0xff, self.unknown_opcode)()

    def get_e_operation(self):
        self.e_opcode_lookup.get(self.current_operation & 0xff, self.unknown_opcode)()

    def unknown_opcode(self):
        raise Exception("Just tried to execute an unknown opcode, shouldnt happen in a bug free ROM")

    def clear_screen(self):  # 00E0 - CLS
        self.screen.clear_screen()

    def return_from_subroutine(self):  # 00EE - RET
        self.sp -= 1
        self.pc = self.stack[self.sp] << 8
        self.sp -= 1
        self.pc += self.stack[self.sp]

    def jump_to_address(self):  # 1nnn - JP addr
        addr = self.current_operation & 0x0fff
        self.pc = addr

    def jump_to_subroutine(self):  # 2nnn - CALL addr
        addr = self.current_operation & 0x0fff
        self.stack[self.sp] = self.pc & 0x00FF
        self.sp += 1
        self.stack[self.sp] = (self.pc & 0xFF00) >> 8
        self.sp += 1
        self.pc = addr

    def skip_if_reg_equals_val(self):  # 3xkk - SE Vx, byte
        x = (self.current_operation & 0x0f00) >> 8
        byte = self.current_operation & 0x00ff
        if self.v[x] == byte:
            self.pc += 2

    def skip_if_reg_not_equals_val(self):  # 4xkk - SNE Vx, byte
        x = (self.current_operation & 0x0f00) >> 8
        byte = self.current_operation & 0x00ff
        if self.v[x] != byte:
            self.pc += 2

    def skip_if_reg_equal_reg(self):  # 5xy0 - SE Vx, Vy
        x = (self.current_operation & 0x0f00) >> 8
        y = (self.current_operation & 0x00f0) >> 4
        if self.v[x] == self.v[y]:
            self.pc += 2

    def move_value_to_reg(self):  # 6xkk - LD Vx, byte
        x = (self.current_operation & 0x0f00) >> 8
        byte = self.current_operation & 0x00ff
        self.v[x] = byte

    def add_value_to_reg(self):  # 7xkk - ADD Vx, byte
        x = (self.current_operation & 0x0f00) >> 8
        byte = self.current_operation & 0x00ff
        self.v[x] += byte
        if self.v[x] > 255:
            self.v[x] -= 256

    def move_reg_into_reg(self):  # 8xy0 - LD Vx, Vy
        x = (self.current_operation & 0x0f00) >> 8
        y = (self.current_operation & 0x00f0) >> 4
        self.v[x] = self.v[y]

    def logical_or(self):  # 8xy1 - OR Vx, Vy
        x = (self.current_operation & 0x0f00) >> 8
        y = (self.current_operation & 0x00f0) >> 4
        self.v[x] |= self.v[y]

    def logical_and(self):  # 8xy2 - AND Vx, Vy
        x = (self.current_operation & 0x0f00) >> 8
        y = (self.current_operation & 0x00f0) >> 4
        self.v[x] &= self.v[y]

    def exclusive_or(self):  # 8xy3 - XOR Vx, Vy
        x = (self.current_operation & 0x0f00) >> 8
        y = (self.current_operation & 0x00f0) >> 4
        self.v[x] ^= self.v[y]

    def add_reg_to_reg(self):  # 8xy4 - ADD Vx, Vy
        x = (self.current_operation & 0x0f00) >> 8
        y = (self.current_operation & 0x00f0) >> 4
        test = self.v[x]+self.v[y]
        if test > 255:
            self.v[x] = test-256
            self.v[0xF] = 1
        else:
            self.v[x] = test
            self.v[0xF] = 0

    def subtract_reg_from_reg(self):  # 8xy5 - SUB Vx, Vy
        x = (self.current_operation & 0x0f00) >> 8
        y = (self.current_operation & 0x00f0) >> 4
        test = self.v[x] - self.v[y]
        if self.v[x] > self.v[y]:
            self.v[x] = test
            self.v[0xF] = 1
        else:
            self.v[x] = test + 256
            self.v[0xF] = 0

    def right_shift_reg(self):  # 8xy6 - SHR Vx {, Vy}
        x = (self.current_operation & 0x0f00) >> 8
        y = (self.current_operation & 0x00f0) >> 4
        self.v[0xF] = self.v[x] & 0x1
        self.v[y] = self.v[x] >> 1

    def subtract_reg_from_reg1(self):  # 8xy7 - SUBN Vx, Vy
        x = (self.current_operation & 0x0f00) >> 8
        y = (self.current_operation & 0x00f0) >> 4
        test = self.v[y] - self.v[x]
        if self.v[y] > self.v[x]:
            self.v[x] = test
            self.v[0xF] = 1
        else:
            self.v[x] = test + 256
            self.v[0xF] = 0

    def left_shift_reg(self):  # 8xyE - SHL Vx {, Vy}
        x = (self.current_operation & 0x0f00) >> 8
        y = (self.current_operation & 0x00f0) >> 4
        self.v[0xF] = (self.v[x] & 0x80) >> 8
        self.v[y] = self.v[x] << 1

    def skip_if_reg_not_equal_reg(self):  # 9xy0 - SNE Vx, Vy
        x = (self.current_operation & 0x0f00) >> 8
        y = (self.current_operation & 0x00f0) >> 4
        if self.v[x] != self.v[y]:
            self.pc += 2

    def load_index_reg_with_value(self):  # Annn - LD I, addr
        addr = self.current_operation & 0x0fff
        self.index = addr

    def jump_to_index_plus_value(self):  # Bnnn - JP V0, addr
        addr = self.current_operation & 0x0fff
        self.pc = addr + self.v[0]

    def generate_random_number(self):  # Cxkk - RND Vx, byte
        x = (self.current_operation & 0x0f00) >> 8
        byte = self.current_operation & 0x00ff
        self.v[x] = byte & r.randint(0, 255)

    def draw_sprite(self):  # Dxyn - DRW Vx, Vy, nibble
        x = self.v[(self.current_operation & 0x0f00) >> 8]
        y = self.v[(self.current_operation & 0x00f0) >> 4]
        sprite_height = self.current_operation & 0x000f
        self.v[0xf] = 0

        for y_line in range(sprite_height):
            sprite_line = self.memory[self.index+y_line]
            for x_line in range(sprite_line):
                if sprite_line & (0x80 >> x_line):
                    if self.screen.get_pixel(x + x_line, y + y_line) == 1:
                        self.v[0xf] = self.v[0xf] | 1
                    color = self.screen.get_pixel(x + x_line, y + y_line) ^ 1
                    self.screen.pixel(x + x_line, y + y_line, color)

    def skip_if_key_press(self):  # Ex9E - SKP Vx
        x = (self.current_operation & 0x0f00) >> 8
        if pygame.key.get_pressed()[self.key_mappings[x]]:
            self.pc += 2

    def skip_if_key_not_press(self):  # ExA1 - SKNP Vx
        x = (self.current_operation & 0x0f00) >> 8
        if not pygame.key.get_pressed()[self.key_mappings[x]]:
            self.pc += 2

    def move_delay_timer_into_reg(self):  # Fx07 - LD Vx, DT
        x = (self.current_operation & 0x0f00) >> 8
        self.v[x] = self.delay_timer

    def wait_for_keypress(self):  # Fx0A - LD Vx, K
        x = (self.current_operation & 0x0f00) >> 8
        key_pressed = False

        while not key_pressed:
            event = pygame.event.wait()
            if event.type == pygame.KEYDOWN:
                keys_pressed = pygame.key.get_pressed()
                for keyval, lookup_key in self.key_mappings.items():
                    if keys_pressed[lookup_key]:
                        self.v[x] = keyval
                        key_pressed = True
                        break

    def move_reg_into_delay_timer(self):  # Fx15 - LD DT, Vx
        x = (self.current_operation & 0x0f00) >> 8
        self.delay_timer = self.v[x]

    def move_reg_into_sound_timer(self):  # Fx18 - LD ST, Vx
        x = (self.current_operation & 0x0f00) >> 8
        self.sound_timer = self.v[x]

    def add_index_with_reg(self):  # Fx1E - ADD I, Vx
        x = (self.current_operation & 0x0f00) >> 8
        self.index = self.index + self.v[x]

    def set_index_to_sprite_reg(self):  # Fx29 - LD F, Vx
        x = (self.current_operation & 0x0f00) >> 8
        self.index = self.v[x]*5

    def store_bcd_of_reg_in_memory_index(self):  # Fx33 - LD B, Vx
        x = (self.current_operation & 0x0f00) >> 8
        bcd_value = '{:03d}'.format(self.v[x])
        self.memory[self.index] = int(bcd_value[0])
        self.memory[self.index + 1] = int(bcd_value[1])
        self.memory[self.index + 2] = int(bcd_value[2])

    def store_regs_in_rpl(self):  # Fx55 - LD [I], Vx
        x = (self.current_operation & 0x0f00) >> 8
        for counter in range(x + 1):
            self.memory[self.index + counter] = self.v[counter]

    def read_regs_from_rpl(self):  # Fx65 - LD Vx, [I]
        x = (self.current_operation & 0x0f00) >> 8
        for counter in range(x + 1):
            self.v[counter] = self.memory[self.index + counter]

    def nothing(self):
        raise Exception("Just tried to execute nothing, shouldnt happen in a bug free ROM")
