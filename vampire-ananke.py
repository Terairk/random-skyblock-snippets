# Script to tell whether using 2 ananke feather's to 'guarantee'
# a burger is better than using 1 ananke feather for each burger. 
#
# In theory I could extend this script to handle most cases:

import copy
import random
import numpy as np
from scipy.stats import skew

## CONSTANTS TO CONTROL

# The Main Loot table weights as referred to in:
# https://wiki.hypixel.net/Slayer
# For simplicity, this is just gonna be a simple array 
# and I need to know the index manually but this could be extended
# to include the names of the items and make them easier to identify
MAIN_LOOT_TABLE_WEIGHTS = [100, 20, 15, 15, 10, 2, 2] # we use a copy of this and this is the base
EXTRA_LOOT_TABLE_WEIGHTS = [20]
INDEX_WANTED = 5 # 0-indexed into MAIN_LOOT_TABLE_WEIGHTS
MAGIC_FIND = 33
DROPS_NEEDED = 2
ANANKE_FEATHERS_LEFT = 2
ANANKE_XP_AMOUNT = 8000
SLAYER_XP_PER_BOSS = 120
required_slayer_XP = 18400 ## THIS IS A CONSTANT FOR NOW
# As I can't line up the calculations on the wiki to match this
# so I use the ingame value

## VARIABLES
stored_slayerXP = 0
bosses_required = 0


## FUNCTIONS

def apply_rng_meter(main_table, stored_slayerXP): 
    rng_selected_weight = main_table[INDEX_WANTED]
    rng_selected_weight *= (1 + min(2 * stored_slayerXP / required_slayer_XP, 2))
    main_table[INDEX_WANTED] = rng_selected_weight

## Applies Magic Find to the Main Drops
def apply_mf(main_table):
    # These names are referred to in 
    # https://wiki.hypixel.net/Slayer
    # These calculations need to be refreshed periodically as 
    # rng meter changes
    # I'm just gonna use a sligthly modified formula compared to the wiki
    # cus mine's simplified for my use case and I ignore extra drops 
    # TODO: implement Extra drops properly
    # In my instance, AddedWeights only considers Token + Main while
    # it should consider everything, however everything - extra = Token + Main
    AddedWeights = sum(main_table)
    AddedExtraWeights = sum(EXTRA_LOOT_TABLE_WEIGHTS)
    for idx, weight in enumerate(main_table):
        new_weight = weight
        base_drop_chance = weight / (AddedWeights)
        if base_drop_chance < 0.05: 
            new_weight *= (1 + MAGIC_FIND / 100)

        main_table[idx] = new_weight

def roll_with_probability(probability):
    if not 0 <= probability <= 1:
        raise ValueError("probability must be between 0 and 1")

    random_number = random.random()
    return random_number <= probability


# This only works for main drops currently
def is_successful_drop(main_table, stored_slayerXP):
    AddedWeights = sum(main_table)
    base_drop_chance = main_table[INDEX_WANTED] / AddedWeights
    # print(base_drop_chance * 100)
    
    # if stored_slayerXP >= required_slayer_XP:
    #     print("RNG METER MAXED")
    return (stored_slayerXP >= required_slayer_XP) or roll_with_probability(base_drop_chance)

def apply_feather(stored_slayerXP, ANANKE_FEATHERS_LEFT):
    if ANANKE_FEATHERS_LEFT > 0:
        ANANKE_FEATHERS_LEFT -= 1
        stored_slayerXP += ANANKE_XP_AMOUNT

    return (stored_slayerXP, ANANKE_FEATHERS_LEFT)


## main loop now

def run_single_simulation(DROPS_NEEDED, ANANKE_FEATHERS_LEFT, stored_slayerXP=0):
    bosses_required = 0
    for _ in range(DROPS_NEEDED):
        # One iteration = one drop 
        stored_slayerXP, ANANKE_FEATHERS_LEFT = apply_feather(stored_slayerXP, ANANKE_FEATHERS_LEFT)
        # stored_slayerXP, ANANKE_FEATHERS_LEFT = apply_feather(stored_slayerXP, ANANKE_FEATHERS_LEFT)

        while True:
            main_table = copy.deepcopy(MAIN_LOOT_TABLE_WEIGHTS)
            apply_rng_meter(main_table, stored_slayerXP)
            apply_mf(main_table)
            bosses_required += 1
            is_successful = is_successful_drop(main_table, stored_slayerXP)
            stored_slayerXP += SLAYER_XP_PER_BOSS
            if is_successful:
                break

        # Now reset stored slayer XP, 
        stored_slayerXP = 0
    return bosses_required


num_trials = 10000
results = [run_single_simulation(2, 2, 0) for _ in range(num_trials)]
mean_bosses = np.mean(results)
std_bosses = np.std(results)
print(f"Mean number of bosses required is: {mean_bosses}")
print(f"Std Deviation is: {std_bosses}")
print(f"Skewness is {skew(results)}")

        

    

    

