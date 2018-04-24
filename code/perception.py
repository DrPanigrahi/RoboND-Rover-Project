# Modified by: Dr. Smruti Panigrahi

import numpy as np
import cv2
import time
from transformation import *


# Apply the above functions in succession and update the Rover state accordingly
def perception_step(Rover):
    # Perform perception steps to update Rover()
    # TODO: 
    # NOTE: camera image is coming to you in Rover.img
    # 1) Define source and destination points for perspective transform
    # 2) Apply perspective transform
    # 3) Apply color threshold to identify navigable terrain/obstacles/rock samples
    # 4) Update Rover.vision_image (this will be displayed on left side of screen)
        # Example: Rover.vision_image[:,:,0] = obstacle color-thresholded binary image
        #          Rover.vision_image[:,:,1] = rock_sample color-thresholded binary image
        #          Rover.vision_image[:,:,2] = navigable terrain color-thresholded binary image

    # 5) Convert map image pixel values to rover-centric coords
    # 6) Convert rover-centric pixel values to world coordinates
    # 7) Update Rover worldmap (to be displayed on right side of screen)
        # Example: Rover.worldmap[obstacle_y_world, obstacle_x_world, 0] += 1
        #          Rover.worldmap[rock_y_world, rock_x_world, 1] += 1
        #          Rover.worldmap[navigable_y_world, navigable_x_world, 2] += 1

    # 8) Convert rover-centric pixel positions to polar coordinates
    # Update Rover pixel distances and angles
        # Rover.nav_dists = rover_centric_pixel_distances
        # Rover.nav_angles = rover_centric_angles
    
    
    # 1) Receive image frame from Rover camera
    image = Rover.img
    
    # 2) Apply perspective transform
    warped_image, mask = perspect_transform(image)
    
    # 3) Apply color threshold to identify navigable terrain/obstacles/rock samples
    navigable_warped_threshed = color_thresh(warped_image, (161, 161, 161), (255, 255, 255))
    #obstacle_warped_threshed = np.absolute(np.float32(navigable_warped_threshed) - 1)*mask
    obstacle_warped_threshed = color_thresh(warped_image, (0, 0, 0), (160, 160, 160))*mask
    rock_warped_threshed = color_thresh(warped_image, (100, 100, 0), (255, 255, 50))

    # 4) Update Rover.vision_image (this will be displayed on left side of screen)
    Rover.vision_image[:,:,0] = obstacle_warped_threshed*255 
    Rover.vision_image[:,:,1] = rock_warped_threshed*255 
    Rover.vision_image[:,:,2] = navigable_warped_threshed*255 
    
    # 5) Convert warped and thresholded map image pixel values to rover-centric coords
    # Calculate pixel values in rover-centric coords and distance/angle to all pixels
    navigable_xpix, navigable_ypix = rover_coords(navigable_warped_threshed)    
    obstacle_xpix, obstacle_ypix = rover_coords(obstacle_warped_threshed)
    rock_xpix, rock_ypix = rover_coords(rock_warped_threshed)
    
    # 5.1) To increase fidelity limit the distance to which the Rover can see clearly
    navigable_xpix, navigable_ypix = pix_in_range(navigable_xpix, navigable_ypix)
    obstacle_xpix, obstacle_ypix = pix_in_range(obstacle_xpix, obstacle_ypix)
    rock_xpix, rock_ypix = pix_in_range(rock_xpix, rock_ypix, range=50) #To not care about rocks on the other side of the road
    
    # 6) Convert rover-centric pixel values to world coords
    # Get Rover position and orientation in world coords
    scale = 10
    world_size = Rover.worldmap.shape[0]
    xpos = Rover.pos[0]
    ypos = Rover.pos[1]
    yaw = Rover.yaw
    # Get navigable pixel positions in world coords
    navigable_x_world, navigable_y_world = pix_to_world(navigable_xpix, navigable_ypix, 
                                    xpos, ypos, yaw, world_size, scale)
    obstacle_x_world, obstacle_y_world = pix_to_world(obstacle_xpix, obstacle_ypix,
                                    xpos, ypos, yaw, world_size, scale)
    rock_x_world, rock_y_world = pix_to_world(rock_xpix, rock_ypix,
                                    xpos, ypos, yaw, world_size, scale)
    
    # 7) Update worldmap (to be displayed on right side of screen)
    # Add pixel positions of navigable terrain/obstacles/samples to worldmap
    # For better fidelity update map only if roll and pitch angles are minimal (near 0/360)
    if (Rover.pitch < Rover.pitch_min or Rover.pitch > Rover.pitch_max) and (Rover.roll < Rover.roll_min or Rover.roll > Rover.roll_max):
        Rover.worldmap[obstacle_y_world, obstacle_x_world, 0] += 1
        Rover.worldmap[rock_y_world, rock_x_world,1]  += 1
        Rover.worldmap[navigable_y_world, navigable_x_world, 2] += 10       
        # remove overlap mesurements
        navigable_pix = Rover.worldmap[:,:,2] > 0 #if blue channel is > 0 then set it as navigable terrain
        Rover.worldmap[navigable_pix,0] = 0 # Make obstacle channels ZERO corresponding to navigable fixels       
        # clip to avoid overflow
        Rover.worldmap = np.clip(Rover.worldmap, 0, 255)

        
    # 8) Convert rover-centric pixel positions to polar coordinates
    # Update Rover pixel distances and angles
    Rover.nav_dists, Rover.nav_angles = to_polar_coords(navigable_xpix, navigable_ypix)
    Rover.obs_dists, Rover.obs_angles = to_polar_coords(obstacle_xpix, obstacle_ypix)
    Rover.rock_dists, Rover.rock_angles = to_polar_coords(rock_xpix, rock_ypix)
    
    navigable_mean_dir = np.mean(Rover.nav_angles)
    obstacle_mean_dir = np.mean(Rover.obs_angles)
    rock_mean_dir = np.mean(Rover.rock_angles)
    
    # 9) Get on mission to look for gold rock samples
    # When rock sample is in sight: approach, stop when near rock, collect it and move on
    if len(Rover.rock_dists) > 0: #if rock_warped_threshed.any():
        Rover.pickup_counter += 1
        rock_idx = np.argmin(Rover.rock_dists) #Returns the indices of the minimum rock distance.
        rock_xcen = rock_x_world[rock_idx] #Make min. Rock dist. in Rover as center of Rock in worldmap
        rock_ycen = rock_y_world[rock_idx]
        Rover.rock_pos = (rock_xcen, rock_ycen)
        #if len(Rover.rock_dists) > 0: #if any Rock pixels detected
        Rover.nav_dists = Rover.rock_dists
        Rover.nav_angles = Rover.rock_angles
        Rover.worldmap[rock_ycen, rock_xcen, 1] = 255
        Rover.vision_image[:, :, 1] = rock_warped_threshed*255    
        Rover.mode = 'pursuit'
        print('Rover detected gold rock sample')
            
    else:
        Rover.pickup_counter = 0
        #print('Rover does not see any golden rock')
        Rover.vision_image[:, :, 1] = 0
        #Rover.nav_dists = Rover.nav_dists
        #Rover.nav_angles = Rover.nav_angles
        if Rover.mode == 'pursuit':
            Rover.mode = 'forward'           
        
    
    return Rover
