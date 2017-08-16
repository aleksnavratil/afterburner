###################################################################################################
###################################################################################################
## afterburner.py
## Monday 10 July 
## Aleks Navratil
## The point of this program is to learn spoken human languages
## It's substantially a ripoff/extension of language-101.com
###################################################################################################
###################################################################################################

import pandas as pd ## For importing data from file as a dataframe
import yaml ## For importing our config file
import pygame ## For playing our audio clips
import os ## For constructing file path names
import sys ## For halting the program if the user runs out of lessons
import datetime ## To decide when a phrase is due for study
import time ## For progressbars
import sqlite3 ## For managing the state of the user's phrases
import pystache ## For sane templating
from easygui import * ## For user interfaces
import zipfile ## For unzipping our cartridge files


###################################################################################################
###################################################################################################

## Load config information from file. We'll later load cart-specific config info from another similar file
with open("config.yaml", 'r') as config_file:
    config = yaml.load(config_file)
        
## For debug
pd.set_option('display.max_columns', 500)
pd.set_option('display.width', 1000)

###################################################################################################
###################################################################################################

def print_welcome_screen():
    ## In this function, we display a welcome screen to the user
    
    welcome_message = """Welcome to Afterburner, one of the faster ways to learn a spoken human language."""
    title="Afterburner"
    
    ## Print a message box on the screen
    msgbox(welcome_message, title = "Afterburner", ok_button = "Let's go!")
    return(welcome_message)

###################################################################################################
###################################################################################################

def get_path_to_cartridge_file():
    ## In this function, we construct and return the absolute path to the cartridge file
    
    path_to_cartridge_library = config['absolute_path_to_cartridge_library']
    name_of_cartridge_file = config['cartridge_name'] + '.zip'
    absolute_path_to_cartridge_file = os.path.join(path_to_cartridge_library, name_of_cartridge_file)
    return(absolute_path_to_cartridge_file)
    
###################################################################################################
###################################################################################################

def unzip_cartridge_file(path_to_cartridge_file):
    ## In this function, we consume as input the path to the cartridge file from the config file.
    ## We unzip this cartridge file into an assets directory which will eventually contain
    ## .mp3's and a .csv and a .sqlite db
    loading_message = """"Since we're running this cartridge for the first time, afterburner is now unpacking the cartridge. This will take a couple minutes."""
    title="Afterburner cartridge loading"
    
    ## Print a message box on the screen explaining why this takes so long
    msgbox(loading_message, title = title)
    
    ## Now unzip the cartridge file:
    ## Get the parent directory of wherever the cartridge is
    directory_to_unzip_into = os.path.dirname(path_to_cartridge_file)
    
    zip_ref = zipfile.ZipFile(path_to_cartridge_file, 'r')
    zip_ref.extractall(directory_to_unzip_into)
    zip_ref.close()
    
    return(directory_to_unzip_into)

###################################################################################################
###################################################################################################

def get_path_to_assets_dir():
    ## In this function, we get the path to the assets directory in which the cart file was unzipped.
    ## This is just a convenience function which is substantially similar to get_path_to_cartridge_file().
    ## It returns the same thing but without a .zip extension
    
    path_to_cartridge_library = config['absolute_path_to_cartridge_library']
    name_of_assets_dir = config['cartridge_name']
    absolute_path_to_assets_dir= os.path.join(path_to_cartridge_library, name_of_assets_dir)
    return(absolute_path_to_assets_dir)

###################################################################################################
###################################################################################################

def load_cartridge_specific_config():
    ## Having unzipped our cart, we should have an /assets directory. We can get the
    ## cartridge specific config file out of here and load it.

    path_to_assets_dir = get_path_to_assets_dir()
    absolute_path_to_cart_config = os.path.join(path_to_assets_dir, 'cartridge_specific_config.yaml')
    with open(absolute_path_to_cart_config, 'r') as cart_config_file:
        cart_config = yaml.load(cart_config_file)

    return(cart_config)
    
###################################################################################################
###################################################################################################

# def show_progress_bar():
#     ## In this function, we print a visual progressbar to the screen.
#     bar = progressbar.ProgressBar()
#     for i in bar(range(500)): ## On my machine, this gives us a roughly 10-second progress bar, which is what we want
#         time.sleep(0.02)
#     return(0)
    
###################################################################################################
###################################################################################################

def ask_if_user_can_say_phrase(phrase):
    ## In this function, we ask the user whether he said the phrase at all
    ## (here we ignore how well he said it, and focus only on whether he attempted to say it at all)
    
    ## Display a pair of buttons to determine whether the user can even say the phrase
    button_text_for_attempted_speech = "I've tried to say this out loud, show me the answer"
    button_text_for_failure_to_speak = "I don't know, show me the answer"

    string1 = "Read this " + cart_config['name_of_known_language'] + " phrase, then say the " + cart_config['name_of_target_language'] + " equivalent out loud.\n"
    string2 = "\nMeaning : " + phrase['phrase_in_known_language']
    string3 = "\nLiteral : " + phrase['literal_translation_from_target_language_to_known_language']
    string4 = "\n\nDid you try to say this out loud?"
    message = string1 + string2 + string3 + string4
    title = "Afterburner"
    choices = [button_text_for_attempted_speech, button_text_for_failure_to_speak]
    
    did_user_say_the_phrase = indexbox(message, title, choices)
    # show_progress_bar() ## TODO: FIGURE OUT WHAT TO DO ABOUT THIS
    
    return(did_user_say_the_phrase)

###################################################################################################
###################################################################################################

def decide_what_to_do(did_user_say_the_phrase, phrase):
    ## In this function, we handle some branching logic based on whether or not the user is 
    ## sufficiently competent to even attempt the phrase
    
    if(did_user_say_the_phrase == 0):
        ## This logical branch corresponds to the case when the user *did say* the phrase
        user_quality_estimate = ask_for_user_quality_estimate(phrase)
        return(user_quality_estimate)
        
    elif(did_user_say_the_phrase == 1):
        ## This branch corresponds to the case when the user *failed to say* the phrase
        show_answer(phrase)
        return(0)
    
###################################################################################################
###################################################################################################

def show_answer(phrase):
    ## In this function, we display the correct answer, and play an audio clip of the phrase by calling the appropriate function
    ## This is basically only useful if the user *didn't even attempt to say the phrase*
    ## Here we grossly mix audio-and-ui related code in a single function here.
    ## However, there's a good reason for this: It allows us to play the sound at almost
    ## the same time as the UI renders
    
    def render_ui():    
        ## We define this as a nested function to make it easier to see what's going on with the audio stream/printing stuff
        string1 = "Read this " + cart_config['name_of_known_language'] + " phrase, then say the " + cart_config['name_of_target_language'] + " equivalent out loud.\n"
        string2 = "\nMeaning : " + phrase['phrase_in_known_language']
        string3 = "\nLiteral : " + phrase['literal_translation_from_target_language_to_known_language']    
        string4 = "\nAnswer  : " + phrase['idiomatic_translation_to_target_language']

        message = string1 + string2 + string3 + string4
        title = "Afterburner"
        msgbox(msg = message, title = "Afterburner", ok_button = "I have said this out loud, show me the next phrase")
        
        
    # Open the file for reading after figuring out the relevant
    name_of_sound_to_play = str(phrase['phrase_uuid'])
    full_path_to_sound_to_play = os.path.join(get_path_to_assets_dir(), name_of_sound_to_play)
    
    pygame.mixer.init()
    pygame.mixer.music.load(full_path_to_sound_to_play)
    pygame.mixer.music.play()
    ## Now that we've started playing the sound, let's display our UI              
    render_ui()
    while pygame.mixer.music.get_busy() == True:
        continue
    
    return(name_of_sound_to_play)          
    
###################################################################################################
###################################################################################################

def ask_for_user_quality_estimate(phrase):
    ## In this function, we take input from the user about how well they said the sentence.
    ## This is basically only useful if the user is *sufficiently competent to even attempt the phrase*
    ## Here we grossly mix audio-and-ui related code in a single function.
    ## However, there's a good reason for this: It allows us to play the sound at almost
    ## the same time as the UI renders
    
    def render_ui():    
        string1 = "Read this " + cart_config['name_of_known_language'] + " phrase, then say the " + cart_config['name_of_target_language'] + " equivalent out loud.\n"
        string2 = "\nMeaning : " + phrase['phrase_in_known_language']
        string3 = "\nLiteral : " + phrase['literal_translation_from_target_language_to_known_language']    
        string4 = "\nAnswer  : " + phrase['idiomatic_translation_to_target_language']

        message = string1 + string2 + string3 + string4
        title = "Afterburner"
        choices = ['Wrong', 'Some Mistakes', 'Shaky', 'Good', 'Perfect']
        users_quality_estimate = indexbox(msg = message, title = "Afterburner", choices = choices)
        return(users_quality_estimate)


    # Open the file for reading after figuring out the relevant id number aka filename
    name_of_sound_to_play = str(phrase['phrase_uuid'])
    full_path_to_sound_to_play = os.path.join(get_path_to_assets_dir(), name_of_sound_to_play)

    pygame.mixer.init()
    pygame.mixer.music.load(full_path_to_sound_to_play)
    pygame.mixer.music.play()
    ## Now that we've started playing the sound, let's display our UI  
    users_quality_estimate = render_ui()
    while pygame.mixer.music.get_busy() == True:
        continue
        
    return(users_quality_estimate)

###################################################################################################
###################################################################################################

def figure_out_when_to_study_next(users_quality_estimate):
    ## In this function, we consume as input the user's estimate of how well he said the phrase.
    ## We emit as output a timestamp, representing when the phrase is next due for study
    ## At some point, this should be refactored as a real spaced-repetition algo.
    
    users_quality_estimate = int(users_quality_estimate)
    if(users_quality_estimate <= 0): ## This corresponds to both the case when the user chooses "I don't know how to say this" and also when he tries to say it, but gives himself a grade of 1.
        study_due_date = datetime.datetime.now() + datetime.timedelta(minutes = 1)
    elif(users_quality_estimate == 1):
        study_due_date = datetime.datetime.now() + datetime.timedelta(minutes = 2)
    elif(users_quality_estimate == 2):
        study_due_date = datetime.datetime.now() + datetime.timedelta(minutes = 4)
    elif(users_quality_estimate == 3):
        study_due_date = datetime.datetime.now() + datetime.timedelta(minutes = 8)
    elif(users_quality_estimate == 4):
        study_due_date = datetime.datetime.now() + datetime.timedelta(minutes = 16)
    else:
        print("Something went wrong with the user's quality estimate of how well he said the phrase :(")
        study_due_date = -1  
    return(study_due_date)
    
# ###################################################################################################
# ###################################################################################################
#
# def convert_csv_to_sqlite():
#     ## In this function, we take our phrase csv and make a sqlite db out of it
#     ## We'll use this db to store our study state. This function will only be run the first time afterburner loads.
#     ## Before we load it, we'll have to unpack our .zip archive into an assets dir, which is itself in the cart library (for now at least)
#
#     path_to_cart_file = get_path_to_cartridge_file()
#     path_to_cart_library = unzip_cartridge_file(path_to_cart_file)
#
#     path_to_assets_dir = get_path_to_assets_dir()
#     path_to_phrases_csv = os.path.join(path_to_assets_dir, config['cartridge_name'] + '.csv')
#     phrases = pd.read_csv(path_to_phrases_csv, encoding = 'utf8') ## Load phrase text from file
#
#     path_to_sqlite_file = os.path.join(path_to_assets_dir, config['cartridge_name'] + '.sqlite')
#     conn = sqlite3.connect(path_to_sqlite_file)
#
#     path_to_sqlite_db = config['cartridge_name']
#     phrases.to_sql(path_to_sqlite_db, conn, if_exists="fail") ## We don't want to overwrite the user's progress
#     conn.commit()
#     conn.close()
#     return("Successfully created a sqlite DB")
    
###################################################################################################
###################################################################################################

def get_path_to_sqlite_db():
    ## In this function, we figure out the name of our sqlite table and return it
    
    path_to_sqlite_db = os.path.join(config['absolute_path_to_cartridge_library'], config['cartridge_name'], config['cartridge_name'] + '.sqlite')
    return(path_to_sqlite_db)

###################################################################################################
###################################################################################################

def get_phrases_to_study(name_of_sqlite_table, current_active_lesson):
    ## In this function, we reorder our phrase db and get N phrases which are due for study
    
    conn = sqlite3.connect(path_to_sqlite_db)
    conn.row_factory = sqlite3.Row ## Important, this allows us to get dicts instead of tuples from the db, which gives us column names in the data we get from the db
    c = conn.cursor()
    query_template = """
    select 
        *
    from
        {{{name_of_sqlite_table}}}
    where
        lesson = {{current_active_lesson}}
    order by
        timestamp_when_phrase_is_due_for_study desc
    limit 1
    """
    
    params_to_sub = {'name_of_sqlite_table' : name_of_sqlite_table
                   , 'current_active_lesson' : current_active_lesson}
    query = pystache.render(query_template, params_to_sub)

    c.execute(query)
    result = c.fetchone()
    conn.commit()
    conn.close()
    
    ## If result is None, it means we have no more lessons left
    if(result is None):
        print("Congratulations. You have finished all available lessons for this language pair. The program will now terminate.\n\n")
        sys.exit()
    return(result)
    
###################################################################################################
###################################################################################################

def update_db(phrase, study_due_date):
    ## In this function, we tell our sqlite db how well we're doing on this phrase
    
    conn = sqlite3.connect(path_to_sqlite_db)
    c = conn.cursor()
    
    update_query_template = """
    update {{{name_of_sqlite_table}}} 
    set timestamp_when_phrase_is_due_for_study = '{{time}}'
    where phrase_uuid = {{relevant_uuid}}
    ;
    """
    params_to_sub = {'name_of_sqlite_table': name_of_sqlite_table
                   , 'time' : study_due_date
                   , 'relevant_uuid' : phrase['phrase_uuid']}
                   
    update_query = pystache.render(update_query_template, params_to_sub)

    c.execute(update_query)
    conn.commit()
    conn.close()
    return(0)
    
###################################################################################################
###################################################################################################
    
def get_current_active_lesson(name_of_sqlite_table):
    ## In this function, we ask the db to tell us which lesson the user is currently working on.
    ## To get this, we just take the highest-numbered lesson that has meaningful due-for-study timestamps
    
    conn = sqlite3.connect(path_to_sqlite_db)
    conn.row_factory = sqlite3.Row ## Important, this allows us to get dicts instead of tuples from the db, which gives us column names in the data we get from the db
    c = conn.cursor()
    
    get_current_active_lesson_query_template = """
    select
        max(lesson)
    from
        {{name_of_sqlite_table}}
    where
        timestamp_when_phrase_is_due_for_study != -1
    """
    params_to_sub = {'name_of_sqlite_table' : name_of_sqlite_table}
    get_current_active_lesson_query = pystache.render(get_current_active_lesson_query_template, params_to_sub)
    
    c.execute(get_current_active_lesson_query)
    result = c.fetchone()
    
    conn.commit()
    conn.close()
    result = result[0] ## Just get the integer we care about
    if(result is None): ## If this happens, it means we haven't learned any phrases yet
        result = 0 ## Set it to the 0th lesson, aka the easiest one
    return(result)
    
    
###################################################################################################
###################################################################################################
    
def detect_if_new_lesson_needed(name_of_sqlite_table, current_active_lesson):
    ## In this function, we ask the db if the user has completed all the phrases in the current lesson.
    ## If that's the case, we should move on to the next lesson.
    
    conn = sqlite3.connect(path_to_sqlite_db)
    conn.row_factory = sqlite3.Row ## Important, this allows us to get dicts instead of tuples from the db, which gives us column names in the data we get from the db
    c = conn.cursor()
    
    query_template = """
    select 
        min(timestamp_when_phrase_is_due_for_study)
    from
        {{name_of_sqlite_table}}
    where
        lesson = {{current_active_lesson}}
        and timestamp_when_phrase_is_due_for_study != -1 -- Avoid the ones we haven't studied yet
    ;
    """
    
    params_to_sub = {'name_of_sqlite_table': name_of_sqlite_table
                   , 'current_active_lesson' : current_active_lesson
                    }
                   
    query = pystache.render(query_template, params_to_sub)

    c.execute(query)
    result = c.fetchone()
    result = result[0] ## Just get the timestamp we care about
    
    conn.commit()
    conn.close()
    
    if(result is None): ## This corresponds to the edge case when we haven't studied any phrases yet, so all the timestamps are -1's
        lesson = current_active_lesson
    elif(result > str(datetime.datetime.now())):
        study_remedial_phrases(name_of_sqlite_table, current_active_lesson) ## If it's time for a lesson change, let's study our remedial phrases
        lesson = current_active_lesson + 1
    else:
        lesson = current_active_lesson
        
    return(lesson)

###################################################################################################
###################################################################################################

def study_remedial_phrases(name_of_sqlite_table, current_active_lesson):
    ## In this function, we look back through previous lessons and identify phrases which are due
    ## for study. We'll do this fairly regularly, to make sure nothing slips though the cracks
    ## and ends up forgotten. Note that here we return phrase rows from arbitrary lessons that
    ## have already been studied.
    
    conn = sqlite3.connect(path_to_sqlite_db)
    conn.row_factory = sqlite3.Row ## Important, this allows us to get dicts instead of tuples from the db, which gives us column names in the data we get from the db
    c = conn.cursor()
    
    query_template = """
    select
        *
    from
        {{name_of_sqlite_table}}
    where
        lesson < {{current_active_lesson}}
    order by
        timestamp_when_phrase_is_due_for_study desc
    -- We intentionally omit a limit clause here. This is an opinonated design decision which may need to be reversed
    """
    
    params_to_sub = {'name_of_sqlite_table': name_of_sqlite_table
                   , 'current_active_lesson' : current_active_lesson
                    }
                   
    query = pystache.render(query_template, params_to_sub)

    c.execute(query)
    result = c.fetchall()    
    conn.commit()
    conn.close()
    
    ## Iterate over the phrases we've received here
    for remedial_phrase in result:
        learn_phrase(remedial_phrase)
    
    return(result)
    
###################################################################################################
###################################################################################################

def learn_phrase(phrase):
    ## In this function, we gang up a bunch of the functions above and expose them 
    ## through a single interface

    did_user_say_the_phrase = ask_if_user_can_say_phrase(phrase)
    users_quality_estimate = decide_what_to_do(did_user_say_the_phrase, phrase)
    delay_till_next_study = figure_out_when_to_study_next(users_quality_estimate)
    update_db(phrase, delay_till_next_study)
    return(phrase)

###################################################################################################
###################################################################################################
## Call functions in a sensible order

if __name__ == "__main__":
    if not os.path.isdir(get_path_to_assets_dir()): ## If we're running for the first time, we can unpack our cartridge zip. Otherwise, we can skip this step
        unzip_cartridge_file(get_path_to_cartridge_file())
    cart_config = load_cartridge_specific_config() ## Figure out the names of our languages etc.
    print_welcome_screen()
    path_to_sqlite_db = get_path_to_sqlite_db()
    name_of_sqlite_table = config['cartridge_name']
    current_active_lesson = get_current_active_lesson(name_of_sqlite_table)
    
    ## Get a phrase to study
    while True:
        current_active_lesson = detect_if_new_lesson_needed(name_of_sqlite_table, current_active_lesson)
        phrase_to_study = get_phrases_to_study(name_of_sqlite_table, current_active_lesson)
        learn_phrase(phrase_to_study)
    
###################################################################################################
###################################################################################################
## TODO's: 
# * Add 10 second progress bar while the user is trying to say the phrase
# * Use a better GUI system that doesn't flicker every time you click something
# * Figure out how to get audio from movies/tv/radio and two-language-track closed-captions, in order to prevent us from having to pay for native speakers
# DONE * Get the phraselist from http://frequencylists.blogspot.com/2016/08/5000-italian-sentences-sorted-from.html
# * Implement a naive machine translation?
# * Build facilities for loading fully-modularized .zip file of all the .mp3's and the .csv, aka "cartridge" like in NES
# * Print study stats, such as total hours studied, what lesson you're on, how many phrases fall into each bucket, etc.
# * Package afterburner as a standalone program