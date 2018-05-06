[//]: # (Image References)

[image1]: ./misc/rover_image.jpg
[image2]: ./calibration_images/example_grid1.jpg
[image3]: ./calibration_images/example_rock1.jpg 
[image4]: ./output/perspective_transform.jpg 
[image5]: ./output/polar_coordinate.jpg 
[image6]: ./output/img2polar.png 
[image7]: ./output/rover2world.png 
[image8]: ./output/autonomous_data/Rover_Forward_Mode.png 
[image9]: ./output/autonomous_data/Rover_Stop_Mode.png 
[image10]: ./output/autonomous_data/Rover_Pursuit_Mode.png 
[image11]: ./output/autonomous_data/Rover_Stuck_Mode_Burried_in_Sand.png 
[image12]: ./output/autonomous_data/Rover_Stuck_Mode_Hit_Obstacles.png 
[image13]: ./output/autonomous_data/Rover_Collecting_Rock_Samples.png
[image14]: ./output/autonomous_data/Rover_All_Rocks_Collected_Mapped63p.png 
[image15]: ./output/autonomous_data/Rover_All_Rocks_Collected_Mapped95p.png


# Project: Search and Sample Return 

This project is modeled after the [NASA sample return challenge](https://www.nasa.gov/directorates/spacetech/centennial_challenges/sample_return_robot/index.html) and it provides first hand experience with the three essential elements of robotics, which are perception, decision making and actuation.  We will carry out this project in a simulator environment built with the Unity game engine. 

![alt text][image1] 

I have outlined the detailed steps taken for perception and decision making process for the autonomous navigation.  I went for the standout submission and collect all the rock samples and map about 97% of the map at fidelity above 80% at around 20fps camera feed. 

**The goals / steps of this project are the following:**  

**Training / Calibration**  

* Download the simulator and take data in "Training Mode"
* Test out the functions in the Jupyter Notebook provided
* Add functions to detect obstacles and samples of interest (golden rocks)
* Fill in the `process_image()` function with the appropriate image processing steps (perspective transform, color threshold etc.) to get from raw images to a map.  The `output_image` you create in this step should demonstrate that your mapping pipeline works.
* Use `moviepy` to process the images in your saved dataset with the `process_image()` function.  Include the video you produce as part of your submission.

**Autonomous Navigation / Mapping**

* Fill in the `perception_step()` function within the `perception.py` script with the appropriate image processing functions to create a map and update `Rover()` data (similar to what you did with `process_image()` in the notebook). 
* Fill in the `decision_step()` function within the `decision.py` script with conditional statements that take into consideration the outputs of the `perception_step()` in deciding how to issue throttle, brake and steering commands. 
* Iterate on your perception and decision function until your rover does a reasonable (need to define metric) job of navigating and mapping.  


## The Simulator
The first step is to download the simulator build that's appropriate for your operating system.  Here are the links for [Linux](https://s3-us-west-1.amazonaws.com/udacity-robotics/Rover+Unity+Sims/Linux_Roversim.zip), [Mac](	https://s3-us-west-1.amazonaws.com/udacity-robotics/Rover+Unity+Sims/Mac_Roversim.zip), or [Windows](https://s3-us-west-1.amazonaws.com/udacity-robotics/Rover+Unity+Sims/Windows_Roversim.zip).  

You can test out the simulator by opening it up and choosing "Training Mode".  Use the mouse or keyboard to navigate around the environment and see how it looks.

## Dependencies
We will need Python 3 and Jupyter Notebooks installed to do this project.  The best way to get setup with these, if you are not already, is to use Anaconda following along with the [RoboND-Python-Starterkit](https://github.com/ryan-keenan/RoboND-Python-Starterkit). 


Here is a great link for learning more about [Anaconda and Jupyter Notebooks](https://classroom.udacity.com/courses/ud1111)

## Recording Data
The git repository came with some saved test data in the folder called `test_dataset`.  In that folder we will find a csv file with the output data for position, orientation, steering, throttle etc. and the pathnames to the images recorded in each run.  There are also some saved images in the folder called `calibration_images` to do some of the initial calibration steps with.  

The first step of this project is to record data on your own.  To do this, we should first create a new folder to store the image data in.  Then launch the simulator and choose "Training Mode" then hit "r".  Navigate to the directory you want to store data in, select it, and then drive around collecting data.  Hit "r" again to stop data collection.

## Image Processing in Jupyter Notebook
Included in the IPython notebook called `Rover_Project_Test_Notebook.ipynb` are the functions from the Udacity Robotics Nanodegree lesson for performing the various steps of this project.  The notebook should function as is without need for modification.  To see what's in the notebook and execute the code there, first change the anaconda environment (I named it `RoboND`) where the cloned git repository lies:

```sh
source activate RoboND
```

and then start the jupyter notebook server at the command line like this:

```sh
jupyter notebook
```

This command will bring up a browser window in the current directory where you can navigate to wherever `Rover_Project_Test_Notebook.ipynb` is and select it.  Run the cells in the notebook from top to bottom to see the various data analysis steps.  

The last two cells in the notebook are for running the analysis on a folder of test images to create a map of the simulator environment and write the output to a video.  These cells should run as-is and save a video called `test_mapping.mp4` to the `output` folder.  This should give you an idea of how to go about modifying the `process_image()` function to perform mapping on your data.  

![alt text][image2]
![alt text][image3] 

Modifying functions to allow for color selection of obstacles and rock samples and performing a perspective transformation we get following sample images.

![alt text][image4]

We then convert the rover centric cordinate to polar coordinate to get distance and angles of each naviagable pixels as shown below.  Then we compute the mean angle to privide the rover the intended direction of travel.

![alt text][image5]

After all the transformations, we then map the rover centric images onto the worldmap. An example of the transfomrations from original image to the rover-centric polar coordinate frame is shown below. 

![alt text][image6]

Then a rotation and translation coordinate transformation is performed to bring the rover-centric image to the worldmap (shown below) assuming the position (x, y) and orientation (yaw) of the rover w.r.t. to the world coordinate system is known.

![alt text][image7]

Doing this resulted in poor fidelity of the map.  To increase the fidelity we limit the reliable vision of the rover to a radius of about 6 meters.  This helped improve the fidelity dramatically. We then move all of these functionalities to the perception function of the Aautonomous navigation stack as discussed below.



## Autonomous Navigation and Mapping 
The file called `drive_rover.py` is what we will use to navigate the environment in autonomous mode.  This script calls functions from within `perception.py` and `decision.py`.  The functions defined in the IPython notebook are all included in`perception.py` and I have filled out the function called `perception_step()` with the appropriate processing steps and update the rover map. `decision.py` includes another function called `decision_step()`, which includes an example of a conditional statement to navigate autonomously.  Here I have implemented other conditionals to make driving decisions based on the rover's state and the results of the `perception_step()` analysis.

`drive_rover.py` should work as is if you have all the required Python packages installed. Call it at the command line like this: 

```sh
python drive_rover.py
```  

Then launch the simulator and choose "Autonomous Mode".  The rover should drive itself now!  Initially the Rover did not drive very well without additional optimization in perception and decission steps.  When Rover got stuck, it was the end of the navigation since we did not have decission steps for stuck mode.  The rover was not able to navigate 40% of the map at 60% fidelity.  The fidelity was quite low around 40-50%.  To improve the fidelity of the map and better navigation, I have described below the steps I have used.  Here I'll talk about the approach I took, what techniques I used, what worked and why, where the pipeline might fail and how I might improve it if I were going to pursue this project further.  


### 1. The perception_step()

For the autonomous navigration, I have added the the image processing from `process_image()` function to the `perception_step` function in the `perception.py`. Without any modifications, at this point, the rover got a very low fidelity (~40%-50%) for navigable path, meaning that the navigable path when overlaid on the worldmap did not produce a good match. So the goal for the perception step is to get a higher fidelity map. Before we get into the details of the map fidelity improvements, I would like to talk about some details of the perspective transformation and the color thresholding. 

I have performed the perspective transformation first and then the color-thresholding. However, one can color threshold first and then apply the perspective transform.

#### Perspective transformation of the raw image
For perspective transform I used the following:
```python
def perspect_transform(image):
    dst_size = 5 
    bottom_offset = 6
    width = image.shape[1]
    height = image.shape[0]
    source = np.float32([[14, 140], [301 ,140],[200, 96], [118, 96]])
    destination = np.float32([[width/2 - dst_size, height - bottom_offset],
                      [width/2 + dst_size, height - bottom_offset],
                      [width/2 + dst_size, height - 2*dst_size - bottom_offset], 
                      [width/2 - dst_size, height - 2*dst_size - bottom_offset],
                      ])

    M = cv2.getPerspectiveTransform(source, destination)
    warped = cv2.warpPerspective(image, M, (image.shape[1], image.shape[0]))# keep same size as input image
    mask = cv2.warpPerspective(np.ones_like(image[:,:,0]), M, (image.shape[1], image.shape[0]))# keep same size as input image
    return warped, mask
```
#### Color thresholding on the warped image
In order to identify the navigable terrain, obstacls/mountains, and rocks we must apply color thresholds.  For color-thresholding I used the following RGB ranges:
```python
    navigable_warped_threshed = color_thresh(warped_image, (161, 161, 161), (255, 255, 255))
    obstacle_warped_threshed = color_thresh(warped_image, (0, 0, 0), (160, 160, 160))*mask
    rock_warped_threshed = color_thresh(warped_image, (100, 100, 0), (255, 255, 50))
```
The `mask` is used to ignore the blind spots of the Rover camera and not consider as obstacles.

The `color_thresh()` function is as below:
```python
def color_thresh(img, rgb_thresh_lower, rgb_thresh_upper):

    color_select = np.zeros_like(img[:,:,0])
    color_thresh = (img[:,:,0] >= rgb_thresh_lower[0]) & (img[:,:,0] <= rgb_thresh_upper[0]) \
                & (img[:,:,1] >= rgb_thresh_lower[1]) & (img[:,:,1] <= rgb_thresh_upper[1]) \
                & (img[:,:,2] >= rgb_thresh_lower[2]) & (img[:,:,2] <= rgb_thresh_upper[2])
    # Index the array of zeros with the boolean array and set to 1
    color_select[color_thresh] = 1
    return color_select
```

In order to improve the fidelity of the map I used the tips provided in the lesson as below.

####  Optimizing Map Fidelity (1): Consider the upper half of the rover vision to be non-navigable.  
I noticed that the upper half of the perspective tansformed image is too far for the rover to see clearly and to make a sound judgement. So clipping the image provides much better fidelity. Also, here you can define the distance upto which the rover can look for the rocks. If your Rover is a wall-crawler and you don't want it to deviate from it's path too much to pick-up the rocks from the other side of the road, then set the radius to about 40 for the rock distance from the Rover. However, I found this to be a problem for picking up rocks since it sees the rocks on it's path very late and sometimes runs over the rocks and does not pick up. I found that it is better for the Rover to pick up rocks from the other side of the road. So I kept the range to 50 to locate and pick-up the rock. In reality, I would imagine that if you send a Rover to the Mars for the sole purpose of locating and picking up rock samples then hugging the mountains would not be the first priority. 

Here is the code snippet:
```python
    navigable_xpix, navigable_ypix = pix_in_range(navigable_xpix, navigable_ypix)
    obstacle_xpix, obstacle_ypix = pix_in_range(obstacle_xpix, obstacle_ypix)
    rock_xpix, rock_ypix = pix_in_range(rock_xpix, rock_ypix, range=50) #To not care about rocks on the other side of the road set smaller range (range <= 40)
```

The function `pix_in_range()` is as below:
```python
def pix_in_range(xpix, ypix, range=60):
    dist = np.sqrt(xpix**2 + ypix**2)
    return xpix[dist < range], ypix[dist < range]
```

By ignoring the upper half of the rover image, the Fidelity significantly improved to around 70%. To improve the fidelity even further we will use the next optimization technique. 

####  Optimizing Map Fidelity (2): Consider putting limits on the roll and pitch angles to determine which transformed images are valid for mapping.  
Since the perspective transform is technically only valid when roll and pitch angles are near zero, if you're slamming on the brakes or turning hard they can depart significantly from zero, and your transformed image will no longer be a valid map. For better fidelity update world map only if roll and pitch angles are minimal (near 0 degrees or near 360 degrees). I used `Rover.pitch_min = Rover.roll_min = 0.5` and `Rover.pitch_max = Rover.roll_max = 359.5`.

Below is the code snippet:
```python
if (Rover.pitch < Rover.pitch_min or Rover.pitch > Rover.pitch_max) and (Rover.roll < Rover.roll_min or Rover.roll > Rover.roll_max):
        Rover.worldmap[obstacle_y_world, obstacle_x_world, 0] += 1
        Rover.worldmap[rock_y_world, rock_x_world,1]  += 1
        Rover.worldmap[navigable_y_world, navigable_x_world, 2] += 10
        navigable_pix = Rover.worldmap[:,:,2] > 0 #if blue channel is > 0 then set it as navigable terrain
        Rover.worldmap[navigable_pix,0] = 0 # Make obstacle channels ZERO corresponding to navigable fixels  
        Rover.worldmap = np.clip(Rover.worldmap, 0, 255) # clip to avoid overflow
```

Doing this, the Fidelity improved to around 80%. I would be interested to know if there are other methods to improve the fidelity even more.  

### 2. The decision_step()

Now, for the decission step, we need to locate the golden/yellow rocks first. This is our mission. Let's collect all the rock samples so that we can go home!

If we see any rock samples, then we must tell our Rover to navigate towards the rock sample (change the mode to `pursuit`), stop when close to the sample, collect the sample and move on. 

```python
    if len(Rover.rock_dists) > 0: #if rock_warped_threshed.any():
        Rover.pickup_counter += 1
        rock_idx = np.argmin(Rover.rock_dists) #Returns the indices of the minimum rock distance.
        rock_xcen = rock_x_world[rock_idx] #Make min. Rock dist. in Rover as center of Rock in worldmap
        rock_ycen = rock_y_world[rock_idx]
        Rover.rock_pos = (rock_xcen, rock_ycen)
        Rover.nav_dists = Rover.rock_dists
        Rover.nav_angles = Rover.rock_angles
        Rover.worldmap[rock_ycen, rock_xcen, 1] = 255
        Rover.vision_image[:, :, 1] = rock_warped_threshed*255    
        Rover.mode = 'pursuit'
        print('Rover detected gold rock sample')
            
    else:
        Rover.pickup_counter = 0
        Rover.vision_image[:, :, 1] = 0
        if Rover.mode == 'pursuit':
            Rover.mode = 'forward'    
```

Apart from `forward` and `stop` modes, I have used multiple modes. Once a rock is in view of the Rover, Rover's navigation angles change to the direction in which the rock was detected. I made my Rover a left-wall crawler. For this I add a 75% of the standard deviation to the mean navigation angle. I got this idea from one of the previous graduates. This way, the Rover does not run onto the mountain unless the speed is too high. Here is the code:
```python
Rover.steer = mean_nav_angle(Rover)
Rover.wall_offset_angle = 0.75 * np.std(Rover.nav_angles)

def mean_nav_angle(Rover):
    return np.clip( (np.mean(Rover.nav_angles) + Rover.wall_offset_angle) * 180/np.pi, -15, 15)
```

The new modes, help my robot to get un-stuck, naviagate towards a rock sample, and go home when all rock samples have been collected and robot has mapped more than 50% of the map. In addidtion to the `forward` and `stop` mode I have added the following modes: `pursuit`, `stuck`, `donut`, `gohome`.  The decission tree for all the decissions made by the Rover can be found in the `decission.py` script. 

Getting unstuck is very challenging. In my case, I let the Rover steer with full throtle whenever it thinks it's stuck. If the the Throttle is non-zero, the velocity is near zero and the Rover is not picking up samples, then we get into stuck mode. In stuck mode we check if the Rover is in spinning mode. If it is in spinning mode we bring it back to forward mode. When in stuck mode, the rover applies full-throttle while steering. If not in spinning mode, then it checks if the velocity is negative, and applies break, turns by -15 degrees and goes to stop mode. While in forward mode, we check if the rover might not be moving. 

I have noticed that, the areas around the huge black rocks/obstacles (not the golden rock samples!) around (x,y) = (148, 108) is extremely difficult to navigate. At some locations around that area it is impossible to get un-stuck even in manual mode. This is due to the fact that the wheels of the rover get burried in the sand and no amount of steering or throttle seem to help get the Rover unstuck. In this situation, I just close the roversim and reopen for a new test run.  

I have used various counters to keep track of how long the Rover is in particular mode to make decissions on when to get out of `stuck` mode, `donut` mode, and `pursuit` mode.  These counters are compared agaist constant values based on the fps.

At this stage, I am able to naviagte most of the terrain, collect all rocks and map more than 95% of the map at fidelity above 80% at around 20fps camera feed.  The fidelity increased to around 85% when the simulation runs on a better machine at 40fps. 

### 3. Visualization
For better visualization, I have added the `fps` and `status` of the rover to the bottom right map. When the rover goes back to the previously mapped areas, it was imposible to know where the Rover is in the map. So, I added a white square same as the rocks to track the Rover's position in realtime. This really helps a lot to understand where the Rover is at any particular time. I have added these functionalities to the `create_output_images` function in `supporting_functions.py`. To clean-up the code, I have moved all the transpformation functions used in `perception.py` into a separate python file `transformation.py`.

```python
def create_output_images(Rover):
...
#Let's track the rover and add it to the map as a 4x4 square grid
    rover_size = 2  
    map_add[int(np.ceil(Rover.pos[1]))-rover_size:int(np.ceil(Rover.pos[1]))+rover_size,\
                    int(np.ceil(Rover.pos[0]))-rover_size:int(np.ceil(Rover.pos[0]))+rover_size, :] = 255

    
    cv2.putText(map_add,"fps: "+str(Rover.fps), (0, 180), 
                      cv2.FONT_HERSHEY_COMPLEX, 0.4, (255, 255, 255), 1)
    cv2.putText(map_add,"Status: "+str(Rover.mode), (0, 195), 
                      cv2.FONT_HERSHEY_COMPLEX, 0.4, (255, 255, 255), 1)
```

### 4. Results
The results here show the Rover in various modes. Performing a screen recording of the RoverSim, the resulting video files were around 500MB after the completion of each run. I will only show some screen shots of the Rover at various modes.

The Forward Mode:
![alt text][image8]

The Stop Mode:
![alt text][image9]

The Pursuit Mode:
![alt text][image10]

The Stuck Mode (Burried in Sand):
![alt text][image11]

The Stuck Mode (Hitting Obstacle):
![alt text][image12]

Rover Collecting Rock Sample:
![alt text][image13]

Rover collected all 6 samples while mapped 63% of the map:
![alt text][image14]

Rover collected all 6 samples while mapped 95% of the map:
![alt text][image15]


### Wish Lists for Improvements
There are so many things that I would like to implement but don't have time to do so.  Here are my wish lists:
1. Better algorithm for detecting and avoiding obstacles
2. Create a speed dependednt brake setting for a smoother drive.
3. Not visit the areas mapped previously (Giving lower weights to the pixles visited and steer in the direction of highly weihted pixels).
4. Better un-stuck mechanism incorporating `reverse` mode.
5. Find the least possible distance the Rover needs to travel in order to go home.
6. Better decission making to avoid hitting the rocks (perhapse by making another color thresholding specific to obstacls other than the mountains, i.e. Big and Small black rocks on the way).
7. Compute total distance travelled based on velocity.
8. Adjust throttle and brake based on computed acceleration from velocity.
9. Increase map fidelity to above 90%.
10. Localization without global position information.

### Simulator Settings
I ran the simulator in an Ubuntu at screen resolution 1024x768 and graphics quality 'Good'. The frames-per-second (FPS) varried a lot from 8fps (when the computer is over loaded!) to 25fps. For above 18fps the fidelity of the map was around 80% and about 78% fidelity for 8fps. But running on a Macbook Pro 13" with core i5 and 8GB RAM, the simulator ran much faster at 40fps, which in turn also helped improving the fidelity of the map to around 85%.  


**Note: running the simulator with different choices of resolution and graphics quality may produce different results, particularly on different machines!  Make a note of your simulator settings (resolution and graphics quality set on launch) and frames per second (FPS output to terminal by `drive_rover.py`) in your writeup when you submit the project so your reviewer can reproduce your results.**
