# Modified by: Dr. Smruti Panigrahi

import numpy as np


def mean_nav_angle(Rover):
    # Add standard deviation to the mean Nav angle to make Rover a left-wall-crawler
    return np.clip( (np.mean(Rover.nav_angles) + Rover.wall_offset_angle) * 180/np.pi, -15, 15)
    
def is_moving(Rover):
    # Checks if the Rover has moved a certain distance since the last frame.
    distance_travelled = np.sqrt( (Rover.pos[0] - Rover.last_pos[0]) ** 2 +
                    (Rover.pos[1] - Rover.last_pos[1]) ** 2 )
    return distance_travelled > Rover.stuck_dist
    
def is_near_home(Rover):
    # Checks if the Rover is near home.
    distance_from_home = np.sqrt( (Rover.pos[0] - Rover.home_pos[0]) ** 2 +
                    (Rover.pos[1] - Rover.home_pos[1]) ** 2 )
    return distance_from_home < Rover.home_dist

    
# This is where you can build a decision tree for determining throttle, brake and steer 
# commands based on the output of the perception_step() function
def decision_step(Rover):

    # Implement conditionals to decide what to do given perception data
    # Here you're all set up with some basic functionality but you'll need to
    # improve on this decision tree to do a good job of navigating autonomously!

    # offset in rad used to hug the left wall 15s after the start time to avoid donut mode
    if Rover.total_time < 15:
        # Steering proportional to the (mean + standard deviation) results in
        # smaller offsets on narrow vison map and large offsets in turns and open areas
        Rover.wall_offset_angle = 0 #-0.65 * np.std(Rover.nav_angles)
    else:
        Rover.wall_offset_angle = 0.75 * np.std(Rover.nav_angles)
    
    
    if Rover.total_time == 0:
        Rover.home_pos = Rover.pos
        print("Rover Home Position (x, y): ", Rover.home_pos)
            
    if Rover.nav_angles is not None:
        # Check for Rover.mode status
         
        # If all samples has been collected and more than 90% mapped then go home           
        if is_near_home(Rover) and Rover.total_time > 30:
            print("Rover is close to Home!")
            #Rover.mode = 'gohome'
        
        if Rover.samples_collected == Rover.total_samples:
            if Rover.mapped >= 50:
                Rover.mode = 'gohome'
            else:
                Rover.mode = 'forward'
 
        if (Rover.throttle >= Rover.throttle_set and np.abs(Rover.vel) <= 0.01 and not Rover.picking_up):
            Rover.stuck_counter += 1
            print("Stuck counter: ", Rover.stuck_counter)
                
            if (Rover.stuck_counter >= 2*Rover.fps):
                print("Rover is still stuck! Try turning in the opposite direction")
                Rover.steer = -15
                Rover.brake = 0
                Rover.throttle = 0 #5*Rover.throttle_set
                Rover.mode = 'stuck'
                Rover.stuck_counter = 0
            else:
                Rover.mode = 'forward'

        elif (Rover.throttle == Rover.throttle_set and Rover.steer == 15 and Rover.vel > 0.5):
            Rover.donut_counter += 1
            if (Rover.donut_counter >= 5*Rover.fps):
                print("Rover eating donut!")
                print("Donut counter: ", Rover.donut_counter)
                Rover.throttle = 0
                Rover.brake = 0 
                Rover.steer = -15
                Rover.mode = 'donut'
                            
        elif Rover.picking_up == 1:
            Rover.throttle = 0
            Rover.steer = 0
            Rover.brake = Rover.brake_set
            Rover.mode = 'stop'
            Rover.samples_collected += 1

        elif Rover.near_sample == 1:
            Rover.throttle = 0
            Rover.steer = 0
            Rover.brake = Rover.brake_set
            Rover.mode = 'stop'
          
        elif Rover.mode == 'pursuit':
            print("Pickup counter: ", Rover.pickup_counter)
            if Rover.pickup_counter <= 100:
                Rover.wall_offset_angle = 0;
                print("Rover Picking up Rock..........")
                Rover.steer = mean_nav_angle(Rover)
                Rover.brake = 0
                Rover.throttle = 0
                if Rover.vel <= 0.2:
                    Rover.throttle = Rover.throttle_set
                else:
                    Rover.throttle = 0
                Rover.samples_located += 1
                Rover.mode == 'stop'
            else:
                Rover.steer = mean_nav_angle(Rover)
                Rover.brake = 0
                Rover.throttle = 0
                Rover.mode = 'forward'
                Rover.pickup_counter = 0

        
        elif Rover.mode == 'forward':            
            # Check the extent of navigable terrain
            if len(Rover.nav_angles) >= Rover.stop_forward:
                # Rover.brake = 0
                # If mode is forward, navigable terrain looks good
                # and velocity is below max, then throttle
                if Rover.vel < Rover.max_vel:
                    # Set throttle value to throttle setting
                    Rover.throttle = Rover.throttle_set
                    Rover.brake = 0
                elif Rover.vel > Rover.max_vel:
                    Rover.throttle = 0
                    Rover.brake = 0.2*Rover.brake_set
                else:  # Else coast
                    Rover.throttle = 0
                    Rover.brake = 0
                # Set steering to average angle clipped to the range +/- 15
                Rover.steer = mean_nav_angle(Rover)
                    
            # If there's a lack of navigable terrain pixels then go to 'stop' mode
            elif len(Rover.nav_angles) < Rover.stop_forward:
                # Set mode to "stop" and hit the brakes!
                Rover.throttle = 0
                # Set brake to stored brake value
                Rover.brake = 5*Rover.brake_set
                Rover.steer = 0
                Rover.mode = 'stop'

        # If we're already in "stop" mode then make different decisions
        elif Rover.mode == 'stop':
            # If we're in stop mode but still moving keep braking
            if Rover.vel > 0.2:
                Rover.throttle = 0
                Rover.brake = 5*Rover.brake_set
                Rover.steer = 0
            # If we're not moving (vel < 0.2) then do something else
            elif Rover.vel <= 0.2:
                # Now we're stopped and we have vision data to see if there's a path forward
                if len(Rover.nav_angles) < Rover.go_forward:
                    Rover.throttle = 0
                    # Release the brake to allow turning
                    Rover.brake = 0
                    # Turn range is +/- 15 degrees, when stopped the next line will induce 4-wheel turning
                    Rover.steer = -15
                # If we're stopped but see sufficient navigable terrain in front then go!
                elif len(Rover.nav_angles) >= Rover.go_forward:
                    # Set throttle back to stored value
                    Rover.throttle = Rover.throttle_set
                    # Release the brake
                    Rover.brake = 0
                    # Set steer to mean angle
                    Rover.steer = mean_nav_angle(Rover)
                    Rover.mode = 'forward'
                    
        elif Rover.mode == 'stuck': 
            if (Rover.throttle == 0 and Rover.brake == 0 and Rover.steer != 0): #spinning in place
                print("Rover is spinning in place")
                Rover.throttle = 0
                Rover.brake = Rover.brake_set
                Rover.steer = 0
                Rover.mode = 'forward'

            elif (Rover.throttle >= Rover.throttle_set and Rover.vel <= 0.5):
                print("Rover is still stuck")
                Rover.steer = -15
                Rover.throttle = 5*Rover.throttle_set
                Rover.brake = 0
                Rover.mode = 'stop'

            elif Rover.vel < -0.2: #if rover moving backwards go to stop mode
                Rover.throttle = 0
                Rover.brake = Rover.brake_set
                Rover.steer = -15
                print("Rover out of stuck mode and going to stop mode")
                Rover.mode = 'stop'
            else:
                Rover.stuck_counter = 0
                Rover.throttle = 0
                Rover.brake = Rover.brake_set
                Rover.steer = -15
                Rover.mode = 'stop'
                
        elif Rover.mode == 'donut':
            Rover.throttle = 0
            Rover.brake = 0 #Rover.brake_set
            Rover.wall_offset_angle *= -2
            Rover.steer = mean_nav_angle(Rover)
            if (Rover.donut_counter >= 5*Rover.fps + 5): # Wait for 6 frames to turn Rover by 90deg
                Rover.donut_counter = 0
                Rover.mode = 'stop'
            else:
                Rover.mode = 'forward'
            
        elif Rover.mode == 'gohome':
            if is_near_home(Rover):
                Rover.throttle = 0
                Rover.brake = Rover.brake_set
                Rover.steer = 0
                print("Rover is home")
            else:
                Rover.mode = 'forward'

    # Just to make the rover do something even if no modifications have been made to the code
    else:
        Rover.throttle = Rover.throttle_set
        Rover.steer = 0
        Rover.brake = 0
    
    
    # If in a state where want to pickup a rock send pickup command
    if Rover.near_sample and Rover.vel == 0 and not Rover.picking_up:
        Rover.send_pickup = True
        
        
    return Rover

