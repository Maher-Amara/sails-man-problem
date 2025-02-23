import imageio.v2 as imageio
import os
import re

def create_gif(image_folder, gif_name, duration=0.5):
    """
    Create a GIF from PNG files in the specified folder.
    
    Args:
        image_folder: Directory containing the PNG files
        gif_name: Output GIF filename
        duration: Duration for each frame in seconds
    """
    images = []
    
    def get_frame_number(filename):
        # Extract number from filename, return -1 if no number found
        if not filename.endswith('.png'):
            return -1
        match = re.search(r'(\d+)', filename)
        return int(match.group(1)) if match else float('inf')
    
    # Sort filenames numerically, putting non-numbered files at the end
    filenames = sorted(os.listdir(image_folder), key=get_frame_number)
    
    for filename in filenames:
        if filename.endswith('.png'):
            file_path = os.path.join(image_folder, filename)
            # Read each image as a fresh frame
            frame = imageio.imread(file_path)
            images.append(frame)
    
    # Save the GIF with disposal mode 2 (restore to background)
    imageio.mimsave(gif_name, images, duration=duration, loop=0, disposal=2)

if __name__ == "__main__":
    # Create diagrams directory if it doesn't exist
    if not os.path.exists('diagrams'):
        os.makedirs('diagrams')
    
    create_gif('diagrams/tsp_solution', 'diagrams/tsp_solution.gif', duration=0.1)