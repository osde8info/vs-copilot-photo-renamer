# Photo Renamer

A Python utility to rename photos based on their EXIF date information.

## Features

- Extracts date from EXIF metadata (DateTime, DateTimeOriginal, or DateTimeDigitized)
- Renames single files or entire directories
- Handles duplicate filenames automatically
- Option to copy instead of rename
- Recursive directory processing
- Custom date format support
- Dry-run mode to preview changes

## Installation

```bash
pip install -r requirements.txt
```

## Usage

### Rename a single photo

```bash
python photo_renamer.py /path/to/photo.jpg
```

### Rename all photos in a directory

```bash
python photo_renamer.py /path/to/photos/
```

### Copy photos to output directory with new names

```bash
python photo_renamer.py /path/to/photos/ -o /output/directory/ -c
```

### Recursively process subdirectories

```bash
python photo_renamer.py /path/to/photos/ -r
```

### Use custom date format

```bash
python photo_renamer.py /path/to/photos/ -f "%Y-%m-%d_%H-%M-%S"
```

### Preview changes without making them (dry-run)

```bash
python photo_renamer.py /path/to/photos/ --dry-run
```

## Command-line Options

- `path`: Path to a photo file or directory (required)
- `-o, --output`: Output directory for renamed files
- `-f, --format`: Date format for filenames (default: `%Y%m%d_%H%M%S`)
- `-c, --copy`: Copy files instead of renaming
- `-r, --recursive`: Process subdirectories recursively
- `--dry-run`: Preview changes without making them

## Date Format Codes

Common date format codes:

- `%Y`: Year (4 digits, e.g., 2026)
- `%m`: Month (01-12)
- `%d`: Day (01-31)
- `%H`: Hour (00-23)
- `%M`: Minute (00-59)
- `%S`: Second (00-59)

Example: `%Y-%m-%d_%H-%M-%S` produces `2026-01-07_14-30-45.jpg`

## Supported Formats

- JPG/JPEG
- PNG
- GIF
- BMP
- TIFF
- WebP

## License

MIT
