#!/bin/sh

WORKINGDIR="$( cd -- "$(dirname "$0")" >/dev/null 2>&1 ; pwd -P )"
pythonScript="${WORKINGDIR}/database.py"

clean_up(){
	while read -r file ; do
		if ! [ -f "$file" ] ; then
			echo "removed: $file"
			python "$pythonScript" del "$file"
		fi
	done <<< "$( python "$pythonScript" get | jq -r '.[]|.location' )"
}

update(){
	tmpfile="/tmp/mydmenu_update_file.csv"
	rm "$tmpfile" 2>/dev/null
	while IFS= read -r -u 3 -d ':'  dir ; do
		#echo "===================================== $dir"
		find "$dir" -type f -iname "*.desktop" -exec grep -L 'NoDisplay=true' {} \; 2>/dev/null |
		while read -r file ; do
			location="$file"
			tname="$(sed -n '/^[nN]ame=/p' "$file" | sed 's/^[nN]ame=//' | tr '\n' ' ' | sed 's/[ \t]*$//' )"
			name=$(echo "$tname" | cut -d' ' -f1,2)
			#echo $file === $name
			exec="$(sed -n '/^[eE]xec=/{s/^[eE]xec=//;s/ %.*//;p;q}' "$file" | tr '\n' ' '  | sed 's/[ \t]*$//' )"
			[[ -z "$exec" ]] && continue
			description="$(sed -n '/^[cC]ategories=/p' "$file" | sed 's/^[cC]ategories=//'  | tr '\n' ' '  | sed 's/[ \t]*$//' )"
			echo "$name,$exec,$location,$description $tname" >> "$tmpfile"
		done
	done 3<<< "$HOME/.local/share/applications:/usr/share/applications:/usr/local/share/applications:"
	python "$pythonScript" update
}

if [ "$1" = "update" ] ; then
	update
	clean_up
	exit
fi

if [ "$1" = "list" ] ; then
	python $WORKINGDIR/database.py get | jq -r '.[]|select(.name)' | less
	exit
fi


data=$(python "$pythonScript" get)
selected=$( echo "$data" | jq -r '.[]|.name' | dmenu -i -fn monospace:20 -p run )
[[ -n "$selected" ]] || exit
program=$(echo "$data" | jq -r ".[]|select(.name|match(\"$selected\"))|.exec" )
python "$pythonScript" increment "$selected"
#echo "$selected"
#echo "$program"
echo "$program" | ${SHELL:-"/bin/sh"} &
