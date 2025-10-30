import argparse
from pathlib import Path
from PIL import Image, ImageOps

VALID_SUFFIXES = {".jpg", ".jpeg", ".png", ".webp", ".bmp", ".tiff"}

def process(in_path: Path, out_path: Path, left: int, right: int, top: int, bottom: int, target_width: int, overwrite: bool):
    try:
        if out_path.exists() and not overwrite:
            print(f"skip (exists): {out_path}")
            return False

        with Image.open(in_path) as im:
            im = ImageOps.exif_transpose(im)
            w, h = im.size

            if w <= left + right or h <= top + bottom:
                print(f"skip (too small): {in_path}")
                return False

            # crop
            box = (left, top, w - right, h - bottom)
            im = im.crop(box)
            cw, ch = im.size

            # resize
            if cw != target_width:
                new_h = round(ch * (target_width / cw))
                im = im.resize((target_width, new_h), Image.LANCZOS)

            out_path.parent.mkdir(parents=True, exist_ok=True)

            fmt = im.format or "JPEG"
            if fmt.upper() == "JPEG":
                im.save(out_path, fmt, quality=95, optimize=True, progressive=True)
            else:
                im.save(out_path, fmt)

        print(f"ok: {in_path} -> {out_path}")
        return True

    except Exception as e:
        print(f"error: {in_path} ({e})")
        return False


def iter_images(root: Path):
    if root.is_file():
        if root.suffix.lower() in VALID_SUFFIXES:
            yield root
    else:
        for p in root.rglob("*"):
            if p.is_file() and p.suffix.lower() in VALID_SUFFIXES:
                yield p


def main():
    parser = argparse.ArgumentParser(
        description="Crop left/right 34px and resize width to 1080px (keep filename)."
    )
    parser.add_argument("input", type=Path)
    parser.add_argument("-o", "--output", type=Path, default=None)
    parser.add_argument("--left", type=int, default=34)
    parser.add_argument("--right", type=int, default=34)
    parser.add_argument("--top", type=int, default=0)
    parser.add_argument("--bottom", type=int, default=0)
    parser.add_argument("--target-width", type=int, default=1080)
    parser.add_argument("--force", action="store_true")

    args = parser.parse_args()
    in_path = args.input

    if not in_path.exists():
        print("input not found:", in_path)
        return 1

    if in_path.is_file():
        # 単一ファイル
        if args.output:
            out_path = args.output if args.output.suffix else args.output / in_path.name
        else:
            out_path = in_path.parent / "_out" / in_path.name
        process(in_path, out_path, args.left, args.right, args.top, args.bottom, args.target_width, args.force)
        return 0

    # フォルダ処理
    out_dir = args.output or (in_path.parent / f"{in_path.name}_out")
    ok_count = ng_count = 0

    for p in iter_images(in_path):
        rel = p.relative_to(in_path)
        out_path = out_dir / rel
        if process(p, out_path, args.left, args.right, args.top, args.bottom, args.target_width, args.force):
            ok_count += 1
        else:
            ng_count += 1

    print(f"done. success={ok_count}, skipped/failed={ng_count}")
    return 0


if __name__ == "__main__":
    main()
