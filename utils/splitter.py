import os
import math
import asyncio
import logging

logger = logging.getLogger(__name__)

PART_SIZE = int(1.9 * 1024 * 1024 * 1024)  # 1.9GB per part


async def split_file(file_path, max_size=PART_SIZE):
    """Split a file into parts if it exceeds max_size.
    
    Returns list of part file paths.
    """
    file_size = os.path.getsize(file_path)
    
    if file_size <= max_size:
        return [file_path]
    
    total_parts = math.ceil(file_size / max_size)
    base_name = os.path.basename(file_path)
    name, ext = os.path.splitext(base_name)
    part_dir = os.path.join(os.path.dirname(file_path), "parts")
    os.makedirs(part_dir, exist_ok=True)
    
    part_paths = []
    
    try:
        with open(file_path, "rb") as f:
            for part_num in range(1, total_parts + 1):
                part_name = f"{name}_part{part_num}{ext}"
                part_path = os.path.join(part_dir, part_name)
                
                bytes_read = 0
                with open(part_path, "wb") as part_f:
                    while bytes_read < max_size:
                        chunk = f.read(min(8192, max_size - bytes_read))
                        if not chunk:
                            break
                        part_f.write(chunk)
                        bytes_read += len(chunk)
                
                part_paths.append(part_path)
                logger.info(f"Created part {part_num}/{total_parts}: {part_name}")
    
    except Exception as e:
        logger.error(f"File splitting failed: {e}")
        # Cleanup partial parts
        for p in part_paths:
            if os.path.exists(p):
                os.remove(p)
        return [file_path]
    
    return part_paths


def get_part_name(base_name, part_num, total_parts, ext):
    """Generate part filename."""
    return f"{base_name}_part{part_num}{ext}"


def cleanup_parts(part_paths, original_path):
    """Cleanup part files after upload."""
    for p in part_paths:
        if p != original_path and os.path.exists(p):
            try:
                os.remove(p)
            except:
                pass
    
    # Cleanup parts directory
    part_dir = os.path.join(os.path.dirname(original_path), "parts")
    if os.path.exists(part_dir):
        try:
            os.rmdir(part_dir)
        except:
            pass
