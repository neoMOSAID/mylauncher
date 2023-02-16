# mylauncher
### this is a personalized dmenu launcher. it gives priority to programs frequently
### used. each execution increments the usage of the program in a sqlite database
### thus making it appear first in the dmenu list
## usage:
```shell
launcher.sh update
launcher.sh list
launcher.sh
```
## in i3 window manager config:
```shell
bindsym     $mod+x	    exec --no-startup-id /path/to/launcher.sh
```

