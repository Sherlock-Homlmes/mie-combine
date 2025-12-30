#! /bin/bash

##### SETUP
linebreak=$'\n'
red="\e[31m"
green="\e[32m"
endcolor="\e[0m"

##### INPUT

args=("$@")

### This is for install tools
if [[ ${args[0]} == "install" ]]; then
    echo $(eval "python3 -m venv env")
    echo $(eval "source env/bin/activate")
    echo $(eval "pip install -r requirements.txt")
    output="Install success. Activate env to use"
    color="$green"
elif [[ ${args[0]} == "zip" ]]; then
    echo $(eval "zip -r bot.zip . -x '/*.git/*' 'env/*'")
    output="Compress bot done"
    color="$green"
# elif [[ ${args[0]} == "discloud" ]]; then
#     echo $(eval "cd store")
#         if [[ ${args[1]} == "bot" ]]; then
#             output="Compress bot done"
#             color="$green"
#         elif [[ ${args[1]} == "site" ]]; then
#             output="Compress site done"
#             color="$green"
#         else


else
    output="Unknow command '${args[0]}'"
    color="$red"
fi

if [[ $color ]]; then
    echo -e "$color$output$endcolor"
else
    echo "$output"
fi
