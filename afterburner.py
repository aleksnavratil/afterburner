###################################################################################################
###################################################################################################
## afterburner.py
## Monday 10 July 2017
## Aleks Navratil
## The point of this program is to learn spoken human languages
## It's substantially a ripoff/extension of language-101.com
###################################################################################################
###################################################################################################
## First, let's handle some boilerplate
# -*- coding: utf8 -*-
import yaml ## For importing our config file
from pygame import mixer ## For playing our audio clips
import os ## For constructing file path names
import sys ## For halting the program if the user runs out of lessons
import datetime ## To decide when a phrase is due for study
import sqlite3 ## For managing the state of the user's phrases
import pystache ## For sane templating
from easygui import * ## For user interfaces
import zipfile ## For unzipping our cartridge files
import emoji ## For displaying emojis in the UI
from Tkinter import Tk ## For hacking around with GUI's to make our UI appear on top
import time ## For timing our study durations
###################################################################################################
###################################################################################################

#-----------------------------------------------------------------------
# Define a class named Settings as a subclass of EgStore. This will 
# handle our persistence of the user's preferred cartridge file
#-----------------------------------------------------------------------
class Settings(EgStore):

    def __init__(self, filename):  # filename is required
        #-------------------------------------------------
        # Specify default/initial values for variables that
        # this particular application wants to remember.
        #-------------------------------------------------
        self.absolute_path_to_last_used_cart_file = ""

        #-------------------------------------------------
        # For subclasses of EgStore, these must be
        # the last two statements in  __init__
        #-------------------------------------------------
        self.filename = filename  # this is required
        self.restore()            # restore values from the storage file if possible

###################################################################################################
###################################################################################################

def print_welcome_screen():
    ## In this function, we display a welcome screen to the user and ask if he'd like to continue
    ## studying the same cartridge as previously, or study a new one

    ## First, try to make our GUI stop appearing at the bottom of the window stack on OSX. Instead, it should appear in the foreground.
    t = Tk()
    # Hope that the destroy is fast enough not to be seen.
    t.destroy()
    
    ## Gaaad what a hack :/
    script = 'tell application "System Events" to set frontmost of the first process whose unix id is {pid} to true'.format(pid=os.getpid())
    os.system("/usr/bin/osascript -e '{script}'".format(script=script))
    
    ## Now we can actually start doing useful stuff
    
    #-----------------------------------------------------------------------
    # create "settings", a persistent Settings object, which inherits from
    # the class defined above.
    # Note that the "filename" argument is required.
    # The directory for the persistent file must already exist.
    #-----------------------------------------------------------------------
    settingsFilename = os.path.join(os.getcwd(), '.afterburner_persistent_settings.txt') ## Here we try to use the parent directory of our executable's pseudo dir
    settings = Settings(settingsFilename)
    
    ## Figure out a polite welcome message, and print it to the screen.
    welcome_message = """Welcome to Afterburner, one of the faster ways to learn a spoken human language."""
    keep_studying_same_language_button_text = "Keep studying the same cartridge as last time"
    pick_a_new_cartridge_button_text = "Study a new cartridge file"
    
    choices = [keep_studying_same_language_button_text, pick_a_new_cartridge_button_text]
    
    users_desire = indexbox(msg = welcome_message, title = "Afterburner", choices = choices)
    
    ## Depending on what the user wants to do, we can take one of two actions
    if(users_desire == 0):
        if(settings.absolute_path_to_last_used_cart_file != ''): ## Make sure the settings file exists
            return(settings.absolute_path_to_last_used_cart_file) ## If it does exist, just return the path from it
        else:
           absolute_path_to_cart = fileopenbox(filetypes = ['*.cart']) ## If it doesn't exist, just ask the user for the path again. This is the same as if users_desire = 1
           settings.absolute_path_to_last_used_cart_file = absolute_path_to_cart
           settings.store()    # Persist the settings to disk
           return absolute_path_to_cart 
        
    elif(users_desire == 1):
        absolute_path_to_cart = fileopenbox(filetypes = ['*.cart'])
        settings.absolute_path_to_last_used_cart_file = absolute_path_to_cart
        settings.store()    # Persist the settings to disk
        return absolute_path_to_cart
    else:
        return("Something went wrong in the print_welcome_screen() function")

###################################################################################################
###################################################################################################

def get_path_to_users_cart():
    ## In this function, we open a file picker GUI and let the user select the path to the 
    ## relevant cartridge file
    
    absolute_path_to_cart = fileopenbox(filetypes = ['*.cart'])
    return absolute_path_to_cart

###################################################################################################
###################################################################################################

def unzip_cartridge_file(path_to_cartridge_file):
    ## In this function, we consume as input the path to the cartridge file from the config file.
    ## We unzip this cartridge file into an assets directory which will eventually contain
    ## .mp3's and a .csv and a .sqlite db
    loading_message = """Since we're running this cartridge for the first time, afterburner is now unpacking the cartridge. This will take a couple minutes."""
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
    
    absolute_path_to_assets_dir = path_to_cartridge_file.replace('.cart', '')
    return(absolute_path_to_assets_dir)

###################################################################################################
###################################################################################################

def load_cartridge_specific_config(path_to_cartridge_file):
    ## Having unzipped our cart, we should have an /assets directory. We can get the
    ## cartridge specific config file out of here and load it.

    path_to_assets_dir = get_path_to_assets_dir()
    absolute_path_to_cart_config = os.path.join(path_to_assets_dir, 'cartridge_specific_config.yaml')
    with open(absolute_path_to_cart_config, 'r') as cart_config_file:
        cart_config = yaml.load(cart_config_file)

    return(cart_config)
    
###################################################################################################
###################################################################################################

def ask_if_user_can_say_phrase(phrase):
    ## In this function, we ask the user whether he said the phrase at all
    ## (here we ignore how well he said it, and focus only on whether he attempted to say it at all)
    
    ## Display a pair of buttons to determine whether the user can even say the phrase
    button_text_for_attempted_speech = "I've tried to say this out loud, show me the answer"
    button_text_for_failure_to_speak = "I don't know, show me the answer"
    button_text_for_quit = "Quit Afterburner"

    string1 = "Read this " + cart_config['name_of_known_language'] + " phrase, then say the " + cart_config['name_of_target_language'] + " equivalent out loud.\n"
    string2 = "\nMeaning : " + phrase['phrase_in_known_language']
    string3 = "\nLiteral : " + phrase['literal_translation_from_target_language_to_known_language']
    string4 = "\n\nDid you try to say this out loud?"
    message = string1 + string2 + string3 + string4
    title = "Afterburner"
    choices = [button_text_for_attempted_speech, button_text_for_failure_to_speak, button_text_for_quit]
    
    did_user_say_the_phrase = indexbox(message, title, choices, cancel_choice = 2)

    if(did_user_say_the_phrase == 2): ## This is a hack, insofar as we're overloading did_user_say_the_phrase :/ But it's expedient.
        sys.exit(0) ## Quit the program
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
    
    mixer.init()
    mixer.music.load(full_path_to_sound_to_play)
    mixer.music.play()
    ## Now that we've started playing the sound, let's display our UI              
    render_ui()
    while mixer.music.get_busy() == True:
        continue
    
    return(name_of_sound_to_play)          
    
###################################################################################################
###################################################################################################

def ask_for_user_quality_estimate(phrase):
    ## In this function, we take input from the user about how well he said the sentence.
    ## This is basically only useful if the user is *sufficiently competent to even attempt the phrase*
    ## Here we grossly mix audio-and-ui related code in a single function.
    ## However, there's a good reason for this: It allows us to play the sound at almost
    ## the same time as the UI renders
    
    def render_ui():    
        string1 = "How well did you say the phrase?\n"
        string2 = "\nMeaning : " + phrase['phrase_in_known_language']
        string3 = "\nLiteral : " + phrase['literal_translation_from_target_language_to_known_language']    
        string4 = "\nAnswer  : " + phrase['idiomatic_translation_to_target_language']

        message = string1 + string2 + string3 + string4
        title = "\xF0\x9F\x94\xA5Afterburner\xF0\x9F\x94\xA5" ## TODO: MAKE THESE EMOJIS APPEAR IN THE TITLEBAR 
        choices = ['\xF0\x9F\x98\x94Wrong\xF0\x9F\x98\x94'
                 , '\xF0\x9F\x98\xA5Some Mistakes\xF0\x9F\x98\xA5'
                 , '\xF0\x9F\x98\x96Shaky\xF0\x9F\x98\x96'
                 , '\xF0\x9F\x98\x83Good\xF0\x9F\x98\x83'
                 , '\xF0\x9F\x98\x81Perfect\xF0\x9F\x98\x81'
                   ] ## Obviously you can't have a UI without emojis. Get the codes for these from e.g. https://apps.timwhitlock.info/emoji/tables/unicode
                 
        users_quality_estimate = indexbox(msg = message, title = "Afterburner", choices = choices)
        return(users_quality_estimate)


    # Open the file for reading after figuring out the relevant id number aka filename
    name_of_sound_to_play = str(phrase['phrase_uuid'])
    full_path_to_sound_to_play = os.path.join(get_path_to_assets_dir(), name_of_sound_to_play)

    mixer.init()
    mixer.music.load(full_path_to_sound_to_play)
    mixer.music.play()
    ## Now that we've started playing the sound, let's display our UI  
    users_quality_estimate = render_ui()
    while mixer.music.get_busy() == True:
        continue
        
    return(users_quality_estimate)

###################################################################################################
###################################################################################################

def figure_out_when_to_study_next(users_quality_estimate):
    ## In this function, we consume as input the user's estimate of how well he said the phrase.
    ## We emit as output a timestamp, representing when the phrase is next due for study
    ## At some point, this should be refactored as a real spaced-repetition algo.
    
    try:
        users_quality_estimate = int(users_quality_estimate)
    except TypeError: ## This is what happens when the user presses escape
        print("The user is trying to quit the program.")
        sys.exit(0) ## Quit immediately
        return(None)
        
    if(users_quality_estimate <= 0): ## This corresponds to both the case when the user chooses "I don't know how to say this" and also when he tries to say it, but gives himself a grade of 1.
        study_due_date = datetime.datetime.now() + datetime.timedelta(minutes = 1)
    elif(users_quality_estimate == 1):
        study_due_date = datetime.datetime.now() + datetime.timedelta(minutes = 2)
    elif(users_quality_estimate == 2):
        study_due_date = datetime.datetime.now() + datetime.timedelta(minutes = 4)
    elif(users_quality_estimate == 3):
        study_due_date = datetime.datetime.now() + datetime.timedelta(minutes = 8)
    elif(users_quality_estimate == 4):
        study_due_date = datetime.datetime.now() + datetime.timedelta(minutes = 16) ## Note that this progression of constants is basically just a bunch of numbers that I made up.
    else:
        print("Something went wrong with the user's quality estimate of how well he said the phrase :(")
        study_due_date = -1  
    return(study_due_date)
    
###################################################################################################
###################################################################################################

def get_path_to_sqlite_db():
    ## In this function, we figure out the name of our sqlite table and return it
    
    # path_to_sqlite_db = os.path.join(config['absolute_path_to_cartridge_library'], config['cartridge_name'], config['cartridge_name'] + '.sqlite')
    path_to_sqlite_db = os.path.join(get_path_to_assets_dir(), cart_config['cartridge_name'] + '.sqlite')
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

def update_phrases_db(phrase, study_due_date):
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

def create_stats_table():
    ## In this function, we create a table to hold statistical facts about our studies, such as
    ## time elapsed during the study of each phrase, etc.
    
    conn = sqlite3.connect(path_to_sqlite_db)
    c = conn.cursor()
    
    stats_table_creation_template = """
    create table if not exists study_stats(
        date integer not null
      , phrase_uuid integer not null
      , time_spent_on_this_phrase integer
      , count_of_study_attempts_on_this_phrase integer
    );
    """
    
    params_to_sub = {}
                   
    update_query = pystache.render(stats_table_creation_template, params_to_sub)
    c.execute(update_query)
    conn.commit()
    conn.close()
    return(0)
    
###################################################################################################
###################################################################################################

def update_stats_table(phrase, time_elapsed):
    ## In this function, we update our study time counter table in the database. We have to hack
    ## around sqlite's lack of upsert
    
    conn = sqlite3.connect(path_to_sqlite_db)
    c = conn.cursor()
    
    duration_of_this_attempt = time_elapsed ## This should be in seconds
    count_of_study_attempts_on_this_phrase = 1
    stats_update_template = """
    -- Try to update any existing row
    update study_stats
    set 
        time_spent_on_this_phrase = time_spent_on_this_phrase + {{duration_of_this_attempt}}
      , count_of_study_attempts_on_this_phrase = count_of_study_attempts_on_this_phrase + 1
    where phrase_uuid = {{relevant_uuid}}
    and date = CURRENT_DATE
    ;
    """
    
    stats_insert_template = """
    -- If no update happened (i.e. the row didn't exist) then insert one
    insert into study_stats (date, phrase_uuid, time_spent_on_this_phrase, count_of_study_attempts_on_this_phrase)
    select
        CURRENT_DATE as date
      , {{relevant_uuid}} as phrase_uuid
      , {{duration_of_this_attempt}} as time_spent_on_this_phrase
      , 1 as count_of_study_attempts_on_this_phrase -- We set the count of study attempts to 1, since by definition if we're running this "insert" query, this is the first attempt to study a phrase.
    where
        (select Changes() = 0)
    ;
    """
    
    ## We'll reuse these params for both of the above queries
    params_to_sub = {'duration_of_this_attempt': duration_of_this_attempt
                   , 'relevant_uuid' : phrase['phrase_uuid']
                    }
                   
    update_query = pystache.render(stats_update_template, params_to_sub)
    c.execute(update_query)
    
    insert_query = pystache.render(stats_insert_template, params_to_sub)
    c.execute(insert_query)
    
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

def display_study_stats():
    ## In this function, we display to the user a few study stats such as elapsed study duration etc
    
    textbox("foobar baz bang")    
    return(0)

    
###################################################################################################
###################################################################################################

def learn_phrase(phrase):
    ## In this function, we gang up a bunch of the functions above and expose them 
    ## through a single interface
    start_time = time.time() ## This is wall-clock time
    did_user_say_the_phrase = ask_if_user_can_say_phrase(phrase)
    users_quality_estimate = decide_what_to_do(did_user_say_the_phrase, phrase)
    end_time = time.time() 
    elapsed_time = end_time - start_time
    delay_till_next_study = figure_out_when_to_study_next(users_quality_estimate)
    update_phrases_db(phrase, delay_till_next_study)
    update_stats_table(phrase, elapsed_time)
    return(0)

###################################################################################################
###################################################################################################
## Call functions in a sensible order

if __name__ == "__main__":
    path_to_cartridge_file = print_welcome_screen()
    if not os.path.isdir(get_path_to_assets_dir()): ## If we're running for the first time, we can unpack our cartridge zip. Otherwise, we can skip this step
        unzip_cartridge_file(path_to_cartridge_file)
    cart_config = load_cartridge_specific_config(path_to_cartridge_file) ## Figure out the names of our languages etc.
    path_to_sqlite_db = get_path_to_sqlite_db()
    name_of_sqlite_table = cart_config['cartridge_name']
    create_stats_table()
    current_active_lesson = get_current_active_lesson(name_of_sqlite_table)
    
    ## Get a phrase to study
    keep_studying = 1
    while(keep_studying == 1):
        current_active_lesson = detect_if_new_lesson_needed(name_of_sqlite_table, current_active_lesson)
        phrase_to_study = get_phrases_to_study(name_of_sqlite_table, current_active_lesson)
        learn_phrase(phrase_to_study)
    display_study_stats()
    
###################################################################################################
###################################################################################################
## TODO's: 
# * Add 10 second progress bar while the user is trying to say the phrase
# * Use a better GUI system that doesn't flicker every time you click something
# * Figure out how to get audio from movies/tv/radio and two-language-track closed-captions, in order to prevent us from having to pay for native speakers recording audio
# DONE * Get the phraselist from http://frequencylists.blogspot.com/2016/08/5000-italian-sentences-sorted-from.html
# * Implement a naive machine translation?
# DONE * Build facilities for loading fully-modularized .zip file of all the .mp3's and the .csv, aka "cartridge" like in NES
# * Print study stats, such as total hours studied, what lesson you're on, how many phrases fall into each bucket, etc. Also do "how many times did you study this phrase"
# DONE * Package afterburner as a standalone program
# DONE * Write gui for selecting cart files
# DONE * Persist the user's most recent choice of cart file
# DONE * Prevent the GUI from loading in the background, behind all the other windows. Make it load in the foreground instead. 
