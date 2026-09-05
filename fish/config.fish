if status is-interactive
    # Enable Vim-style navigation and editing in Fish
    fish_vi_key_bindings
    abbr -a pac sudo pacman -S

    # Quick alias to jump into protected persistent tmux session
    alias tm "tmux attach-session -t base 2>/dev/null; or tmux new-session -s base"
end

fish_add_path $HOME/.local/bin
fish_add_path $HOME/computational-materials-suite/bin
fish_add_path $HOME/.gemini/antigravity-cli/bin

set -gx MATERIALS_SUITE_DIR $HOME/computational-materials-suite
set -gx EDITOR nvim
set -gx VISUAL nvim

set -g fish_greeting ""

if type -q starship
    starship init fish | source
end

alias r ranger
alias "c." "cd .."
alias sp spotatui
alias nv nvim
alias n nvim
alias vim nvim
alias nano nvim
alias ntl "nvim to-do-list.txt"

alias ls exa
alias vesta "env GTK_THEME=Adwaita:dark /usr/bin/VESTA"
alias VESTA "env GTK_THEME=Adwaita:dark /usr/bin/VESTA"

# Materials Project API Key
set -gx MP_API_KEY "12HpMWJB5cHfd4zv3BCIaVKKOJ6h3ICX"
set -gx PMG_MAPI_KEY "12HpMWJB5cHfd4zv3BCIaVKKOJ6h3ICX"
set -gx MATERIALS_PROJECT_API_KEY "12HpMWJB5cHfd4zv3BCIaVKKOJ6h3ICX"

# ==============================================================================
#  HPC Cluster File Transfer Suite (Huk, Carbono, Titanio, Bastião)
# ==============================================================================

function __cluster_send -d "Upload local files/directories to a remote HPC host"
    set -l host $argv[1]
    set -l files $argv[2..-1]

    if test (count $files) -lt 1
        set_color red
        echo "Uso: sn$host <origen>... [directorio_remoto]"
        set_color normal
        return 1
    end

    set -l sources
    set -l dest ""

    if test (count $files) -gt 1
        set -l last_arg $files[-1]
        # If last argument ends in / or does not exist locally, treat as remote destination
        if string match -q -r '/$' "$last_arg"; or not test -e "$last_arg"
            set sources $files[1..-2]
            set dest $last_arg
        else
            set sources $files
        end
    else
        set sources $files[1]
    end

    set -l target
    if test -z "$dest"; or test "$dest" = "."
        set target "$host:"
    else
        set target "$host:$dest"
    end

    set_color cyan
    echo "➜ [$host] Subiendo "(count $sources)" elemento(s) hacia $target"
    set_color normal
    scp -r -p $sources "$target"
end

function __cluster_get -d "Download remote files/directories from an HPC host"
    set -l host $argv[1]
    set -l items $argv[2..-1]

    if test (count $items) -lt 1
        set_color red
        echo "Uso: gn$host <ruta/remota>... [destino/local]"
        set_color normal
        return 1
    end

    set -l rpaths
    set -l dest "."

    if test (count $items) -gt 1
        set -l last_arg $items[-1]
        set -l last_expanded (string replace -r '^~' "$HOME" "$last_arg")
        if test -d "$last_expanded"; or string match -q -r '/$' "$last_arg"; or test "$last_arg" = "."
            set dest $last_expanded
            set -l remotes $items[1..-2]
            for r in $remotes
                set rpaths $rpaths "$host:$r"
            end
        else
            for r in $items
                set rpaths $rpaths "$host:$r"
            end
        end
    else
        set rpaths "$host:$items[1]"
    end

    # Create local destination directory if needed
    if test "$dest" != "."
        if test -d "$dest"; or string match -q -r '/$' "$dest"
            mkdir -p -- "$dest"
        else
            set -l parent (dirname "$dest")
            mkdir -p -- "$parent"
        end
    end

    set_color green
    echo "➜ [$host] Descargando "(count $rpaths)" elemento(s) hacia $dest"
    set_color normal
    scp -r -p $rpaths "$dest"
end

# --- Huk Cluster (via Bastião jump host) ---
function snhuk -d "Enviar archivos a Huk"; __cluster_send huk $argv; end
function gnhuk -d "Descargar archivos de Huk"; __cluster_get huk $argv; end
alias snh snhuk
alias gnh gnhuk
alias sshuk "ssh huk"
complete -c snhuk -F
complete -c snh -F

# --- Carbono Cluster (UFABC) ---
function sncarbono -d "Enviar archivos a Carbono"; __cluster_send carbono $argv; end
function gncarbono -d "Descargar archivos de Carbono"; __cluster_get carbono $argv; end
alias snc sncarbono
alias gnc gncarbono
alias sshc "ssh carbono"
complete -c sncarbono -F
complete -c snc -F

# --- Titanio Cluster (UFABC) ---
function sntitanio -d "Enviar archivos a Titanio"; __cluster_send titanio $argv; end
function gntitanio -d "Descargar archivos de Titanio"; __cluster_get titanio $argv; end
alias snt sntitanio
alias gnt gntitanio
alias ssht "ssh titanio"
complete -c sntitanio -F
complete -c snt -F

# --- Bastião Gateway (UNMSM) ---
function snbastiao -d "Enviar archivos a Bastião gateway"; __cluster_send bastiao $argv; end
function gnbastiao -d "Descargar archivos de Bastião gateway"; __cluster_get bastiao $argv; end
alias snb snbastiao
alias gnb gnbastiao
alias sshb "ssh bastiao"
complete -c snbastiao -F
complete -c snb -F
