# Houdini VEX Editor v1.0.8

![alt tag](http://www.paulwinex.ru/wp-content/uploads/2016/03/vex-splash_x.x.x.jpg)

#### [paulwinex.ru](http://www.paulwinex.ru/vex_editor_1_0_5/)

## [Download](http://paulwinex.ru/php/vexeditor/to_download.php)

## [Demo video](https://vimeo.com/145107371)

## [Install guide](https://vimeo.com/151224709)

I am proud to present the latest tool I made for Houdini. This time an editor for VEX code!
It is a good alternative to builtin editor in Houdini. During development user feedback and requests have been a decisive factor.
And yes you can now change font size! This is only one small feature. Following text will present a full list of features
and abilities it will give you. I am open for new ideas and suggestions for expanding it further. Feedback, suggestions ideas
and feature requests can be sent to my email: paulwinex@gmail.com.


### What can VEX Editor do

  - edit VEX code and parameters of any node
  - edit code sections of VEX operator
  - edit *.h or *.vfl files
  - connect editor with source, quick saving of code by Ctrl+Enter
  - auto creation of parameters, used in code when saving
  - removal of unused and renamed parameters
  - avto change type parameter when saving
  - VEX syntax highlighting
  - quick change of font size (Ctrl + Mouse Scroll)
  - color themes mimicking Houdini themes as well as custom, editor specific themes
  - quick access to help cards by pressing Shift+F1
  - autocompletion for VEX functions, data types, keywords. List of functions generated automatically for current build of Houdini
  - auto complete functions and variables of the current code, as well as of the connected through #include files
  - auto complete context
    - nodes existing parameters for the function ch, chv, chi, etc.
    - standard attributes, switched on after the @
    - the existing attributes of the current geometry SOP Content (node ​​Wrangle)
    - *Global variables are switched on after the symbol $
  - input and output parameters of inline node, switched on after the $ symbol in the node inline
  - directives and their parameters are switched on after the # symbol
  - included files from path HOUDINI_VEX_PATH, switched on after entering the "#include" and the opening quotation marks, " ' or <
  - templates as well as templates for quick insertion of the Tab key after the keyword
  - regular backup in case of the crash of Houdini
  - preservation of open tabs in a hip file and automatic recovery when reopening
  - display an error message in the editor’s interface
  - auto indentation and indentation control with Tab and Shift + Tab


###    *Attention!

>    NOT recommended that you use global variables in the VEX code.

>   It's possible to read and write global variables directly (for example,
>        P and Cd in the SOP context). However, we strongly recommend you do not use
>        global variables directly. Houdini does not guarantee the order in which
>        VOPs generate their code, so assigning values to globals can give unpredictable
>        results. Instead, you should explicitly wire from the globals node into this node.
>        Unlike the Point SOP, this does not use local variables. Further, all backtick expressions
>        and $ F variables will be evaluated at frame 1, not the current time. Use Frame, Time, or TimeInc instead.

### New in v1.0.6

>   You can show or hide tool bar

>   Drag and drop node parameter on VEX Editor UI to create new tab connected to this parameter

>   Added "Save as..." action in Tabs menu

>   Added "Open settings folder" action in Editor menu

### Bugfix

>   Renamed settings folder

>   Skipping creation of parameters if path is external

>   Number bar now have static width

>   Some fixes for linux systems

### New in v1.0.7

>   Added help window to show quick help for function in cursor focus (Menu -> Editor -> Help Window)

>   Now context help (Shift + F1) worked if cursor not only above function name but also inside arguments

>   Added "Find and Replace" window. Use Ctrl+F to open

### Bugfix

>   Fixed disappearing autocomplite widget in Houdini 15

>   "Select node" button now open parent network in active network tab

>   Now help browser open help in same window in Houdini 15

### New in v1.0.7

>   Support Houdini 16

# Interface Description
![alt tag](http://www.paulwinex.ru/wp-content/uploads/2015/11/interface.png)
### Buttons main panel

| | |
|---|---|
| ![alt tag](http://www.paulwinex.ru/wp-content/uploads/2015/10/btn1.jpg) | Quick connection nodes. This button is looking for attributes and the snippet code, or section VflCode. If one of the items found, immediately opens the editor with reference to the found item. It can also act as a rapid transition to the tab with the parameters of the selected node |
| ![alt tag](http://www.paulwinex.ru/wp-content/uploads/2015/10/btn2.jpg) | Selecting from the list |
| ![alt tag](http://www.paulwinex.ru/wp-content/uploads/2015/10/btn3.jpg) | Opening a file |
| ![alt tag](http://www.paulwinex.ru/wp-content/uploads/2015/10/btn4.jpg) | Create a blank tabs with the ability to bind it to a parameter or saving a file|
| ![alt tag](http://www.paulwinex.ru/wp-content/uploads/2015/10/btn5.jpg) | Saving code tied to a parameter or a file. The same as the keys Ctrl + Enter|
| ![alt tag](http://www.paulwinex.ru/wp-content/uploads/2015/10/btn6.jpg) | Reload the source code of the bound parameter or file or in the current tab|
| ![alt tag](http://www.paulwinex.ru/wp-content/uploads/2015/10/btn7.jpg) | Highlights node connected to the current tab (if the tab is attached to the parameter node)|
| ![alt tag](http://www.paulwinex.ru/wp-content/uploads/2015/10/btn8.jpg) | Open the folder with the file (if the tab is attached to the file)|

### Menu
#### Tabs:

###### Create From Selected Node
&nbsp;&nbsp;&nbsp;&nbsp;Creates tab for the selected node
###### Create From File
&nbsp;&nbsp;&nbsp;&nbsp;Creates from File tab
###### Create Empty Tab
&nbsp;&nbsp;&nbsp;&nbsp;Creates an empty tab
###### Save Current Code
&nbsp;&nbsp;&nbsp;&nbsp;Saving code from current tab to the connected parameter or file
###### Reload Current Tab From Source
&nbsp;&nbsp;&nbsp;&nbsp;Reload the source code from the bound parameter or a file in the current editor
###### Load Tabs From Current HIP
&nbsp;&nbsp;&nbsp;&nbsp;Loading saved tabs in the current hip file. For example, if you open another file without restarting VEX Editor
###### Clear Saved Tabs
&nbsp;&nbsp;&nbsp;&nbsp;Removal of saved tabs in the current hip file
###### Backups
&nbsp;&nbsp;&nbsp;&nbsp;AutoSave

#### Editor:

###### Theme
&nbsp;&nbsp;&nbsp;&nbsp;Selecting a color theme of editor UI
###### Options ...
&nbsp;&nbsp;&nbsp;&nbsp;The settings dialog

#### Templates:
###### Templates Editor ...
&nbsp;&nbsp;&nbsp;&nbsp;Editor templates

Next comes a list of available templates

#### Help:

###### Manual
&nbsp;&nbsp;&nbsp;&nbsp;Open this page
###### VEX Documentation
&nbsp;&nbsp;&nbsp;&nbsp;VEX documentation page on the official website
###### Show help for selected method
&nbsp;&nbsp;&nbsp;&nbsp;Context-sensitive help function on which the cursor is located. Just invoked by pressing Shift + F1
###### Check New Version
&nbsp;&nbsp;&nbsp;&nbsp;Checking for new version of VEX Editor
###### About
&nbsp;&nbsp;&nbsp;&nbsp;About dialog

#### Settings window

###### Default Font Size
&nbsp;&nbsp;&nbsp;&nbsp;The font size for new tabs
###### Font Family
&nbsp;&nbsp;&nbsp;&nbsp;Selecting a font family
###### Auto Update Spare Parameters On Save
&nbsp;&nbsp;&nbsp;&nbsp;Automatically create the parameters used in your code when saving (only Wrangle)
###### Create Spare Parameters on Top
&nbsp;&nbsp;&nbsp;&nbsp;Creating parameters at the top of the interface node (for Wrangle)
###### Auto Save Tabs In HIP
&nbsp;&nbsp;&nbsp;&nbsp;Save open tabs in hip file
###### Create backup
&nbsp;&nbsp;&nbsp;&nbsp;Create autosave. By default, all of the tabs are saved every 3 minutes. Configured in settings.json
###### Show Whitespaces
&nbsp;&nbsp;&nbsp;&nbsp;Display non-printing characters in the editor
###### Use Online Manual
&nbsp;&nbsp;&nbsp;&nbsp;Use online documentation for quick reference instead of a local
###### Use External Browser For Quick Help
&nbsp;&nbsp;&nbsp;&nbsp;Use external browser for quick reference instead of the standard browser Houdini

#### Editor templates

###### Add New
&nbsp;&nbsp;&nbsp;&nbsp;Creates a new template
###### Remove
&nbsp;&nbsp;&nbsp;&nbsp;Deletes the selected template
###### Keyword
&nbsp;&nbsp;&nbsp;&nbsp;The keyword for the selected template. The template will be inserted at the current cursor position after the keyword by pressing the Tab key
###### $ cursor $
&nbsp;&nbsp;&nbsp;&nbsp;Button to insert a marker indicating the position of the cursor after inserting the template. By default, the cursor moves to end.
###### Save
&nbsp;&nbsp;&nbsp;&nbsp;Saves all the changes and create files for new templates
###### Cancel
&nbsp;&nbsp;&nbsp;&nbsp;Exits without saving
###### Open Folder
&nbsp;&nbsp;&nbsp;&nbsp;Opens the folder with the template

#### Hotkeys

###### In the editor

- Ctrl + Enter - save the current code
- Shift + F1 - open help about the function, which is currently under the cursor
- Tab - to add a space from the current position or to highlight the code
- Tab - after the keyword template is added to the current cursor position
- Shift + Tab - to remove the indentation of the current line or selected lines
- Alt + Q - comment out or uncomment the current line or selected lines
- Ctrl + D - duplication of the line or a selected code
- Ctrl + Z - Cancel
- Ctrl + Y - Redo
- Ctrl + C - Copy
- Ctrl + X - Cut
- Ctrl + V - Paste
- Ctrl + Mouse Scroll - change the font size of the current tab
- Alt + Mouse Scroll - Editor to scroll left \ right

###### When you open the widget autocomplete

- Arrow Up / Arrow Down - move the focus on completer, select a row
- Enter - to use the current line completer. By default, the first
- Esc - close completer if it is not in focus
- Any other key - to go back to the editor and continue typing

# Installation

First, download and unzip the package pw_VEX_Editor his path PATH, PYTHONPATH or standard directory Houdini for Python scripts. For example $ HFS / Houdini / scripts / python.
Next, you need only to load the script as PythonPanel. Also, you definitely need a module hqt. Download last version!

##### Houdini 13

If you are using version 13, you have no way to open the editor as a PythonPanel. Then you can try to use module hqt. I myself am at this version of Houdini did not tested. Read the documentation of hqt, try to run.

##### Houdini 14

Since this is a common VEX Editor PythonPanel you can adjust its opening alone. Either use a ready file python_panels / vexeditor.pypanel. In addition, the 14th version of Houdini you can use the module hqt to quickly create and open PythonPanel. About how to do this, see the documentation for the module hqt.

##### Houdini 15

In Houdini version 15 implemented an excellent opportunity to add specific PythonPanel as a new Houdini panel. Therefore, you can simply add the supplied script python_panels / vexeditor.pypanel to python_panels folder in your HOUDINI_PATH and include VEX Editor to the list of panels. Hqt module is still required.

##### Linux

Installation is no different. Tests were conducted on Ubuntu, Kubuntu, and Debian.

# Using

To start writing code in the VEX Editor is enough to make three simple steps:

- VEX Editor Open in new tab (see the installation instructions)
- Select node wrangle, inline, snippet or VEX operator
- Press btn1 to quickly create tabs. The required parameter will be found automatically.

Everything is ready to edit code! Save the result at any time using a hotkey Ctrl + Enter or the button on the panel.

# Known Issues

The main problems associated with the implementation of Qt on a particular system. In view of such problems on MacOS, some interface elements do not display correctly. Their defeat is not yet possible. Therefore, for the performance of the script on the Mac I can not vouch. In the future, I will try to fix it.

Houdini 15 at this time was released recently and has a number of problems both with conventional tools and with the implementation of Qt. This is in particular caused the error in the module and replacement hqt widget auto complete list of the standard. All this will be corrected as the stabilization of Houdini.

Another problem is the custom VEX operators. To create a parameter on the custom operator you need to specify the arguments of main function. For example like this:
```
sop myoperator (int value) {
...
} 
```
Once you add the new arguments and click Apply in the Type Properties, Houdini recreates parameters of your operator. Unfortunately, the same does not occur if you replace the operator code programmatically, and in the current implementation of HOM or HScript I have not found a way to do this programmatically. I am hoping to solve this issue soon. Temporary solution to the problem - open the Type Properties window and click Accept.

 ------------------------------------------------

I really hope that this tool is useful to you in your work. Ideas for new chips and error messages as usual to send paulwinex@gmail.com.

### Thanks to lubitel for translation http://lubitel.no/
