import io
import tkinter as tk
import mutagen.id3
import pygame
from pygame import mixer
from tkinter import filedialog
from tkinter import messagebox
import os
from mutagen.mp3 import MP3
from mutagen.id3 import ID3
from PIL import Image,ImageTk
from time import sleep
from threading import Thread
import random
from idlelib.tooltip import Hovertip

def play_pause_resume():
    global  last_selected_file,player_queue,loop_count
    if len(player_queue)==0:
        messagebox.showerror("No song selected","Open & select any audio file from your computer")
    else:
        # Play the last selected file from beginning
        thread_play_song()
def play_song():
    global song_at_top,playing_status,player_queue,loop_count,song_pointer,running,last_slider_value,prev_button_clicked
    global running_status,total_length_audio,num,shuffled_player_queue
    playing_status = True
    mixer.init()
    if len(player_queue)>=1 and song_pointer<len(player_queue):
        if (clicked_from_listbox==True and shuffle_status==True) or shuffle_status==False or (clicked_from_listbox==True and shuffle_status==False):
            song_at_top = player_queue[song_pointer]
        elif shuffle_status==True:
            song_at_top = shuffled_player_queue[song_pointer]
    last_slider_value = 0
    # Using try catch statements to avoid playing any corrupted file. It loads the file.
    # If it is corrupted, the 'except' part is run.
    try:
        mixer.music.load(song_at_top)
        mixer.music.play(start=last_slider_value)
        running_status = True
        # Reset the slider in scale to 0 as the audio file has started to play from the beginning now.
        scale.set(0)
        show_album_art(song_at_top)
        loop_count = loop_var.get()
        # Extracting metadata of audio file using mutagen.
        filestats = MP3(song_at_top)
        audio_name_label.config(text="Now Playing: "+song_at_top[song_at_top.rfind("/")+1:],font=("Times New Roman",15,"italic"))
        audio_album = filestats.get("TALB")
        singers = filestats.get("TPE1")
        year = filestats.get("TDRC")
        album_name_label.config(text=f"Album: {audio_album}")
        artists_label.config(text=f"Artists: {singers}")
        album_year_label.config(text=f"Album year: {year}")
        duration = divmod(filestats.info.length,60)
        minutes = int(duration[0])
        seconds_ = int(duration[1])
        duration_label.config(text="Duration: "+str(minutes)+":"+str(seconds_))
        end_duration = (int(duration[0])*60)+int(duration[1])
        scale.config(from_=0,to=filestats.info.length)
        # Change play button to pause button
        play_button1.config(text="Pause",command=pause_song,image=pause_icon,compound=tk.LEFT)
        id = pygame.USEREVENT
        mixer.music.set_endevent(id)
        # Initializing 'num' to 0 to display with scale as number.
        num=0
        running=True
        while running:
            for event in pygame.event.get():
                if running is False: # Stopping the mixer from playing, when any external way is used to force stop.
                    running=False
                if event.type==id:
                    # Song file playing completed fully on its own.
                    running=False
                    running_status = False
                root.update()
            root.update()
            if running==False:
                if loop_count==-1: # Playing the current audio file repeatedly. Loop one audio file.
                    thread_play_song()
                elif loop_count==-2: # Close GUI
                    break
                elif loop_count==1: # Continuous playing
                    # Playing Next song in listbox.
                    play_button1.config(text="Play", command=thread_play_song, image=play_icon, compound=tk.LEFT)
                    next_audio()
                elif loop_count==0: # When an audio file is played fully and ends on its own.
                    play_button1.config(text="Play", command=thread_play_song, image=play_icon, compound=tk.LEFT)
                    # Now the audio is played fully. Click play to play again!")
                    listbox1.selection_clear(0, tk.END)
                    play_button1.config(text="Play",command=thread_play_song,image=play_icon,compound=tk.LEFT)
                    break
                break
            root.update()
            controls_frame.update()
            thread_show_visualization()
            if play_button1.cget('text')=="Pause":
                num += 1
                move_slider(num)
            sleep(1)
            root.update()
        # Broke out
    except pygame.error as err:
        messagebox.showerror("Corrupted file", "There is some error in this audio. Cannot play!")
        # ERROR CORRUPTED FILE, incrementing song_pointer.
        if prev_button_clicked==True:
            previous_audio()
            prev_button_clicked = False
        else:
            next_audio()

def thread_play_song():
    thread_var_play_song = Thread(target=play_song())
    thread_var_play_song.start()
def move_slider(num):
    scale.set(num)

# Function to run when the slider on scale is moved and released somewhere in the scale.
def set_slider_position(event):
    global num
    scale.set(scale.get())
    play_button1.config(text="Pause", command=pause_song, image=pause_icon, compound=tk.LEFT)
    num = scale.get()
    mixer.music.play(start=scale.get())
def thread_set_slider_position(event):
    thread_var = Thread(target=set_slider_position(event))
    thread_var.start()

# Function to pause the song
def pause_song():
    global playing_status,running_status
    if mixer.music.get_busy():
        playing_status = False
        mixer.music.pause()
        play_button1.config(text="Resume",command=resume_song,image=resume_icon,compound=tk.LEFT)

# Function to resume the song playing
def resume_song():
    global playing_status,running_status,last_slider_value
    playing_status=True
    if mixer.music.get_busy()==False:
        play_button1.config(text="Pause", command=pause_song, image=pause_icon, compound=tk.LEFT)
        mixer.music.unpause()


def stop_song():
    global loop_count,running_status
    mixer.init()
    mixer.music.stop()
    loop_count = -2   # Change this to 0 if possible. Because i assigned -2 for closing GUI only.
    # Change 'play_button1' text to 'Play'.
    play_button1.config(text="Play", command=thread_play_song, image=play_icon, compound=tk.LEFT)
    running_status = False
    root.update()
    loop_count = 0
    loop_button1.config(text="Loop OFF",image=repeat_none_image,compound=tk.LEFT)
    loop_var.set(0)

def repeat_loop():
    global loop_count
    if loop_count==0: # Now 'Loop OFF'. Changing it to 'Loop single audio ON'.
        loop_count = -1
        loop_button1.config(text="Loop ON",image=repeat_one_image,compound=tk.LEFT)
        loop_var.set(-1)
    elif loop_count==-1: # Now 'Loop single audio ON'. Changing it to 'Loop All'.
        loop_count = 1
        loop_button1.config(text="Loop All",image=repeat_no_image,compound=tk.LEFT)
        loop_var.set(1)
    elif loop_count==1:  # Now 'Loop All'. Changing it to 'Loop OFF'.
        loop_count = 0
        loop_button1.config(text="Loop OFF", image=repeat_none_image, compound=tk.LEFT)
        loop_var.set(0)
    elif loop_count==-2:  # Stopped player
        loop_count = 0
        loop_button1.config(text="Loop OFF",image=repeat_none_image,compound=tk.LEFT)
        loop_var.set(0)
def thread_repeat_loop():
    thread_repeat_loop_var = Thread(target=repeat_loop())
    thread_repeat_loop_var.start()

def next_audio():
    global song_pointer,prev_button_clicked,clicked_from_listbox
    clicked_from_listbox = False
    if len(player_queue)>0:
        prev_button_clicked = False
        if song_pointer==len(player_queue)-1:
            # No more songs to play!
            pass
        else:
            song_pointer += 1
            thread_play_song()
def thread_next_audio():
    thread_next_audio_var = Thread(target=next_audio())
    thread_next_audio_var.start()
def previous_audio():
    global song_pointer,prev_button_clicked,clicked_from_listbox
    clicked_from_listbox = False
    if len(player_queue)>0:
        if song_pointer==0:
            # No more songs to play!
            pass
        else:
            song_pointer -= 1
            prev_button_clicked = True
            thread_play_song()
def thread_previous_audio():
    thread_prev_audio_var = Thread(target=previous_audio())
    thread_prev_audio_var.start()

def close_window():
    global running,loop_count
    mixer.music.unload()
    mixer.music.stop()
    running = False
    loop_count = -2
    root.update()
    root.destroy()
def play_button_key_event(event):
    global play_button1
    if play_button1.cget('text')=="Pause":
        pause_song()
    elif play_button1.cget('text')=="Resume":
        resume_song()
    elif play_button1.cget('text')=="Play":
        play_pause_resume()

def volume_up():
    global canvas1,line1
    if mixer.music.get_volume()<1.0:
        mixer.music.set_volume(mixer.music.get_volume()+0.1)
        volume_label.config(text=str(mixer.music.get_volume())[0:3])
        current_audio_level = float(str(mixer.music.get_volume())[0:3])*100
        canvas1.delete('all')
        line1 = canvas1.create_line(5, 5, current_audio_level, 5, fill=main_color, width=4)

def thread_volume_up():
    thread_volume_up_var = Thread(target=volume_up())
    thread_volume_up_var.start()
def volume_down():
    global canvas1,line1
    if mixer.music.get_volume()>0.1:
        mixer.music.set_volume(mixer.music.get_volume()-0.1)
        volume_label.config(text=str(mixer.music.get_volume())[0:3])
        current_audio_level = float(str(mixer.music.get_volume())[0:3]) * 100
        canvas1.delete('all')
        line1 = canvas1.create_line(5, 5, current_audio_level, 5, fill=main_color, width=4)
def thread_volume_down():
    thread_volume_down_var = Thread(target=volume_down())
    thread_volume_down_var.start()
def volume_mute():
    global canvas1,line1
    mixer.music.set_volume(0.0)
    canvas1.delete('all')
    line1 = canvas1.create_line(5, 5, 5, 5, fill=main_color)
def thread_volume_mute():
    thread_volume_mute_var = Thread(target=volume_mute())
    thread_volume_mute_var.start()
def select_folder():
    global player_queue,song_pointer,songs_dictionary,shuffled_player_queue
    selected_folder = filedialog.askdirectory()
    if len(selected_folder)>0:
        listbox1.delete(0, tk.END)
        play_button1.config(state=tk.DISABLED)
        next_button.config(state=tk.DISABLED)
        previous_button.config(state=tk.DISABLED)
        # Change appearance of the buttons above listbox.
        btn_sort_by_album.config(relief=tk.RAISED, bd=6)
        btn_sort_by_atoz.config(relief=tk.RAISED, bd=2)
        btn_sort_by_album_year.config(relief=tk.RAISED, bd=2)
        player_queue = []   # CLEAR THIS. UNCOMMENT THIS
        songs_dictionary = {}  # Dictionary to hold filename as key and array of file path 'root' as values.
        for (root,dirs,files) in os.walk(selected_folder):
            if len(files)>0:
                for file_in_folder in files:
                    if file_in_folder[-4:]==".mp3":
                        if file_in_folder not in songs_dictionary:
                            songs_dictionary.update({file_in_folder:[root]})
                        else:
                            arr = songs_dictionary.get(file_in_folder)
                            arr.append(root)
                            songs_dictionary.update({file_in_folder:arr})
                        player_queue.append(root+"/"+file_in_folder)
                        listbox1.insert(listbox1.size(),file_in_folder)
        # Creating shuffled array of songs from array 'player_queue'.
        shuffled_player_queue = player_queue.copy()
        random.shuffle(shuffled_player_queue)
        play_button1.config(state=tk.NORMAL)
        next_button.config(state=tk.NORMAL)
        previous_button.config(state=tk.NORMAL)
        scale.config(state=tk.NORMAL)
        scale.bind("<ButtonRelease-1>", thread_set_slider_position)
        song_pointer = 0
        thread_play_song()
def thread_select_folder():
    thread_select_folder_var = Thread(target=select_folder())
    thread_select_folder_var.start()
def sort_songs_list_atoz():
    global listbox_file_names,songs_dictionary,song_pointer,player_queue,shuffled_player_queue
    btn_sort_by_album.config(relief=tk.RAISED, bd=2)
    btn_sort_by_atoz.config(relief=tk.RAISED, bd=6)
    btn_sort_by_album_year.config(relief=tk.RAISED, bd=2)
    if len(songs_dictionary)>0:
        player_queue = []
        listbox1.delete(0, tk.END)
        songs_dictionary_keys = list(songs_dictionary.keys())
        songs_dictionary_keys.sort()
        sorted_songs_dictionary = {k:songs_dictionary[k] for k in songs_dictionary_keys}
        for song in sorted_songs_dictionary:
            song_locations_list = sorted_songs_dictionary.get(song)
            for location_path in song_locations_list:
                player_queue.append(location_path+"/"+song)
                listbox1.insert(listbox1.size(),song)
        # Creating shuffled array of songs from array 'player_queue'.
        shuffled_player_queue = player_queue.copy()
        random.shuffle(shuffled_player_queue)
        song_pointer = 0
        thread_play_song()
def thread_sort_songs_list_atoz():
    thread_sort_songs_list_atoz_var = Thread(target=sort_songs_list_atoz())
    thread_sort_songs_list_atoz_var.start()

def sort_songs_list_by_album_year():
    global player_queue,song_pointer,listbox1,shuffled_player_queue
    btn_sort_by_album.config(relief=tk.RAISED,bd=2)
    btn_sort_by_atoz.config(relief=tk.RAISED,bd=2)
    btn_sort_by_album_year.config(relief=tk.RAISED,bd=6)
    if len(songs_dictionary)>0:
        # Mapping album year with list of songs containing file name with filepath
        year_song_dictionary = {}
        listbox1.delete(0, tk.END)
        for song in player_queue:
            try:
                mixer.music.load(song)
                filestats = MP3(song)
                if str(filestats.get("TDRC")) not in year_song_dictionary:
                    year_song_dictionary.update({str(filestats.get('TDRC')):[song]})
                else:
                    songs_in_this_year = year_song_dictionary.get(str(filestats.get('TDRC')))
                    songs_in_this_year.append(song)
                    year_song_dictionary.update({str(filestats.get('TDRC')):songs_in_this_year})
            except pygame.error as err:
                # File corrupted. No MP3 tags for file.
                pass
        # Get list of keys in dictionary 'year_song_dictionary'.
        years_list_keys = list(year_song_dictionary.keys())
        # Sort the list 'years_list_keys'.
        years_list_keys.sort()
        # Create a new dictionary 'sorted_songs_by_years_dictionary' with sorted years as key, and list of songs with file path as values.
        sorted_songs_by_years_dictionary = {k: year_song_dictionary[k] for k in years_list_keys}
        # Clear the player queue list now.
        player_queue = []
        # Insert every item from the newly created dictionary's value to the array 'player_queue'.
        for song_location_with_name_list in sorted_songs_by_years_dictionary.values():
            for song_name_with_location in song_location_with_name_list:
                player_queue.append(song_name_with_location)
                listbox1.insert(listbox1.size(), song_name_with_location[song_name_with_location.rfind("/")+1:])
        # Creating shuffled array of songs from array 'player_queue'.
        shuffled_player_queue = player_queue.copy()
        random.shuffle(shuffled_player_queue)
        song_pointer = 0
        thread_play_song()
def thread_sort_songs_list_by_album_year():
    thread_var = Thread(target=sort_songs_list_by_album_year())
    thread_var.start()

def sort_songs_list_album():
    global listbox_file_names,songs_dictionary,song_pointer,player_queue
    btn_sort_by_album.config(relief=tk.RAISED, bd=6)
    btn_sort_by_atoz.config(relief=tk.RAISED, bd=2)
    btn_sort_by_album_year.config(relief=tk.RAISED, bd=2)
    if len(songs_dictionary):
        player_queue = []
        listbox1.delete(0, tk.END)
        for song in songs_dictionary:
            song_locations_list = songs_dictionary.get(song)
            for location_path in song_locations_list:
                player_queue.append(location_path+"/"+song)
                listbox1.insert(listbox1.size(),song)
        song_pointer = 0
        thread_play_song()
def thread_sort_songs_list_album():
    thread_var_sort_songs_list_album = Thread(target=sort_songs_list_album())
    thread_var_sort_songs_list_album.start()
def show_album_art(song_playing):
    filestats = MP3(song_playing, ID3=ID3)
    # If the audio file has no album art, set default image 'record' as album art.
    if str(type(filestats.get("APIC:"))) == "<class 'NoneType'>":
        music_image_label.config(image=music_art_image)
        music_image_label.image = music_art_image
    else:   # If the audio file has album art, fetch it from metadata and display it.
        try:  # Use try catch statement if there are more errors while getting ID3 data. This prevents any error.
            # Getting ready to show Album Art
            id3_playing_song = ID3(song_playing)
            id3_data = id3_playing_song.getall("APIC")[0].data
            img = Image.open(io.BytesIO(id3_data))
            max_width, max_height = music_image_label.winfo_width(), music_image_label.winfo_height()
            img.thumbnail((max_width, max_height))
            photo = ImageTk.PhotoImage(img)
            music_image_label.config(image=photo)
            music_image_label.image = photo
        except:  # If there is any error in getting ID3 of audio file, set the default 'record' as album art.
            music_image_label.config(image=music_art_image)
            music_image_label.image = music_art_image

def show_listbox(event):
    global song_pointer,clicked_from_listbox
    if listbox1.size()>0:
        selected_index = listbox1.curselection()[0]
        song_pointer = selected_index
        listbox1.selection_clear(0,tk.END)
        clicked_from_listbox = True
        thread_play_song()
        clicked_from_listbox = False

def get_slider_value(v):
    global last_slider_value
    slider_value = scale.get()
    return slider_value

def about():
    new_popup_window = tk.Toplevel()
    new_popup_window.title("About PC Musique Player")
    new_popup_window.geometry("500x250")
    new_popup_window.transient(root) # To avoid it from preventing the root window to be paused.
    new_popup_window.wm_attributes('-topmost', True)
    app_icon_label = tk.Label(new_popup_window,image=app_logo_image)
    app_icon_label.pack()
    tk.Label(new_popup_window,text="PC Musique Player",font=("Arial",16)).pack()
    content = "Version: 1.0.0\nRelease Date: 5th June 2024\nDeveloper: Reshma Haridhas\nOS: Windows 10 or later\nCopyright: © 2024 Reshma Haridhas. All Rights Reserved"
    content_label = tk.Label(new_popup_window,text=content,font=("Arial",10),fg="#000000")
    content_label.pack()
    # Do not use mainloop() here.

def thread_about():
    thread_var_about = Thread(target=about())
    thread_var_about.start()

def show_visualizations():
    global canvas_visualization,random_line_1,random_line_2,random_line_3,random_line_4,random_line_5,random_line_6,\
        random_line_7,random_line_8,random_line_9
    canvas_visualization.delete('all')
    starting_y_list = [5,10,15,20,25,30,35,40]
    random.shuffle(starting_y_list)
    random_line_1 = canvas_visualization.create_line(5, starting_y_list[0], 5, 50, width=5, fill=main_color)
    random_line_2 = canvas_visualization.create_line(12, starting_y_list[1], 12, 50, width=5, fill=button_ui_bg_color)
    random_line_3 = canvas_visualization.create_line(19, starting_y_list[2], 19, 50, width=5, fill=main_color)
    random_line_4 = canvas_visualization.create_line(26, starting_y_list[3], 26, 50, width=5, fill=button_ui_bg_color)
    random_line_5 = canvas_visualization.create_line(33, starting_y_list[4], 33, 50, width=5, fill=main_color)
    random_line_6 = canvas_visualization.create_line(40, starting_y_list[5], 40, 50, width=5, fill=button_ui_bg_color)
    random_line_7 = canvas_visualization.create_line(47, starting_y_list[6], 47, 50, width=5, fill=main_color)
    random_line_8 = canvas_visualization.create_line(54, starting_y_list[7], 54, 50, width=5, fill=button_ui_bg_color)
    random_line_9 = canvas_visualization.create_line(61, starting_y_list[0], 61, 50, width=5, fill=main_color)
def thread_show_visualization():
    thread_var_visualization = Thread(target=show_visualizations())
    thread_var_visualization.start()
def change_player_theme(index_number):
    global main_color,button_ui_bg_color,text_color,btn_sort_by_album,btn_sort_by_album_year,btn_sort_by_album_year
    main_color = color_themes_main_color[index_number]
    button_ui_bg_color = color_themes_button_ui_bg_color[index_number]
    text_color = color_themes_text_color[index_number]
    # action
    root.config(bg=main_color)
    frame1.config(bg=main_color)
    mainFrame.config(bg=main_color)
    sideFrame.config(bg=main_color)
    music_image_label.config(bg=main_color)
    audio_name_label.config(bg=main_color,fg=text_color)
    album_name_label.config(bg=main_color,fg=text_color)
    artists_label.config(bg=main_color,fg=text_color)
    album_year_label.config(bg=main_color,fg=text_color)
    duration_label.config(bg=main_color,fg=text_color)
    scale.config(bg=main_color,troughcolor=button_ui_bg_color,activebackground=main_color,fg=text_color)
    controls_frame.config(background=main_color)
    shuffle_button.config(bg=button_ui_bg_color,activebackground=button_ui_bg_color)
    previous_button.config(bg=button_ui_bg_color,activebackground=button_ui_bg_color)
    play_button1.config(bg=button_ui_bg_color,activebackground=button_ui_bg_color)
    next_button.config(bg=button_ui_bg_color,activebackground=button_ui_bg_color)
    loop_button1.config(bg=button_ui_bg_color,activebackground=button_ui_bg_color)
    stop_button.config(bg=button_ui_bg_color,activebackground=button_ui_bg_color)
    controls_frame2.config(background=main_color)
    volume_down_button.config(bg=button_ui_bg_color,activebackground=button_ui_bg_color)
    volume_up_button.config(bg=button_ui_bg_color,activebackground=button_ui_bg_color)
    volume_mute_button.config(bg=button_ui_bg_color,activebackground=button_ui_bg_color)
    open_folder_button.config(bg=button_ui_bg_color,activebackground=button_ui_bg_color)
    songs_label.config(bg=main_color,activebackground=main_color,fg=text_color)
    sort_frame.config(background=main_color)
    btn_sort_by_album.config(bg=button_ui_bg_color, activebackground=button_ui_bg_color, fg=text_color)
    btn_sort_by_atoz.config(bg=button_ui_bg_color,activebackground=button_ui_bg_color, fg=text_color)
    btn_sort_by_album_year.config(bg=button_ui_bg_color, activebackground=button_ui_bg_color, fg=text_color)
    listbox1.config(bg=main_color,fg=text_color,highlightbackground=text_color)
    canvas1.itemconfig(line1,fill=main_color)
    canvas_visualization.itemconfig(random_line_1,fill=main_color)
    canvas_visualization.itemconfig(random_line_2, fill=button_ui_bg_color)
    canvas_visualization.itemconfig(random_line_3, fill=main_color)
    canvas_visualization.itemconfig(random_line_4, fill=button_ui_bg_color)
    canvas_visualization.itemconfig(random_line_5, fill=main_color)
    canvas_visualization.itemconfig(random_line_6, fill=button_ui_bg_color)
    canvas_visualization.itemconfig(random_line_7, fill=main_color)
    canvas_visualization.itemconfig(random_line_8, fill=button_ui_bg_color)
    canvas_visualization.itemconfig(random_line_9, fill=main_color)
    if index_number==14:
        fileMenu.config(background=button_ui_bg_color, fg="white")
        audio_Menu.config(background=button_ui_bg_color, fg="white")
        player_Menu.config(background=button_ui_bg_color, fg="white")
        help_Menu.config(background=button_ui_bg_color,fg="white")
        btn_sort_by_album.config(bg=button_ui_bg_color, activebackground=button_ui_bg_color, fg="white")
        btn_sort_by_atoz.config(bg=button_ui_bg_color, activebackground=button_ui_bg_color, fg="white")
        btn_sort_by_album_year.config(bg=button_ui_bg_color, activebackground=button_ui_bg_color, fg="white")
    else:
        fileMenu.config(background=button_ui_bg_color, fg="black")
        audio_Menu.config(background=button_ui_bg_color, fg="black")
        player_Menu.config(background=button_ui_bg_color,fg="black")
        help_Menu.config(background=button_ui_bg_color,fg="black")
    if index_number == 0 or index_number == 4 or index_number==5 or index_number==7 or index_number==8 or index_number==9 or index_number==15:
        btn_sort_by_album.config(bg=button_ui_bg_color, activebackground=button_ui_bg_color, fg="black")
        btn_sort_by_atoz.config(bg=button_ui_bg_color, activebackground=button_ui_bg_color, fg="black")
        btn_sort_by_album_year.config(bg=button_ui_bg_color, activebackground=button_ui_bg_color, fg="black")

def hide_library():
    root.minsize(width=1020,height=750)
    root.maxsize(width=1020,height=750)
def show_library():
    root.minsize(width=1520,height=770)
    root.maxsize(width=1520,height=770)
    root.geometry("1520x770")
def shuffle_song_playing_order():
    global shuffle_status
    shuffle_status = not shuffle_status
    change_text_shuffle_button()
def thread_shuffle_song_playing_order():
    thread_shuffle_song_playing_order_var = Thread(target=shuffle_song_playing_order())
    thread_shuffle_song_playing_order_var.start()
def change_text_shuffle_button():
    if shuffle_status==False:
        shuffle_button.config(text="Shuffle OFF",image=shuffle_no_image)
        Hovertip(shuffle_button, "Shuffle Off")
    else:
        shuffle_button.config(text="Shuffle ON",image=shuffle_image)
        Hovertip(shuffle_button, "Shuffle On")



root = tk.Tk()
root.title("PC Musique Player")
root.geometry("1450x750")
root.minsize(width=1450,height=750)
# List of colors for varied themes
color_theme_names = ["French Rouge","French Bleu","French Vert","French Reef","Jalapeno Red","Dutch Red",
                     "Dutch Sunflower","Merchant Marine Blue","Dutch Green","Dutch Purple","Lavender",
                     "Dutch Purple Dark","Gloomy purple","Hibiscus Orange","NYC Taxi","Midnight Blue"]
color_themes_main_color = ["#eb2f06","#1e3799","#78e08f","#079992","#b71540","#EA2027","#FFC312","#0652DD","#009432",
                           "#5758BB","#D980FA","#6F1E51","#8854d0","#fa8231","#f7b731","#2c3e50"]
color_themes_button_ui_bg_color = ["#f3826a","#4a69bd","#b8e994","#38ada9","#db8aa0","#EE5A24","#F79F1F","#12CBC4",
                                   "#A3CB38","#9980FA","#FDA7DF","#B53471","#a55eea","#fd9644","#4d4d4d","white"]
color_themes_text_color = ["white","white","black","#000000","white","#FFFFFF","black","white","white","#FFFFFF","black",
                           "white","black","black","black","white"]
current_audio_level = 50
# Setting the color theme initially in GUI
main_color = color_themes_main_color[1]
button_ui_bg_color = color_themes_button_ui_bg_color[1]
text_color = color_themes_text_color[1]
root.config(bg=main_color)
root.protocol("WM_DELETE_WINDOW",close_window)
# PhotoImage variables
music_art_image = tk.PhotoImage(file="assets/images/record.png")
music_icon = tk.PhotoImage(file="assets/images/icons8-music-96.png").subsample(2,2)
play_icon = tk.PhotoImage(file="assets/images/icons8-circled-play-100.png").subsample(2,2)
pause_icon = tk.PhotoImage(file="assets/images/icons8-pause-button-100.png").subsample(2,2)
resume_icon = tk.PhotoImage(file="assets/images/icons8-resume-button-100.png").subsample(2,2)
stop_icon = tk.PhotoImage(file="assets/images/icons8-stop-circled-100.png").subsample(2,2)
next_image = tk.PhotoImage(file="assets/images/icons8-next-100.png").subsample(2,2)
previous_image = tk.PhotoImage(file="assets/images/icons8-previous-100.png").subsample(2,2)
repeat_one_image = tk.PhotoImage(file="assets/images/icons8-repeat-one-100.png").subsample(2,2)
repeat_no_image = tk.PhotoImage(file="assets/images/icons8-repeat-no-100.png").subsample(2,2)
repeat_none_image = tk.PhotoImage(file="assets/images/icons8-repeat-none-100.png").subsample(2,2)
shuffle_image = tk.PhotoImage(file="assets/images/icons8-shuffle-100.png").subsample(2,2)
shuffle_no_image = tk.PhotoImage(file="assets/images/icons8-no-shuffle-100.png").subsample(2,2)
low_volume_image = tk.PhotoImage(file="assets/images/icons8-volume-down-100-black.png").subsample(3,3)
high_volume_image = tk.PhotoImage(file="assets/images/icons8-volumeup-100-black.png").subsample(3,3)
mute_image = tk.PhotoImage(file="assets/images/icons8-volume-mute-100.png").subsample(3,3)
folder_icon = tk.PhotoImage(file="assets/images/icons8-music-folder-100.png").subsample(2,2)
folder_icon_small = tk.PhotoImage(file="assets/images/icons8-music-folder-small-50.png").subsample(2,2)
close_icon_small = tk.PhotoImage(file="assets/images/icons8-close-window-48.png").subsample(2,2)
app_logo_image = tk.PhotoImage(file="assets/images/icons8-musical-100.png")
# UI
playing_status = False
menubar1 = tk.Menu(root)
root.config(menu=menubar1)
fileMenu = tk.Menu(menubar1,tearoff=0,background=button_ui_bg_color,fg=text_color)
menubar1.add_cascade(label="File",menu=fileMenu)
fileMenu.add_command(label="Import from folder",command=thread_select_folder,image=folder_icon_small,compound=tk.LEFT)
fileMenu.add_separator()
fileMenu.add_command(label="Show library",command=show_library)
fileMenu.add_command(label="Hide library",command=hide_library)
fileMenu.add_separator()
fileMenu.add_command(label="Exit",command=close_window,image=close_icon_small,compound=tk.LEFT)
audio_Menu = tk.Menu(menubar1,tearoff=0,background=button_ui_bg_color,fg=text_color)
menubar1.add_cascade(label="Audio",menu=audio_Menu)
audio_Menu.add_command(label="Volume Up",command=thread_volume_up,image=high_volume_image,compound=tk.LEFT)
audio_Menu.add_command(label="Volume Down",command=thread_volume_down,image=low_volume_image,compound=tk.LEFT)
audio_Menu.add_command(label="Mute",command=thread_volume_mute,image=mute_image,compound=tk.LEFT)
# menu 'Player'
player_Menu = tk.Menu(menubar1,tearoff=0,background=button_ui_bg_color,fg=text_color)
menubar1.add_cascade(label="Themes",menu=player_Menu)
player_Menu.add_command(label=color_theme_names[0],command=lambda:change_player_theme(0))
player_Menu.add_command(label=color_theme_names[1],command=lambda :change_player_theme(1))
player_Menu.add_command(label=color_theme_names[2],command=lambda :change_player_theme(2))
player_Menu.add_command(label=color_theme_names[3],command=lambda :change_player_theme(3))
player_Menu.add_command(label=color_theme_names[4],command=lambda :change_player_theme(4))
player_Menu.add_command(label=color_theme_names[5],command=lambda :change_player_theme(5))
player_Menu.add_command(label=color_theme_names[6],command=lambda :change_player_theme(6))
player_Menu.add_command(label=color_theme_names[7],command=lambda :change_player_theme(7))
player_Menu.add_command(label=color_theme_names[8],command=lambda :change_player_theme(8))
player_Menu.add_command(label=color_theme_names[9],command=lambda :change_player_theme(9))
player_Menu.add_command(label=color_theme_names[10],command=lambda :change_player_theme(10))
player_Menu.add_command(label=color_theme_names[11],command=lambda :change_player_theme(11))
player_Menu.add_command(label=color_theme_names[12],command=lambda :change_player_theme(12))
player_Menu.add_command(label=color_theme_names[13],command=lambda :change_player_theme(13))
player_Menu.add_command(label=color_theme_names[14],command=lambda :change_player_theme(14))
player_Menu.add_command(label=color_theme_names[15],command=lambda :change_player_theme(15))
help_Menu = tk.Menu(menubar1,tearoff=0,background=button_ui_bg_color,fg=text_color)
menubar1.add_cascade(label="Help",menu=help_Menu)
help_Menu.add_command(label="About",command=thread_about)
frame1 = tk.Frame(root,bg=main_color)
frame1.pack()
mainFrame = tk.Frame(frame1,bg=main_color)
mainFrame.grid(row=0,column=0)
sideFrame = tk.Frame(frame1,bg=main_color)
sideFrame.grid(row=0,column=1)
music_image_label = tk.Label(mainFrame,image=music_art_image,bg=main_color,width=320,height=320)
music_image_label.pack(pady=17)
canvas_visualization = tk.Canvas(mainFrame,width=64,height=50)
canvas_visualization.pack()
random_line_1 = canvas_visualization.create_line(5, 35, 5, 50, width=5, fill=main_color)
random_line_2 = canvas_visualization.create_line(12, 15, 12, 50, width=5, fill=button_ui_bg_color)
random_line_3 = canvas_visualization.create_line(19, 5, 19, 50, width=5, fill=main_color)
random_line_4 = canvas_visualization.create_line(26, 25, 26, 50, width=5, fill=button_ui_bg_color)
random_line_5 = canvas_visualization.create_line(33, 15, 33, 50, width=5, fill=main_color)
random_line_6 = canvas_visualization.create_line(40, 45, 40, 50, width=5, fill=button_ui_bg_color)
random_line_7 = canvas_visualization.create_line(47, 35, 47, 50, width=5, fill=main_color)
random_line_8 = canvas_visualization.create_line(54, 5, 54, 50, width=5, fill=button_ui_bg_color)
random_line_9 = canvas_visualization.create_line(61, 15, 61, 50, width=5, fill=main_color)
audio_name_label = tk.Label(mainFrame,fg=text_color,bg=main_color)
audio_name_label.pack()
album_name_label = tk.Label(mainFrame,fg=text_color,bg=main_color)
album_name_label.pack()
artists_label = tk.Label(mainFrame,fg=text_color,bg=main_color)
artists_label.pack()
album_year_label = tk.Label(mainFrame,fg=text_color,bg=main_color)
album_year_label.pack()
duration_label = tk.Label(mainFrame,fg=text_color,bg=main_color)
duration_label.pack()
scale_var = tk.IntVar()
scale = tk.Scale(mainFrame,from_=0,to=50,orient=tk.HORIZONTAL,length=700,command=get_slider_value,variable=scale_var,
                 bg=main_color,fg=text_color,troughcolor=button_ui_bg_color,activebackground=main_color,bd=0,
                 state=tk.DISABLED, highlightthickness=0)
scale.pack()
# controls
controls_frame = tk.Frame(mainFrame,pady=15,padx=20,background=main_color)
controls_frame.pack()
open_folder_button = tk.Button(controls_frame,text="Select folder",command=thread_select_folder,bg=button_ui_bg_color,activebackground=button_ui_bg_color,fg="black",font=("Georgia",15),image=folder_icon,compound=tk.LEFT,padx=6)
open_folder_button.grid(row=0,column=0,padx=5)
shuffle_button = tk.Button(controls_frame,text="Shuffle OFF",command=thread_shuffle_song_playing_order,bg=button_ui_bg_color,activebackground=button_ui_bg_color,fg="black",font=("Georgia",15),image=shuffle_no_image)
shuffle_button.grid(row=0,column=1,padx=5)
previous_button = tk.Button(controls_frame,text="Previous",command=thread_previous_audio,activebackground=button_ui_bg_color,bg=button_ui_bg_color,fg="black",font=("Georgia",15),image=previous_image,compound=tk.LEFT)
previous_button.grid(row=0,column=2,padx=5)
play_button1 = tk.Button(controls_frame,text="Play",command=play_pause_resume,bg=button_ui_bg_color,activebackground=button_ui_bg_color,fg="black",font=("Georgia",15),image=play_icon,compound=tk.LEFT,padx=6,width=120)
play_button1.grid(row=0,column=3,padx=5)
next_button = tk.Button(controls_frame,text="Next",command=thread_next_audio,bg=button_ui_bg_color,activebackground=button_ui_bg_color,fg="black",font=("Georgia",15),image=next_image,compound=tk.LEFT,padx=6)
next_button.grid(row=0,column=4,padx=5)
loop_var = tk.IntVar()
loop_button1 = tk.Button(controls_frame,text="Loop OFF",width=150,bg=button_ui_bg_color,activebackground=button_ui_bg_color,fg="black",font=("Georgia",15),image=repeat_none_image,compound=tk.LEFT,padx=6,command=thread_repeat_loop)
loop_button1.grid(row=0,column=5,padx=5)
stop_button = tk.Button(controls_frame,text="Stop",command=stop_song,fg="black",bg=button_ui_bg_color,activebackground=button_ui_bg_color,font=("Georgia",15),image=stop_icon,compound=tk.LEFT,padx=6)
stop_button.grid(row=0,column=6,padx=5)
controls_frame2 = tk.Frame(mainFrame,background=main_color)
controls_frame2.pack(side=tk.RIGHT,padx=20)
volume_down_button = tk.Button(controls_frame2,text="-",bg=button_ui_bg_color,activebackground=button_ui_bg_color,fg="black",font=("Georgia",15),command=thread_volume_down,image=low_volume_image)
volume_down_button.grid(row=0,column=0)
canvas1 = tk.Canvas(controls_frame2,width=100,height=6)
canvas1.grid(row=0,column=1)
line1 = canvas1.create_line(5,5,50,5,fill=main_color,width=4)
volume_up_button = tk.Button(controls_frame2,text="+",bg=button_ui_bg_color,activebackground=button_ui_bg_color,fg="black",font=("Georgia",15),command=thread_volume_up,image=high_volume_image)
volume_up_button.grid(row=0,column=2)
volume_mute_button = tk.Button(controls_frame2,text="Mute",bg=button_ui_bg_color,activebackground=button_ui_bg_color,fg="black",font=("Georgia",15),command=thread_volume_mute,image=mute_image)
volume_mute_button.grid(row=0,column=3,padx=10)
volume_label = tk.Label(controls_frame2,text="0.5",padx=44)
# Side frame
songs_label=tk.Label(sideFrame,text="Songs",bg=main_color,fg=text_color,font=("Georgia",18))
songs_label.pack(pady=7)
sort_frame = tk.Frame(sideFrame,background=main_color)
sort_frame.pack()
btn_sort_by_album = tk.Button(sort_frame,text="Sort by Album",command=thread_sort_songs_list_album,bg=button_ui_bg_color,activebackground=button_ui_bg_color,fg=text_color,font=("Georgia",12))
btn_sort_by_album.grid(row=0,column=0)
btn_sort_by_atoz = tk.Button(sort_frame,text="Sort by A-Z",command=thread_sort_songs_list_atoz,bg=button_ui_bg_color,activebackground=button_ui_bg_color,fg=text_color,font=("Georgia",12))
btn_sort_by_atoz.grid(row=0,column=1,padx=5)
btn_sort_by_album_year = tk.Button(sort_frame,text="Sort by Album year",command=thread_sort_songs_list_by_album_year,bg=button_ui_bg_color,activebackground=button_ui_bg_color,fg=text_color,font=("Georgia",12))
btn_sort_by_album_year.grid(row=0,column=2)
yscrollbar = tk.Scrollbar(sideFrame)
yscrollbar.pack(side = tk.RIGHT, fill = tk.Y)
listbox1 = tk.Listbox(sideFrame,font=("Times New Roman",16),bg=main_color,height=24,width=35,fg=text_color,
                      yscrollcommand=yscrollbar.set,selectmode=tk.SINGLE,highlightthickness=1,highlightbackground=text_color)
listbox1.pack(fill=tk.BOTH,expand=True,padx=5)
yscrollbar.config(command = listbox1.yview)
listbox1.bind("<Double-1>",show_listbox)
last_selected_file = ""
song_at_top=""
player_queue = []
listbox_file_names = []
songs_dictionary = {}
loop_count = 0
song_pointer = 0
shuffle_status = False
shuffled_player_queue = []
clicked_from_listbox = False
running = False
last_slider_value = 0
running_status = False  # flag to monitor slider movement
prev_button_clicked = False
total_length_audio = 0
num = 0  # audio slider position
pygame.init()  # Initialise pygame MUST
mixer.music.set_volume(0.5)
# key event
root.bind("<space>",play_button_key_event)
# Tooltips
Hovertip(stop_button,"Stop player")
Hovertip(shuffle_button,"Shuffle Off")
Hovertip(volume_down_button,"Decrease volume")
Hovertip(volume_up_button,"Increase volume")
Hovertip(volume_mute_button,"Mute")
# Setting the icon in title bar
root.iconphoto(True,app_logo_image)
root.mainloop()