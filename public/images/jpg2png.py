from pathlib import Path
from PIL import Image

def convert_jpg_to_png_and_delete():
    current_dir = Path(__file__).parent

    for jpg_path in current_dir.iterdir():
        if jpg_path.suffix.lower() in {".jpg", ".jpeg"}:
            png_path = jpg_path.with_suffix(".png")
            try:
                with Image.open(jpg_path) as img:
                    img.save(png_path, format="PNG")
                jpg_path.unlink()  # 删除原 jpg
                print(f"Converted and removed: {jpg_path.name}")
            except Exception as e:
                print(f"Failed on {jpg_path.name}: {e}")

if __name__ == "__main__":
    convert_jpg_to_png_and_delete()
