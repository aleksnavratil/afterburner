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


## Load config information from file
with open("config.yaml", 'r') as config_file:
    config = yaml.load(config_file)

## Load phrase text from file
phrases = pd.read_csv('phrases.csv')
    
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

def display_phrase(uuid_of_phrase):
    ## Display text in the target language
    print("\n\n\n\nRead this " + config['name_of_known_language'] + " phrase, then say the " + config['name_of_target_language'] + " equivalent out loud.\n")
    print("\nMeaning :" + phrases['phrase_in_known_language'][1])
    print("\nLiteral :" + phrases['literal_translation_from_target_language_to_known_language'][1])
    print
    print

###################################################################################################
###################################################################################################

def ask_if_user_can_say_phrase(uuid_of_phrase):
    
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


def decide_what_to_do(did_user_say_the_phrase, uuid_of_phrase):
    if(did_user_say_the_phrase == ''):
        ## This logical branch corresponds to the case when the user did say the phrase
        show_answer(uuid_of_phrase)
        ask_for_user_quality_estimate(uuid_of_phrase)
        
    elif(did_user_say_the_phrase == ' '):
        ## This branch corresponds to the case when the user failed to say the phrase
        show_answer(uuid_of_phrase)
        
    
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
def show_answer(uuid_of_phrase):
    print("\n\n\n\nRead this " + config['name_of_known_language'] + " phrase, then say the " + config['name_of_target_language'] + " equivalent out loud.\n")
    print("\nMeaning :" + phrases['phrase_in_known_language'][1])
    print("\nLiteral :" + phrases['literal_translation_from_target_language_to_known_language'][1])
    print("\nAnswer  :" + phrases['idiomatic_translation_to_target_language'][1])
    print
    print
    name_of_sound_to_play = str(uuid_of_phrase) + '.wav'
    full_path_to_sound_to_play = os.getcwd() + os.path.sep + 'assets' + os.path.sep + name_of_sound_to_play
    play_sound(full_path_to_sound_to_play)
    return(None)

###################################################################################################
###################################################################################################

## Take input from the user about how well they said the sentence
def ask_for_user_quality_estimate(uuid_of_phrase):
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

## Gang up a bunch of the functions above and expose them through a single interface
def learn_phrase(uuid_of_phrase):
    print_welcome_screen()
    display_phrase(uuid_of_phrase)
    did_user_say_the_phrase = ask_if_user_can_say_phrase(uuid_of_phrase)
    decide_what_to_do(did_user_say_the_phrase, uuid_of_phrase)

## Process that user input through some spaced-repetition algo that will decide how long to wait before showing the same clip to the user again

###################################################################################################
###################################################################################################
## Call functions in a sensible order
if __name__ == "__main__":
    ## Iterate over our phrases file
    for index, phrase in phrases.iterrows():
        # print(phrase)
        # print(phrase['phrase_uuid'])
        learn_phrase(phrase['phrase_uuid'])
        