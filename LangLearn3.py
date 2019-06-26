import sqlite3

import json
import random
#import numpy as np

from flask import Flask, request, render_template, flash, url_for, redirect
                                                        # url_for allows you to get the URL for a given app.route
                                                        # redirect allows you to render that route instead of the current one
                                                        #essentially a combination of the two allows the coder to "redirect" to the "url_for" an app.route

app = Flask(__name__)
app.secret_key = 'secretKey'

############################### <intro PAGE> ################################################################################################
@app.route("/intro") #when we have http://127.0.0.1:5000/intro and nothing after the intro we are directed here, to this "app.route"
def intro():
    try:
        print("this is the intro function in Python")
        flash("Hi! This is a FLASH message to client side from Python! All rights reserved. All wrongs reserved also!")
        return render_template("intro.html")       #...send a template, called intro.html in this case
    except Exception as e:
        errorString = "Something went wrong while rendering. Error " + str(e)
        return(errorString)                                       

############################### </intro PAGE> ################################################################################################

############################### <dictionaries PAGE> ################################################################################################
@app.route("/dictionaries") #when we have http://127.0.0.1:5000/dictionaries and nothing after the dictionaries we are directed here, to this "app.route"
def dictionaries():

    conn = sqlite3.connect('LanguageLearner.db')
    c = conn.cursor()
    c.execute('SELECT DISTINCT ForeignLanguage FROM DICT_RECORD')
    myData = c.fetchall()                 # fetchall retrieves a LIST of TUPLES, e.g. [('GERMAN',), ('ITALIAN',), ('FRENCH',)]
    c.execute('select count (distinct ForeignLanguage) from DICT_RECORD;')
    NumberOfLanguagesTuple = c.fetchone() # fetchone retrives a single TUPLE e.g. (3,) if there are 3 languages
    numberOfLanguages = NumberOfLanguagesTuple[0]

    listOfLanguages = []                            #initialise an empty list
    for eachTuple in myData:                        #extract each tuple from the list of tuples in myData
        for eachLanguage in eachTuple:              #extract the individual language from each tuple
            listOfLanguages.append(eachLanguage)    #add the individual language to a list which we'll later convert to JSON array

    JSONlistOfLanguages = json.dumps(listOfLanguages)

    return render_template("dictionaries.html",
                           flask_numberOfLanguages = numberOfLanguages,
                           flask_arrayOfLanguages  = JSONlistOfLanguages)

############################### </dictionaries PAGE> ################################################################################################


############################### MISCELLANEOUS FUNCTIONS ##############################################

def create_new_dict_entry(row):
    """use of placeholders seems to be mandatory with SQLITE..."""
    print("ENTER FUNCTION create_new_dict_entry")
    print("trying to connect to DB...")
    conn = sqlite3.connect('LanguageLearner.db')
    print("trying to open cursor...")
    c = conn.cursor()
    print("trying to insert into SQL...")
    c.execute('insert into DICT_RECORD values (?,?,?,?,?,?,?)', row) # row is a tuple of elements. One element for each "?" placeholder
    print("trying to commit to DB...")
    conn.commit()

#######################################

def modify_existing_dict_entry(row): 
    """use of placeholders seems to be mandatory with SQLITE..."""
    print("ENTER FUNTION modify_existing_dict_entry")
    conn = sqlite3.connect('LanguageLearner.db')
    c = conn.cursor()
    c.execute('update DICT_RECORD     \
               set NativeWord    = ?, \
                   NativeHint    = ?, \
                   ForeignWord   = ?, \
                   ForeignHint   = ?, \
                   ForeignPlural = ?  \
               where ForeignLanguage = ? \
               and UniqueNum         = ? \
              ', (row[0],row[1],row[2],row[3],row[4],row[5],row[6]))
    conn.commit()

#######################################

def write_test_history_record(row):
    """use of placeholders seems to be mandatory with SQLITE..."""
    print("ENTER FUNCTION write_test_history_record")
    conn = sqlite3.connect('LanguageLearner.db')
    print("connected to database...")
    c = conn.cursor()
    print("cursor opened...")
    c.execute('insert into TEST_HISTORY values (?,?,?,?,?,?,?,?)', row) # row is a tuple of elements. One element for each "?" placeholder
    print("SQL insert executed...")
    conn.commit()
    print("SQL committed...")

#######################################

def right_justify_zero_fill(rjzf_field, field_length):
    """
    Right Justify & Zero Fill the incoming rjzf_field (to be total of field_length chars long)
     Notes:
        1) ("0" * field_length) creates a string of 0's of length = field_length parameter
        2) [-field_length] is a python substring (slice) feature that obtains the rightmost (due to presence of - sign) field_length # of chars
        
        So for example the UniqueNum field on the DB is 8 chars long. Function right_justify_zero_fill is called with (e.g.) the following parameters:
            rjzf_field = 123 (i.e. row 123 an integer value) --- field_length = 8 (also integer)
            we get "0" * 8 = "00000000" + str(123) = "123" so we have "00000000123" and then "slice" that with -8 => we end up with "00000123"
    """
    return (("0" * field_length) + str(rjzf_field))[-field_length:] 

#######################################

def chooseRandomWord(py_currentLanguage, py_list_of_word_IDs_to_test):
    """
    1. choose a random number between 0 and the length of LIST py_list_of_word_IDs_to_test
    2. delete (using pop command) the chosen list member so it can't be chosen again
    3. read the DICT_RECORD file at the ID & Language of the chosen LIST Item
    4. return the parameters of the dictionary entry chosen

    Note: once the random number is chosen, its corresponding element must be deleted from the list so it can't be chosen again
    """

    global py_uniqueNum

    print("In chooseRandomWord function")
    #print(py_currentLanguage)
    #print("type(py_currentLanguage)",type(py_currentLanguage))
    #print(py_list_of_word_IDs_to_test)

    # choose a random number between 0 and "length of LIST -1". This will be the INDEX of the next word in the test.
       # (random.randint will choose integer N between a and b where a <= N <= b 
       #  but of course length of LIST is 1 bigger than index for last LIST item)
    indexOfNextItemFromList = random.randint(0, len(py_list_of_word_IDs_to_test)-1) 
    
    print(indexOfNextItemFromList)
    
    py_uniqueNum = py_list_of_word_IDs_to_test.pop(indexOfNextItemFromList) # "pop" will remove the item from the list (at the index in brackets)
                                                                            # AND return the value removed (into py_uniqueNum)

    print("py_uniqueNum:",py_uniqueNum)

    conn = sqlite3.connect('LanguageLearner.db')
    c = conn.cursor()
    c.execute('SELECT NativeWord, \
                      ForeignWord, \
                      NativeHint, \
                      ForeignHint, \
                      ForeignPlural \
               FROM DICT_RECORD \
               WHERE ForeignLanguage = ? \
               AND UniqueNum = ?', \
               (py_currentLanguage, py_uniqueNum)) #placeholder variables comma-separated and in brackets as they need to be a TUPLE

    row_to_test = c.fetchone() # select what should be a unique row (LANG & UNIQUE NUM form the primary key of the DICT_RECORD file)
    print(row_to_test)

    return row_to_test

#######################################

def chooseRandomWordDirection():
    print("In chooseRandomWordDirection function")

    if  random.randint(0, 1) == 0:
        print(const_nativeToForeign)
        return const_nativeToForeign
    else:
        print(const_foreignToNative)
        return const_foreignToNative

#######################################

def find_next_available_TestID(py_currentLanguage):
    """
    1. Find the current highest TestID for the language being tested
    2. The value to be returned will be the "current highest + 1"
    """
    print("ENTER FUNTION find_next_available_TestID")

    print("py_currentLanguage", py_currentLanguage)

    conn = sqlite3.connect('LanguageLearner.db')

    print("connected to DB...")

    c = conn.cursor()

    print("Cursor Open...")

    c.execute('SELECT max(TestID)          \
               FROM TEST_HISTORY           \
               WHERE ForeignLanguage = ?', \
                   (py_currentLanguage,)) #placeholder variables comma-separated and in brackets as they need to be a TUPLE

    print("SQL executed...")

    tuple_data = c.fetchone()

    print("fetch one executed...")
    print("tuple_data:",tuple_data)
    print("tuple element:",tuple_data[0])

    if  tuple_data[0] is None:    # "is None" => no record found => we don't have an history entry for this language yet so we can safely assume the next number is "00000001"
        print("No records found for this language so assuming 00000001...")
        return "00000001"
    else:
        current_highest_TestID = tuple_data[0]

        print("current_highest_TestID:",current_highest_TestID)

        next_available_TestID = right_justify_zero_fill(str((int(current_highest_TestID) + 1)),8) #rjzf(the_string_of(the_integer_of(cur_high_TestID + 1),resulting string len=8)

        print("next_available_TestID:",next_available_TestID)

        return next_available_TestID

#######################################

def load_direct_object_genders(py_currentLanguage):

    print("ENTER FUNTION load_direct_object_genders")

    conn = sqlite3.connect('LanguageLearner.db')

    print("connected to DB...")

    c = conn.cursor()

    print("Cursor Open...")

    c.execute('SELECT DirectObject         \
               FROM DIRECT_OBJECT_GENDERS  \
               WHERE ForeignLanguage = ?', \
                   (py_currentLanguage,)) # placeholder variables comma-separated and in brackets as they need to be a TUPLE

    print("SQL executed...")

    sql_data = c.fetchall() # result will be a list of tuples, for example: [('Der',), ('Die',), ('Das',)]

    print("data retrieved:", sql_data)

    return sql_data

#######################################

def load_special_chars(py_currentLanguage):

    print("ENTER FUNTION load_special_chars")

    conn = sqlite3.connect('LanguageLearner.db')

    print("connected to DB...")

    c = conn.cursor()

    print("Cursor Open...")

    c.execute('SELECT Key, SpecialChar, CompareChar \
               FROM SPECIAL_CHARS                   \
               WHERE ForeignLanguage = ?            \
               ORDER BY Key',
                   (py_currentLanguage,)) # placeholder variables comma-separated and in brackets as they need to be a TUPLE

    print("SQL executed...")

    sql_data = c.fetchall() # result will be a list of tuples, for example: [('1', 'ä', 'a'), ('2', 'ö', 'o'), ('3', 'ü', 'u'), ('4', 'ß', 'ß'), ('5', 'Ä', 'A'), ('6', 'Ö', 'O'), ('7', 'Ü', 'U')]

    print("data retrieved:", sql_data)

    return sql_data

############################## /MISCELLANEOUS FUNCTIONS ##############################################


############################### <viewModifyDictionary PAGE> ################################################################################################

@app.route("/viewModifyDictionary/<string:viewModifyDictionaryLanguage>", methods=["GET","POST"]) #when we have http://127.0.0.1:5000/viewModifyDictionary plus the name of a language (e.g. GERMAN) we are directed here, to this "app.route"
def viewModifyDictionary(viewModifyDictionaryLanguage):

    list_special_chars = load_special_chars(viewModifyDictionaryLanguage)
    JSON_list_special_chars = json.dumps(list_special_chars)

    try:
        if request.method == "POST":
            #JSON_tableOfWordsFromFrontEnd = request.form['JSON_tableOfWords']
            #print(JSON_tableOfWordsFromFrontEnd)
            #print("post method executed by Phil")
            print("this is the viewModifyDictionary function in Python - POST method")
            #xyz = request.form['toPythonTableData'] #toPythonTableData comes from the 'name' attribute in an input field on the form submitted from HTML! No need for flask specific stuff here
            #print(xyz)
            #return render_template("viewModifyDictionary.html")

            print("JSON String Sent:",request.form['toPythonTableData'])

            in_toPythonTableData = request.form['toPythonTableData']
            #JSON_allRowsForSpecificLanguage = json.dumps(Python_allRowsForSpecificLanguage)

            listData = json.loads(in_toPythonTableData)
            print("listData:", listData)

            for eachItem in listData:
                if eachItem[0] == "CREATE":
                    print ("let's make something out of almost nowt")
                    rjzf_rownum = ("00000000" + str(eachItem[7]))[-8:] #rjzf => Right Justify & Zero Fill the incoming rownum (to be total of 8 chars long)
                    row = (eachItem[1],eachItem[2],eachItem[3],eachItem[4],eachItem[5],eachItem[6],rjzf_rownum) #row is a TUPLE because it's enclosed in roundie brackets
                    print("row:",row)
                    print(type(row))
                    create_new_dict_entry(row)
                elif eachItem[0] == "MODIFY":
                    print ("let's change something")
                    rjzf_rownum = right_justify_zero_fill(eachItem[7], 8) # Zero Fill Right Justify the incoming rownum (to be total of 8 chars long)
                    row = (eachItem[1],eachItem[2],eachItem[3],eachItem[4],eachItem[5],eachItem[6],rjzf_rownum) # row is a TUPLE because it's enclosed in roundie brackets
                    print("row:",row)
                    modify_existing_dict_entry(row)
                else:
                    print ("we're neither creating nor modifying...could we be deleting?")


            #### We now want to re-render the same html template in order to refresh the dictionary table
            print("new code")
            print("currentLanguage Sent:",request.form['currentLanguage'])
            py_currentLanguage = request.form['currentLanguage']
            print("py_currentLanguage:",py_currentLanguage)

            viewModifyDictionaryLanguageTuple = (py_currentLanguage,) #convert "post"ed currentLanguage variable to a one-element tuple

            print("viewModifyDictionaryLanguageTuple:",viewModifyDictionaryLanguageTuple)

            conn = sqlite3.connect('LanguageLearner.db')
            c = conn.cursor()
            c.execute('SELECT * FROM DICT_RECORD WHERE ForeignLanguage=?', viewModifyDictionaryLanguageTuple)
    
            Python_allRowsForSpecificLanguage = c.fetchall() # fetchall retrives a LIST (size >=1) of TUPLEs. Each tuple represents a row of data and consists of one element per DATABASE column
    
            print("Python_allRowsForSpecificLanguage:",Python_allRowsForSpecificLanguage)

            JSON_allRowsForSpecificLanguage = json.dumps(Python_allRowsForSpecificLanguage)
            #myNumberOfWordsInLanguageDictStr = myNumberOfWordsInLanguageDictTuple[0]

            return render_template("viewModifyDictionary.html",
                                   EditLanguage                    = viewModifyDictionaryLanguage,
                                   flask_listOfSpecialChars        = JSON_list_special_chars,
                                   JSON_allRowsForSpecificLanguage = JSON_allRowsForSpecificLanguage)

            #request.form['postRowNum'] = "XYZ"
            #return ('', 204) #This line specifies that the RESPONSE is empty. There must BE a response, but in this case, it doesn't contain anything so the Client Side doesn't need to act (i.e. no rendering reqired, etc)
        else:
            print("this is the viewModifyDictionary function in Python - NON-POST method")
            viewModifyDictionaryLanguageTuple = (viewModifyDictionaryLanguage,) #convert incoming Flask string to a one-element tuple

            conn = sqlite3.connect('LanguageLearner.db')
            c = conn.cursor()
            c.execute('SELECT * FROM DICT_RECORD WHERE ForeignLanguage=?', viewModifyDictionaryLanguageTuple)
    
            Python_allRowsForSpecificLanguage = c.fetchall() # fetchall retrives a LIST (size >=1) of TUPLEs. Each tuple represents a row of data and consists of one element per DATABASE column
    
            JSON_allRowsForSpecificLanguage = json.dumps(Python_allRowsForSpecificLanguage)

            return render_template("viewModifyDictionary.html",
                                   EditLanguage                    = viewModifyDictionaryLanguage,
                                   flask_listOfSpecialChars        = JSON_list_special_chars,
                                   JSON_allRowsForSpecificLanguage = JSON_allRowsForSpecificLanguage)
    except Exception as e:
        flash(e)
        return render_template("yikes_404.html")

############################### </viewModifyDictionary PAGE> ################################################################################################

############################### <test PAGE> ################################################################################################

@app.route("/test") #when we have http://127.0.0.1:5000/test and nothing after the test we are directed here, to this "app.route"
def test():

    conn = sqlite3.connect('LanguageLearner.db')
    c = conn.cursor()
    c.execute('SELECT DISTINCT ForeignLanguage FROM DICT_RECORD')
    myData = c.fetchall()                 # fetchall retrieves a LIST of TUPLES, e.g. [('GERMAN',), ('ITALIAN',), ('FRENCH',)]
    c.execute('select count (distinct ForeignLanguage) from DICT_RECORD;')
    numberOfLanguagesTuple = c.fetchone() # fetchone retrives a single TUPLE e.g. (3,)
    numberOfLanguages = numberOfLanguagesTuple[0]

    listOfLanguages = []                            #initialise an empty list
    for eachTuple in myData:                        #extract each tuple from the list of tuples in myData
        for eachLanguage in eachTuple:              #extract the individual language from each tuple
            listOfLanguages.append(eachLanguage)    #add the individual language to a list which we'll later convert to JSON array

    JSONlistOfLanguages = json.dumps(listOfLanguages)

    return render_template("test.html",
                           flask_numberOfLanguages = numberOfLanguages,
                           flask_arrayOfLanguages  = JSONlistOfLanguages)

#@app.route("/test/<string:sentTestWord>") #when we have http://127.0.0.1:5000/test and nothing after the intro we are directed here, to this "app.route"
#def testWord(sentTestWord):
#    global a # declare variable as global inside the function if you want to do update them. global is not needed for printing and accessing
#    #a = a + 1
#    sentTestWord = sentTestWord + str(a)
#    return render_template("test.html", theTestWord=sentTestWord)

############################### </test PAGE> ################################################################################################

############################### <runningTest PAGE> ################################################################################################

@app.route("/runningTest", methods=["GET","POST"]) #when we have http://127.0.0.1:5000/runningTest and nothing after the test we are directed here, to this "app.route"
def runningTest():

    ############ INITIALISE VARIABLES ############
    global py_list_of_word_IDs_to_test                ### NOTE: The "global" keyword instructs this function (runningTest) to use the global variables declared in the area
    global py_currentPointInTest                      ###       of this Python program which falls outside of any functions. Without the "global" keyword, declaring variables
    global py_currentLanguage                         ###       here would of course declare them locally to this function, irrespective of the fact the variables have the
    global py_translationDirectionOfTest              ###       same name.
    global py_translationDirectionOfWord
    global py_nativeWord 
    global py_foreignWord
    global py_allOrRange     
    global py_inputRangeFrom 
    global py_inputRangeTo
    global py_totalCorrectOnFirstTryCount
    global py_totalCorrectOnSubsequentTryCount
    global py_totalGiveUpsCount
    global py_TestID
    global py_uniqueNum

    global gbl_JSON_list_direct_object_genders
    global gbl_JSON_list_special_chars

    global const_nativeToForeign
    global const_foreignToNative
    global const_randomDuringTest

    py_actionToTake = "" # this variable will be set to certain values when this app.route is called from front end:
                         # "ReturnNextWord" -> Send the next word up to the front end
                         # "EndTest"        -> Front End is asking for test to end as all words have been tested

                         # "ProcessWord"    -> Process the word that has been sent from the front end (update DB with results, get next word/end test, etc)
                         # "SaveTest"       -> Future expansion functionality will save test so it can be restarted later

    ############ /INITIALISE VARIABLES ############

    try:
        if  request.method == "POST":

         ###################################################
         ### START OF "SUBSEQUENT TIME IN" SPECIFIC CODE ###

            py_FirstTimeIn = False      # call has come from a POST from the front end. We know this isn't the first time in because 
                                        # first time in is always via a redirect from the "chooseTestParams" @app.route
            print("we're in runningTest FUNCTION now - SUBSEQUENT (**NOT** FIRST) TIME IN!!")

            py_actionToTake = request.form['actionToTake']
            print("py_actionToTake:", py_actionToTake)

            py_resultForThisWord = request.form['resultForThisWord']
            print("py_resultForThisWord:", py_resultForThisWord)

            print("py_currentPointInTest:", py_currentPointInTest)

            print("BEFORE ADDING! py_totalCorrectOnFirstTryCount:", py_totalCorrectOnFirstTryCount)

            if   py_resultForThisWord == "RightFirstTime":
                 print("BUMP Right First Time Score!! **************************")
                 py_totalCorrectOnFirstTryCount += 1
            elif py_resultForThisWord == "RightSubsequentTime":
                 py_totalCorrectOnSubsequentTryCount += 1
            elif py_resultForThisWord == "GiveUp":
                 py_totalGiveUpsCount += 1

            print("AFTER ADDING! py_totalCorrectOnFirstTryCount:", py_totalCorrectOnFirstTryCount)

         ## write the "result" statistic of the Current Word to the TEST_HISTORY file (keeps a record of whether answer was: Right First Try/Right Subsequent Try/Give Up
            myRow = (1,2,3)
            print(type(myRow))

            print(py_currentLanguage)
            print(py_TestID)
            print(py_nativeWord)
            print(py_foreignWord)
            print(py_resultForThisWord)

            row = (py_currentLanguage,py_TestID,py_uniqueNum,py_currentPointInTest,py_translationDirectionOfWord,py_nativeWord,py_foreignWord,py_resultForThisWord) #we know the variable "row" is a TUPLE because it's enclosed in roundie brackets
            print("history row:",row)
            print(type(row))
            write_test_history_record(row)

           ### END OF "SUBSEQUENT TIME IN" SPECIFIC CODE ###
           #################################################

        else:

         ##############################################
         ### START OF "FIRST TIME IN" SPECIFIC CODE ###

          # when we first get redirected to this function/URL (from chooseTestParams) 
            py_FirstTimeIn = True

            py_actionToTake = "ProcessWord"       # Future expansion may dictate that this variable will be set to something else
                                                  # when we are restarting a test after a SAVE (having loaded it from a SAVE file)

            print("we're in runningTest FUNCTION now - FIRST TIME IN!!")
            print("Initialising Variables...")

            py_translationDirectionOfTest = request.args.get('py_translationDirectionOfTest')
            py_allOrRange                 = request.args.get('py_allOrRange')        # These py_blabla_etc variables are populated via the parameters in the
            py_inputRangeFrom             = request.args.get('py_inputRangeFrom')    # return redirect(url_for('runningTest'...) statement in the           
            py_inputRangeTo               = request.args.get('py_inputRangeTo')      # app.route "chooseTestParams".           
            py_currentLanguage            = request.args.get('py_currentLanguage')   # The "request.args.get" statement is specfic to this functionality

            py_totalCorrectOnFirstTryCount      = 0
            py_totalCorrectOnSubsequentTryCount = 0
            py_totalGiveUpsCount                = 0

            # Establish the py_TestID - this is a unique 8-digit number which will be used to store the results of this test, and to allow
            # individual tests to be saved mid-test (and re-loaded so they can be continued)
            py_TestID = find_next_available_TestID(py_currentLanguage)

            # initialise the list to have no elements
            py_list_of_word_IDs_to_test = [] 

            print("we're about to generate the list of 8 digit numbers")

            # HERE WE CREATE A LIST OF NUMBERS, EACH 8 DIGITS LONG, BASED ON THE TO/FROM PARAMETERS REQUESTED ON THE CLIENT SIDE
            #  - USER ENTERED 1 TO 8  => LIST GENERATED IS 00000000 to 00000007 (ie prefix with 0's and subtract 1)
            #  - USER ENTERED 5 TO 15 => LIST GENERATED IS 00000004 to 00000014 (ie prefix with 0's and subtract 1)
            # AN ITEM FROM THE LIST IS CHOSEN AT RANDOM AND USED TO SQL-SELECT A WORD FROM THE LANGUAGE DICTIONARY BEING TESTED
            # AS EACH WORD IS PROCESSED, THE CORRESPONDING NUMBER IS DELETED FROM THE LIST SO IT CAN'T BE PICKED AGAIN
            for i in range(int(py_inputRangeFrom)-1, int(py_inputRangeTo)):
                rjzf_i = right_justify_zero_fill(i, 8)     # Zero Fill Right Justify i (to be total of 8 chars long) via this bespoke function
                py_list_of_word_IDs_to_test.append(rjzf_i) # Append the new 8-digit long number to the list

            print("we've just generated the list of 8 digit numbers")

            py_currentPointInTest = 0 # Since we only go down the main ELSE route for the first time in, we know current progress is "0" (first word in test run)
                                      # This will get incremented (to 1) in the merged (first & subsequent) code before being sent to front end.

            # Only need to do these loads once. However, for restarts (after SAVE) we'll possibly need to do them again
            list_direct_object_genders = load_direct_object_genders(py_currentLanguage) 
            gbl_JSON_list_direct_object_genders = json.dumps(list_direct_object_genders)

            list_special_chars = load_special_chars(py_currentLanguage)
            gbl_JSON_list_special_chars = json.dumps(list_special_chars)

         ### END OF "FIRST TIME IN" SPECIFIC CODE ###
         ############################################

         ##########################################################
         ### FIRST & SUBSEQUENT TIME IN CODE MERGES FROM NOW ON ###

        #print("py_list_of_word_IDs_to_test:",py_list_of_word_IDs_to_test)
        print("length of: py_list_of_word_IDs_to_test", len(py_list_of_word_IDs_to_test))

        if  len(py_list_of_word_IDs_to_test) == 0:
            py_actionToTake = "EndTest"

            py_nativeWord  = ""
            py_foreignWord = ""
            nativeHint     = ""
            foreignHint    = ""
            foreignPlural  = ""

            print("Tested all words => Changing py_actionToTake to EndTest")

        if  py_actionToTake == "ProcessWord":

          # call "chooseRandomWord" function to establish the next word in the test (list member is also deleted in this function)
            py_nativeWord,  \
            py_foreignWord, \
            nativeHint,     \
            foreignHint,    \
            foreignPlural = \
                chooseRandomWord(py_currentLanguage, py_list_of_word_IDs_to_test) # Automatic tuple unpacking (tuple returned from function)

          # if the user has picked a translation direction for the test, go with that for this word.
          # if the user has picked "random translation direction during test", call chooseRandomWordDirection() to pick one randomly
            print("py_translationDirectionOfTest",py_translationDirectionOfTest)

            if   (py_translationDirectionOfTest == const_nativeToForeign) \
            or   (py_translationDirectionOfTest == const_foreignToNative):
                  py_translationDirectionOfWord = py_translationDirectionOfTest
            elif (py_translationDirectionOfTest == const_randomDuringTest):
                  py_translationDirectionOfWord = chooseRandomWordDirection()

            print("py_translationDirectionOfWord:",py_translationDirectionOfWord)

            py_currentPointInTest += 1

            print("nativeWord:",py_nativeWord)
            print("foreignWord:",py_foreignWord)
            print("nativeHint:",nativeHint)
            print("foreignHint:",foreignHint)
            print("foreignPlural:",foreignPlural)

        if py_actionToTake == "EndTest":    # declare (and populate with default values) any variables that need to be sent to front end in render_template
            nativeWord    = "" 
            foreignWord   = ""
            nativeHint    = ""
            foreignHint   = ""
            foreignPlural = ""

        py_totalWordsInTest = int(py_inputRangeTo) - int(py_inputRangeFrom) + 1
            
        print("Sending these values to the client:")
        print("py_currentPointInTest:",py_currentPointInTest)
        print("py_currentLanguage:",py_currentLanguage)
        print("py_totalWordsInTest:",py_totalWordsInTest)
        print("py_translationDirectionOfWord:",py_translationDirectionOfWord)
        print("py_totalCorrectOnFirstTryCount:",py_totalCorrectOnFirstTryCount)
        print("py_totalCorrectOnSubsequentTryCount:",py_totalCorrectOnSubsequentTryCount)
        print("py_totalGiveUpsCount:",py_totalGiveUpsCount)
        print("py_nativeWord:",py_nativeWord)
        print("py_foreignWord:",py_foreignWord) 
        print("nativeHint:",nativeHint)
        print("foreignHint:",foreignHint) 
        print("foreignPlural:",foreignPlural)
        print("py_actionToTake:",py_actionToTake)

        return render_template("runningTest.html",
                               flask_currentPointInTest               = py_currentPointInTest,
                               flask_currentLanguage                  = py_currentLanguage,
                               flask_totalWordsInTest                 = py_totalWordsInTest,
                               flask_translationDirectionOfWord       = py_translationDirectionOfWord,
                               flask_totalCorrectOnFirstTryCount      = py_totalCorrectOnFirstTryCount,
                               flask_totalCorrectOnSubsequentTryCount = py_totalCorrectOnSubsequentTryCount,
                               flask_totalGiveUpsCount                = py_totalGiveUpsCount,
                               flask_NativeWord                       = py_nativeWord, 
                               flask_ForeignWord                      = py_foreignWord, 
                               flask_NativeHint                       = nativeHint, 
                               flask_ForeignHint                      = foreignHint, 
                               flask_ForeignPlural                    = foreignPlural,
                               flask_TestID                           = py_TestID,
                               flask_actionToTake                     = py_actionToTake,
                               flask_JSON_list_direct_object_genders  = gbl_JSON_list_direct_object_genders,
                               flask_listOfSpecialChars               = gbl_JSON_list_special_chars)
    except Exception as e:                                                                                                                              
        flash(e)                                                                                                                                        
        return render_template("yikes_404.html")


############################### </runningTest PAGE> ################################################################################################

############################### <chooseTestParams PAGE> ################################################################################################

@app.route("/chooseTestParams/<string:TestLanguage>", methods=["GET","POST"]) #when we have http://127.0.0.1:5000/chooseTestParams plus the name of a language (e.g. GERMAN) we are directed here, to this "app.route"
def chooseTestParams(TestLanguage):

    try:
        if request.method == "POST":

            print("this is the chooseTestParams function in Python - POST method")

            print("translationDirectionOfTest Sent:",request.form['translationDirectionOfTest'])
            print("allOrRange Sent:",request.form['allOrRange'])
            print("inputRangeFrom Sent:",request.form['inputRangeFrom'])
            print("inputRangeTo Sent:",request.form['inputRangeTo'])
            print("currentLanguage Sent:",request.form['currentLanguage'])

            py_translationDirectionOfTest = request.form['translationDirectionOfTest']
            py_allOrRange                 = request.form['allOrRange']
            py_inputRangeFrom             = request.form['inputRangeFrom']
            py_inputRangeTo               = request.form['inputRangeTo']
            py_currentLanguage            = request.form['currentLanguage']

            return redirect(url_for('runningTest', 
                                    py_translationDirectionOfTest = py_translationDirectionOfTest, 
                                    py_allOrRange                 = py_allOrRange, 
                                    py_inputRangeFrom             = py_inputRangeFrom, 
                                    py_inputRangeTo               = py_inputRangeTo, 
                                    py_currentLanguage            = py_currentLanguage))
        else:

            TestLanguageTuple = (TestLanguage,) # this line converts (eg) string "GERMAN" to tuple ("GERMAN",) as a tuple is needed for "?" in SQLite substitutions
                                                #NB - The comma MUST be included, otherwise TestLanguageTuple becomes a string (equal to TestLanguage)
                                                #NB - You can't use TestLanguageTuple = tuple(TestLanguage,) or TestLanguageTuple = tuple(TestLanguage) here 
                                                #     as those commands break string into individual chars and uses each char as a separate element in the tuple.
                                                #     This is because a string is an iterable object!
             

            conn = sqlite3.connect('LanguageLearner.db')
            c = conn.cursor()
            c.execute('SELECT COUNT(*) FROM DICT_RECORD WHERE ForeignLanguage=?', TestLanguageTuple)
            myNumberOfWordsInLanguageDictTuple = c.fetchone() # fetchone retrives a single TUPLE e.g. (3,)
            myNumberOfWordsInLanguageDictStr = myNumberOfWordsInLanguageDictTuple[0] #next we extract the only element from the tuple 

            return render_template("chooseTestParams.html",
                                   TestLanguage     = TestLanguage,
                                   SizeOfDictionary = myNumberOfWordsInLanguageDictStr)

    except Exception as e:
        flash(e)
        return render_template("yikes_404.html")


############################### </chooseTestParams PAGE> ################################################################################################

############################### <error PAGE> ################################################################################################

@app.errorhandler(404) #page not found because URL doesn't match anything in here? 
def yikes_page_not_found(e):
    global a # declare variable as global inside the function if you want to do update them. global is not needed for printing and accessing

    if a == 1:
        return("Something's not found bud!")
    elif a == 2:
        return render_template("yikes_404.html")
    else:
        return("page not found and control variable a not set to 1 or 2!")

############################### </error PAGE> ################################################################################################

############################### MAIN (Outside of Functions) ##################################################################################

a = 2 # global variable set up here

### global variables set up here ### 
##  NOTE: ONLY GLOBAL VARIABLES ARE RETAINED BETWEEN CALLS TO AND FROM FRONT END!!
py_list_of_word_IDs_to_test = [] #create a global (empty for now) list which we'll use later to store the ID of the words in our test. We'll remove the ID's from the list as the words are tested. If the test is saved, a list of untested ID's can be saved to file
py_currentPointInTest         = 0
py_translationDirectionOfTest = ""
py_translationDirectionOfWord = ""
py_allOrRange                 = ""
py_inputRangeFrom             = 0
py_inputRangeTo               = 0
py_currentLanguage            = ""
py_nativeWord                 = ""
py_foreignWord                = ""
py_TestID                     = ""
py_uniqueNum                  = ""

py_totalCorrectOnFirstTryCount      = 0
py_totalCorrectOnSubsequentTryCount = 0
py_totalGiveUpsCount                = 0

gbl_JSON_list_direct_object_genders = ""
gbl_JSON_list_special_chars         = ""

const_nativeToForeign  = "nativeToForeign" # These aren't real constants (constants don't exist in Python) but the const_ tag indicates the intention!
const_foreignToNative  = "foreignToNative"
const_randomDuringTest = "randomDuringTest"
### /global variables set up here ###

if __name__ == "__main__":
    app.run()

############################### /MAIN (Outside of Functions) ##################################################################################