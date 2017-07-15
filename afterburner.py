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
import datetime ## To decide when a phrase is due for study
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

def ask_if_user_can_say_phrase():
    
    ## Display a pair of buttons to determine whether the user can even say the phrase
    button_text_for_attempted_speech = "I've tried to say this out loud, show me the answer (Press enter)"
    button_text_for_failure_to_speak = "I don't know, show me the answer (Press spacebar then enter)"

    print(button_text_for_attempted_speech + "          " + button_text_for_failure_to_speak)
    print
    print
    print

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

    # open the file for reading.
    wf = wave.open(name_of_audio_file, 'rb')

    # create an audio object
    p = pyaudio.PyAudio()

    # open stream based on the wave object which has been input.
    stream = p.open(format =
                    p.get_format_from_width(wf.getsampwidth()),
                    channels = wf.getnchannels(),
                    rate = wf.getframerate(),
                    output = True)

    # read data (based on the chunk size)
    data = wf.readframes(chunk)

    # play stream (looping from beginning of file to the end)
    while data != '':
        # writing to the stream is what *actually* plays the sound.
        stream.write(data)
        data = wf.readframes(chunk)

    # cleanup stuff.
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
## Make a db to hold our study state

def create_db():
    ## In this function, we create a database in our sqlite connection. This db will store
    ## our study state
    
    name_of_sqlite_table = 'afterburner_' + config['name_of_known_language'] + '_to_' + config['name_of_target_language']
    name_of_sqlite_table = name_of_sqlite_table.lower()
    conn = sqlite3.connect(config['path_to_sqlite_file'])
    c = conn.cursor()
    
    create_table_query_template = """
    create table if not exists {{name_of_sqlite_table}} (
    phrase_uuid integer PRIMARY KEY,
    phrase_in_known_language TEXT NOT NULL,
    literal_translation_from_target_language_to_known_language TEXT NOT NULL,
    idiomatic_translation_to_target_language TEXT NOT NULL,
    timestamp_when_phrase_is_due_for_study TEXT NOT NULL    
    )
    ;
    """
    
    params_to_sub = {'name_of_sqlite_table' : name_of_sqlite_table}
    create_table_query = pystache.render(create_table_query_template, params_to_sub)

    c.execute(create_table_query)
    conn.commit()
    conn.close()
    return(name_of_sqlite_table)

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

## Get the top N phrases that are due for study

def get_phrases_to_study(name_of_sqlite_table):
    ## In this function, we reorder our phrase db and get N phrases which are due for study
    
    conn = sqlite3.connect(config['path_to_sqlite_file'])
    conn.row_factory = sqlite3.Row ## Important, this allows us to get dicts instead of tuples from the db, which gives us column names in the data we get from the db
    c = conn.cursor()
    query_template = """
    select 
        *
    from
        {{name_of_table}}
    order by
        timestamp_when_phrase_is_due_for_study desc
    limit 1
    """
    
    params_to_sub = {'name_of_table' : name_of_sqlite_table}
    query = pystache.render(query_template, params_to_sub)
    
    c.execute(query)
    result = c.fetchone()
    
    conn.commit()
    conn.close()
    return(result)
###################################################################################################
###################################################################################################
## Update our study state db

def update_db(phrase, study_due_date):
    ## In this function, we add our phrase to our sqlite db, which will store our study state
    conn = sqlite3.connect(config['path_to_sqlite_file'])
    c = conn.cursor()
    
    upsert_query_template = """
    INSERT OR REPLACE INTO {{name_of_sqlite_table}} (phrase_uuid,
                                          phrase_in_known_language,
                                          literal_translation_from_target_language_to_known_language,
                                          idiomatic_translation_to_target_language,
                                          timestamp_when_phrase_is_due_for_study    
                                          )
    VALUES ({{uuid}}, '{{phrase}}', '{{literal}}', '{{idomatic}}', '{{time}}');
    """
    params_to_sub = {'name_of_sqlite_table': name_of_sqlite_table
                   , 'uuid'      : phrase['phrase_uuid']
                   , 'phrase'    : phrase['phrase_in_known_language']
                   , 'literal'   : phrase['literal_translation_from_target_language_to_known_language']
                   , 'idiomatic' : phrase['idiomatic_translation_to_target_language']
                   , 'time' : study_due_date}
    upsert_query = pystache.render(upsert_query_template, params_to_sub)

    c.execute(upsert_query)
    conn.commit()
    conn.close()
    return(0)
    
    
def get_current_active_study_flight(name_of_sqlite_table):
    ## In this function, we ask the db to tell us which study flight the user is currently working on.
    ## To get this, we just take the highest-numbered study flight that has meaningful due-for-study timestamps
    
    get_current_active_study_flight_query_template = """
    select
        max(study_flight)
    from
        {{name_of_sqlite_table}}
    where
        timestamp_when_phrase_is_due_for_study != -1
    """
    params_to_sub = {'name_of_sqlite_table' : name_of_sqlite_table}
    get_current_active_study_flight_query = pystache.render(get_current_active_study_flight_query, params_to_sub)
    ## TODO: SEND TO DB ETC.
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
    
    ## Get a phrase to study
    while True:
        phrase_to_study = get_phrases_to_study(name_of_sqlite_table)
        print(phrase_to_study)
        print(type(phrase_to_study))
        print('bro')
        # import pdb
        # pdb.set_trace()
        learn_phrase(phrase_to_study)
    
    ## Iterate over our phrases file
    # for index, phrase in phrases.iterrows():
    #     learn_phrase(phrase)
        