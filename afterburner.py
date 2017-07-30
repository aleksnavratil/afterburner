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
import os ## For constructing file path names
import sys ## For halting the program if the user runs out of lessons
import datetime ## To decide when a phrase is due for study
import time ## For progressbars
import progressbar ## For progressbars
import sqlite3 ## For managing the state of the user's phrases
import pystache ## For sane templating

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
    ## Print welcome screen
    welcome_message = """\n\n\n
    ##############################################################
    ##############################################################
    Welcome to Afterburner, one of the faster ways to learn 
    a spoken human language
    ##############################################################
    ##############################################################"""
    print(welcome_message)
    return(welcome_message)

###################################################################################################
###################################################################################################

def display_phrase(phrase):
    ## Display text in the target language
    print("\n\n\n\nRead this " + config['name_of_known_language'] + " phrase, then say the " + config['name_of_target_language'] + " equivalent out loud.\n")
    print("\nMeaning :" + phrase['phrase_in_known_language'])
    print("\nLiteral :" + phrase['literal_translation_from_target_language_to_known_language'])
    print
    print


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

def ask_if_user_can_say_phrase():
    
    ## Display a pair of buttons to determine whether the user can even say the phrase
    button_text_for_attempted_speech = "I've tried to say this out loud, show me the answer (Press enter)"
    button_text_for_failure_to_speak = "I don't know, show me the answer (Press spacebar then enter)"

    print(button_text_for_attempted_speech + "          " + button_text_for_failure_to_speak)
    print
    print
    print
    # show_progress_bar() ## TODO: FIGURE OUT WHAT TO DO ABOUT THIS
    
    ## Let the user tell us whether he said the phrase at all (here we ignore how well he said it, and
    ## focus only on whether he attempted to say it at all)

    while True:
        did_user_say_the_phrase = raw_input('\n')
        if did_user_say_the_phrase not in ('', ' '): ## Note that the empty string '' here tests for the enter key, and ' ' tests for the spacebar
            print("\n\n\nPlease press either enter or spacebar. Try again :)")
            continue
        else:
            break

    return(did_user_say_the_phrase)

###################################################################################################
###################################################################################################

def decide_what_to_do(did_user_say_the_phrase, phrase):
    if(did_user_say_the_phrase == ''):
        ## This logical branch corresponds to the case when the user *did say* the phrase
        show_answer(phrase)
        user_quality_estimate = ask_for_user_quality_estimate()
        return(user_quality_estimate)
        
    elif(did_user_say_the_phrase == ' '):
        ## This branch corresponds to the case when the user *failed to say* the phrase
        show_answer(phrase)
        return(0)
        
    
###################################################################################################
###################################################################################################
def play_sound(name_of_audio_file):
    ## In this function, we consume as input the uuid of a phrase and play the corresponding audio clip
    ## If we refactor this program to be python3, we should use simpleaudio instead

    ## Define a constant bitesize
    chunk = 1024

    # Open the file for reading.
    wf = wave.open(name_of_audio_file, 'rb')

    # Create an audio object
    p = pyaudio.PyAudio()

    # Open stream based on the wave object which has been input.
    stream = p.open(format =
                    p.get_format_from_width(wf.getsampwidth()),
                    channels = wf.getnchannels(),
                    rate = wf.getframerate(),
                    output = True)

    # Read data (based on the chunk size)
    data = wf.readframes(chunk)

    # Play stream (looping from beginning of file to the end)
    while data != '':
        # Writing to the stream is what *actually* plays the sound.
        stream.write(data)
        data = wf.readframes(chunk)

    # Cleanup stuff.
    stream.close()    
    p.terminate()
    return(name_of_audio_file)
    
###################################################################################################
###################################################################################################
## Display the correct answer, and play an audio clip of the phrase by calling the appropriate function
def show_answer(phrase):
    print("\n\n\n\nRead this " + config['name_of_known_language'] + " phrase, then say the " + config['name_of_target_language'] + " equivalent out loud.\n")
    print("\nMeaning :" + phrase['phrase_in_known_language'])
    print("\nLiteral :" + phrase['literal_translation_from_target_language_to_known_language'])
    print("\nAnswer  :" + phrase['idiomatic_translation_to_target_language'])
    print
    print
    name_of_sound_to_play = str(phrase['phrase_uuid']) + '.wav'
    full_path_to_sound_to_play = os.getcwd() + os.path.sep + 'assets' + os.path.sep + name_of_sound_to_play
    play_sound(full_path_to_sound_to_play)
    return(None)

###################################################################################################
###################################################################################################

## Take input from the user about how well they said the sentence
def ask_for_user_quality_estimate():
    prompt_string_for_user_input = """\n(1) Wrong     (2) Some Mistakes     (3) Shaky     (4) Good     (5) Perfect\n"""
    print(prompt_string_for_user_input)

    while True:
        users_quality_estimate = raw_input('How well did you say this?\n')
        if users_quality_estimate not in ('1', '2', '3', '4', '5'):
            print("\n\n\nPlease enter a integer between 1 and 5, inclusive. Try again :)")
            continue
        else:
            break
    return(users_quality_estimate)

###################################################################################################
###################################################################################################

## Decide process the user's quality estimate and use it to assign a timestamp when the phrase is next due for study
def figure_out_when_to_study_next(users_quality_estimate):
    ## In this function, we consume as input the user's estimate of how well he said the phrase.
    ## We emit as output a timestamp, representing when the phrase is next due for study
    ## At some point, this should be refactored as a real spaced-repetition algo.
    
    users_quality_estimate = int(users_quality_estimate)
    if(users_quality_estimate <= 1): ## This corresponds to both the case when the user chooses "I don't know how to say this" and also when he tries to say it, but gives himself a grade of 1.
        study_due_date = datetime.datetime.now() + datetime.timedelta(minutes = 1)
    elif(users_quality_estimate == 2):
        study_due_date = datetime.datetime.now() + datetime.timedelta(minutes = 2)
    elif(users_quality_estimate == 3):
        study_due_date = datetime.datetime.now() + datetime.timedelta(minutes = 4)
    elif(users_quality_estimate == 4):
        study_due_date = datetime.datetime.now() + datetime.timedelta(minutes = 8)
    elif(users_quality_estimate == 5):
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
    print('doggggyyy')
    print(query)
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
    print('brooooskidoodle')
    print(result)
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
    
    print('broooo')
    print(result)
    print(type(result))
    
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
        print('brewwwwww')
        print(remedial_phrase)
        learn_phrase(remedial_phrase)
    
    return(result)
    
###################################################################################################
###################################################################################################
## Gang up a bunch of the functions above and expose them through a single interface
def learn_phrase(phrase):
    display_phrase(phrase)
    did_user_say_the_phrase = ask_if_user_can_say_phrase()
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
        print('browskiiiyyy')
        print(phrase_to_study)
        learn_phrase(phrase_to_study)
    