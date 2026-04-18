#!/usr/bin/env python3
import sys
import os

os.environ["TERM"] = "xterm-256color"

import curses
import random
import time
import math


class SnowSimulator:
    def __init__(self):
        self.snowflakes = []
        self.piled_snow = {}
        self.temperature = 0
        self.wind = 0
        self.snow_intensity = 1.0
        self.frame_count = 0
        self.melt_timer = 0

    def init_pile_map(self, width, height):
        ground_y = height - 3
        self.piled_snow = {x: ground_y for x in range(width)}

    def spawn_snowflake(self, width):
        intensity = int(self.snow_intensity * 10)
        for _ in range(intensity):
            self.snowflakes.append(
                {
                    "x": random.randint(0, width - 1),
                    "y": random.randint(-5, -1),
                    "speed": random.uniform(1.0, 3.0),
                    "drift": random.uniform(-0.3, 0.3),
                    "size": random.choice([1, 1, 2, 2, 3]),
                    "rotation": random.uniform(0, 360),
                }
            )

    def check_collapse(self, x, ground_y):
        if x not in self.piled_snow:
            return

        height = ground_y - self.piled_snow[x]

        if height > 4:
            for offset in [-1, 1]:
                nx = x + offset
                if nx in self.piled_snow:
                    neighbor_height = ground_y - self.piled_snow[nx]
                    if height - neighbor_height >= 3:
                        self.piled_snow[x] = self.piled_snow[nx] + 1
                        return

        if height > 6:
            self.piled_snow[x] = ground_y - 2

    def update(self, width, height, dt):
        self.frame_count += 1

        self.temperature += (random.random() - 0.5) * 2 * dt
        self.temperature = max(-15, min(5, self.temperature))

        if self.temperature > 2:
            self.melt_timer += dt
            if self.melt_timer > 2:
                self.melt_timer = 0
                for x in list(self.piled_snow.keys()):
                    if random.random() < 0.3 * (self.temperature / 5):
                        self.piled_snow[x] = min(self.piled_snow[x] + 1, height - 3)
        else:
            self.melt_timer = 0

        self.wind += (random.random() - 0.5) * 1.5 * dt
        self.wind = max(-3, min(3, self.wind))

        self.snow_intensity += (random.random() - 0.5) * 0.1 * dt
        self.snow_intensity = max(0.3, min(2.0, self.snow_intensity))

        ground_y = height - 3

        for flake in self.snowflakes:
            base_wind = self.wind

            if self.temperature < -5 and flake["size"] >= 2:
                base_wind *= 0.7

            flake["y"] += flake["speed"] * dt * 15
            flake["x"] += (base_wind + flake["drift"]) * dt * 5
            flake["rotation"] += dt * 30

            pile_height = self.piled_snow.get(int(flake["x"]), ground_y)

            if flake["y"] >= pile_height:
                px = int(flake["x"])
                if 0 <= px < width:
                    if self.temperature <= 2:
                        current_pile = self.piled_snow.get(px, ground_y)
                        if current_pile > ground_y - 10:
                            self.piled_snow[px] = current_pile - 1
                            self.check_collapse(px, ground_y)
                    flake["y"] = -10

        self.snowflakes = [
            f for f in self.snowflakes if -15 <= f["x"] < width and f["y"] < height
        ]

        if len(self.snowflakes) < int(self.snow_intensity * 80):
            self.spawn_snowflake(width)

    def render(self, stdscr, width, height):
        stdscr.erase()

        ground_y = height - 3

        for x in range(width - 1):
            if x in self.piled_snow:
                pile_height = self.piled_snow[x]
                for y in range(int(pile_height), ground_y + 1):
                    if 0 <= y < height - 1:
                        try:
                            dist_from_ground = ground_y - y
                            if dist_from_ground == 0:
                                char = "_"
                            elif dist_from_ground == 1:
                                char = random.choice([".", ",", "~"])
                            elif dist_from_ground == 2:
                                char = "*"
                            else:
                                char = random.choice(["@", "#", "*"])
                            color = (
                                curses.color_pair(7)
                                if dist_from_ground < 3
                                else curses.color_pair(6)
                            )
                            stdscr.addch(y, x, char, color)
                        except:
                            pass

        if self.temperature > 2:
            for x in range(0, width - 1, 4):
                if random.random() < 0.2 * (self.temperature / 5):
                    y = ground_y - 1
                    try:
                        stdscr.addch(y, x, "~", curses.color_pair(3) | curses.A_BOLD)
                    except:
                        pass

        for flake in self.snowflakes:
            ix, iy = int(flake["x"]), int(flake["y"])
            if 0 <= ix < width - 1 and 0 <= iy < ground_y:
                try:
                    chars = {1: ".", 2: "*", 3: "❄"}
                    stdscr.addch(
                        iy, ix, chars.get(flake["size"], "."), curses.color_pair(2)
                    )
                except:
                    pass

        try:
            stdscr.border(0, 0, 0, 0, 0, 0, 0, 0)

            title = " ❄️  SNOW SIMULATOR  ❄️ "
            stdscr.addstr(
                0,
                (width - len(title)) // 2,
                title,
                curses.color_pair(5) | curses.A_BOLD,
            )

            info_y = height - 2

            temp_str = f"{self.temperature:.1f}°C"
            if self.temperature < -10:
                temp_color = curses.color_pair(1)
            elif self.temperature < 0:
                temp_color = curses.color_pair(4)
            else:
                temp_color = curses.color_pair(3)

            stdscr.addstr(info_y, 2, f"Temp: {temp_str}", temp_color | curses.A_BOLD)

            bar_len = int(self.snow_intensity * 8)
            bar = "▰" * bar_len + "▱" * (16 - bar_len)
            stdscr.addstr(info_y, 15, f"Intensity: {bar}", curses.color_pair(5))

            wind_indicator = (
                "◀◀◀" if self.wind < -1 else "▶▶▶" if self.wind > 1 else "───"
            )
            stdscr.addstr(info_y, 40, f"Wind: {wind_indicator}", curses.color_pair(5))

            state = (
                "MELTING"
                if self.temperature > 2
                else "FREEZING"
                if self.temperature < -5
                else "ACCUMULATING"
            )
            stdscr.addstr(
                info_y + 1, 2, f"State: {state}", curses.color_pair(8) | curses.A_BOLD
            )

            snow_depth = (
                ground_y - min(self.piled_snow.values()) if self.piled_snow else 0
            )
            stdscr.addstr(info_y + 1, 20, f"Depth: {snow_depth}", curses.color_pair(8))

            stdscr.addstr(
                1, 2, "[+/-] Intensity  [T] Temperature  [Q]uit", curses.color_pair(8)
            )

            stats = f"Flakes: {len(self.snowflakes)}"
            stdscr.addstr(1, width - len(stats) - 2, stats, curses.color_pair(8))

        except:
            pass

        stdscr.refresh()


def main(stdscr):
    try:
        curses.curs_set(0)
    except:
        pass

    try:
        curses.start_color()
        curses.use_default_colors()
    except:
        pass

    try:
        curses.init_pair(1, curses.COLOR_CYAN, -1)
        curses.init_pair(2, curses.COLOR_WHITE, -1)
        curses.init_pair(3, curses.COLOR_BLUE, -1)
        curses.init_pair(4, curses.COLOR_MAGENTA, -1)
        curses.init_pair(5, curses.COLOR_GREEN, -1)
        curses.init_pair(6, curses.COLOR_WHITE, -1)
        curses.init_pair(7, curses.COLOR_YELLOW, -1)
        curses.init_pair(8, curses.COLOR_BLACK, -1)
    except:
        pass

    height, width = stdscr.getmaxyx()
    width = max(30, width - 1)
    height = max(15, height - 1)

    simulator = SnowSimulator()
    simulator.init_pile_map(width, height)

    last_time = time.time()

    stdscr.nodelay(True)

    while True:
        current_time = time.time()
        dt = current_time - last_time
        dt = min(dt, 0.1)
        last_time = current_time

        simulator.update(width, height, dt)
        simulator.render(stdscr, width, height)

        curses.napms(50)

        try:
            key = stdscr.getch()
            if key == ord("q") or key == ord("Q"):
                break
            elif key == ord("+") or key == ord("="):
                simulator.snow_intensity = min(2.0, simulator.snow_intensity + 0.1)
            elif key == ord("-"):
                simulator.snow_intensity = max(0.3, simulator.snow_intensity - 0.1)
            elif key == ord("t") or key == ord("T"):
                simulator.temperature = -simulator.temperature - 5
                simulator.temperature = max(-15, min(5, simulator.temperature))
            elif key == ord("w") or key == ord("W"):
                simulator.wind = -simulator.wind * 1.5
        except:
            pass


def run():
    curses.wrapper(main)
