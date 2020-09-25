"""
Sync It V0.60 - 24th Sept 2020
Windows only. Freeware.

Sync two folders from systray
By Steve Shambles.
-----------------------------------------------
Even though I have tested and used this program
on my Windows 7 64bit every day for weeks without a hitch
I have to remind you that if you use this program,
it's at your own risk.
-----------------------------------------------
pip3 install dirsync
pip3 install infi.systray
pip3 install Pillow

These icons will be auto-downloaded if missing:
sync-it.ico in current dir
sync-it-red.ico in current dir

V0.60 changes:
---------------
Added load and save and view profiles.
This basically just means saving the settings
for each sync you wish to perform, previously
you could only have one folder to sync with another
now you can have as many as you want.

Save a profile with the name "default" and this will
auto load on start up.

Fixed menu seperators
See this post if you see dashes instaed of proper seperator bars:
https://stevepython.wordpress.com/2020/04/26/infi-systray-separator-bar/

Added donate option.
Updated help and about texts.
"""
import logging
import os
import re
from time import sleep
from tkinter import filedialog, Label, messagebox, simpledialog, Tk, Toplevel
import webbrowser as web
import wget

from dirsync import sync
from infi.systray import SysTrayIcon as stray
from PIL import ImageGrab  # Hidden import, required only for pyinstaller exe.

root = Tk()
root.withdraw()  # Stops ugly default window opening when using filedialog.

# Set up logging.------------------------
logging.basicConfig(format='%(message)s',
                    filename="syncit.log",
                    filemode='w+',
                    level=logging.INFO)
my_log = logging.getLogger('dirsync')


class Glo:
    """Global store. This makes these vars global, e.g Glo.scrc_fldr."""
    custom_mbox = ''
    src_fldr = ''
    dest_fldr = ''
    limit_src = ''
    limit_dest = ''
    purge_status = 'ON'
    sync_purge = True
    ask_dl = ''
    default_dir = ''
    profiles_dir = ''


def chk_profiles_dir():
    """Check profiles folder exists, if not create it."""
    check_folder = os.path.isdir('profiles')
    if not check_folder:
        os.mkdir('profiles')

def dwnld_yn_msgbox():
    """Offer user option to auto download missing files."""
    Glo.ask_dl = messagebox.askyesno('Question:',
                                     'Auto download missing files?\n\n'
                                     'One or more icon files are missing\n'
                                     'from the current directory.\n\n'
                                     'Should I try to download and install\n'
                                     'these files for you?')

def check_icons():
    """Check if icons required are present in cwd,
       if not offer to auto download them from GitHub."""
    if not os.path.exists('sync-it.ico') or not os.path.exists('sync-it-red.ico'):
        dwnld_yn_msgbox()

    if not os.path.exists('sync-it.ico'):
        if Glo.ask_dl:
            wget.download('https://raw.githubusercontent.com/steveshambles/' \
                          'Sync-It/master/sync-it.ico')

    if not os.path.exists('sync-it-red.ico'):
        if Glo.ask_dl:
            wget.download('https://raw.githubusercontent.com/steveshambles/' \
                          'Sync-It/master/sync-it-red.ico')

def default_profile():
    """Read in default profile to auto load settings if found."""
    if os.path.exists('profiles\\default.sync'):
        with open('profiles\\default.sync', 'r') as contents:
            Glo.src_fldr = contents.readline().rstrip('\n')
            Glo.dest_fldr = contents.readline().rstrip('\n')
    else:
        Glo.src_fldr = ''
        Glo.dest_fldr = ''

def truncate_fldr_names():
    """Shorten folder name strings to max 50 chrs in case crazy length used."""
    Glo.limit_src = Glo.src_fldr[:50]
    Glo.limit_dest = Glo.dest_fldr[:50]

def msg_box(stray):
    """Custom non-blocking message box."""
    Glo.custom_mbox = Toplevel(root)
    Glo.custom_mbox.title('Sync It V0.60. ')
    Glo.custom_mbox.attributes('-topmost', 1) # Bring custom window to front.

    # Remove the toolbar from the msg box.
    Glo.custom_mbox.attributes('-toolwindow', 1)
    # Iconify msg box if exit X is hit by user, rather than lose the window.
    Glo.custom_mbox.protocol('WM_DELETE_WINDOW', Glo.custom_mbox.iconify)

    truncate_fldr_names()

    cstm_mb_label = Label(Glo.custom_mbox, bg='limegreen',
                          text='   By Steve Shambles. Sept 2020.   \n\n'
                          'Syncing folders:\n'
                          '\n'+str(Glo.limit_src)+''
                          '\n'+str(Glo.limit_dest)+'\n'
                          '\nPurge files: '+str(Glo.purge_status)+'\n'
                          '\nplease wait...\n')
    cstm_mb_label.grid()

    centre_msg_box()

    sleep(3) # Gives a chance to read text in case it's a very quick sync.

def set_src_fldr(stray):
    """Change source folder location, which is then written to default-profile.sync."""
    get_new_sf = filedialog.askdirectory (title='Please select source folder to sync')
    if get_new_sf == '':
        return
    Glo.src_fldr = get_new_sf

def set_dest_fldr(stray):
    """Change dest folder location, which is then written to default-profile.sync."""
    get_new_df = filedialog.askdirectory (title='Please select destination folder to sync')
    if get_new_df == '':
        return
    Glo.dest_fldr = get_new_df

def open_src_folder(stray):
    """File browser to view contents of source folder."""
    if Glo.src_fldr == '':
        messagebox.showerror('ERROR',
                             'No Source folder has been set!\n\n'
                             'Please select source folder to sync\n'
                             'from the Sync It "Settings" menu,\n\n'
                             'or load a previously saved profile.')
        return
    web.open(Glo.src_fldr)

def open_dest_folder(stray):
    """File browser to view contents of destination folder."""
    if Glo.dest_fldr == '':
        messagebox.showerror('ERROR',
                             'No Destination folder has been set!\n\n'
                             'Please select destination folder to sync\n'
                             'from the Sync It "Settings" menu,\n\n'
                             'or load a previously saved profile.')
        return
    web.open(Glo.dest_fldr)

def view_profiles_folder(stray):
    """File browser to view contents of profiles folder."""
    web.open(Glo.profiles_dir)

def exit_prg(stray):
    """This is a fake callback required by systray. Once this def is called
       the program is unable to return. This means I cant use a y\n exit msg box
       for example."""
    os.system("taskkill /f /im sync-it-v060.exe")

def sync_help(stray):
    """Help pop up message."""
    messagebox.showinfo('Sync It Help',
                        'Sync It V0.60 Sept 2020\n\n'
                        'Sync It allows any two folders\n'
                        'to be kept in sync manually.\n\n'
                        'First choose the two folders that you would like to\n'
                        'synchronize by Setting the source and destination folders\n'
                        'from the "Settings" menu \n\n\n'
                        'In the "Options" menu you can open both these folders to\n'
                        'to view their contents by selecting "Open source folder"\n'
                        'and "Open destination folder".\n\n\n'
                        'You can choose to set PURGE files to ON or OFF in the\n'
                        '"Settings menu". A pop up will explain what this means.\n\n\n'
                        'To perform a sync you can either select "Sync It"'
                        ' from the menu\n'
                        'or you can just double click the blue Sync It sys-tray icon.\n\n\n'
                        'If you have more than one folder to sync, then you can save '
                        'each setup as a profile from the "Profiles menu" '
                        'and load in each profile as and when required.'
                        '\n\nYou can save as many profiles as you want.'
                        '\n\nYou can also view the contents of the profiles folder via\n'
                        'the "View profiles folder" option where you can check on,\n'
                        'or maybe delete profiles you no longer require.\n\n\n'
                        'If you save a profile with the name "default" this profile\n'
                        'will auto load on start up to save you loading it in each time.\n\n')

def about_syncit(stray):
    """About program pop up."""
    messagebox.showinfo('Sync It Info',
                        'Sync It V0.60\n\n'
                        'Freeware by Steve Shambles'
                        '\nSept 2020.\n\n'
                        'Sync It allows any two folders\n'
                        'to be kept in sync manually.\n\n'
                        'By using this software you are agreeing\n'
                        'that you use it at your own risk.\n\n'
                        'If you find this program useful\n'
                        'please consider making a small donation.')

def visit_blog(stray):
    """Open webbrowser and go to my Python blog site."""
    web.open('https://stevepython.wordpress.com/2020/04/02/python-folder-sync')

def contact_me(stray):
    """Open webbrowser and go to my blog contact page."""
    web.open('https://stevepython.wordpress.com/contact')

def donate_me(stray):
    web.open("https:\\paypal.me/photocolourizer")

def set_purge_on(stray):
    """Purge on-off setting. On."""
    Glo.sync_purge = True
    Glo.purge_status = 'ON'
    messagebox.showinfo('Sync It Info',
                        'Sync It V0.60\n\n'
                        'Purge files set to ON.\n\n'
                        'This is the default mode.\n\n'
                        'This means any files or folders deleted in your\n'
                        'source folder WILL ALSO BE DELETED in your\n'
                        'destination folder.')

def set_purge_off(stray):
    """Purge on-off setting. Off."""
    Glo.sync_purge = False
    Glo.purge_status = 'OFF'
    messagebox.showinfo('Sync It Info',
                        'Sync It V0.60\n\n'
                        'Purge files set to OFF.\n\n'
                        'This means any files or folders deleted in your\n'
                        'source folder will NOT BE DELETED in your\n'
                        'destination folder.')

def sync_it(stray):
    """Perform syncing of the two folders Glo.scr_fldr and Glo.dest_fldr."""
    if Glo.src_fldr == '':
        messagebox.showerror('ERROR',
                             'Please set the source folder\n'
                             'from the Sync It "Settings" menu first,\n\n'
                             'or load a previously saved profile.')
        return

    if Glo.dest_fldr == '':
        messagebox.showerror('ERROR',
                             'Please set the destination folder\n'
                             'from the Sync It "Settings" menu first,\n\n'
                             'or load a previously saved profile.')
        return

    if Glo.src_fldr == Glo.dest_fldr:
        messagebox.showerror('ERROR',
                             'Source and destination folders are the same!\n\n'
                             'Please select two different folders to sync\n'
                             'from the Sync It "Settings" menu.')
        return

    truncate_fldr_names()

    ask_yn = messagebox.askyesno('Question:',
                                 'Sync these two folders?'
                                 '\n\n'+str(Glo.limit_src)+''
                                 '\n'+str(Glo.limit_dest)+'\n\n'
                                 'Purge files: '+str(Glo.purge_status)+'\n')
    if ask_yn is False:
        return

    # Switch to red icon display.
    stray.update(icon='sync-it-red.ico')

    msg_box(stray)

    # Clear old log data.
    with open('syncit.log', 'w+'):
        pass

    # Clear tmp last log data.
    with open('lastlog.log', 'w+'):
        pass

    # Perform the actual syncing.
    if Glo.sync_purge:
        sync(Glo.src_fldr, Glo.dest_fldr, 'sync', logger=my_log, purge=True)
    else:
        sync(Glo.src_fldr, Glo.dest_fldr, 'sync', logger=my_log, purge=False)

    # Create new empty log.
    with open('lastlog.log', 'w+'):
        pass

    msg_log = ''

    with open('syncit.log', 'r') as f:
        logtext = f.readlines()

    with open('lastlog.log', 'w+') as f:
        for line in logtext:
            line = re.sub(r'[\x00-\x1F]+', '', line) # Strip some non ascii.
            msg = (line)
            f.write(msg)
            msg_log = msg_log + msg+'\n'

    Glo.custom_mbox.destroy()

    # Switch back to original icon display.
    stray.update(icon='sync-it.ico')

    messagebox.showinfo('Sync It Info',
                        'Sync It V0.60\n\n'
                        'Sync completed.\n\n'
                         + str(msg_log))

    os.chdir(Glo.default_dir)

def fake():
    """Fake def for menu seperator bars to call."""
    pass

def centre_msg_box():
    """Centre custom box on screen.
       From code snippets vol.4, snippet 20.
       https://stevepython.wordpress.com/2018/09/07/python-code-snippets-4/"""
    WINDOW_WIDTH = Glo.custom_mbox.winfo_reqwidth()
    WINDOW_HEIGHT = Glo.custom_mbox.winfo_reqheight()
    POSITION_RIGHT = int(Glo.custom_mbox.winfo_screenwidth()/2 - WINDOW_WIDTH/2)
    POSITION_DOWN = int(Glo.custom_mbox.winfo_screenheight()/2 - WINDOW_HEIGHT/2)
    Glo.custom_mbox.geometry('+{}+{}'.format(POSITION_RIGHT, POSITION_DOWN))
    # Note: There is a better and simple way using tk window can't find
    # it for now.

def save_profile(stray):
    """Save new profile txt for current src and dest folders with .sync extension."""
    if not Glo.src_fldr or not Glo.dest_fldr:
        messagebox.showerror('ERROR',
                             'Please set up source and destination folders\n'
                             'from the settings menu first.')
        return

    newWin = Tk()
    newWin.withdraw()
    # required because of tkinter bug.
    # https://stackoverflow.com/questions/53480400/
    # tkinter-askstring-deleted-before-its-visibility-changed

    user_input = ''

    user_input = simpledialog.askstring('Save Profile',
                                        'Please enter a new name :', parent=newWin)
    newWin.destroy()

    if not user_input:
        return

    message = ''
    if user_input == 'default':
        message = '\n\nThis profile will auto load when\n'  \
                  'Sync It is next run.'

    user_input = user_input + '.sync'

    os.chdir(Glo.profiles_dir)

    with open(user_input, 'w') as contents:
        contents.write(str(Glo.src_fldr) + '\n')
        contents.write(str(Glo.dest_fldr))

    messagebox.showinfo('Sync It Info',
                        'Sync profile saved.\n\n'
                         + str(user_input) + ''
                         + str(message))
    os.chdir(Glo.default_dir)

def load_profile(stray):
    """Load saved profile - plain text - of previously saved settings."""
    pro_file = filedialog.askopenfilename(initialdir=Glo.profiles_dir,
                                          title='Select a sync file',
                                          filetypes=(('Sync It profiles', '*.sync'),
                                                     ('All files', '*.*')))

    if not pro_file:
        return

    with open(pro_file, 'r') as contents:
        Glo.src_fldr = contents.readline().rstrip('\n')
        Glo.dest_fldr = contents.readline().rstrip('\n')

    messagebox.showinfo('Sync It Info',
                        'Sync profile loaded.\n\n'
                        + str(pro_file))

def main(stray):
    """Main program control using infi.systray module."""
    hover_text = 'Sync It V0.60'

    menu_options = (('Sync it', None, sync_it),


                    ('Settings', None, (('Set source folder', None, set_src_fldr),
                                        ('Set destination folder', None, set_dest_fldr),
                                        ('-----', None, fake),
                                        ('Purge ON', None, set_purge_on),
                                        ('Purge OFF', None, set_purge_off),)),

                    ('Options', None, (('Open source folder', None, open_src_folder),
                                       ('Open destination folder', None, open_dest_folder),
                                       ('-----', None, fake),
                                       ('About', None, about_syncit),
                                       ('Help', None, sync_help),
                                       ('-----', None, fake),
                                       ('Contact author', None, contact_me),
                                       ('Make a small donation to author', None, donate_me),
                                       ('Visit blog', None, visit_blog),)),

                    ('Profiles', None, (('Load Profile', None, load_profile),
                                        ('Save Profile', None, save_profile),
                                        ('View profiles folder', None, view_profiles_folder),)))

    stray = stray('sync-it.ico',
                  hover_text, menu_options, on_quit=exit_prg,
                  default_menu_index=0)
    stray.start()
# --------------------
Glo.default_dir = os.getcwd()
chk_profiles_dir()
Glo.profiles_dir = Glo.default_dir + r'\profiles'

check_icons()
default_profile()
main(stray)

root.mainloop()
