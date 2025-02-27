# Beepbox-mod-visualiser
this is a program which takes a .json file, exported from one of the many Beepbox.co mods (or itself), and generates a sequence of images, visualising each channel's notes

i will refer to "beepbox or its mods" as just "beepbox" in this document

### how to use
- export your beepbox song in the .json file format
- place the .json file in the same folder as the code, it doesn't matter how it's named

- remember to update which channels in your song are the kick channel in settings.txt with its corresponding screen shake power level (for screenshake effect)
for example: '"kick channels": {"9": 1, "5": 3}' in this case, we have channel 6 with a power level of 3 and channel 10 with a power level of 1 
(remember that the first channel is 0 unlike what beepbox have as their channel number (it starts at 1 in there))
you can also play around with the other settings, just that they have to be in the correct format and value type

- run code
- you should get a window showing you the rendering/song progress, it's not necesary but I wanted to have it instead of a boring progress bar
- each frame is saved into the "frames" folder

after it has rendered you can close the window, if you want it as a video, you're going to have to stitch these frames together with the song audio file in some video editor, I usualy just do it in blender

### keep in mind
- the visualiser doesn't stop by itself so you're going to have to catch it when it's done and turn if off yourself, otherwise it's going to keep rendering empty frames, 
you can try to fix/add that feature if you want
- if your song uses the "tempo" setting in the mod channel, it wont render properly because I couldn't figure out how to implement it

### some other info: 
I've went in before posting this to github and marked some stuff I didn't manage to add/finish or other things with a "MINT NOTE:" comment

I made the "gaze star" version for a song I was working on, the song is still WIP as I've ran out of ideas, if you want you can try to merge it with the normal visualiser and add a star option in settings.txt
