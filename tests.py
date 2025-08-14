import scrabble
import random


def dawg_test(error=None):
    # creates a random set of strings for testing purposes
    strings1 = []  # set of strings with no repeats, or substrings
    strings2 = []  # set of strings containing strings from strings1
    strings3 = []  # set if strings contains duplicates from strings1
    letters = [chr(i) for i in range(ord("A"), ord("Z") + 1)]
    # creates 8.000 random strings
    counter = 0
    while counter < 8000:
        string = ""
        # generates string between 2 and 15 characters
        for j in range(random.randint(2, 15)):
            string += random.choice(letters)
        # checks if string is a subset of any other word in strings1
        if string not in [i[:len(string)] for i in strings1]:
            strings1.append(string)
            counter += 1
    print("strings1: created")
    # adds 0.000 substrings to strings2, for a total of 100.000 strings (some will be repeats)
    counter = 0
    while counter < 1000:
        string = random.choice(strings1)
        if len(string) != 2:
            new_string = string[:random.randint(2, len(string) - 1)]
            if new_string not in strings1 and new_string not in strings2:
                strings2.append(new_string)
                counter += 1
    print("strings2: created")
    # adds 1.000 duplicates to strings3
    counter = 0
    print("strings3: created")
    while counter < 1000:
        strings3.append(random.choice(strings1))
        counter += 1
    # tests1 DAWG creation
    a, b, c, d = [None]*4
    try:
        a = scrabble.DAWG(strings1)
        print("DAWG a: created")
    except error:
        print("DAWG a: failed", error)
    try:
        b = scrabble.DAWG(strings1+strings2)
        print("DAWG b: created")
    except error:
        print("DAWG b: failed", error)
    try:
        c = scrabble.DAWG(strings1+strings3)
        print("DAWG c: created")
    except error:
        print("DAWG c: failed", error)
    try:
        d = scrabble.DAWG(strings1+strings2+strings3)
        print("DAWG d: created")
    except error:
        print("DAWG d: failed", error)
    DAWGs = []
    for key, value in locals().items():
        if isinstance(value, scrabble.DAWG):
            DAWGs.append([key, value])
    # test2 retrieval
    for name, dawg in DAWGs:
        print("Retrieval tests for dawg {0}".format(name))
        try:
            true, false, none, = [0] * 3
            for string in strings1:
                rtn = dawg.contains(string)
                if rtn:
                    true += 1
                elif not rtn:
                    false += 1
                else:
                    none += 1
            print("test 1: found {0}, not found {1}, none {2}".format(true, false, none))
        except error:
            print("test 1: failed", error)
        try:
            true, false, none, = [0] * 3
            for string in strings1 + strings2:
                rtn = dawg.contains(string)
                if rtn:
                    true += 1
                elif not rtn:
                    false += 1
                else:
                    none += 1
            print("test 2: found {0}, not found {1}, none {2}".format(true, false, none))
        except error:
            print("test 2: failed", error)
        try:
            true, false, none, = [0] * 3
            for string in strings1 + strings3:
                rtn = dawg.contains(string)
                if rtn:
                    true += 1
                elif not rtn:
                    false += 1
                else:
                    none += 1
            print("test 3: found {0}, not found {1}, none {2}".format(true, false, none))
        except error:
            print("test 3: failed", error)
        try:
            true, false, none, = [0] * 3
            for string in strings1 + strings2 + strings3:
                rtn = dawg.contains(string)
                if rtn:
                    true += 1
                elif not rtn:
                    false += 1
                else:
                    none += 1
            print("test 4: found {0}, not found {1}, none {2}".format(true, false, none))
        except error:
            print("test 4: failed", error)


if __name__ == "__main__":
    # dawg_test()
    dawg = scrabble.DAWG(["AAA", "ABA", "AAB"])
    print(dawg.nodes)
    print(dawg.find("A**"))
