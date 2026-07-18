import sys
import time


def progress_bar(current, total, start_time, prefix="Progress"):
    """Display a progress bar in the terminal."""
    elapsed = time.time() - start_time
    if elapsed == 0:
        elapsed = 0.001
    speed = current / elapsed
    eta = (total - current) / speed if speed > 0 else 0
    pct = current / total * 100

    bar_len = 30
    filled = int(bar_len * current / total)
    bar = "█" * filled + "░" * (bar_len - filled)

    sys.stdout.write(
        f"\r{prefix}: |{bar}| {pct:.1f}% "
        f"[{current}/{total}] "
        f"[{speed / 1024 / 1024:.1f}MB/s] "
        f"[ETA: {int(eta)}s]"
    )
    sys.stdout.flush()
