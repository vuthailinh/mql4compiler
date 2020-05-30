import sublime, sublime_plugin
import os
import subprocess
import re
import time

import sys

PLATFORM      = sublime.platform()
METALANG_PATH = 'C:\\Program Files (x86)\\MetaTrader 4 IC Markets\\metaeditor.exe'
EXTENSION     = '.mq4'

def which(file):

    for dir in os.environ['PATH'].split(os.pathsep):
        path = os.path.join(dir, file)
        if os.path.exists(path):
            return path

    print ("PATH = {0}".format(os.environ['PATH']))
    return None


class Mql4CompilerCommand(sublime_plugin.TextCommand):

    def init(self):
        view = self.view

        if view.file_name() is not None :
            self.dirname   = os.path.realpath(os.path.dirname(view.file_name()))
            self.filename  = os.path.basename(view.file_name())
            self.extension = os.path.splitext(self.filename)[1]
            self.compilelog= self.dirname+"\\"+os.path.splitext(self.filename)[0] + ".log"
            if os.path.exists(self.compilelog):
                os.remove(self.compilelog)
                print("File log "+self.filename+" removed")


    def isError(self):

        iserror = False

        if not os.path.exists(METALANG_PATH):
            print (METALANG_PATH) # Debug
            print ("MQL Compiler | error: metaeditor.exe not found")
            iserror = True

        if self.view.file_name() is None :
            # check if console..
            print ("MQL Compiler | error: Buffer has to be saved first")
            iserror = True

        else :

            if self.extension != EXTENSION:
                print ("MQL Compiler | error: wrong file extension: ({0})".format(self.extension))
                iserror = True

            if self.view.is_dirty():
                print ("MQL Compiler | error: Save File before compiling")
                iserror = True

        return iserror

    def runMetalang(self):

        command = [METALANG_PATH,"/compile:"+self.filename, "/log"]

        startupinfo = None

        # hide pop-up window on windows
        if PLATFORM == 'windows':
            startupinfo = subprocess.STARTUPINFO()
            startupinfo.dwFlags |= subprocess.STARTF_USESHOWWINDOW

        # execution:
        proc = subprocess.Popen(command,
        cwd= self.dirname,
        stdout=None,
        shell=False,
        startupinfo=startupinfo)

    def newLogWindow(self, output):
        window = self.view.window()

        new_view = window.create_output_panel("mql4log")
        new_view.run_command('erase_view')
        new_view.run_command('append', {'characters': output})
        window.run_command("show_panel", {"panel": "output.mql4log"})

        sublime.status_message('Metalang')

        pass

    def run(self , edit):

        self.init()
        if self.isError():
            return

        self.runMetalang()

        while not os.path.exists(self.compilelog):
            time.sleep(1)

        with open(self.compilelog, 'r', encoding='UTF-16') as content_file:
            content = content_file.read()
            print(content)
            self.newLogWindow(content)

        os.remove(self.compilelog)