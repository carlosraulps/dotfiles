if status is-interactive
    # Enable Vim-style navigation and editing in Fish
    fish_vi_key_bindings
    abbr -a pac sudo pacman -S

    # Automatically start or attach to protected base tmux session
    if not set -q TMUX
        tmux attach-session -t base 2>/dev/null; or tmux new-session -s base
    end
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
