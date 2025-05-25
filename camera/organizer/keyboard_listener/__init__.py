import threading
import time

import keyboard


class KeyboardListener:
    def __init__(self):
        # Holds the most recent key press ('' if none)
        self._last_key = ''
        # Lock to protect access from hook thread
        self._lock = threading.Lock()
        # Install the hook and keep its handler so we can unhook later
        self._hook = keyboard.hook(self._on_key)

    def _on_key(self, event):
        # Only care about key‐down of single-character keys
        if event.event_type == 'down' and len(event.name) == 1:
            char = event.name
            # Check if Shift is held right now
            if keyboard.is_pressed('shift'):
                char = char.upper()
            else:
                char = char.lower()
            with self._lock:
                self._last_key = char

    def key_available(self) -> bool:
        """Return True if a key has been pressed since last get_key()."""
        with self._lock:
            return bool(self._last_key)

    def get_key(self) -> str:
        """
        Return the last key pressed (respecting Shift for case),
        or '' if none. Clears it immediately.
        """
        with self._lock:
            key = self._last_key
            self._last_key = ''
        return key

    def stop(self):
        """Remove the keyboard hook when you're done."""
        keyboard.unhook(self._hook)

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc, tb):
        self.stop()


if __name__ == '__main__':
    listener = KeyboardListener()
    print("Press keys (Ctrl-C to exit)...")
    try:
        while True:
            if listener.key_available():
                k = listener.get_key()
                print(f"Key pressed: {k!r}")
                if k == '\x03':  # Ctrl-C
                    break
            # Your other non-blocking work here
            time.sleep(0.05)
    except KeyboardInterrupt:
        pass
    finally:
        listener.stop()
        print("Listener stopped. Exiting.")
