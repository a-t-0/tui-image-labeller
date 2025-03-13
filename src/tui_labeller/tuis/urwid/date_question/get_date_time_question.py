import calendar
import datetime

import urwid


class DateTimeEdit(urwid.Edit):
    # ... (the DateTimeEdit class from the previous response) ...
    def __init__(self, caption, date_only=False, **kwargs):
        super().__init__(caption, **kwargs)
        self.date_only = date_only
        self.error_text = urwid.Text("")
        self.help_text = urwid.Text("")
        self.date_parts = [4, 2, 2]  # year, month, day
        self.time_parts = [2, 2]  # hour, minute
        self.current_part = 0
        self.date_values = [None, None, None]
        self.time_values = [None, None]
        self.date_separator = "-"
        self.time_separator = ":"
        # TODO: Start with today as default value.
        # TODO: Allow showing an autocomplete suggestion that can be selected with tab.
        # TODO: Ensure that pressing "Tab" moves it to the next segment, e.g.
        # from yyyy to mm, or mm to dd or from dd to hh. At the end of ss, the
        # focus/selector should move to the next answer box.
        # TODO: ensure that enter moves to the next answer box.
        # TODO: ensure that left right moves the cursor per digit instead of per
        # yyyy, hh, mm box.

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
        if key == "ctrl h":
            self.show_help()
            return None
        if key == "enter":
            return "enter"  # Signal to move to the next box
        if key == "tab":
            # Implement suggestion selection here
            return None
        if key == "left":
            self.move_to_previous_part()
            return None
        if key == "right":
            self.move_to_next_part()
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
        # Calculate cursor position based on current_part
        cursor_pos = 0
        if self.date_only:
            for i in range(self.current_part):
                cursor_pos += self.date_parts[i] + 1
        else:
            if self.current_part < len(self.date_parts):
                for i in range(self.current_part):
                    cursor_pos += self.date_parts[i] + 1
            else:
                cursor_pos = sum(self.date_parts) + 1
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
            self.date_values[0] = 2024  # Default year
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

        # TODO: check if after changing the month, the day is still valid.
        # If the month is too large, move it down to the largest possible day of the month.

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
