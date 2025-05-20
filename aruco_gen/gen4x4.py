import cv2
import cv2.aruco as aruco
import numpy as np


def generate_aruco_markers_with_border(dictionary_id=aruco.DICT_4X4_50,
                                       output_size=100,
                                       border_width=10,
                                       output_prefix="output/aruco_marker"):
    """
    Generate ArUco markers with white borders

    Parameters:
    - dictionary_id: ArUco dictionary identifier (default: 4x4 with 50 markers)
    - output_size: Total output image size in pixels (including border)
    - border_width: Width of white border in pixels
    - output_prefix: Prefix for output filenames
    """
    # Calculate marker size (output_size minus borders on both sides)
    marker_size = output_size - 2 * border_width

    # Load the predefined dictionary
    aruco_dict = aruco.getPredefinedDictionary(dictionary_id)

    # Generate and save each marker in the dictionary
    for marker_id in range(aruco_dict.bytesList.shape[0]):
        # Create marker image (black marker on white background)
        marker_img = aruco.generateImageMarker(
            aruco_dict, marker_id, marker_size, borderBits=1)

        # Convert to RGB
        marker_img_rgb = cv2.cvtColor(marker_img, cv2.COLOR_GRAY2RGB)

        # Create white canvas for final image
        final_img = np.ones((output_size, output_size, 3),
                            dtype=np.uint8) * 255

        # Place the marker in the center with border
        final_img[border_width:border_width+marker_size,
                  border_width:border_width+marker_size] = marker_img_rgb

        # Save the marker
        filename = f"{output_prefix}_{marker_id:02d}.png"
        cv2.imwrite(filename, final_img)
        print(
            f"Saved {filename} ({output_size}x{output_size}px with {border_width}px border)")


if __name__ == "__main__":
    # Generate all 4x4 markers with 10px white border in 100x100px images
    generate_aruco_markers_with_border(dictionary_id=aruco.DICT_4X4_50,
                                       output_size=100,
                                       border_width=10)
