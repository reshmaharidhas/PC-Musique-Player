import io
import sys
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


class Player:
    def __init__(self):
        self.root = tk.Tk()
        self.root.title("PC Musique Player")
        self.root.geometry("1450x750")
        self.root.minsize(width=1450,height=750)
        self.root.resizable(True,True)
        # List of colors for varied themes
        self.color_theme_names = ["French Rouge","French Bleu","French Vert","French Reef","Jalapeno Red","Dutch Red",
                             "Dutch Sunflower","Merchant Marine Blue","Dutch Green","Dutch Purple","Lavender",
                             "Dutch Purple Dark","Gloomy purple","Hibiscus Orange","NYC Taxi","Midnight Blue","Black",
                                  "Spanish Red","Spooky purple","Russian Rose","Watermelon","Sailor","Green Apple"]
        self.color_themes_main_color = ["#eb2f06","#1e3799","#78e08f","#079992","#b71540","#EA2027","#FFC312","#0652DD",
                                        "#009432","#5758BB","#D980FA","#6F1E51","#8854d0","#fa8231","#f7b731","#2c3e50",
                                        "#000000","#ff5252","#2c2c54","#c44569","#ff4757","#341f97","#6ab04c"]
        self.color_themes_button_ui_bg_color = ["#f3826a","#4a69bd","#b8e994","#38ada9","#db8aa0","#EE5A24","#F79F1F",
                                                "#12CBC4","#A3CB38","#9980FA","#FDA7DF","#B53471","#a55eea","#fd9644",
                                                "#4d4d4d","white","#36454F","#ff793f","#40407a","#cf6a87","#ff6b81",
                                                "#FF2E51","#badc58"]
        self.color_themes_text_color = ["white","white","black","#000000","white","#FFFFFF","black","white","white",
                                        "#FFFFFF","black","white","black","black","black","white","white","#000000",
                                        "#FFFFFF","#000000","#000000","#FFFFFF","#000000"]
        self.current_audio_level = 50
        # Setting the color theme initially in GUI
        self.main_color = self.color_themes_main_color[11]
        self.button_ui_bg_color = self.color_themes_button_ui_bg_color[11]
        self.text_color = self.color_themes_text_color[11]
        self.root.config(bg=self.main_color)
        self.root.protocol("WM_DELETE_WINDOW",self.close_window)
        # PhotoImage variables
        self.music_art_image = tk.PhotoImage(file="assets/images/record.png")
        self.music_icon = tk.PhotoImage(file="assets/images/icons8-music-96.png").subsample(2,2)
        self.play_icon = tk.PhotoImage(file="assets/images/icons8-circled-play-100.png").subsample(2,2)
        self.pause_icon = tk.PhotoImage(file="assets/images/icons8-pause-button-100.png").subsample(2,2)
        self.resume_icon = tk.PhotoImage(file="assets/images/icons8-resume-button-100.png").subsample(2,2)
        self.stop_icon = tk.PhotoImage(file="assets/images/icons8-stop-circled-100.png").subsample(2,2)
        self.next_image = tk.PhotoImage(file="assets/images/icons8-next-100.png").subsample(2,2)
        self.previous_image = tk.PhotoImage(file="assets/images/icons8-previous-100.png").subsample(2,2)
        self.repeat_one_image = tk.PhotoImage(file="assets/images/icons8-repeat-one-100.png").subsample(2,2)
        self.repeat_no_image = tk.PhotoImage(file="assets/images/icons8-repeat-no-100.png").subsample(2,2)
        self.repeat_none_image = tk.PhotoImage(file="assets/images/icons8-repeat-none-100.png").subsample(2,2)
        self.shuffle_image = tk.PhotoImage(file="assets/images/icons8-shuffle-100.png").subsample(2,2)
        self.shuffle_no_image = tk.PhotoImage(file="assets/images/icons8-no-shuffle-100.png").subsample(2,2)
        self.low_volume_image = tk.PhotoImage(file="assets/images/icons8-volume-down-100-black.png").subsample(3,3)
        self.high_volume_image = tk.PhotoImage(file="assets/images/icons8-volumeup-100-black.png").subsample(3,3)
        self.mute_image = tk.PhotoImage(file="assets/images/icons8-volume-mute-100.png").subsample(3,3)
        self.mini_player_image = tk.PhotoImage(file="assets/images/collapse-arrows.png").subsample(3,3)
        self.open_player_wide_image = tk.PhotoImage(file="assets/images/enlarge_player.png").subsample(3,3)
        self.open_file_icon = tk.PhotoImage(file="assets/images/open_file_small_icon_50.png").subsample(3,3)
        self.folder_icon = tk.PhotoImage(file="assets/images/icons8-music-folder-100.png").subsample(2,2)
        self.folder_icon_small = tk.PhotoImage(file="assets/images/icons8-music-folder-small-50.png").subsample(2,2)
        self.close_icon_small = tk.PhotoImage(file="assets/images/icons8-close-window-48.png").subsample(2,2)
        self.app_logo_image = tk.PhotoImage(file="assets/images/icons8-musical-100.png")
        # UI
        self.playing_status = False
        self.menubar1 = tk.Menu(self.root)
        self.root.config(menu=self.menubar1)
        self.fileMenu = tk.Menu(self.menubar1,tearoff=0,background=self.button_ui_bg_color,fg=self.text_color)
        self.menubar1.add_cascade(label="File",menu=self.fileMenu)
        self.fileMenu.add_command(label="Open file",command=self.select_single_file,compound=tk.LEFT,image=self.open_file_icon)
        self.fileMenu.add_command(label="Import from folder",command=self.thread_select_folder,image=self.folder_icon_small,compound=tk.LEFT)
        self.fileMenu.add_separator()
        self.fileMenu.add_command(label="Show library",command=self.show_library)
        self.fileMenu.add_command(label="Hide library",command=self.hide_library)
        self.fileMenu.add_separator()
        self.fileMenu.add_command(label="Exit",command=self.close_window,image=self.close_icon_small,compound=tk.LEFT)
        self.audio_Menu = tk.Menu(self.menubar1,tearoff=0,background=self.button_ui_bg_color,fg=self.text_color)
        self.menubar1.add_cascade(label="Audio",menu=self.audio_Menu)
        self.audio_Menu.add_command(label="Volume Up",command=self.thread_volume_up,image=self.high_volume_image,compound=tk.LEFT)
        self.audio_Menu.add_command(label="Volume Down",command=self.thread_volume_down,image=self.low_volume_image,compound=tk.LEFT)
        self.audio_Menu.add_command(label="Mute",command=self.thread_volume_mute,image=self.mute_image,compound=tk.LEFT)
        # menu 'Player'
        self.player_Menu = tk.Menu(self.menubar1,tearoff=0,background=self.button_ui_bg_color,fg=self.text_color)
        self.menubar1.add_cascade(label="Themes",menu=self.player_Menu)
        self.player_Menu.add_command(label=self.color_theme_names[0],command=lambda:self.change_player_theme(0))
        self.player_Menu.add_command(label=self.color_theme_names[1],command=lambda :self.change_player_theme(1))
        self.player_Menu.add_command(label=self.color_theme_names[2],command=lambda :self.change_player_theme(2))
        self.player_Menu.add_command(label=self.color_theme_names[3],command=lambda :self.change_player_theme(3))
        self.player_Menu.add_command(label=self.color_theme_names[4],command=lambda :self.change_player_theme(4))
        self.player_Menu.add_command(label=self.color_theme_names[5],command=lambda :self.change_player_theme(5))
        self.player_Menu.add_command(label=self.color_theme_names[6],command=lambda :self.change_player_theme(6))
        self.player_Menu.add_command(label=self.color_theme_names[7],command=lambda :self.change_player_theme(7))
        self.player_Menu.add_command(label=self.color_theme_names[8],command=lambda :self.change_player_theme(8))
        self.player_Menu.add_command(label=self.color_theme_names[9],command=lambda :self.change_player_theme(9))
        self.player_Menu.add_command(label=self.color_theme_names[10],command=lambda :self.change_player_theme(10))
        self.player_Menu.add_command(label=self.color_theme_names[11],command=lambda :self.change_player_theme(11))
        self.player_Menu.add_command(label=self.color_theme_names[12],command=lambda :self.change_player_theme(12))
        self.player_Menu.add_command(label=self.color_theme_names[13],command=lambda :self.change_player_theme(13))
        self.player_Menu.add_command(label=self.color_theme_names[14],command=lambda :self.change_player_theme(14))
        self.player_Menu.add_command(label=self.color_theme_names[15],command=lambda :self.change_player_theme(15))
        self.player_Menu.add_command(label=self.color_theme_names[16], command=lambda: self.change_player_theme(16))
        self.player_Menu.add_command(label=self.color_theme_names[17], command=lambda: self.change_player_theme(17))
        self.player_Menu.add_command(label=self.color_theme_names[18], command=lambda: self.change_player_theme(18))
        self.player_Menu.add_command(label=self.color_theme_names[19], command=lambda: self.change_player_theme(19))
        self.player_Menu.add_command(label=self.color_theme_names[20], command=lambda: self.change_player_theme(20))
        self.player_Menu.add_command(label=self.color_theme_names[21], command=lambda: self.change_player_theme(21))
        self.player_Menu.add_command(label=self.color_theme_names[22], command=lambda: self.change_player_theme(22))

        self.help_Menu = tk.Menu(self.menubar1,tearoff=0,background=self.button_ui_bg_color,fg=self.text_color)
        self.menubar1.add_cascade(label="Help",menu=self.help_Menu)
        self.help_Menu.add_command(label="About",command=self.thread_about)
        self.frame1 = tk.Frame(self.root,bg=self.main_color)
        self.frame1.pack()
        self.mainFrame = tk.Frame(self.frame1,bg=self.main_color)
        self.mainFrame.grid(row=0,column=0)
        self.sideFrame = tk.Frame(self.frame1,bg=self.main_color,padx=100)
        self.sideFrame.grid(row=0,column=1)
        self.music_image_label = tk.Label(self.mainFrame,image=self.music_art_image,bg=self.main_color,width=320,height=320)
        self.music_image_label.pack(pady=17)
        self.canvas_visualization = tk.Canvas(self.mainFrame,width=64,height=50)
        self.canvas_visualization.pack()
        self.random_line_1 = self.canvas_visualization.create_line(5, 35, 5, 50, width=5, fill=self.main_color)
        self.random_line_2 = self.canvas_visualization.create_line(12, 15, 12, 50, width=5, fill=self.button_ui_bg_color)
        self.random_line_3 = self.canvas_visualization.create_line(19, 5, 19, 50, width=5, fill=self.main_color)
        self.random_line_4 = self.canvas_visualization.create_line(26, 25, 26, 50, width=5, fill=self.button_ui_bg_color)
        self.random_line_5 = self.canvas_visualization.create_line(33, 15, 33, 50, width=5, fill=self.main_color)
        self.random_line_6 = self.canvas_visualization.create_line(40, 45, 40, 50, width=5, fill=self.button_ui_bg_color)
        self.random_line_7 = self.canvas_visualization.create_line(47, 35, 47, 50, width=5, fill=self.main_color)
        self.random_line_8 = self.canvas_visualization.create_line(54, 5, 54, 50, width=5, fill=self.button_ui_bg_color)
        self.random_line_9 = self.canvas_visualization.create_line(61, 15, 61, 50, width=5, fill=self.main_color)
        self.audio_name_label = tk.Label(self.mainFrame,fg=self.text_color,bg=self.main_color)
        self.audio_name_label.pack(pady=5)
        self.album_name_label = tk.Label(self.mainFrame,fg=self.text_color,bg=self.main_color)
        self.album_name_label.pack()
        self.artists_label = tk.Label(self.mainFrame,fg=self.text_color,bg=self.main_color)
        self.artists_label.pack()
        self.album_year_label = tk.Label(self.mainFrame,fg=self.text_color,bg=self.main_color)
        self.album_year_label.pack()
        self.duration_label = tk.Label(self.mainFrame,fg=self.text_color,bg=self.main_color)
        self.duration_label.pack()
        self.scale_var = tk.IntVar()
        self.scale = tk.Scale(self.mainFrame,from_=0,to=50,orient=tk.HORIZONTAL,length=600,command=self.get_slider_value,variable=self.scale_var,
                         bg=self.main_color,fg=self.text_color,troughcolor=self.button_ui_bg_color,activebackground=self.main_color,bd=0,
                         state=tk.DISABLED, highlightthickness=0)
        self.scale.pack()
        # controls
        self.controls_frame = tk.Frame(self.mainFrame,pady=15,padx=20,background=self.main_color)
        self.controls_frame.pack()
        self.open_folder_button = tk.Button(self.controls_frame,command=self.thread_select_folder,bg=self.button_ui_bg_color,activebackground=self.button_ui_bg_color,fg="black",font=("Georgia",15),image=self.folder_icon,compound=tk.LEFT,padx=6)
        self.open_folder_button.grid(row=0,column=0,padx=15)
        self.shuffle_button = tk.Button(self.controls_frame,text="Shuffle OFF",command=self.thread_shuffle_song_playing_order,bg=self.button_ui_bg_color,activebackground=self.button_ui_bg_color,fg="black",font=("Georgia",15),image=self.shuffle_no_image)
        self.shuffle_button.grid(row=0,column=1,padx=15)
        self.previous_button = tk.Button(self.controls_frame,command=self.thread_previous_audio,activebackground=self.button_ui_bg_color,bg=self.button_ui_bg_color,fg="black",font=("Georgia",15),image=self.previous_image,compound=tk.LEFT)
        self.previous_button.grid(row=0,column=2,padx=15)
        self.play_button_text_var = tk.StringVar(value="Play")
        self.play_button1 = tk.Button(self.controls_frame,command=self.play_pause_resume,bg=self.button_ui_bg_color,activebackground=self.button_ui_bg_color,fg="black",font=("Georgia",15),image=self.play_icon,compound=tk.LEFT,padx=6)
        self.play_button1.grid(row=0,column=3,padx=15)
        self.next_button = tk.Button(self.controls_frame,command=self.thread_next_audio,bg=self.button_ui_bg_color,activebackground=self.button_ui_bg_color,fg="black",font=("Georgia",15),image=self.next_image,compound=tk.LEFT,padx=6)
        self.next_button.grid(row=0,column=4,padx=15)
        # Variable to store integer value for loop modes.
        self.loop_var = tk.IntVar()
        # Repeat or Loop button.
        self.loop_button1 = tk.Button(self.controls_frame,bg=self.button_ui_bg_color,activebackground=self.button_ui_bg_color,fg="black",font=("Georgia",15),image=self.repeat_none_image,compound=tk.LEFT,padx=6,command=self.thread_repeat_loop)
        self.loop_button1.grid(row=0,column=5,padx=15)
        # Button to stop the player from playing.
        self.stop_button = tk.Button(self.controls_frame,command=self.stop_song,fg="black",bg=self.button_ui_bg_color,activebackground=self.button_ui_bg_color,font=("Georgia",15),image=self.stop_icon,compound=tk.LEFT,padx=6)
        self.stop_button.grid(row=0,column=6,padx=15)
        # Frame to hold volume control buttons.
        self.controls_frame2 = tk.Frame(self.mainFrame,background=self.main_color)
        self.controls_frame2.pack(side=tk.RIGHT,padx=20,pady=5)
        # Button to increase the volume.
        self.volume_down_button = tk.Button(self.controls_frame2,text="-",bg=self.button_ui_bg_color,activebackground=self.button_ui_bg_color,fg="black",font=("Georgia",15),command=self.thread_volume_down,image=self.low_volume_image)
        self.volume_down_button.grid(row=0,column=0)
        # Canvas hold the volume bar.
        self.canvas1 = tk.Canvas(self.controls_frame2,width=100,height=6)
        self.canvas1.grid(row=0,column=1)
        # Volume bar is created using a line.
        self.line1 = self.canvas1.create_line(5,5,50,5,fill=self.main_color,width=4)
        # Button to increase volume.
        self.volume_up_button = tk.Button(self.controls_frame2,text="+",bg=self.button_ui_bg_color,activebackground=self.button_ui_bg_color,fg="black",font=("Georgia",15),command=self.thread_volume_up,image=self.high_volume_image)
        self.volume_up_button.grid(row=0,column=2)
        # Button to mute volume in mixer directly.
        self.volume_mute_button = tk.Button(self.controls_frame2,text="Mute",bg=self.button_ui_bg_color,activebackground=self.button_ui_bg_color,fg="black",font=("Georgia",15),command=self.thread_volume_mute,image=self.mute_image)
        self.volume_mute_button.grid(row=0,column=3,padx=10)
        # Open mini player button
        self.mini_max_player_button = tk.Button(self.controls_frame2,command=self.change_to_smallplayer,image=self.mini_player_image,bg=self.button_ui_bg_color,activebackground=self.button_ui_bg_color)
        self.mini_max_player_button.grid(row=0,column=4)
        # Side frame
        self.songs_label=tk.Label(self.sideFrame,text="Songs",bg=self.main_color,fg=self.text_color,font=("Georgia",18))
        self.songs_label.pack(pady=7)
        self.sort_frame = tk.Frame(self.sideFrame,background=self.main_color)
        self.sort_frame.pack()
        self.btn_sort_by_album = tk.Button(self.sort_frame,text="Sort by Album",command=self.thread_sort_songs_list_album,bg=self.button_ui_bg_color,activebackground=self.button_ui_bg_color,fg=self.text_color,font=("Georgia",12))
        self.btn_sort_by_album.grid(row=0,column=0)
        self.btn_sort_by_atoz = tk.Button(self.sort_frame,text="Sort by A-Z",command=self.thread_sort_songs_list_atoz,bg=self.button_ui_bg_color,activebackground=self.button_ui_bg_color,fg=self.text_color,font=("Georgia",12))
        self.btn_sort_by_atoz.grid(row=0,column=1,padx=5)
        self.btn_sort_by_album_year = tk.Button(self.sort_frame,text="Sort by Album year",command=self.thread_sort_songs_list_by_album_year,bg=self.button_ui_bg_color,activebackground=self.button_ui_bg_color,fg=self.text_color,font=("Georgia",12))
        self.btn_sort_by_album_year.grid(row=0,column=2)
        self.yscrollbar = tk.Scrollbar(self.sideFrame)
        self.yscrollbar.pack(side = tk.RIGHT, fill = tk.Y)
        self.listbox1 = tk.Listbox(self.sideFrame,font=("Times New Roman",16),bg=self.main_color,height=24,width=45,fg=self.text_color,
                              yscrollcommand=self.yscrollbar.set,selectmode=tk.SINGLE,highlightthickness=1,highlightbackground=self.text_color)
        self.listbox1.pack(fill=tk.BOTH,expand=True,padx=5)
        self.yscrollbar.config(command = self.listbox1.yview)
        self.listbox1.bind("<Double-1>",self.show_listbox)
        self.last_selected_file = ""
        self.song_at_top=""
        self.player_queue = []
        self.listbox_file_names = []
        self.songs_dictionary = {}
        self.loop_count = 0
        self.song_pointer = 0
        self.current_audio_total_length = 0
        self.shuffle_status = False
        self.shuffled_player_queue = []
        self.clicked_from_listbox = False
        self.running = False
        self.last_slider_value = 0
        self.running_status = False  ##
        self.prev_button_clicked = False
        self.total_length_audio = 0
        self.num = 0  # audio slider position
        pygame.init()  # Initialise pygame MUST
        mixer.music.set_volume(0.5)
        # key event
        self.root.bind("<space>",self.play_button_key_event)
        # Tooltips
        Hovertip(self.open_folder_button,"Open from folder")
        Hovertip(self.stop_button,"Stop player")
        Hovertip(self.shuffle_button,"Shuffle Off")
        Hovertip(self.volume_down_button,"Decrease volume")
        Hovertip(self.volume_up_button,"Increase volume")
        Hovertip(self.volume_mute_button,"Mute")
        # Setting the icon in title bar
        self.root.iconphoto(True,self.app_logo_image)
        self.root.mainloop()

    def play_pause_resume(self):
        global player_queue
        if len(self.player_queue) == 0:
            messagebox.showerror("No song selected", "Open & select any audio file from your computer")
        else:
            # Play the last selected file from beginning
            self.thread_play_song()

    def play_song(self):
        global song_at_top, playing_status, player_queue, loop_count, song_pointer, running, last_slider_value, prev_button_clicked
        global running_status, total_length_audio, num, shuffled_player_queue
        self.playing_status = True
        mixer.init()
        if len(self.player_queue) >= 1 and self.song_pointer < len(self.player_queue):
            if (self.clicked_from_listbox == True and self.shuffle_status == True) or self.shuffle_status == False or (
                    self.clicked_from_listbox == True and self.shuffle_status == False):
                self.song_at_top = self.player_queue[self.song_pointer]
            #elif self.shuffle_status == True:
            else:
                self.song_at_top = self.shuffled_player_queue[self.song_pointer]
        self.scale.config(sliderlength=20)
        self.last_slider_value = 0
        # Using try catch statements to avoid playing any corrupted file. It loads the file.
        # If it is corrupted, the 'except' part is run.
        try:
            mixer.music.load(self.song_at_top)
            mixer.music.play(start=self.last_slider_value)
            self.running_status = True
            # Reset the slider in scale to 0 as the audio file has started to play from the beginning now.
            self.show_album_art(self.song_at_top)
            self.loop_count = self.loop_var.get()
            # Extracting metadata of audio file using mutagen.
            filestats = MP3(self.song_at_top)
            self.audio_name_label.config(text="Now Playing: " + self.song_at_top[self.song_at_top.rfind("/") + 1:],
                                    font=("Times New Roman", 15, "italic"))
            audio_album = filestats.get("TALB")
            singers = filestats.get("TPE1")
            year = filestats.get("TDRC")
            self.album_name_label.config(text=f"Album: {audio_album}")
            self.artists_label.config(text=f"Artists: {singers}")
            self.album_year_label.config(text=f"Album year: {year}")
            duration = divmod(filestats.info.length, 60)
            minutes = int(duration[0])
            seconds_ = int(duration[1])
            self.duration_label.config(text="Duration: " + str(minutes) + ":" + str(seconds_))
            end_duration = (int(duration[0]) * 60) + int(duration[1])
            self.scale.config(from_=0, to=filestats.info.length)
            self.current_audio_total_length = filestats.info.length
            # Change play button to pause button
            self.play_button_text_var.set("Pause")
            self.play_button1.config(command=self.pause_song, image=self.pause_icon, compound=tk.LEFT)
            id = pygame.USEREVENT
            mixer.music.set_endevent(id)
            # Initializing 'num' to 0 to display with scale as number.
            self.num = 0
            running = True
            while running:
                for event in pygame.event.get():
                    if event.type==pygame.QUIT:
                        pygame.quit()
                        exit()
                    if self.running_status==False:
                        running=False
                    if running is False:  # Stopping the mixer from playing, when any external way is used to force stop.
                        running = False
                    if event.type == id:
                        # Song file playing completed fully on its own.
                        running = False
                        self.running_status = False
                    self.root.update()
                self.root.update()
                if running == False:
                    if self.loop_count == -1:  # Playing the current audio file repeatedly. Loop one audio file.
                        self.thread_play_song()
                    elif self.loop_count == -2:  # Close GUI
                        break
                    elif self.loop_count == 1:  # Continuous playing
                        # Playing Next song in listbox.
                        self.play_button_text_var.set("Play")
                        self.play_button1.config(command=self.play_song, image=self.play_icon, compound=tk.LEFT)
                        self.next_audio()
                    elif self.loop_count == 0:  # When an audio file is played fully and ends on its own.
                        # Change the slider appearance as 0 to avoid seeking, because if it is moved, the song plays, but slider does not move.
                        self.scale.config(sliderlength = 0)
                        self.play_button_text_var.set("Play")
                        self.play_button1.config(command=self.play_song, image=self.play_icon, compound=tk.LEFT)
                        # Now the audio is played fully. Click play to play again!")
                        self.listbox1.selection_clear(0, tk.END)
                        self.play_button_text_var.set("Play")
                        self.play_button1.config(command=self.play_song, image=self.play_icon, compound=tk.LEFT)
                        running = False
                        break
                    break
                self.root.update()
                self.controls_frame.update()
                self.thread_show_visualization()
                # Slider moving
                if self.play_button_text_var.get()=="Pause":
                    self.num += 1
                    self.thread_move_slider(self.num)
                # wait for 1 second.
                sleep(1)
                self.root.update()
                # If loop_count==-2, break out of 'while loop'.
                if self.loop_count==-2:
                    break
            # Broke out
        except pygame.error as err:
            messagebox.showerror("Corrupted file", "There is some error in this audio. Cannot play!")
            # ERROR CORRUPTED FILE, incrementing song_pointer.
            if self.prev_button_clicked == True:
                self.previous_audio()
                self.prev_button_clicked = False
            else:
                self.next_audio()

    def thread_play_song(self):
        thread_var_play_song = Thread(target=self.play_song())
        thread_var_play_song.start()
    def make_slider_move_every_1_second(self):
        self.looping = True
        while self.looping:
            if self.play_button_text_var.get() == "Pause":
                self.num += 1
                self.thread_move_slider(self.num)
            sleep(1)
            self.root.update()
            if self.scale.get()==self.current_audio_total_length:
                self.looping = False
                break
            if self.looping==False:
                break
    def thread_make_slider_move_every_1_second(self):
        self.thread_var = Thread(target=self.make_slider_move_every_1_second())
        self.thread_var.start()

    def select_single_file(self):
        self.song_at_top = filedialog.askopenfilename(filetypes=[("MP3 files", ".mp3")])
        self.play_single_audio()
    def play_single_audio(self):
        global song_at_top, playing_status, player_queue, loop_count, song_pointer, running, last_slider_value, prev_button_clicked
        global running_status, total_length_audio, num, shuffled_player_queue
        self.playing_status = True
        mixer.init()
        if len(self.song_at_top)>0:
            self.last_slider_value = 0
            # Using try catch statements to avoid playing any corrupted file. It loads the file.
            # If it is corrupted, the 'except' part is run.
            try:
                mixer.music.load(self.song_at_top)
                self.scale.config(state=tk.NORMAL)
                self.scale.bind("<ButtonRelease-1>", self.thread_set_slider_position)
                mixer.music.play(start=self.last_slider_value)
                self.running_status = True
                # Reset the slider in scale to 0 as the audio file has started to play from the beginning now.
                self.scale.config(sliderlength=20)
                self.scale.set(0)
                self.show_album_art(self.song_at_top)
                self.loop_count = self.loop_var.get()
                # Extracting metadata of audio file using mutagen.
                filestats = MP3(self.song_at_top)
                self.audio_name_label.config(text="Now Playing: " + self.song_at_top[self.song_at_top.rfind("/") + 1:],
                                        font=("Times New Roman", 15, "italic"))
                audio_album = filestats.get("TALB")
                singers = filestats.get("TPE1")
                year = filestats.get("TDRC")
                self.album_name_label.config(text=f"Album: {audio_album}")
                self.artists_label.config(text=f"Artists: {singers}")
                self.album_year_label.config(text=f"Album year: {year}")
                duration = divmod(filestats.info.length, 60)
                minutes = int(duration[0])
                seconds_ = int(duration[1])
                self.duration_label.config(text="Duration: " + str(minutes) + ":" + str(seconds_))
                end_duration = (int(duration[0]) * 60) + int(duration[1])
                self.scale.config(from_=0, to=filestats.info.length)
                # Change play button to pause button
                self.play_button_text_var.set("Pause")
                self.play_button1.config(command=self.pause_song, image=self.pause_icon, compound=tk.LEFT)
                id = pygame.USEREVENT
                mixer.music.set_endevent(id)
                # Initializing 'num' to 0 to display with scale as number.
                self.num = 0
                running = True
                while running:
                    for event in pygame.event.get():
                        if event.type==pygame.QUIT:
                            pygame.quit()
                            exit()
                        if self.running_status==False:
                            running=False
                        if running is False:  # Stopping the mixer from playing, when any external way is used to force stop.
                            running = False
                        if event.type == id:
                            # Song file playing completed fully on its own.
                            running = False
                            self.running_status = False
                        self.root.update()
                    self.root.update()
                    if running == False:
                        if self.loop_count == -1:  # Playing the current audio file repeatedly. Loop one audio file.
                            self.play_single_audio()
                        elif self.loop_count == -2:  # Close GUI
                            break
                        elif self.loop_count == 0 or self.loop_count == 1:  # When an audio file is played fully and ends on its own.
                            self.scale.config(sliderlength=0)
                            self.play_button_text_var.set("Play")
                            self.play_button1.config(command=self.play_song, image=self.play_icon, compound=tk.LEFT)
                            # Now the audio is played fully. Click play to play again!")
                            self.listbox1.selection_clear(0, tk.END)
                            self.play_button_text_var.set("Play")
                            self.play_button1.config(command=self.play_song, image=self.play_icon, compound=tk.LEFT)
                            running = False
                            break
                        break
                    self.root.update()
                    self.controls_frame.update()
                    self.thread_show_visualization()
                    # Slider moving
                    if self.play_button_text_var.get()=="Pause":
                        self.num += 1
                        self.thread_move_slider(self.num)
                    # wait for 1 second.
                    sleep(1)
                    self.root.update()
                    # If loop_count==-2, break out of 'while loop'.
                    if self.loop_count == -2:
                        break
                # Broke out
            except pygame.error as err:
                messagebox.showerror("Corrupted file", "There is some error in this audio. Cannot play!")
                # ERROR CORRUPTED FILE, incrementing song_pointer.

    def move_slider(self,num):
        self.scale.set(num)
    def thread_move_slider(self,num):
        thread_var = Thread(target=self.move_slider(num))
        thread_var.start()

    # Function to run when the slider on scale is moved and released somewhere in the scale.
    def set_slider_position(self,event):
        global num
        self.scale.set(self.scale.get())
        self.play_button_text_var.set("Pause")
        self.play_button1.config(command=self.pause_song, image=self.pause_icon, compound=tk.LEFT)
        self.num = self.scale.get()
        mixer.music.play(start=self.scale.get())
        #self.thread_make_slider_move_every_1_second()

    def thread_set_slider_position(self,event):
        thread_var = Thread(target=self.set_slider_position(event))
        thread_var.start()

    # Function to pause the song
    def pause_song(self):
        global playing_status
        if mixer.music.get_busy():
            self.playing_status = False
            mixer.music.pause()
            self.play_button_text_var.set("Resume")
            self.play_button1.config(command=self.resume_song, image=self.resume_icon, compound=tk.LEFT)

    # Function to resume the song playing
    def resume_song(self):
        global playing_status
        self.playing_status = True
        if mixer.music.get_busy() == False:
            self.play_button_text_var.set("Pause")
            self.play_button1.config(command=self.pause_song, image=self.pause_icon, compound=tk.LEFT)
            mixer.music.unpause()

    def stop_song(self):
        global loop_count, running_status
        mixer.init()
        mixer.music.stop()
        self.loop_count = -2  # Change this to 0 if possible. Because i assigned -2 for closing GUI only.
        # Change 'play_button1' text to 'Play'.
        self.play_button_text_var.set("Play")
        self.play_button1.config(command=self.play_song, image=self.play_icon, compound=tk.LEFT)
        self.running_status = False
        self.root.update()
        self.loop_count = 0
        self.loop_button1.config(image=self.repeat_none_image, compound=tk.LEFT)
        self.loop_var.set(0)

    def repeat_loop(self):
        global loop_count
        if self.loop_count == 0:  # Now 'Loop OFF'. Changing it to 'Loop single audio ON'.
            self.loop_count = -1
            self.loop_button1.config(image=self.repeat_one_image, compound=tk.LEFT)
            self.loop_var.set(-1)
        elif self.loop_count == -1:  # Now 'Loop single audio ON'. Changing it to 'Loop All'.
            self.loop_count = 1
            self.loop_button1.config(image=self.repeat_no_image, compound=tk.LEFT)
            self.loop_var.set(1)
        elif self.loop_count == 1:  # Now 'Loop All'. Changing it to 'Loop OFF'.
            self.loop_count = 0
            self.loop_button1.config(image=self.repeat_none_image, compound=tk.LEFT)
            self.loop_var.set(0)
        elif self.loop_count == -2:  # Stopped player
            self.loop_count = 0
            self.loop_button1.config(image=self.repeat_none_image, compound=tk.LEFT)
            self.loop_var.set(0)

    def thread_repeat_loop(self):
        thread_repeat_loop_var = Thread(target=self.repeat_loop())
        thread_repeat_loop_var.start()

    def next_audio(self):
        global song_pointer, prev_button_clicked, clicked_from_listbox
        self.clicked_from_listbox = False
        if len(self.player_queue) > 0:
            self.prev_button_clicked = False
            if self.song_pointer == len(self.player_queue) - 1:
                # No more songs to play!
                pass
            else:
                # self.stop_song()
                self.song_pointer += 1
                self.thread_play_song()

    def thread_next_audio(self):
        thread_next_audio_var = Thread(target=self.next_audio())
        thread_next_audio_var.start()

    def previous_audio(self):
        global song_pointer, prev_button_clicked, clicked_from_listbox
        self.clicked_from_listbox = False
        if len(self.player_queue) > 0:
            if self.song_pointer == 0:
                # No more songs to play!
                pass
            else:
                self.song_pointer -= 1
                self.prev_button_clicked = True
                self.thread_play_song()

    def thread_previous_audio(self):
        thread_prev_audio_var = Thread(target=self.previous_audio())
        thread_prev_audio_var.start()

    def close_window(self):
        global loop_count
        self.loop_count = -2
        self.stop_song()
        self.root.update()
        sys.exit()

    def play_button_key_event(self,event):
        if self.play_button_text_var.get() == "Pause":
            self.pause_song()
        elif self.play_button_text_var.get() == "Resume":
            self.resume_song()
        elif self.play_button_text_var.get() == "Play":
            self.play_pause_resume()

    def volume_up(self):
        global canvas1, line1
        if mixer.music.get_volume() < 1.0:
            mixer.music.set_volume(mixer.music.get_volume() + 0.1)
            self.current_audio_level = float(str(mixer.music.get_volume())[0:3]) * 100
            self.canvas1.delete('all')
            self.line1 = self.canvas1.create_line(5, 5, self.current_audio_level, 5, fill=self.main_color, width=4)

    def thread_volume_up(self):
        thread_volume_up_var = Thread(target=self.volume_up())
        thread_volume_up_var.start()

    def volume_down(self):
        global canvas1, line1
        if mixer.music.get_volume() > 0.1:
            mixer.music.set_volume(mixer.music.get_volume() - 0.1)
            self.current_audio_level = float(str(mixer.music.get_volume())[0:3]) * 100
            self.canvas1.delete('all')
            self.line1 = self.canvas1.create_line(5, 5, self.current_audio_level, 5, fill=self.main_color, width=4)

    def thread_volume_down(self):
        thread_volume_down_var = Thread(target=self.volume_down())
        thread_volume_down_var.start()

    def volume_mute(self):
        global canvas1, line1
        mixer.music.set_volume(0.0)
        self.canvas1.delete('all')
        self.line1 = self.canvas1.create_line(5, 5, 5, 5, fill=self.main_color)

    def thread_volume_mute(self):
        thread_volume_mute_var = Thread(target=self.volume_mute())
        thread_volume_mute_var.start()

    def select_folder(self):
        global player_queue, song_pointer, songs_dictionary, shuffled_player_queue
        selected_folder = filedialog.askdirectory()
        if len(selected_folder) > 0:
            self.listbox1.delete(0, tk.END)
            self.play_button1.config(state=tk.DISABLED)
            self.next_button.config(state=tk.DISABLED)
            self.previous_button.config(state=tk.DISABLED)
            # Change appearance of the buttons above listbox.
            self.btn_sort_by_album.config(relief=tk.RAISED, bd=6)
            self.btn_sort_by_atoz.config(relief=tk.RAISED, bd=2)
            self.btn_sort_by_album_year.config(relief=tk.RAISED, bd=2)
            self.player_queue = []  # CLEAR THIS. UNCOMMENT THIS
            self.songs_dictionary = {}  # Dictionary to hold filename as key and array of file path 'root' as values.
            for (root, dirs, files) in os.walk(selected_folder):
                if len(files) > 0:
                    for file_in_folder in files:
                        if file_in_folder[-4:] == ".mp3":
                            if file_in_folder not in self.songs_dictionary:
                                self.songs_dictionary.update({file_in_folder: [root]})
                            else:
                                arr = self.songs_dictionary.get(file_in_folder)
                                arr.append(root)
                                self.songs_dictionary.update({file_in_folder: arr})
                            self.player_queue.append(root + "/" + file_in_folder)
                            self.listbox1.insert(self.listbox1.size(), file_in_folder)
            # Creating shuffled array of songs from array 'player_queue'.
            self.shuffled_player_queue = self.player_queue.copy()
            random.shuffle(self.shuffled_player_queue)
            self.play_button1.config(state=tk.NORMAL)
            self.next_button.config(state=tk.NORMAL)
            self.previous_button.config(state=tk.NORMAL)
            self.scale.config(state=tk.NORMAL)
            self.scale.bind("<ButtonRelease-1>", self.thread_set_slider_position)
            self.song_pointer = 0
            self.thread_play_song()
            # Playing this twice avoided to help come out of 'running while loop' when opening new window Tk().
            #self.thread_play_song()

    def thread_select_folder(self):
        thread_select_folder_var = Thread(target=self.select_folder())
        thread_select_folder_var.start()

    def sort_songs_list_atoz(self):
        global listbox_file_names, songs_dictionary, song_pointer, player_queue, shuffled_player_queue
        self.btn_sort_by_album.config(relief=tk.RAISED, bd=2)
        self.btn_sort_by_atoz.config(relief=tk.RAISED, bd=6)
        self.btn_sort_by_album_year.config(relief=tk.RAISED, bd=2)
        if len(self.songs_dictionary) > 0:
            self.player_queue = []
            self.listbox1.delete(0, tk.END)
            songs_dictionary_keys = list(self.songs_dictionary.keys())
            songs_dictionary_keys.sort()
            sorted_songs_dictionary = {k: self.songs_dictionary[k] for k in songs_dictionary_keys}
            for song in sorted_songs_dictionary:
                song_locations_list = sorted_songs_dictionary.get(song)
                for location_path in song_locations_list:
                    self.player_queue.append(location_path + "/" + song)
                    self.listbox1.insert(self.listbox1.size(), song)
            # Creating shuffled array of songs from array 'player_queue'.
            self.shuffled_player_queue = self.player_queue.copy()
            random.shuffle(self.shuffled_player_queue)
            self.song_pointer = 0
            self.thread_play_song()

    def thread_sort_songs_list_atoz(self):
        thread_sort_songs_list_atoz_var = Thread(target=self.sort_songs_list_atoz())
        thread_sort_songs_list_atoz_var.start()

    def sort_songs_list_by_album_year(self):
        global player_queue, song_pointer, listbox1, shuffled_player_queue
        self.btn_sort_by_album.config(relief=tk.RAISED, bd=2)
        self.btn_sort_by_atoz.config(relief=tk.RAISED, bd=2)
        self.btn_sort_by_album_year.config(relief=tk.RAISED, bd=6)
        if len(self.songs_dictionary) > 0:
            # Mapping album year with list of songs containing file name with filepath
            year_song_dictionary = {}
            self.listbox1.delete(0, tk.END)
            for song in self.player_queue:
                try:
                    mixer.music.load(song)
                    filestats = MP3(song)
                    if str(filestats.get("TDRC")) not in year_song_dictionary:
                        year_song_dictionary.update({str(filestats.get('TDRC')): [song]})
                    else:
                        songs_in_this_year = year_song_dictionary.get(str(filestats.get('TDRC')))
                        songs_in_this_year.append(song)
                        year_song_dictionary.update({str(filestats.get('TDRC')): songs_in_this_year})
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
            self.player_queue = []
            # Insert every item from the newly created dictionary's value to the array 'player_queue'.
            for song_location_with_name_list in sorted_songs_by_years_dictionary.values():
                for song_name_with_location in song_location_with_name_list:
                    self.player_queue.append(song_name_with_location)
                    self.listbox1.insert(self.listbox1.size(), song_name_with_location[song_name_with_location.rfind("/") + 1:])
            # Creating shuffled array of songs from array 'player_queue'.
            self.shuffled_player_queue = self.player_queue.copy()
            random.shuffle(self.shuffled_player_queue)
            self.song_pointer = 0
            self.thread_play_song()

    def thread_sort_songs_list_by_album_year(self):
        thread_var = Thread(target=self.sort_songs_list_by_album_year())
        thread_var.start()

    def sort_songs_list_album(self):
        global listbox_file_names, songs_dictionary, song_pointer, player_queue
        self.btn_sort_by_album.config(relief=tk.RAISED, bd=6)
        self.btn_sort_by_atoz.config(relief=tk.RAISED, bd=2)
        self.btn_sort_by_album_year.config(relief=tk.RAISED, bd=2)
        if len(self.songs_dictionary):
            self.player_queue = []
            self.listbox1.delete(0, tk.END)
            for song in self.songs_dictionary:
                song_locations_list = self.songs_dictionary.get(song)
                for location_path in song_locations_list:
                    self.player_queue.append(location_path + "/" + song)
                    self.listbox1.insert(self.listbox1.size(), song)
            self.song_pointer = 0
            self.thread_play_song()

    def thread_sort_songs_list_album(self):
        thread_var_sort_songs_list_album = Thread(target=self.sort_songs_list_album())
        thread_var_sort_songs_list_album.start()

    def show_album_art(self,song_playing):
        filestats = MP3(song_playing, ID3=ID3)
        # If the audio file has no album art, set default image 'record' as album art.
        if str(type(filestats.get("APIC:"))) == "<class 'NoneType'>":
            self.music_image_label.config(image=self.music_art_image)
            self.music_image_label.image = self.music_art_image
        else:  # If the audio file has album art, fetch it from metadata and display it.
            try:  # Use try catch statement if there are more errors while getting ID3 data. This prevents any error.
                # Getting ready to show Album Art
                id3_playing_song = ID3(song_playing)
                id3_data = id3_playing_song.getall("APIC")[0].data
                img = Image.open(io.BytesIO(id3_data))
                max_width, max_height = self.music_image_label.winfo_width(), self.music_image_label.winfo_height()
                img.thumbnail((max_width, max_height))
                photo = ImageTk.PhotoImage(img)
                self.music_image_label.config(image=photo)
                self.music_image_label.image = photo
            except:  # If there is any error in getting ID3 of audio file, set the default 'record' as album art.
                self.music_image_label.config(image=self.music_art_image)
                self.music_image_label.image = self.music_art_image

    def show_listbox(self,event):
        global song_pointer, clicked_from_listbox
        if self.listbox1.size() > 0:
            selected_index = self.listbox1.curselection()[0]
            self.song_pointer = selected_index
            self.listbox1.selection_clear(0, tk.END)
            self.clicked_from_listbox = True
            self.thread_play_song()
            self.clicked_from_listbox = False

    def get_slider_value(self,v):
        global last_slider_value
        self.slider_value = self.scale.get()
        return self.slider_value

    def about(self):
        new_popup_window = tk.Toplevel()
        new_popup_window.title("About PC Musique Player")
        new_popup_window.geometry("500x250")
        new_popup_window.transient(self.root)  # To avoid it from preventing the root window to be paused.
        new_popup_window.wm_attributes('-topmost', True)
        app_icon_label = tk.Label(new_popup_window, image=self.app_logo_image)
        app_icon_label.pack()
        tk.Label(new_popup_window, text="PC Musique Player", font=("Arial", 16)).pack()
        content = "Version: 1.1.0\nRelease Date: 13th June 2024\nDeveloper: Reshma Haridhas\nOS: Windows 10 or later\nCopyright: © 2024 Reshma Haridhas. All Rights Reserved"
        content_label = tk.Label(new_popup_window, text=content, font=("Arial", 10), fg="#000000")
        content_label.pack()
        # Do not use mainloop() here.

    def thread_about(self):
        thread_var_about = Thread(target=self.about())
        thread_var_about.start()

    def show_visualizations(self):
        global canvas_visualization, random_line_1, random_line_2, random_line_3, random_line_4, random_line_5, random_line_6, \
            random_line_7, random_line_8, random_line_9
        self.canvas_visualization.delete('all')
        starting_y_list = [5, 10, 15, 20, 25, 30, 35, 40]
        random.shuffle(starting_y_list)
        self.random_line_1 = self.canvas_visualization.create_line(5, starting_y_list[0], 5, 50, width=5, fill=self.main_color)
        self.random_line_2 = self.canvas_visualization.create_line(12, starting_y_list[1], 12, 50, width=5,
                                                         fill=self.button_ui_bg_color)
        self.random_line_3 = self.canvas_visualization.create_line(19, starting_y_list[2], 19, 50, width=5, fill=self.main_color)
        self.random_line_4 = self.canvas_visualization.create_line(26, starting_y_list[3], 26, 50, width=5,
                                                         fill=self.button_ui_bg_color)
        self.random_line_5 = self.canvas_visualization.create_line(33, starting_y_list[4], 33, 50, width=5, fill=self.main_color)
        self.random_line_6 = self.canvas_visualization.create_line(40, starting_y_list[5], 40, 50, width=5,
                                                         fill=self.button_ui_bg_color)
        self.random_line_7 = self.canvas_visualization.create_line(47, starting_y_list[6], 47, 50, width=5, fill=self.main_color)
        self.random_line_8 = self.canvas_visualization.create_line(54, starting_y_list[7], 54, 50, width=5,
                                                         fill=self.button_ui_bg_color)
        self.random_line_9 = self.canvas_visualization.create_line(61, starting_y_list[0], 61, 50, width=5, fill=self.main_color)

    def thread_show_visualization(self):
        thread_var_visualization = Thread(target=self.show_visualizations())
        thread_var_visualization.start()

    def change_player_theme(self,index_number):
        global main_color, button_ui_bg_color, text_color, btn_sort_by_album, btn_sort_by_album_year, btn_sort_by_album_year
        self.main_color = self.color_themes_main_color[index_number]
        self.button_ui_bg_color = self.color_themes_button_ui_bg_color[index_number]
        self.text_color = self.color_themes_text_color[index_number]
        # action
        self.root.config(bg=self.main_color)
        self.frame1.config(bg=self.main_color)
        self.mainFrame.config(bg=self.main_color)
        self.sideFrame.config(bg=self.main_color)
        self.music_image_label.config(bg=self.main_color)
        self.audio_name_label.config(bg=self.main_color, fg=self.text_color)
        self.album_name_label.config(bg=self.main_color, fg=self.text_color)
        self.artists_label.config(bg=self.main_color, fg=self.text_color)
        self.album_year_label.config(bg=self.main_color, fg=self.text_color)
        self.duration_label.config(bg=self.main_color, fg=self.text_color)
        self.scale.config(bg=self.main_color, troughcolor=self.button_ui_bg_color, activebackground=self.main_color, fg=self.text_color)
        self.controls_frame.config(background=self.main_color)
        self.shuffle_button.config(bg=self.button_ui_bg_color, activebackground=self.button_ui_bg_color)
        self.previous_button.config(bg=self.button_ui_bg_color, activebackground=self.button_ui_bg_color)
        self.play_button1.config(bg=self.button_ui_bg_color, activebackground=self.button_ui_bg_color)
        self.next_button.config(bg=self.button_ui_bg_color, activebackground=self.button_ui_bg_color)
        self.loop_button1.config(bg=self.button_ui_bg_color, activebackground=self.button_ui_bg_color)
        self.stop_button.config(bg=self.button_ui_bg_color, activebackground=self.button_ui_bg_color)
        self.controls_frame2.config(background=self.main_color)
        self.volume_down_button.config(bg=self.button_ui_bg_color, activebackground=self.button_ui_bg_color)
        self.volume_up_button.config(bg=self.button_ui_bg_color, activebackground=self.button_ui_bg_color)
        self.volume_mute_button.config(bg=self.button_ui_bg_color, activebackground=self.button_ui_bg_color)
        self.mini_max_player_button.config(bg=self.button_ui_bg_color,activebackground=self.button_ui_bg_color)
        self.open_folder_button.config(bg=self.button_ui_bg_color, activebackground=self.button_ui_bg_color)
        self.songs_label.config(bg=self.main_color, activebackground=self.main_color, fg=self.text_color)
        self.sort_frame.config(background=self.main_color)
        self.btn_sort_by_album.config(bg=self.button_ui_bg_color, activebackground=self.button_ui_bg_color, fg=self.text_color)
        self.btn_sort_by_atoz.config(bg=self.button_ui_bg_color, activebackground=self.button_ui_bg_color, fg=self.text_color)
        self.btn_sort_by_album_year.config(bg=self.button_ui_bg_color, activebackground=self.button_ui_bg_color, fg=self.text_color)
        self.listbox1.config(bg=self.main_color, fg=self.text_color, highlightbackground=self.text_color)
        self.canvas1.itemconfig(self.line1, fill=self.main_color)
        self.canvas_visualization.itemconfig(self.random_line_1, fill=self.main_color)
        self.canvas_visualization.itemconfig(self.random_line_2, fill=self.button_ui_bg_color)
        self.canvas_visualization.itemconfig(self.random_line_3, fill=self.main_color)
        self.canvas_visualization.itemconfig(self.random_line_4, fill=self.button_ui_bg_color)
        self.canvas_visualization.itemconfig(self.random_line_5, fill=self.main_color)
        self.canvas_visualization.itemconfig(self.random_line_6, fill=self.button_ui_bg_color)
        self.canvas_visualization.itemconfig(self.random_line_7, fill=self.main_color)
        self.canvas_visualization.itemconfig(self.random_line_8, fill=self.button_ui_bg_color)
        self.canvas_visualization.itemconfig(self.random_line_9, fill=self.main_color)
        if index_number == 14 or index_number==18:
            self.fileMenu.config(background=self.button_ui_bg_color, fg="white")
            self.audio_Menu.config(background=self.button_ui_bg_color, fg="white")
            self.player_Menu.config(background=self.button_ui_bg_color, fg="white")
            self.help_Menu.config(background=self.button_ui_bg_color, fg="white")
            self.btn_sort_by_album.config(bg=self.button_ui_bg_color, activebackground=self.button_ui_bg_color, fg="white")
            self.btn_sort_by_atoz.config(bg=self.button_ui_bg_color, activebackground=self.button_ui_bg_color, fg="white")
            self.btn_sort_by_album_year.config(bg=self.button_ui_bg_color, activebackground=self.button_ui_bg_color, fg="white")
        else:
            self.fileMenu.config(background=self.button_ui_bg_color, fg="black")
            self.audio_Menu.config(background=self.button_ui_bg_color, fg="black")
            self.player_Menu.config(background=self.button_ui_bg_color, fg="black")
            self.help_Menu.config(background=self.button_ui_bg_color, fg="black")
        if index_number == 0 or index_number == 4 or index_number == 5 or index_number == 7 or index_number == 8 or index_number == 9 or index_number == 15:
            self.btn_sort_by_album.config(bg=self.button_ui_bg_color, activebackground=self.button_ui_bg_color, fg="black")
            self.btn_sort_by_atoz.config(bg=self.button_ui_bg_color, activebackground=self.button_ui_bg_color, fg="black")
            self.btn_sort_by_album_year.config(bg=self.button_ui_bg_color, activebackground=self.button_ui_bg_color, fg="black")

    def hide_library(self):
        self.root.minsize(width=640, height=750)
        self.root.maxsize(width=640, height=750)

    def show_library(self):
        self.root.minsize(width=1520, height=770)
        self.root.maxsize(width=1520, height=770)
        self.root.geometry("1520x770")

    def shuffle_song_playing_order(self):
        global shuffle_status
        self.shuffle_status = not self.shuffle_status
        self.change_text_shuffle_button()

    def thread_shuffle_song_playing_order(self):
        thread_shuffle_song_playing_order_var = Thread(target=self.shuffle_song_playing_order())
        thread_shuffle_song_playing_order_var.start()

    def change_text_shuffle_button(self):
        if self.shuffle_status == False:
            self.shuffle_button.config(text="Shuffle OFF", image=self.shuffle_no_image)
            Hovertip(self.shuffle_button, "Shuffle Off")
        else:
            self.shuffle_button.config(text="Shuffle ON", image=self.shuffle_image)
            Hovertip(self.shuffle_button, "Shuffle On")

    def func2(self):
        self.close_window()
        sys.exit()

    def thread_stop_song(self):
        Thread(target=self.stop_song()).start()

    def change_to_smallplayer(self):
        self.root.geometry("660x210")
        self.root.resizable(0,0)
        self.root.minsize(width=660,height=210)
        self.root.maxsize(width=660,height=210)
        self.root.config(menu="")
        self.music_image_label.pack_forget()
        self.canvas_visualization.pack_forget()
        self.album_name_label.pack_forget()
        self.artists_label.pack_forget()
        self.album_year_label.pack_forget()
        self.duration_label.pack_forget()
        self.mini_max_player_button.config(command=self.open_main_player,image=self.open_player_wide_image)
        self.sideFrame.grid_forget()

    def open_main_player(self):
        self.root.config(menu="")
        self.audio_name_label.pack_forget()
        self.scale.pack_forget()
        self.controls_frame.pack_forget()
        self.controls_frame2.pack_forget()
        self.root.geometry("1450x750")
        self.root.minsize(width=1450, height=750)
        self.root.resizable(True,True)
        self.root.config(menu=self.menubar1)
        self.music_image_label.pack(pady=17)
        self.canvas_visualization.pack()
        self.audio_name_label.pack(pady=5)
        self.album_name_label.pack()
        self.artists_label.pack()
        self.album_year_label.pack()
        self.duration_label.pack()
        self.scale.pack()
        self.controls_frame.pack()
        self.mini_max_player_button.config(command=self.change_to_smallplayer,image=self.mini_player_image)
        self.controls_frame2.pack(side=tk.RIGHT, padx=20)
        self.sideFrame.grid(row=0, column=1)
