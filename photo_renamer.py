#!/usr/bin/env python3
"""
Photo Renamer - Rename photos based on their EXIF date information
"""

import os
import sys
from pathlib import Path
from datetime import datetime
from PIL import Image
from PIL.ExifTags import TAGS
import shutil
import argparse


def get_exif_date(image_path):
    """
    Extract the date from EXIF data of an image.
    Returns datetime object or None if not found.
    """
    try:
        image = Image.open(image_path)
        exif_data = image._getexif()
        
        if exif_data is None:
            return None
        
        # Convert EXIF tags from numbers to names
        exif_dict = {TAGS[k]: v for k, v in exif_data.items() if k in TAGS}
        
        # Look for DateTime, DateTimeOriginal, or DateTimeDigitized
        date_tags = ['DateTime', 'DateTimeOriginal', 'DateTimeDigitized']
        
        for tag in date_tags:
            if tag in exif_dict:
                date_string = exif_dict[tag]
                # EXIF date format is typically "YYYY:MM:DD HH:MM:SS"
                return datetime.strptime(date_string, "%Y:%m:%d %H:%M:%S")
        
        return None
    except Exception as e:
        print(f"Error reading EXIF data from {image_path}: {e}")
        return None


def format_new_filename(date_obj, original_path, format_string="%Y%m%d_%H%M%S"):
    """
    Create a new filename based on the date from EXIF.
    
    Args:
        date_obj: datetime object
        original_path: Path object of original file
        format_string: datetime format string for the new filename
    
    Returns:
        New filename with extension preserved
    """
    ext = original_path.suffix  # Preserves the extension
    new_name = date_obj.strftime(format_string) + ext
    return new_name


def rename_photo(image_path, output_dir=None, format_string="%Y%m%d_%H%M%S", copy=False):
    """
    Rename a single photo based on its EXIF date.
    
    Args:
        image_path: Path to the image file
        output_dir: Directory to place renamed file (if None, renames in place)
        format_string: datetime format for the new filename
        copy: If True, copy the file instead of renaming
    
    Returns:
        Tuple of (success: bool, original_name: str, new_name: str, message: str)
    """
    image_path = Path(image_path)
    
    if not image_path.exists():
        return False, image_path.name, None, f"File not found: {image_path}"
    
    if not image_path.is_file():
        return False, image_path.name, None, f"Not a file: {image_path}"
    
    # Extract EXIF date
    exif_date = get_exif_date(image_path)
    
    if exif_date is None:
        return False, image_path.name, None, "No EXIF date found"
    
    # Create new filename
    new_filename = format_new_filename(exif_date, image_path, format_string)
    
    # Determine output path
    if output_dir:
        output_path = Path(output_dir) / new_filename
        output_dir = Path(output_dir)
        output_dir.mkdir(parents=True, exist_ok=True)
    else:
        output_path = image_path.parent / new_filename
    
    # Handle duplicate filenames
    if output_path.exists() and output_path != image_path:
        base_name = output_path.stem
        ext = output_path.suffix
        counter = 1
        while output_path.exists():
            output_path = output_path.parent / f"{base_name}_{counter}{ext}"
            counter += 1
        new_filename = output_path.name
    
    # Rename or copy the file
    try:
        if copy:
            shutil.copy2(image_path, output_path)
            return True, image_path.name, new_filename, f"Copied to {new_filename}"
        else:
            image_path.rename(output_path)
            return True, image_path.name, new_filename, f"Renamed to {new_filename}"
    except Exception as e:
        return False, image_path.name, new_filename, f"Error: {e}"


def rename_directory(directory, output_dir=None, format_string="%Y%m%d_%H%M%S", 
                    copy=False, recursive=False, dry_run=False):
    """
    Rename all photos in a directory based on EXIF date.
    
    Args:
        directory: Directory containing photos
        output_dir: Directory to place renamed files (if None, renames in place)
        format_string: datetime format for new filenames
        copy: If True, copy files instead of renaming
        recursive: If True, process subdirectories
        dry_run: If True, show what would be done without making changes
    """
    directory = Path(directory)
    
    if not directory.is_dir():
        print(f"Error: {directory} is not a directory")
        return
    
    # Photo file extensions to look for
    photo_extensions = {'.jpg', '.jpeg', '.png', '.gif', '.bmp', '.tiff', '.webp'}
    
    # Find all photo files
    if recursive:
        photo_files = [f for f in directory.rglob('*') 
                      if f.is_file() and f.suffix.lower() in photo_extensions]
    else:
        photo_files = [f for f in directory.iterdir() 
                      if f.is_file() and f.suffix.lower() in photo_extensions]
    
    if not photo_files:
        print(f"No photo files found in {directory}")
        return
    
    print(f"\nFound {len(photo_files)} photo(s)")
    print("=" * 70)
    
    successful = 0
    failed = 0
    
    for image_path in sorted(photo_files):
        success, original, new_name, message = rename_photo(
            image_path, output_dir, format_string, copy
        )
        
        status = "✓" if success else "✗"
        print(f"{status} {original:40} -> {new_name or 'ERROR':40}")
        print(f"  {message}")
        
        if success:
            successful += 1
        else:
            failed += 1
    
    print("=" * 70)
    print(f"\nResults: {successful} successful, {failed} failed")
    
    if dry_run:
        print("(Dry run - no changes made)")


def main():
    parser = argparse.ArgumentParser(
        description='Rename photos based on their EXIF date information'
    )
    parser.add_argument(
        'path',
        type=str,
        help='Path to a photo file or directory'
    )
    parser.add_argument(
        '-o', '--output',
        type=str,
        help='Output directory for renamed files (default: same directory)'
    )
    parser.add_argument(
        '-f', '--format',
        type=str,
        default='%Y%m%d_%H%M%S',
        help='Date format for new filenames (default: %%Y%%m%%d_%%H%%M%%S)'
    )
    parser.add_argument(
        '-c', '--copy',
        action='store_true',
        help='Copy files instead of renaming'
    )
    parser.add_argument(
        '-r', '--recursive',
        action='store_true',
        help='Process subdirectories recursively'
    )
    parser.add_argument(
        '--dry-run',
        action='store_true',
        help='Show what would be done without making changes'
    )
    
    args = parser.parse_args()
    
    path = Path(args.path)
    
    if not path.exists():
        print(f"Error: Path does not exist: {args.path}")
        sys.exit(1)
    
    if path.is_file():
        # Single file
        success, original, new_name, message = rename_photo(
            path, args.output, args.format, args.copy
        )
        status = "✓" if success else "✗"
        print(f"{status} {original} -> {new_name or 'ERROR'}")
        print(message)
        sys.exit(0 if success else 1)
    else:
        # Directory
        rename_directory(
            path,
            args.output,
            args.format,
            args.copy,
            args.recursive,
            args.dry_run
        )


if __name__ == '__main__':
    main()
