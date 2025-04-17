import cv2
import numpy as np

def show_point_on_image(image_path, x, y, radius=5, color=(0, 0, 255)):
    """
    Display an image with a point at the specified coordinates
    
    Args:
        image_path: Path to the image file
        x: X coordinate of the point
        y: Y coordinate of the point
        radius: Size of the point (circle radius)
        color: Color of the point in BGR format (default: red)
    """
    # Load the image
    image = cv2.imread(image_path)
    if image is None:
        print(f"Error: Could not load image file at {image_path}")
        return
    
    # Create a copy of the image to draw on
    display_image = image.copy()
    
    # Convert coordinates to integers
    x_int = int(x)
    y_int = int(y)
    
    # Draw the point as a filled circle
    cv2.circle(display_image, (x_int, y_int), radius=radius, color=color, thickness=-1)
    
    # Add text with coordinates
    text = f"({x}, {y})"
    cv2.putText(display_image, text, (x_int + 10, y_int), 
                cv2.FONT_HERSHEY_SIMPLEX, 0.5, color, 2)
    
    # Get image dimensions
    height, width = image.shape[:2]
    
    # Create a window and display the image
    window_name = "Image with Point"
    cv2.namedWindow(window_name, cv2.WINDOW_NORMAL)
    cv2.resizeWindow(window_name, width, height)
    cv2.imshow(window_name, display_image)
    cv2.waitKey(0)
    cv2.destroy# filepath: c:\Users\aryav\projects\orbitagent\opencv.py
import cv2
import numpy as np

def show_point_on_image(image_path, x, y, radius=5, color=(0, 0, 255)):
    """
    Display an image with a point at the specified coordinates
    
    Args:
        image_path: Path to the image file
        x: X coordinate of the point
        y: Y coordinate of the point
        radius: Size of the point (circle radius)
        color: Color of the point in BGR format (default: red)
    """
    # Load the image
    image = cv2.imread(image_path)
    if image is None:
        print(f"Error: Could not load image file at {image_path}")
        return
    
    # Create a copy of the image to draw on
    display_image = image.copy()
    
    # Convert coordinates to integers
    x_int = int(x)
    y_int = int(y)
    
    # Draw the point as a filled circle
    cv2.circle(display_image, (x_int, y_int), radius=radius, color=color, thickness=-1)
    
    # Add text with coordinates
    text = f"({x}, {y})"
    cv2.putText(display_image, text, (x_int + 10, y_int), 
                cv2.FONT_HERSHEY_SIMPLEX, 0.5, color, 2)
    
    # Get image dimensions
    height, width = image.shape[:2]
    
    # Create a window and display the image
    window_name = "Image with Point"
    cv2.namedWindow(window_name, cv2.WINDOW_NORMAL)
    cv2.resizeWindow(window_name, width, height)
    cv2.imshow(window_name, display_image)
    cv2.waitKey(0)
    cv2.destroy
# Example usage:
# Replace with your own values
image_path = "./screenshot_2.png"
x_coordinate = 512
y_coordinate = 384

show_point_on_image(image_path, x_coordinate, y_coordinate)

# now the get position is working very much fine. 
# we must have the loop logic going on with us to get it done.
# buy the .com and lunch your first product.
# here we go