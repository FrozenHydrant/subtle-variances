import sys
import array
import random
import os
import uuid
import shutil
from pydub import *

def true_speed_increase(seg, increment):
    seg_array = seg.get_array_of_samples()
    new_array = []
    for i in range(int(len(seg_array)/increment)):
        new_array.append(seg_array[int(i*increment)])

    return seg._spawn(array.array(song.array_type, new_array))

def verify_diffname(my_file, target_diffname):
    my_line = my_file.readline()
    while "Version:" not in my_line:
        my_line = my_file.readline()
    diffname = my_line.split(":")[1].strip("\n")
    return diffname == target_diffname
    
arg_count = len(sys.argv)

if arg_count < 4:
    print("Error: Needs more arguments.")
else:
    path = sys.argv[1]
    diffname = sys.argv[2]
    true_file_name = ""

    #finding the filename of the difficulty we want (loosely)
    for (dirpath, dirnames, filenames) in os.walk(path):
        for file_name in filenames:
            if file_name.split(".")[1] == "osu":
                if diffname in file_name:
                    with open(os.path.join(path, file_name), "r", encoding="utf-8") as opened_file:
                        # Then verify the diffname is correct (tightly)
                        if verify_diffname(opened_file, diffname):
                            true_file_name = file_name
        break

    #open the osu file to read contents
    opened_file = open(os.path.join(path, true_file_name), "r", encoding="utf-8")
    opened_file_contents = opened_file.read()
    opened_file.close()

    # get metadata
    title_index = opened_file_contents.index("Title:")
    title = opened_file_contents[title_index+len("Title:"):opened_file_contents.index("\n",title_index):]
    artist_index = opened_file_contents.index("Artist:")
    artist = opened_file_contents[artist_index+len("Artist:"):opened_file_contents.index("\n",artist_index):]
    host_index = opened_file_contents.index("Creator:")
    host = opened_file_contents[host_index+len("Creator:"):opened_file_contents.index("\n",host_index):]

    #get the audio file name, it's audio.mp3 like 99% of the time
    file_name_index = opened_file_contents.index("AudioFilename: ")
    audio_file_name = opened_file_contents[file_name_index+len("AudioFilename: "):opened_file_contents.index("\n", file_name_index):]

    #go to the directory
    os.chdir(path)
    
    if sys.argv[3] == "speed" and arg_count == 5:

        #get the multiplier
        change = float(sys.argv[4])
        new_diffname = diffname + " x" + str(change)
        
        #get the song mp3
        song = AudioSegment.from_mp3(os.path.join(path, audio_file_name))
        song = song.set_channels(1)

        #speed/slow it
        song = true_speed_increase(song, change)

        #generating a title
        song.export(new_diffname + ".mp3", format="mp3")
        with open(artist + " - " + title + " (" + host + ") [" + new_diffname + "]" + ".osu", "w+", encoding="utf-8") as osufile:
            innards = opened_file_contents.split("\n")
            i = -1
            while i < len(innards):
                if ("AudioFilename:" in innards[i]):
                    innards[i] = innards[i].replace(audio_file_name, new_diffname+".mp3")
                if ("Version:" in innards[i]):
                    innards[i] = innards[i].replace(diffname, new_diffname)
                if ("[TimingPoints]" in innards[i]):
                    i = i + 1
                    while innards[i] != "":
                        innards_split = innards[i].split(",")
                        innards_new_timing = int(int(innards_split[0]) / change)
                        innards_split[0] = str(innards_new_timing)

                        if (innards_split[6] == "1"):
                            innards_new_bpm = float(innards_split[1]) / change
                            innards_split[1] = str(innards_new_bpm)

                        innards[i] = ",".join(innards_split)
                        i = i + 1
                    i = i - 1
                if ("[HitObjects]" in innards[i]):
                    i = i + 1
                    while innards[i] != "":
                        innards_split = innards[i].split(",")
                        innards_new_timing = int(int(innards_split[2]) / change)
                        innards_split[2] = str(innards_new_timing)
                        innards[i] = ",".join(innards_split)
                        i = i + 1
                    i = i - 1
                i = i + 1
            osufile.write("\n".join(innards))
            
