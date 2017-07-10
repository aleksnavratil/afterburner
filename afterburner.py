## afterburner.py
## Monday 10 July 
## Aleks Navratil
## The point of this program is to make a CLI for learning spoken human languages
## It's substantially a ripoff/extension of language-101.com
###################################################################################################
###################################################################################################

import pandas as pd ## For importing data from file as a dataframe
import yaml ## For importing our config file

###################################################################################################
###################################################################################################

## Print welcome screen
welcome_message = """\n\n\n\n##############################################################\n##############################################################\nWelcome to Afterburner, one of the faster ways to learn\na spoken human language\n##############################################################\n##############################################################"""
print(welcome_message)

## Load config information from file
with open("config.yaml", 'r') as config_file:
    config = yaml.load(config_file)

## Load phrase text from file
phrases = pd.read_csv('phrases.csv')

## Play an audio clip

## Display text in the target language
print("\n\n\n\nRead this " + config['name_of_known_language'] + " phrase, then say the " + config['name_of_target_language'] + " equivalent out loud.\n")
print("Phrase in your known language..........................................." + phrases['phrase_in_known_language'][1])
print("Literal translation from target language to known language.............." + phrases['literal_translation_from_target_language_to_known_language'][1])
print("Idiomatic translation of phrase into target language...................." + phrases['idiomatic_translation_to_target_language'][1])
print
print

## Display a pair of buttons to determine whether the user can even say the phrase
button_text_for_attempted_speech = "I've tried to say this out loud, show me the answer (Press enter)"
button_text_for_failure_to_speak = "I don't know, show me the answer (Press escape)"

print(button_text_for_attempted_speech + "          " + button_text_for_failure_to_speak)
print
print
print

## Take input from the user about how well they said the sentence

prompt_string_for_user_input = """\n(1) Wrong     (2) Some Mistakes     (3) Shaky     (4) Good     (5) Perfect\n"""
print(prompt_string_for_user_input)

while True:
    users_quality_estimate = raw_input('How well did you say this?\n')
    if users_quality_estimate not in ('1', '2', '3', '4', '5'):
        print("\n\n\nPlease enter a integer between 1 and 5, inclusive. Try again :)")
        continue
    else:
        break


## Process that user input through some spaced-repetition algo that will decide how long to wait before showing the same clip to the user again


