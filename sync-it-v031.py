"""
Sync two folders from systray V0.31 April 2020
Windows only.
------------------------
If you use this program, it's at your own risk.
-------------------------
pip3 install dirsync
pip3 install infi.systray
pip3 install Pillow

sync-it.ico in same dir as this code is run from.
if not found the default system icon will be used.
"""
import os
import logging
from time import sleep
from tkinter import filedialog, Label, messagebox, Tk, Toplevel
import webbrowser as web

from dirsync import sync
from infi.systray import SysTrayIcon as stray
from PIL import ImageGrab # Hidden import, required only for pyinstaller exe.

root = Tk()
root.withdraw()

class Glo:
    """Global store, this makes these vars global,e.g Glo.var."""
    custom_mbox = ''
    src_fldr = ''
    dest_fldr = ''
    limit_src = ''
    limit_dest = ''
    sync_purge = True

def settings(stray):
    """Read or create settings files."""
    if os.path.exists('sync-src.txt'):
        with open('sync-src.txt', 'r') as contents:
            Glo.src_fldr = contents.read()
    else:
        with open('sync-src.txt', 'w') as contents:
            Glo.src_fldr = ''

    if os.path.exists('sync-dest.txt'):
        with open('sync-dest.txt', 'r') as contents:
            Glo.dest_fldr = contents.read()
    else:
        with open('sync-dest.txt', 'w') as contents:
            Glo.dest_fldr = ''

def trun_cate():
    """Truncate folder name strings to max 50 chars in case crazy length used."""
    Glo.limit_src = Glo.src_fldr[:50]
    Glo.limit_dest = Glo.dest_fldr[:50]

def msg_box(stray):
    """Custom non blocking message box."""
    Glo.custom_mbox = Toplevel(root)
    Glo.custom_mbox.title('Sync It V0.31. ')
    Glo.custom_mbox.attributes('-topmost', 1) # Bring custom window to front.

    trun_cate()
    cstm_mb_label = Label(Glo.custom_mbox,
                          text='   By Steve Shambles. April 2020.   \n\n'
                          'Syncing folders:\n'
                          '\n'+str(Glo.limit_src)+''
                          '\n'+str(Glo.limit_dest)+'\n'
                          '\n\nplease wait...')
    cstm_mb_label.grid()

    # Centre custom box on screen.
    # From code snippets vol.4, snippet 20.
    # https://stevepython.wordpress.com/2018/09/07/python-code-snippets-4/
    WINDOWWIDTH = Glo.custom_mbox.winfo_reqwidth()
    WINDOWHEIGHT = Glo.custom_mbox.winfo_reqheight()
    POSITIONRIGHT = int(Glo.custom_mbox.winfo_screenwidth()/2 - WINDOWWIDTH/2)
    POSITIONDOWN = int(Glo.custom_mbox.winfo_screenheight()/2 - WINDOWHEIGHT/2)
    # Positions the window in the center of the page.
    Glo.custom_mbox.geometry("+{}+{}".format(POSITIONRIGHT, POSITIONDOWN))

    sleep(3) # Gives a chance to read text in case it's a very quick sync.

def set_src_fldr(stray):
    """Change source folder location, which is then written to a text file."""
    get_new_sf = filedialog.askdirectory()

    if get_new_sf == '':
        return

    with open('sync-src.txt', 'w') as contents:
        contents.write(str(get_new_sf))
        Glo.src_fldr = get_new_sf

def set_dest_fldr(stray):
    """Change destination folder location, which is then written to text file."""
    get_new_df = filedialog.askdirectory()
    if get_new_df == '':
        return

    with open('sync-dest.txt', 'w') as contents:
        contents.write(str(get_new_df))
        Glo.dest_fldr = get_new_df

def open_src_folder(stray):
    """File browser to view contents of source folder."""
    if Glo.src_fldr == '':
        return
    web.open(Glo.src_fldr)

def open_dest_folder(stray):
    """File browser to view contents of destination."""
    if Glo.dest_fldr == '':
        return
    web.open(Glo.dest_fldr)

def exit_prg(stray):
    """This is fake callback required by systray."""
    pass

def sync_help(stray):
    """Help pop up message."""
    messagebox.showinfo('Sync It Help',
                        'Sync It V0.31\n\n'
                        'Sync It allows any two pre-selected folders\n'
                        'to be kept in sync manually.\n\n'
                        'First choose the two folders that you would like to\n'
                        'synchronize by right-clicking on the Sync It\n'
                        'system tray icon and using the Set source folder and\n'
                        'Set destination folder menu options in the settings menu.\n'
                        '\nThese settings will be saved so you only need to do\n'
                        'this once, unless you decide to change folders later.\n\n'
                        'In the Options menu you can open both these folders to\n'
                        'check they are correct by selecting Open source folder\n'
                        'and Open destination folder.\n\n'
                        'You choose to set PURGE files to TRUE or FALSE in the\n'
                        'settings menu. A pop up will explain what this means.\n\n'
                        'To perform a sync either select Sync It from the menu\n'
                        'or you can just double click the Sync It systray icon.\n\n'
                        )

def about_syncit(stray):
    """About program pop up."""
    messagebox.showinfo('Sync It Info',
                        'Sync It V0.31\n\n'
                        'Freeware by Steve Shambles'
                        ' April 2020.\n\n'
                        'Sync It allows any two pre-selected folders\n'
                        'to be kept in sync manually.\n\n'
                        'By using this software you are agreeing\n'
                        'that you use it at your own risk.')

def visit_blog(stray):
    """Open webbrowser and go to my Python blog site."""
    web.open('https://stevepython.wordpress.com/2020/04/02/python-folder-sync')

def set_purge_on(stray):
    Glo.sync_purge = True
    messagebox.showinfo('Sync It Info',
                        'Sync It V0.31\n\n'
                        'Purge files set to TRUE.\n\n'
                        'This is Sync Its default mode.\n\n'
                        'This means any files or folders deleted in your\n'
                        'source folder WILL ALSO BE DELETED in your\n'
                        'destination folder.')

def set_purge_off(stray):
    Glo.sync_purge = False
    messagebox.showinfo('Sync It Info',
                        'Sync It V0.31\n\n'
                        'Purge files set to FALSE.\n\n'
                        'This means any files or folders deleted in your\n'
                        'source folder will NOT BE DELETED in your\n'
                        'destination folder.')

def sync_it(stray):
    """Perform syncing of the two folders scr_fldr and dest_fldr."""
    if Glo.src_fldr == '' or Glo.dest_fldr == '':
        messagebox.showinfo('Info',
                            'please set source and destination\n'
                            'folders from the systray menu first.')
        return

    trun_cate()

    ask_yn = messagebox.askyesno('Question:',
                                 'Sync these two folders?'
                                 '\n\n'+str(Glo.limit_src)+''
                                 '\n'+str(Glo.limit_dest)+'\n\n'
                                 'Purge files '+str(Glo.sync_purge)+'\n\n ')
    if ask_yn is False:
        return

    msg_box(stray)

    if Glo.sync_purge:
        sync(Glo.src_fldr, Glo.dest_fldr, 'sync', logger=my_log, purge=True)
    else:
        sync(Glo.src_fldr, Glo.dest_fldr, 'sync', logger=my_log, purge=False)


    Glo.custom_mbox.destroy()

    # Display report log.
    web.open('syncit.txt')


    messagebox.showinfo('Sync It Info',
                        'Sync It V0.31\n\n'
                        'Purge files '+str(Glo.sync_purge)+'\n\n '
                        'Sync completed.\n\n'
                        'See opened log file for details')


def main(stray):
    """Main program control using infi.systray module."""
    hover_text = 'Sync It V0.31'

    menu_options = (('Sync it', None, sync_it),
                    ('Options', None, (('Help', None, sync_help),
                                       ('About', None, about_syncit),
                                       ('Open source folder', None, open_src_folder),
                                       ('Open destination folder', None, open_dest_folder),
                                       ('Visit blog', None, visit_blog),)),

                    ('Settings', None, (('Set source folder', None, set_src_fldr),
                                        ('Set destination folder', None, set_dest_fldr),
                                        ('Purge ON', None, set_purge_on),
                                        ('Purge OFF', None, set_purge_off))))

    stray = stray('sync-it.ico',
                  hover_text, menu_options, on_quit=exit_prg,
                  default_menu_index=0)
    stray.start()
#---------------------------------------
logging.basicConfig(format='%(asctime)s %(message)s',
                    filename="syncit.txt",
                    filemode='w+',
                    datefmt='%d/%m/%Y %I:%M:%S %p',
                    level=logging.INFO)
my_log = logging.getLogger('dirsync')


settings(stray)
main(stray)

root.mainloop()
