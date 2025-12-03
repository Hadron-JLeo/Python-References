"""
Display Event Days (Simple GUI)
--------------------------------
Loads events from an .ics file (default: Downloads/my_events.ics) and shows
a simple display where each day that has at least one event is rendered as
a square "card" containing the date and event summary lines.

Requirements:
    pip install ics

How it works (high level):
- load_ics_file: reads an .ics file and returns a list of parsed events.
- group_events_by_date: groups events by local calendar date (YYYY-MM-DD).
- build_day_cards_gui: creates a Tkinter window and draws one square box per date.
- The user can also pick another .ics file using the "Load .ics..." button.

Author: ChatGPT
"""

from pathlib import Path
from datetime import datetime, date
from zoneinfo import ZoneInfo, ZoneInfoNotFoundError
import tkinter as tk
from tkinter import ttk, filedialog, messagebox
from ics import Calendar
import textwrap
import regex as re

# ------------------------------
# Configuration / Defaults
# ------------------------------
DEFAULT_ICS_FILENAME = "my_events.ics"
DEFAULT_DOWNLOADS = Path.home() / "Downloads"
DEFAULT_ICS_PATH = DEFAULT_DOWNLOADS / DEFAULT_ICS_FILENAME
LOCAL_TZ_NAME = "Europe/Berlin"  # adjust if you want another default local tz
TIMEZONE = ZoneInfo(LOCAL_TZ_NAME)

# ------------------------------
# Utility Functions (single-responsibility)
# ------------------------------
def get_local_zone() -> ZoneInfo:
    """Return a ZoneInfo for the local timezone (fallback to system default)."""
    try:
        return ZoneInfo(LOCAL_TZ_NAME)
    except Exception:
        # If ZoneInfo for the named zone isn't available, fall back to system local tz via datetime
        try:
            return datetime.now().astimezone().tzinfo or ZoneInfo("UTC")
        except Exception:
            return ZoneInfo("UTC")


def load_ics_file(path: Path) -> list:
    """
    Read an .ics file and return a list of event dicts with keys:
    - 'title' (str)
    - 'begin' (datetime)
    - 'end' (datetime or None)
    """
    if not path.exists():
        raise FileNotFoundError(f"ICS file not found: {path}")

    text = path.read_text(encoding="utf-8")
    cal = Calendar(text)

    # Convert events into simple dicts
    events = []
    local_tz = get_local_zone()
    for ev in cal.events:
        # The ics library exposes begin as arrow.Arrow like object; safe access:
        try:
            ev_begin = ev.begin.datetime  # may be tz-aware or naive
        except Exception:
            # fallback: use the raw .begin if needed
            ev_begin = getattr(ev, "begin", None)
        try:
            ev_end = ev.end.datetime
        except Exception:
            ev_end = None

        # If naive, interpret as local_tz
        if isinstance(ev_begin, datetime):
            if ev_begin.tzinfo is None:
                ev_begin = ev_begin.replace(tzinfo=local_tz)
            else:
                # convert to local tz for consistent grouping/display
                try:
                    ev_begin = ev_begin.astimezone(local_tz)
                except Exception:
                    # if astimezone fails, keep as-is
                    pass

        if isinstance(ev_end, datetime):
            if ev_end.tzinfo is None:
                ev_end = ev_end.replace(tzinfo=local_tz)
            else:
                try:
                    ev_end = ev_end.astimezone(local_tz)
                except Exception:
                    pass

        events.append({
            "title": ev.name or "Untitled",
            "begin": ev_begin,
            "end": ev_end
        })

    # sort events by begin time
    events.sort(key=lambda e: e["begin"] or datetime.min)
    return events


def filter_future_events(events) -> list:
    
    """Return only events that are today or in the future."""
    now = datetime.now(TIMEZONE)
    return [e for e in events if e["begin"].date() >= now.date()]


def group_events_by_date(events: list) -> dict:
    """
    Group events by calendar date (YYYY-MM-DD) in the local timezone.
    Returns dict[str(date_iso)] -> list of event dicts for that date.
    """
    grouped = {}    
    future_events = filter_future_events(events)
    
    for e in future_events:
        begin = e.get("begin")
        if not isinstance(begin, datetime):
            continue
        # Use the date portion in local tz
        event_date = begin.date()  # datetime is already in local tz in load_ics_file
        key = event_date.isoformat()
        grouped.setdefault(key, []).append(e)
    return grouped


def import_events_from_text():
    """Import events automatically from a .txt file with time/date patterns."""
    
    events = []
    file_path = filedialog.askopenfilename(
        title="Select text file",
        filetypes=[("Text files", "*.txt")]
    )
    if not file_path:
        return  # User canceled

    try:
        with open(file_path, "r", encoding="utf-8") as f:
            text = f.read()
    except Exception as e:
        messagebox.showerror("Error", f"Could not read file: {e}")
        return

    # Pattern: "HH:MM-HH:MM DD.MM"
    pattern = r"(\d{1,2}:\d{2})-(\d{1,2}:\d{2})\s*(\d{1,2}\.\d{1,2})"
    matches = re.findall(pattern, text)

    if not matches:
        messagebox.showinfo("No Matches", "No valid time/date patterns found in the file.")
        return

    added = 0
    for start_str, end_str, date_str in matches:
        try:
            date_full = f"{date_str}.{datetime.now().year}"

            start_dt = datetime.strptime(f"{date_full} {start_str}", "%d.%m.%Y %H:%M").replace(tzinfo=TIMEZONE)
            end_dt = datetime.strptime(f"{date_full} {end_str}", "%d.%m.%Y %H:%M").replace(tzinfo=TIMEZONE)

            cutoff = datetime.strptime("16:30", "%H:%M").time()
            title = "X1" if start_dt.time() < cutoff else "X2"

            events.append({
                "title": title,
                "begin": start_dt,
                "end": end_dt
            })
            added += 1
        except Exception as e:
            print(f"Skipping invalid pattern: {start_str}-{end_str} {date_str} ({e})")

    messagebox.showinfo("Import Complete", f"{added} events added from text file.")
    
    print(f'{len(events)} Events ')
    return events


# ------------------------------
# GUI / Drawing Functions
# ------------------------------
def create_day_card(parent, day_iso: str, events: list, card_size=180):
    """
    Create a square frame representing a day with its events.
    - day_iso: 'YYYY-MM-DD'
    - events: list of event dicts (title, begin, end)
    """
    frame = ttk.Frame(parent, width=card_size, height=card_size, relief="raised", borderwidth=2)
    frame.grid_propagate(False)  # keep size fixed

    # Date header
    d = date.fromisoformat(day_iso)
    header = ttk.Label(frame, text=d.strftime("%a\n%d %b %Y"), anchor="center", justify="center",
                       font=("Segoe UI", 10, "bold"))
    header.grid(row=0, column=0, padx=4, pady=(6, 2), sticky="n")

    # Text area for events (use a label with wrapped text)
    # Build a short textual summary of events for the day
    lines = []
    for e in events:
        begin = e.get("begin")
        end = e.get("end")
        if isinstance(begin, datetime):
            tstr = begin.strftime("%H:%M")
            if isinstance(end, datetime):
                tstr += "–" + end.strftime("%H:%M")
            lines.append(f"{tstr} {e.get('title')}")
        else:
            lines.append(e.get("title"))

    # Wrap each line so it fits in the card reasonably
    wrapped_lines = []
    for line in lines:
        wrapped_lines.extend(textwrap.wrap(line, width=18))  # adjust width if you want more text
    if not wrapped_lines:
        wrapped_lines = ["(no details)"]

    content = "\n".join(wrapped_lines[:10])  # cap lines to avoid overflow
    label = ttk.Label(frame, text=content, anchor="n", justify="left", wraplength=card_size - 16,
                      font=("Segoe UI", 9))
    label.grid(row=1, column=0, padx=8, pady=(2, 8), sticky="nw")

    return frame


def build_day_cards_gui(grouped_events: dict, events: list):
    """
    Build and show the main Tkinter window containing one square per date in grouped_events.
    Layout: wraps cards with a fixed number of columns depending on window width.
    """
    root = tk.Tk()
    root.title("Event Days")
    padding = 12

    # Top controls: file info and Quit
    top_frame = ttk.Frame(root)
    top_frame.pack(side="top", fill="x", padx=padding, pady=(padding, 0))

    info_label = ttk.Label(top_frame, text=f"Showing {len(grouped_events)} DAYS with {len(events)} HOURS")
    info_label.pack(side="left")

    def quit_cb():
        root.destroy()

    quit_btn = ttk.Button(top_frame, text="Quit", command=quit_cb)
    quit_btn.pack(side="right")

    # Canvas + scrollbar so many days can be scrolled
    canvas = tk.Canvas(root, highlightthickness=0)
    scrollbar = ttk.Scrollbar(root, orient="vertical", command=canvas.yview)
    canvas.configure(yscrollcommand=scrollbar.set)

    container = ttk.Frame(canvas)
    container_id = canvas.create_window((0, 0), window=container, anchor="nw")

    canvas.pack(side="left", fill="both", expand=True, padx=(padding, 0), pady=padding)
    scrollbar.pack(side="right", fill="y", padx=(0, padding), pady=padding)

    # Card layout params
    card_size = 180
    gap = 12
    cols = 3  # default columns; we'll adjust based on window width

    # Render cards in a wrapping grid
    day_keys = sorted(grouped_events.keys())  # iso date strings sorted
    for idx, key in enumerate(day_keys):
        r = idx // cols
        c = idx % cols
        card = create_day_card(container, key, grouped_events[key], card_size=card_size)
        card.grid(row=r, column=c, padx=(0 if c == 0 else gap), pady=(0 if r == 0 else gap))

    # Make sure canvas scrollregion updates
    def on_configure(event):
        canvas.configure(scrollregion=canvas.bbox("all"))
        # Optionally adjust columns based on width:
        # cols = max(1, event.width // (card_size + gap))
        # (In this simple version we keep cols fixed.)

    container.bind("<Configure>", on_configure)

    # Allow mousewheel scrolling
    def _on_mousewheel(event):
        canvas.yview_scroll(int(-1 * (event.delta / 120)), "units")

    # Windows/Mac differences for mousewheel binding
    canvas.bind_all("<MouseWheel>", _on_mousewheel)
    canvas.bind_all("<Button-4>", lambda e: canvas.yview_scroll(-1, "units"))
    canvas.bind_all("<Button-5>", lambda e: canvas.yview_scroll(1, "units"))

    root.geometry("620x520")
    root.mainloop()


# ------------------------------
# Main Program Flow
# ------------------------------
def main():
    """
    Main entry:
    - Try to load DEFAULT_ICS_PATH from Downloads.
    - If missing, ask the user to pick an .ics file via file dialog.
    - Then group events by date and show the GUI with day-cards.
    """
    # Attempt to load default ICS from Downloads
    ics_path = DEFAULT_ICS_PATH
    if not ics_path.exists():
        # ask user to pick a file
        root = tk.Tk()
        root.withdraw()  # hide root window
        messagebox.showinfo("Select .ics file", f"Default .ics not found at:\n{ics_path}\n\nPlease select an .ics file.")
        chosen = filedialog.askopenfilename(title="Open .ics file", filetypes=[("iCalendar files", "*.ics")])
        root.destroy()
        if not chosen:
            print("No .ics file selected. Exiting.")
            return
        ics_path = Path(chosen)

    try:
        events = import_events_from_text()
        #events = load_ics_file(ics_path)
        
    except Exception as e:
        messagebox.showerror("Error loading .ics", str(e))
        return

    grouped = group_events_by_date(events)

    if not grouped:
        # Inform user and exit
        root = tk.Tk()
        root.withdraw()
        messagebox.showinfo("No events", f"No events found in {ics_path}")
        root.destroy()
        print("No events to show. Exiting.")
        return

    # Build and show GUI
    build_day_cards_gui(grouped, events)


if __name__ == "__main__":
    main()
