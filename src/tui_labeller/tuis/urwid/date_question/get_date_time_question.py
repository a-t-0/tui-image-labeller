import calendar
import datetime

import urwid

from tui_labeller.file_read_write_helper import write_to_file


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
        # Start with today as default value.
        today = datetime.datetime.now()
        self.date_values = [today.year, today.month, today.day]
        if not self.date_only:
            self.time_values = [today.hour, today.minute]
        self.update_text()  # Set initial text based on today's date/time
        # TODO 2: Allow showing an autocomplete suggestion (we'll add a simple placeholder for this).
        self.suggestion = None

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
            # TODO: make it move to the next question, do nothing if date is not yet completed.
            return (  # Signal to move to the next box (already implemented)
                "enter"
            )
        if key in ["delete", "backspace"]:
            return None
        # TODO 3: Ensure that pressing "Tab" moves it to the next segment
        if key == "tab":
            if (
                self.suggestion
            ):  # If there's a suggestion, accept it (placeholder for TODO 2)
                self.accept_suggestion()
            else:
                # TODO: check the position is at the end, if yes move to the next question.
                self.move_to_next_part()

            return None
        # TODO 5: Ensure that left/right moves the cursor per digit
        if key == "left":
            return self.move_cursor_to_left(current_pos=current_pos)

        if key == "right":
            return self.move_cursor_to_right(current_pos=current_pos)

        if key == "up" or key == "down":
            # self.adjust_value(key, current_part=self.current_part)
            self.update_values(direction=key)
            return None

        if key.isdigit():
            self.update_digit_value(new_digit=key)
            return self.move_cursor_to_right(current_pos=current_pos)
            # raise ValueError(f"FOUND DIGIT:{key}. TODO substitute digit in place.")

        result = super().keypress(size, key)
        if result:
            self.error_text.set_text("")  # Clear error on valid input
            # self.update_values()
        return result

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

    def adjust_year(self, direction, amount):
        if self.date_values[0] is None:
            self.date_values[0] = 2024
        if direction == "up":
            self.date_values[0] += amount
        elif direction == "down":
            if (self.date_values[0] - amount) < 1:
                self.date_values[0] = 1970
            else:
                self.date_values[0] -= amount

    def adjust_month(self, direction, amount):
        if self.date_values[1] is None:
            self.date_values[1] = amount
        if direction == "up":
            if (self.date_values[1] + amount) > 12:
                self.date_values[1] = 1
            else:
                self.date_values[1] += amount
        elif direction == "down":
            if (self.date_values[1] - amount) < 1:
                self.date_values[1] = 12
            else:
                self.date_values[1] -= amount
        if self.date_values[2] is not None:
            max_days = self.get_max_days()
            if self.date_values[2] > max_days:
                self.date_values[2] = max_days

    def adjust_day(self, direction, amount):
        if self.date_values[2] is None:
            self.date_values[2] = amount
        max_days = self.get_max_days()
        if direction == "up":
            if (self.date_values[2] + amount) > max_days:
                self.date_values[2] = 1
            else:
                self.date_values[2] += amount
        elif direction == "down":
            if (self.date_values[2] - amount) < 1:
                self.date_values[2] = max_days
            else:
                self.date_values[2] -= amount

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

    def show_help(self):
        self.help_text.set_text(
            "Use arrows to adjust, Tab to move parts, Enter to next field"
        )

    def update_values(self, direction):
        """Main function to orchestrate updating values based on cursor
        position."""
        text = self.get_edit_text()
        current_pos: int = self.edit_pos  # Use the cursor position

        if self.date_only:
            parts = text.split(self.date_separator)
            write_to_file(
                filename="eg.txt",
                content=f"parts={parts}, current_pos={current_pos}",
                append=True,
            )
            # Year adjustments (format: yyyy-mm-dd)
            if current_pos == 0:  # Thousands place of year
                self.adjust_year(direction=direction, amount=1000)
            elif current_pos == 1:  # Hundreds place of year
                self.adjust_year(direction=direction, amount=100)
            elif current_pos == 2:  # Tens place of year
                self.adjust_year(direction=direction, amount=10)
            elif current_pos == 3:  # Ones place of year
                self.adjust_year(direction=direction, amount=1)
            # Month adjustments
            elif current_pos == 5:  # Tens place of month
                self.adjust_month(direction=direction, amount=10)
            elif current_pos == 6:  # Ones place of month
                self.adjust_month(direction=direction, amount=1)
            # Day adjustments
            elif current_pos == 8:  # Tens place of day
                self.adjust_day(direction=direction, amount=10)
            elif current_pos == 9:  # Ones place of day
                self.adjust_day(direction=direction, amount=1)
            self.update_text()
        else:
            raise NotImplementedError(
                "TODO: implement like yyyy-mm-dd for hh:mm:ss"
            )

    def update_digit_value(self, new_digit):
        """Update the active value based on cursor position and incoming digit
        value."""
        text = self.get_edit_text()
        current_pos: int = self.edit_pos  # Use the cursor position
        current_digit = int(
            text[current_pos]
        )  # Get the digit at the cursor position
        new_digit = int(new_digit)  # Ensure the incoming digit is an integer

        if self.date_only:
            parts = text.split(self.date_separator)
            write_to_file(
                filename="eg.txt",
                content=(
                    f"parts={parts}, current_pos={current_pos},"
                    f" current_digit={current_digit}, new_digit={new_digit}"
                ),
                append=True,
            )
            # Year adjustments (format: yyyy-mm-dd)
            if current_pos in [0, 1, 2, 3]:  # Year digits
                place_values = [1000, 100, 10, 1]
                digit_index = current_pos
                change = (new_digit - current_digit) * place_values[digit_index]
                self.adjust_year(
                    direction="up" if change >= 0 else "down",
                    amount=abs(change),
                )
            # Month adjustments
            elif current_pos in [5, 6]:  # Month digits
                place_values = [10, 1]
                digit_index = current_pos - 5  # Adjust for position offset
                change = (new_digit - current_digit) * place_values[digit_index]
                self.adjust_month(
                    direction="up" if change >= 0 else "down",
                    amount=abs(change),
                )
            # Day adjustments
            elif current_pos in [8, 9]:  # Day digits
                place_values = [10, 1]
                digit_index = current_pos - 8  # Adjust for position offset
                change = (new_digit - current_digit) * place_values[digit_index]
                self.adjust_day(
                    direction="up" if change >= 0 else "down",
                    amount=abs(change),
                )
            self.update_text()
        else:
            raise NotImplementedError(
                "TODO: implement like yyyy-mm-dd for hh:mm:ss"
            )

    def move_cursor_to_right(self, current_pos):
        if current_pos < len(self.get_edit_text()):
            if current_pos in [3, 6]:
                self.set_edit_pos(current_pos + 2)
            else:
                self.set_edit_pos(current_pos + 1)
            return None
        else:
            return "next_question"

    def move_cursor_to_left(self, current_pos):
        if current_pos > 0:
            if current_pos in [5, 8]:
                self.set_edit_pos(current_pos - 2)
            else:
                self.set_edit_pos(current_pos - 1)
            return None
        else:
            return "previous_question"
