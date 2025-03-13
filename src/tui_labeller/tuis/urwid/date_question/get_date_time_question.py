import calendar
import datetime

import urwid

from src.tui_labeller.file_read_write_helper import write_to_file


class DateTimeEdit(urwid.Edit):
    def __init__(self, caption, date_only=False, **kwargs):
        super().__init__(caption, **kwargs)
        self.date_only = date_only
        self.error_text = urwid.Text("")
        self.help_text = urwid.Text("")
        self.date_parts = [4, 2, 2]  # year, month, day
        self.time_parts = [2, 2]  # hour, minute
        self.current_part = 0
        self.date_values = [None, None, None]  # year, month, day
        self.time_values = [None, None]  # hour, minute
        self.date_separator = "-"
        self.time_separator = ":"
        # TODO 1: Start with today as default value
        today = datetime.datetime.now()
        self.date_values = [today.year, today.month, today.day]
        if not self.date_only:
            self.time_values = [today.hour, today.minute]
        self.update_text()  # Set initial text based on today's date/time
        # TODO 2: Allow showing an autocomplete suggestion (we'll add a simple placeholder for this)
        self.suggestion = None

    def valid_char(self, ch):
        if (
            ch.isdigit()
            or ch == self.date_separator
            or (not self.date_only and ch == self.time_separator)
        ):
            return True
        else:
            self.error_text.set_text(f"invalid character entered: '{ch}'")
            return False

    def keypress(self, size, key):
        current_pos: int = self.edit_pos
        write_to_file(
            filename="eg.txt",
            content=f"key={key}, current_pos={current_pos}",
            append=True,
        )
        if key == "ctrl h":
            self.show_help()
            return None
        # TODO 4: Ensure that enter moves to the next answer box
        if key == "enter":
            return (  # Signal to move to the next box (already implemented)
                "enter"
            )
        # TODO 3: Ensure that pressing "Tab" moves it to the next segment
        if key == "tab":
            if (
                self.suggestion
            ):  # If there's a suggestion, accept it (placeholder for TODO 2)
                self.accept_suggestion()
            else:
                self.move_to_next_part()
            return None
        # TODO 5: Ensure that left/right moves the cursor per digit
        if key == "left":
            if current_pos > 0:
                self.set_edit_pos(current_pos - 1)
            else:
                raise NotImplementedError(
                    "Specify what to do after beginning is reached, going left."
                )
        if key == "right":
            write_to_file(
                filename="eg.txt",
                content=(
                    f"key={key},"
                    f" current_pos={current_pos},self.get_edit_text()={self.get_edit_text()}"
                ),
                append=True,
            )
            if current_pos < len(self.get_edit_text()):
                self.set_edit_pos(current_pos + 1)
            else:
                raise NotImplementedError(
                    "Specify what to do after end is reached, going right."
                )
            return None
        if key == "up" or key == "down":
            self.adjust_value(key)
            return None

        result = super().keypress(size, key)
        if result:
            self.error_text.set_text("")  # Clear error on valid input
            self.update_values()
        return result

    def update_values(self):
        text = self.get_edit_text()
        if self.date_only:
            parts = text.split(self.date_separator)
            for i, part in enumerate(parts):
                if part:
                    try:
                        self.date_values[i] = int(part)
                    except ValueError:
                        self.date_values[i] = None
        else:
            date_time_parts = text.split(" ")
            if len(date_time_parts) > 0:
                date_parts = date_time_parts[0].split(self.date_separator)
                for i, part in enumerate(date_parts):
                    if part:
                        try:
                            self.date_values[i] = int(part)
                        except ValueError:
                            self.date_values[i] = None
            if len(date_time_parts) > 1:
                time_parts = date_time_parts[1].split(self.time_separator)
                for i, part in enumerate(time_parts):
                    if part:
                        try:
                            self.time_values[i] = int(part)
                        except ValueError:
                            self.time_values[i] = None

    def move_to_next_part(self):
        if self.date_only:
            if self.current_part < len(self.date_parts) - 1:
                self.current_part += 1
        else:
            if (
                self.current_part
                < len(self.date_parts) + len(self.time_parts) - 1
            ):
                self.current_part += 1
        self.update_cursor()

    def move_to_previous_part(self):
        if self.current_part > 0:
            self.current_part -= 1
        self.update_cursor()

    def update_cursor(self):
        cursor_pos = 0
        if self.date_only:
            for i in range(self.current_part):
                cursor_pos += self.date_parts[i] + 1
        else:
            if self.current_part < len(self.date_parts):
                for i in range(self.current_part):
                    cursor_pos += self.date_parts[i] + 1
            else:
                cursor_pos = (
                    sum(self.date_parts) + 1
                )  # Skip date part and space
                for i in range(self.current_part - len(self.date_parts)):
                    cursor_pos += self.time_parts[i] + 1
        self.set_edit_pos(cursor_pos)

    def adjust_value(self, direction):
        if self.date_only:
            if self.current_part == 0:
                self.adjust_year(direction)
            elif self.current_part == 1:
                self.adjust_month(direction)
            elif self.current_part == 2:
                self.adjust_day(direction)
        else:
            if self.current_part == 0:
                self.adjust_year(direction)
            elif self.current_part == 1:
                self.adjust_month(direction)
            elif self.current_part == 2:
                self.adjust_day(direction)
            elif self.current_part == 3:
                self.adjust_hour(direction)
            elif self.current_part == 4:
                self.adjust_minute(direction)
        self.update_text()

    def adjust_year(self, direction):
        if self.date_values[0] is None:
            self.date_values[0] = 2024
        if direction == "up":
            self.date_values[0] += 1
        elif direction == "down":
            self.date_values[0] -= 1

    def adjust_month(self, direction):
        if self.date_values[1] is None:
            self.date_values[1] = 1
        if direction == "up":
            self.date_values[1] = (self.date_values[1] % 12) + 1
        elif direction == "down":
            self.date_values[1] = (self.date_values[1] - 2) % 12 + 1
        # TODO in adjust_month: Check if day is still valid after month change
        if self.date_values[2] is not None:
            max_days = self.get_max_days()
            if self.date_values[2] > max_days:
                self.date_values[2] = max_days

    def adjust_day(self, direction):
        if self.date_values[2] is None:
            self.date_values[2] = 1
        max_days = self.get_max_days()
        if direction == "up":
            self.date_values[2] = (self.date_values[2] % max_days) + 1
        elif direction == "down":
            self.date_values[2] = (self.date_values[2] - 2) % max_days + 1

    def adjust_hour(self, direction):
        if self.time_values[0] is None:
            self.time_values[0] = 0
        if direction == "up":
            self.time_values[0] = (self.time_values[0] + 1) % 24
        elif direction == "down":
            self.time_values[0] = (self.time_values[0] - 1) % 24

    def adjust_minute(self, direction):
        if self.time_values[1] is None:
            self.time_values[1] = 0
        if direction == "up":
            self.time_values[1] = (self.time_values[1] + 1) % 60
        elif direction == "down":
            self.time_values[1] = (self.time_values[1] - 1) % 60

    def get_max_days(self):
        if self.date_values[0] is None or self.date_values[1] is None:
            return 31
        try:
            _, max_days = calendar.monthrange(
                self.date_values[0], self.date_values[1]
            )
            return max_days
        except ValueError:
            return 31

    def update_text(self):
        date_str = self.date_separator.join(
            map(
                lambda x: str(x).zfill(2) if x is not None else "00",
                self.date_values,
            )
        )
        if self.date_only:
            self.set_edit_text(date_str)
        else:
            time_str = self.time_separator.join(
                map(
                    lambda x: str(x).zfill(2) if x is not None else "00",
                    self.time_values,
                )
            )
            self.set_edit_text(date_str + " " + time_str)

    # Placeholder for TODO 2: Autocomplete suggestion
    def accept_suggestion(self):
        if self.suggestion:
            self.set_edit_text(self.suggestion)
            self.update_values()
            self.suggestion = None

    def show_help(self):
        self.help_text.set_text(
            "Use arrows to adjust, Tab to move parts, Enter to next field"
        )
