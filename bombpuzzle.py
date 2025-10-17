import curses
import random
import shutil
import sys

GRID_SIZE = 25
NUM_BOMBS = 3
TARGETS_PER_BOMB = (5, 10)

def check_terminal_size(grid_size):
    cols, rows = shutil.get_terminal_size()
    required_cols = grid_size * 2
    required_rows = grid_size + 3
    if cols < required_cols or rows < required_rows:
        print(f"Error: Terminal too small for {grid_size}×{grid_size} grid.")
        print(f"Required: {required_cols}×{required_rows}, Available: {cols}×{rows}")
        sys.exit(1)

def generate_targets(grid_size, bomb_positions):
    def get_attacks(x, y):
        attacks = set()
        for i in range(grid_size):
            attacks.add((x, i))
            attacks.add((i, y))
            for dx, dy in [(x - i, y - i), (x + i, y + i), (x + i, y - i), (x - i, y + i)]:
                if 0 <= dx < grid_size and 0 <= dy < grid_size:
                    attacks.add((dx, dy))
        attacks.discard((x, y))
        return list(attacks)

    targets = set()
    for bx, by in bomb_positions:
        attackable = [pos for pos in get_attacks(bx, by) if pos not in bomb_positions]
        count = random.randint(*TARGETS_PER_BOMB)
        if attackable:
            targets.update(random.sample(attackable, min(count, len(attackable))))
    return targets

def get_covered_by_bombs(grid_size, placed_bombs):
    covered = set()
    for bx, by in placed_bombs:
        for i in range(grid_size):
            covered.add((bx, i))
            covered.add((i, by))
            for dx, dy in [(bx - i, by - i), (bx + i, by + i), (bx + i, by - i), (bx - i, by + i)]:
                if 0 <= dx < grid_size and 0 <= dy < grid_size:
                    covered.add((dx, dy))
    return covered

def main(stdscr):
    curses.curs_set(0)
    curses.start_color()

    curses.init_pair(1, curses.COLOR_BLACK, curses.COLOR_WHITE)
    curses.init_pair(2, curses.COLOR_BLACK, curses.COLOR_BLACK)
    curses.init_pair(3, curses.COLOR_BLACK, curses.COLOR_RED)
    curses.init_pair(4, curses.COLOR_BLACK, curses.COLOR_BLUE)
    curses.init_pair(5, curses.COLOR_BLACK, curses.COLOR_YELLOW)
    curses.init_pair(6, curses.COLOR_BLACK, curses.COLOR_GREEN)
    curses.init_pair(7, curses.COLOR_BLACK, curses.COLOR_MAGENTA)

    hidden_bombs = set()
    while len(hidden_bombs) < NUM_BOMBS:
        hidden_bombs.add((random.randint(0, GRID_SIZE - 1), random.randint(0, GRID_SIZE - 1)))
    targets = generate_targets(GRID_SIZE, hidden_bombs)

    placed_bombs = set()
    cursor_x, cursor_y = 0, 0
    game_over = False
    reveal_hidden = False
    message = ""

    def draw():
        stdscr.clear()
        covered = get_covered_by_bombs(GRID_SIZE, placed_bombs)
        for y in range(GRID_SIZE):
            for x in range(GRID_SIZE):
                is_light = (x + y) % 2 == 0
                color = curses.color_pair(1 if is_light else 2)
                if (x, y) in targets:
                    color = curses.color_pair(6 if (x, y) in covered else 3)
                if (x, y) in placed_bombs:
                    color = curses.color_pair(4)
                if reveal_hidden and (x, y) in hidden_bombs:
                    color = curses.color_pair(7)
                if not game_over and (x, y) == (cursor_x, cursor_y):
                    color = curses.color_pair(5)
                stdscr.addstr(y, x * 2, "  ", color)
        stdscr.addstr(GRID_SIZE + 1, 0, f"Bombs placed: {len(placed_bombs)} / {NUM_BOMBS}")
        if message:
            stdscr.addstr(GRID_SIZE + 2, 0, message)
        stdscr.refresh()

    while True:
        draw()
        key = stdscr.getch()
        if key == 27: break
        elif not game_over:
            if key in [curses.KEY_UP, ord('w')]: cursor_y = max(0, cursor_y - 1)
            elif key in [curses.KEY_DOWN, ord('s')]: cursor_y = min(GRID_SIZE - 1, cursor_y + 1)
            elif key in [curses.KEY_LEFT, ord('a')]: cursor_x = max(0, cursor_x - 1)
            elif key in [curses.KEY_RIGHT, ord('d')]: cursor_x = min(GRID_SIZE - 1, cursor_x + 1)
            elif key == ord(' '):
                if (cursor_x, cursor_y) not in targets and (cursor_x, cursor_y) not in placed_bombs:
                    if len(placed_bombs) < NUM_BOMBS:
                        placed_bombs.add((cursor_x, cursor_y))
                        if len(placed_bombs) == NUM_BOMBS:
                            game_over = True
                            covered = get_covered_by_bombs(GRID_SIZE, placed_bombs)
                            message = "You win! Press any key to exit." if targets.issubset(covered) else "You lose! Press any key to exit."
                            reveal_hidden = True
                            draw()
                            stdscr.getch()
                            break

check_terminal_size(GRID_SIZE)
curses.wrapper(main)