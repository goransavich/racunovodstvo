import ctypes


class KeyboardController:

    def __get_keyboard_language(self):
        """
        Gets the keyboard language in use by the current
        active window process.
        """
        user32 = ctypes.WinDLL('user32', use_last_error=True)

        # Get the current active window handle
        handle = user32.GetForegroundWindow()

        # Get the thread id from that window handle
        threadid = user32.GetWindowThreadProcessId(handle, 0)

        # Get the keyboard layout id from the threadid
        layout_id = user32.GetKeyboardLayout(threadid)

        # Extract the keyboard language id from the keyboard layout id
        language_id = layout_id & (2 ** 16 - 1)

        # Convert the keyboard language id from decimal to hexadecimal
        language_id_hex = hex(language_id)

        return language_id_hex

    def check_language(self):
        jezik = self.__get_keyboard_language()
        if jezik == '0x281a' or jezik == '0x281A':
            return True
        else:
            return False
