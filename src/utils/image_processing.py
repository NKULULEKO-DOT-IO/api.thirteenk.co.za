from io import BytesIO
from PIL import Image as PILImage
from typing import Tuple, Optional, Union


def resize_image(
        image_bytes: bytes,
        max_size: Tuple[int, int] = (800, 800),
        format: Optional[str] = None
) -> BytesIO:
    """
    Resize an image to fit within the specified dimensions while maintaining aspect ratio.

    Args:
        image_bytes: Raw image bytes
        max_size: Maximum width and height
        format: Output format (JPEG, PNG, etc.). If None, uses original format.

    Returns:
        BytesIO object containing the resized image
    """
    # Open image from bytes
    image = PILImage.open(BytesIO(image_bytes))

    # Get original format if not specified
    if not format:
        format = image.format or "JPEG"

    # Calculate new dimensions
    width, height = image.size
    ratio = min(max_size[0] / width, max_size[1] / height)

    # Only resize if image is larger than max_size
    if ratio < 1:
        new_width = int(width * ratio)
        new_height = int(height * ratio)
        image = image.resize((new_width, new_height), PILImage.LANCZOS)

    # Save to BytesIO
    output = BytesIO()
    image.save(output, format=format)
    output.seek(0)

    return output


def generate_thumbnail(
        image_bytes: bytes,
        size: Tuple[int, int] = (200, 200),
        format: str = "JPEG"
) -> BytesIO:
    """
    Generate a thumbnail for an image.

    Args:
        image_bytes: Raw image bytes
        size: Thumbnail size
        format: Output format

    Returns:
        BytesIO object containing the thumbnail
    """
    # Open image from bytes
    image = PILImage.open(BytesIO(image_bytes))

    # Create thumbnail (maintains aspect ratio)
    image.thumbnail(size)

    # Save to BytesIO
    output = BytesIO()
    image.save(output, format=format)
    output.seek(0)

    return output


def get_image_dimensions(image_bytes: bytes) -> Tuple[int, int]:
    """
    Get the dimensions of an image.

    Args:
        image_bytes: Raw image bytes

    Returns:
        Tuple of (width, height)
    """
    image = PILImage.open(BytesIO(image_bytes))
    return image.size