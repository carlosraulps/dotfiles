
set fish_greeting ""
set fish_mode_prompt ''

# Alias 

alias s='sudo'
alias ssn='sudo shutdown now'
alias srn='sudo reboot now'

alias cab='conda activate base'
alias mab='mamba activate base'
alias vim='nvim'
alias vi='nvim'
alias n='nvim'
alias sn='sudo nvim'

alias r='ranger'
alias z='zathura'
alias pm='mocp -T /home/crlsrl/pmi/mocp-themes/rhowaldt'

alias 'a.'='git add .'
alias add='git add'
alias clone='git clone'
alias commit='git commit -m'
alias push='git push'
alias gstatus='git status'

alias spu='sudo pacman -Syu'
alias spi='sudo pacman -Sy'
alias sps='sudo pacman -Ss'
alias spr='sudo pacman -Rns'

alias yu='yay -Syu'
alias yi='yay -Sy'
alias ys='yay -Ss'
alias yr='yay -Rns'

alias 'c.'='cd ..'

alias gfc='gfortran -c'


function gf
    set -l num_args (count $argv)
    set -l main_file (string join " " $argv[1..(math $num_args - 1)])
    set -l output_file (string replace ".f08" ".out" $argv[$num_args])

    gfortran $main_file $argv[$num_args] -o outputs/$output_file
    echo "Compiled $argv[$num_args] to outputs/$output_file"

    #set -l exe_file (string replace ".f08" ".exe" $argv[$num_args])
    #cp outputs/$output_file outputs/$exe_file
    #echo "Copied $output_file to $exe_file"
end
alias bt='bluetoothctl'
alias bton='sudo systemctl start bluetooth.service && sudo rfkill unblock bluetooth'
alias btoff='sudo systemctl stop bluetooth.service && sudo rfkill block bluetooth'
alias btrst='sudo systemctl restart bluetooth.service && sudo rfkill unblock bluetooth'

alias wfon='sudo ip link set wlp4s0 up'
alias wfoff='sudo ip link set wlp4s0 down'

alias storage='df -hT /'
alias battery='acpi -V'

alias grep="grep --color=auto"
alias cat="bat --style=plain --paging=never"
alias ls="exa --group-directories-first"
alias ll="ls -la"
alias tree="exa -T"
alias egrep='grep -E'

alias ':D'='echo "Dos puntos d mayuscula."'
alias 'crj'='echo "Carajo como el pericote?"'

# Prompt

set -gx PATH $HOME/.local/bin $PATH
set -x PATH $PATH /root/.local/share/gem/ruby/3.0.0/bin
set -x VISUAL nvim
set -g SPACEFISH_PROMPT_CHAR_DISPLAY false

function ClipboardCopy
  commandline -s | xclip -selection clipboard
end

# Source
# starship init fish | source

# >>> conda initialize >>>
if test -f /home/crlsrl/miniconda3/bin/conda
    eval /home/crlsrl/miniconda3/bin/conda "shell.fish" "hook" $argv | source
end


if test -f "/home/crlsrl/miniconda3/etc/fish/conf.d/mamba.fish"
    source "/home/crlsrl/miniconda3/etc/fish/conf.d/mamba.fish"
end
# <<< conda initialize <<<
