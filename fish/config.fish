
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
alias push='git push -u origin master'
alias gstatus='git status'
alias gpull='git pull origin master'
alias gpnr='git pull --no-rebase origin master'

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
alias 'p3'='python3'
alias 'pyr'='python3 -m pip freeze > requirements.txt'


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


set -x PYENV_ROOT $HOME/.pyenv
set -x PATH $PYENV_ROOT/bin $PATH
# Aggiungi il binario di vaspkit all’inizio del PATH
set -gx PATH /home/crls/documents/research/abc/vaspkit.1.3.5/bin $PATH

# Enable pyenv init
# echo 'status --is-interactive; and . (pyenv init -|psub)' >> ~/.config/fish/config.fish

set -Ux CUDA_HOME /opt/cuda
set -Ux PATH $CUDA_HOME/bin $PATH
set -Ux LD_LIBRARY_PATH $CUDA_HOME/lib64 $LD_LIBRARY_PATH

function ClipboardCopy
  commandline -s | xclip -selection clipboard
end

# Source
# starship init fish | source

# >>> conda initialize >>>
# !! Contents within this block are managed by 'conda init' !!
if test -f /opt/miniconda3/bin/conda
    eval /opt/miniconda3/bin/conda "shell.fish" "hook" $argv | source
else
    if test -f "/opt/miniconda3/etc/fish/conf.d/conda.fish"
        . "/opt/miniconda3/etc/fish/conf.d/conda.fish"
    else
        set -x PATH "/opt/miniconda3/bin" $PATH
    end
end

# <<< conda initialize <<<
status --is-interactive; and . (pyenv init -|psub)

set -Ux fish_user_path $fish_user_paths /home/crls/.local/share/gem/ruby/3.3.0/bin
set -Ux fish_user_paths $HOME/.rbenv/bin $fish_user_paths



function sn8
    if test (count $argv) -ne 1
        echo "Usage: sn8 <file-or-directory>"
        return 1
    end

    set path $argv[1]
    # Bastion (passarela) SSH endpoint
    set bastion "carlos@gmcan.unmsm.edu.pe:7722"
    # Destination node (CN08)
    set remote "carlos@192.168.16.128"
    # Remote home directory
    set dest "$remote:/home/carlos/"

    if test -d $path
        # If it's a directory, copy recursively
        scp -r -o ProxyJump="$bastion" $path $dest
    else if test -f $path
        # If it's a regular file
        scp -o ProxyJump="$bastion" $path $dest
    else
        echo "Error: '$path' not found"
        return 1
    end
end



# --------------------------------------------------------------------------------------------------
# get8dir: scarica una directory intera da CN08 al locale via bastion
# Uso: get8dir <percorso/remoto> <destinazione/locale>
# --------------------------------------------------------------------------------------------------
function get8dir
    # controllo argomenti
    if test (count $argv) -ne 2
        echo "Utilizzo: get8dir <percorso/remoto> <destinazione/locale>"
        return 1
    end

    # parametri
    set -l bastion bastiao
    set -l remote  cn128
    set -l rpath   $argv[1]
    set -l dest    $argv[2]

    # espandi ~ in $HOME se necessario
    set dest (string replace -r '^~' $HOME $dest)

    # crea destinazione
    mkdir -p -- "$dest"

    # esegue lo scp ricorsivo
    scp -r -J $bastion $remote:$rpath $dest
end

# --------------------------------------------------------------------------------------------------
# gn8: scarica file o directory da CN08 al locale via bastion
# Uso: gn8 <percorso/remoto> <destinazione/locale>
# --------------------------------------------------------------------------------------------------
function gn8
    # 1) Controllo che ci siano almeno 2 argomenti (una o più sorgenti + destinazione)
    if test (count $argv) -lt 2
        echo "Utilizzo: gn8 <percorso/remoto>... <destinazione/locale>"
        return 1
    end

    # 2) Parametri di connessione (bastion e host remoto definiti in ~/.ssh/config)
    set -l bastion bastiao
    set -l remote  cn128

    # 3) Destinazione: ultimo argomento
    set -l dest $argv[-1]
    # espandi tilde se presente
    set dest (string replace -r '^~' $HOME $dest)

    # 4) Crea la directory locale (dirname in caso di file)
    mkdir -p -- (dirname $dest)

    # 5) Raccolgo tutti i percorsi remoti (tutti gli argv tranne l’ultimo)
    set -l sources $argv[1..-2]

    # 6) Preparo la lista "host:path" per scp
    set -l rpaths
    for src in $sources
        set rpaths $rpaths $remote:$src
    end

    # 7) Copia ricorsiva di tutti i sorgenti nella destinazione
    scp -r -J $bastion $rpaths $dest
end

function snhuk
    if test (count $argv) -ne 1
        echo "Uso: sn_huk <archivo_o_directorio>"
        return 1
    end

    set -l path $argv[1]
    # Alias definidos en ~/.ssh/config
    set -l bastion bastiao
    set -l remote  huk
    set -l dest    "$remote:/home/carlos/"

    if test -d $path
        scp -r -J $bastion $path $dest
    else if test -f $path
        scp -J $bastion $path $dest
    else
        echo "Error: '$path' no existe"
        return 1
    end
end

function gnhuk
    if test (count $argv) -lt 2
        echo "Uso: gnhuk <ruta/remota>... <destino/local>"
        return 1
    end

    set -l bastion bastiao
    set -l remote  huk

    set -l dest $argv[-1]
    set dest (string replace -r '^~' $HOME $dest)
    mkdir -p -- (dirname $dest)

    set -l sources $argv[1..-2]
    set -l rpaths
    for src in $sources
        set rpaths $rpaths $remote:$src
    end

    scp -r -J $bastion $rpaths $dest
end

# VASPKIT environment variables
set -gx PATH /home/crls/downloads/vaspkit.1.5.1/bin $PATH
set -gx VASPKIT_UTILITIES_PATH /home/crls/downloads/vaspkit.1.5.1/utilities
