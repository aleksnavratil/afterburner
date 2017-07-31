## afterburner.py
## Monday 10 July 
## Aleks Navratil
## The point of this program is to make a CLI for learning spoken human languages
## It's substantially a ripoff/extension of language-101.com
###################################################################################################
###################################################################################################

import pandas as pd ## For importing data from file as a dataframe
import yaml ## For importing our config file
import pyaudio ## For playing our audio clips
import wave ## For playing our audio clips
# from multiprocessing import Process ## For playing sounds at the same time as we render the UI
import multiprocessing
# import threading
import os ## For constructing file path names
import sys ## For halting the program if the user runs out of lessons
import datetime ## To decide when a phrase is due for study
import time ## For progressbars
# import progressbar ## For progressbars
import sqlite3 ## For managing the state of the user's phrases
import pystache ## For sane templating
from easygui import * ## For user interfaces

## Load config information from file
with open("config.yaml", 'r') as config_file:
    config = yaml.load(config_file)

## Load phrase text from file
phrases = pd.read_csv(config['name_of_phrases_csv'])
    
## For debug
pd.set_option('display.max_columns', 500)
pd.set_option('display.width', 1000)

###################################################################################################
###################################################################################################

def print_welcome_screen():
    ## In this function, we display a welcome screen to the user
    welcome_message = """
    Welcome to Afterburner, one of the faster ways to learn 
    a spoken human language. Press enter to continue.
    """
    title="Afterburner"
    
    ## Print a message box on the screen
    msgbox(welcome_message, title = "Afterburner", ok_button = "Let's go!")
    return(welcome_message)

###################################################################################################
###################################################################################################
def show_progress_bar():
    ## In this function, we print a visual progressbar to the screen.
    bar = progressbar.ProgressBar()
    for i in bar(range(500)): ## On my machine, this gives us a roughly 10-second progress bar, which is what we want
        time.sleep(0.02)
    return(0)
    
    
###################################################################################################
###################################################################################################

def ask_if_user_can_say_phrase(phrase):
    
    ## In this function, we ask the user whether he said the phrase at all
    ## (here we ignore how well he said it, and focus only on whether he attempted to say it at all)
    
    ## Display a pair of buttons to determine whether the user can even say the phrase
    button_text_for_attempted_speech = "I've tried to say this out loud, show me the answer"
    button_text_for_failure_to_speak = "I don't know, show me the answer"

    string1 = "Read this " + config['name_of_known_language'] + " phrase, then say the " + config['name_of_target_language'] + " equivalent out loud.\n"
    string2 = "\nMeaning :" + phrase['phrase_in_known_language']
    string3 = "\nLiteral :" + phrase['literal_translation_from_target_language_to_known_language']
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
def play_sound(name_of_audio_file):
    ## In this function, we consume as input the uuid of a phrase and play the corresponding audio clip
    ## If we refactor this program to be python3, we should use simpleaudio instead

    # Open the file for reading.
    wf = wave.open(name_of_audio_file, 'rb')

    ## Instantiate PyAudio
    p = pyaudio.PyAudio()

    # Define callback
    def callback(in_data, frame_count, time_info, status):
        data = wf.readframes(frame_count)
        return (data, pyaudio.paContinue)

    # Open stream using callback
    stream = p.open(format=p.get_format_from_width(wf.getsampwidth()),
                    channels=wf.getnchannels(),
                    rate=wf.getframerate(),
                    output=True,
                    stream_callback=callback)
                    
    # Start the stream
    stream.start_stream()

    # Wait for stream to finish
    while stream.is_active():
        time.sleep(0.1)

    # Stop stream
    stream.stop_stream()
    stream.close()
    wf.close()

    # Close PyAudio
    p.terminate()
    
    return(name_of_audio_file)
    
###################################################################################################
###################################################################################################
def show_answer(phrase):
    ## In this function, we display the correct answer, and play an audio clip of the phrase by calling the appropriate function
    ## This is basically only useful if the user *didn't even attempt to say the phrase*
    
    def render_ui():    
        string1 = "Read this " + config['name_of_known_language'] + " phrase, then say the " + config['name_of_target_language'] + " equivalent out loud.\n"
        string2 = "\nMeaning :" + phrase['phrase_in_known_language']
        string3 = "\nLiteral :" + phrase['literal_translation_from_target_language_to_known_language']    
        string4 = "\nAnswer  :" + phrase['idiomatic_translation_to_target_language']

        message = string1 + string2 + string3 + string4
        title = "Afterburner"
        msgbox(msg = message, title = "Afterburner", ok_button = "I have said this out loud, show me the next phrase")

    def handle_audio():
        ## Start playing our sounds asap, since they're the longest-duration thing that happens TODO: FIGURE OUT CONCURRENCY
        name_of_sound_to_play = str(phrase['phrase_uuid']) + '.wav'
        full_path_to_sound_to_play = os.getcwd() + os.path.sep + 'assets' + os.path.sep + name_of_sound_to_play
        play_sound(full_path_to_sound_to_play)    

    handle_audio()
    render_ui()

    # d = multiprocessing.Process(name='gui_stuff', target=render_ui)
    # n = multiprocessing.Process(name='audio_stuff', target=handle_audio)
    # d.daemon = True
    
    # d.start()
    # n.start()
    # Process(target=handle_audio).start()
    # Process(target=render_ui).start()
    

    
    return(None)

###################################################################################################
###################################################################################################

## Take input from the user about how well they said the sentence
def ask_for_user_quality_estimate(phrase):
    
    def render_ui():    
        string1 = "Read this " + config['name_of_known_language'] + " phrase, then say the " + config['name_of_target_language'] + " equivalent out loud.\n"
        string2 = "\nMeaning :" + phrase['phrase_in_known_language']
        string3 = "\nLiteral :" + phrase['literal_translation_from_target_language_to_known_language']    
        string4 = "\nAnswer  :" + phrase['idiomatic_translation_to_target_language']

        message = string1 + string2 + string3 + string4
        title = "Afterburner"
        choices = ['Wrong', 'Some Mistakes', 'Shaky', 'Good', 'Perfect']
        users_quality_estimate = indexbox(msg = message, title = "Afterburner", choices = choices)
        return(users_quality_estimate)

    def handle_audio():
        ## Start playing our sounds asap, since they're the longest-duration thing that happens TODO: FIGURE OUT CONCURRENCY
        name_of_sound_to_play = str(phrase['phrase_uuid']) + '.wav'
        full_path_to_sound_to_play = os.getcwd() + os.path.sep + 'assets' + os.path.sep + name_of_sound_to_play
        play_sound(full_path_to_sound_to_play)    

    handle_audio()
    users_quality_estimate = render_ui()
    return(users_quality_estimate)

###################################################################################################
###################################################################################################

## Decide process the user's quality estimate and use it to assign a timestamp when the phrase is next due for study
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
    
###################################################################################################
###################################################################################################
## Take our .csv file and make a sqlite db out of it
def convert_csv_to_sqlite():
    ## In this function, we take our phrase csv and send it to a sqlite db
    ## We'll use this db to store our study state
    conn = sqlite3.connect(config['path_to_sqlite_file'])
    phrases.to_sql(name_of_sqlite_table, conn, if_exists="fail") ## We don't want to overwrite the user's progress
    conn.commit()
    conn.close()
    return("Successfully created a sqlite DB")
###################################################################################################
###################################################################################################

def get_name_of_sqlite_table():
    ## In this function, we figure out the name of our sqlite table
    name_of_sqlite_table = 'afterburner_' + config['name_of_known_language'] + '_to_' + config['name_of_target_language']
    name_of_sqlite_table = name_of_sqlite_table.lower()
    return(name_of_sqlite_table)

###################################################################################################
###################################################################################################

## Get the top N phrases that are due for study

def get_phrases_to_study(name_of_sqlite_table, current_active_lesson):
    ## In this function, we reorder our phrase db and get N phrases which are due for study
    
    conn = sqlite3.connect(config['path_to_sqlite_file'])
    conn.row_factory = sqlite3.Row ## Important, this allows us to get dicts instead of tuples from the db, which gives us column names in the data we get from the db
    c = conn.cursor()
    query_template = """
    select 
        *
    from
        {{name_of_table}}
    where
        lesson = {{current_active_lesson}}
    order by
        timestamp_when_phrase_is_due_for_study desc
    limit 1
    """
    
    params_to_sub = {'name_of_table' : name_of_sqlite_table
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
## Update our study state db

def update_db(phrase, study_due_date):
    ## In this function, we update our phrase in our sqlite db
    conn = sqlite3.connect(config['path_to_sqlite_file'])
    c = conn.cursor()
    
    update_query_template = """
    update {{name_of_sqlite_table}} 
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
    
    conn = sqlite3.connect(config['path_to_sqlite_file'])
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
    
    conn = sqlite3.connect(config['path_to_sqlite_file'])
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
    conn = sqlite3.connect(config['path_to_sqlite_file'])
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
## Gang up a bunch of the functions above and expose them through a single interface
def learn_phrase(phrase):
    did_user_say_the_phrase = ask_if_user_can_say_phrase(phrase)
    users_quality_estimate = decide_what_to_do(did_user_say_the_phrase, phrase)
    delay_till_next_study = figure_out_when_to_study_next(users_quality_estimate)
    update_db(phrase, delay_till_next_study)
    return(phrase)

###################################################################################################
###################################################################################################
## Call functions in a sensible order
if __name__ == "__main__":
    print_welcome_screen()
    name_of_sqlite_table = get_name_of_sqlite_table()
    if not os.path.isfile(config['path_to_sqlite_file']): ## If we're running for the first time, we can create a db to hold our study state. Otherwise, we can skip this step
        convert_csv_to_sqlite()
    current_active_lesson = get_current_active_lesson(name_of_sqlite_table)
    
    ## Get a phrase to study
    while True:
        current_active_lesson = detect_if_new_lesson_needed(name_of_sqlite_table, current_active_lesson)
        phrase_to_study = get_phrases_to_study(name_of_sqlite_table, current_active_lesson)
        learn_phrase(phrase_to_study)
    
    ## TODO's: progress bar, concurrent audio