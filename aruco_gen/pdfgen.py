from reportlab.lib.pagesizes import A4, landscape
from reportlab.lib.units import mm
from reportlab.pdfgen import canvas


def create_pdf_with_images(output_filename, image_paths, rotations=[0, 0, 0, 0], padding=10):
    """
    Creates a landscape A4 PDF with images in each corner with padding and rotation.

    Args:
        output_filename (str): Name of the output PDF file
        image_paths (list): List of 4 image paths for [top-left, top-right, bottom-left, bottom-right]
        rotations (list): List of 4 rotation angles in degrees for each image
        padding (float): Padding from edges in millimeters
    """
    # Set up PDF in landscape A4
    page_width, page_height = landscape(A4)
    c = canvas.Canvas(output_filename, pagesize=(page_width, page_height))

    # Image size (100x100 pixels, converted to points - 1px = 0.75pt at 72dpi)
    image_width = 100 * 0.75
    image_height = 100 * 0.75

    # Convert padding from mm to points (1mm = 2.83465 points)
    padding_pt = padding * mm

    # Calculate positions for each corner image
    positions = [
        (padding_pt, page_height - padding_pt - image_height),  # Top-left
        (page_width - padding_pt - image_width, page_height -
         padding_pt - image_height),  # Top-right
        (padding_pt, padding_pt),  # Bottom-left
        (page_width - padding_pt - image_width, padding_pt)  # Bottom-right
    ]

    # Draw each image with rotation
    for i, (img_path, pos) in enumerate(zip(image_paths, positions)):
        if img_path:  # Only draw if image path is provided
            c.saveState()  # Save the current graphics state

            # Calculate center point of image for rotation
            center_x = pos[0] + image_width / 2
            center_y = pos[1] + image_height / 2

            # Move to center, rotate, then move back
            c.translate(center_x, center_y)
            c.rotate(rotations[i])
            c.translate(-center_x, -center_y)

            # Draw the image
            c.drawImage(img_path, pos[0], pos[1],
                        width=image_width, height=image_height)

            c.restoreState()  # Restore the graphics state

    # Save the PDF
    c.save()
    print(f"PDF created successfully: {output_filename}")


if __name__ == "__main__":
    # Replace these with your actual image paths
    # Order: [top-left, top-right, bottom-left, bottom-right]
    front = [
        "output/aruco_marker_10.png",
        "output/aruco_marker_11.png",
        "output/aruco_marker_12.png",
        "output/aruco_marker_13.png",
    ]

    back = [
        "output/aruco_marker_14.png",
        "output/aruco_marker_15.png",
        "output/aruco_marker_16.png",
        "output/aruco_marker_17.png",
    ]

    # Rotation angles for each corner (in degrees)
    # Order matches image_files: [top-left, top-right, bottom-left, bottom-right]
    rotation_angles = [
        180,    # Top-left (no rotation)
        90,   # Top-right (rotate 90° clockwise)
        270,  # Bottom-left (rotate 90° counter-clockwise)
        0    # Bottom-right (upside down)
    ]

    # Create PDF with 10mm padding and rotations
    create_pdf_with_images("front.pdf", front,
                           rotations=rotation_angles, padding=10)

    create_pdf_with_images("back.pdf", back,
                           rotations=rotation_angles, padding=10)
