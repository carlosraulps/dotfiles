
vim.g.mapleader = ' '
vim.g.maplocalleader = ' '
vim.g.magma_config = {
  -- Use Mamba to find Conda and Mamba environments
  find_env_with = "mamba",
  -- Automatically detect all kernels in Conda/Mamba environments
  detect_all_envs = true,
}
-- Install package manager
--    https://github.com/folke/lazy.nvim
--    `:help lazy.nvim.txt` for more info
local lazypath = vim.fn.stdpath 'data' .. '/lazy/lazy.nvim'
if not vim.loop.fs_stat(lazypath) then
  vim.fn.system {
    'git',
    'clone',
    '--filter=blob:none',
    'https://github.com/folke/lazy.nvim.git',
    '--branch=stable', -- latest stable release
    lazypath,
  }
end
vim.opt.rtp:prepend(lazypath)

-- NOTE: Here is where you install your plugins.
--  You can configure plugins using the `config` key.
--
--  You can also configure plugins after the setup call,
--    as they will be available in your neovim runtime.
require('lazy').setup({
  -- NOTE: First, some plugins that don't require any configuration

  -- Git related plugins
  'tpope/vim-fugitive',
  'tpope/vim-rhubarb',

  -- Detect tabstop and shiftwidth automatically
  'tpope/vim-sleuth',

  -- NOTE: This is where your plugins related to LSP can be installed.
  --  The configuration is done below. Search for lspconfig to find it below.
  { -- LSP Configuration & Plugins
    'neovim/nvim-lspconfig',
    dependencies = {
      -- Automatically install LSPs to stdpath for neovim
      'williamboman/mason.nvim',
      'williamboman/mason-lspconfig.nvim',

      -- Useful status updates for LSP
      -- NOTE: `opts = {}` is the same as calling `require('fidget').setup({})`
      { 'j-hui/fidget.nvim', opts = {} },

      -- Additional lua configuration, makes nvim stuff amazing!
      'folke/neodev.nvim',
    },
  },

  { -- Autocompletion
    'hrsh7th/nvim-cmp',
    dependencies = { 'hrsh7th/cmp-nvim-lsp', 'L3MON4D3/LuaSnip', 'saadparwaiz1/cmp_luasnip' },
  },

  -- Useful plugin to show you pending keybinds.
  { 'folke/which-key.nvim', opts = {} },
  {
   'dense-analysis/ale',
    config = function()
      vim.cmd [[
        let g:ale_linters = {
          \ 'fortran': ['gfortran'],
          \}
        let g:ale_fixers = {
          \ 'fortran': ['gfortran'],
          \}
        let g:ale_lint_on_text_changed = 'never'
        let g:ale_lint_on_insert_leave = 1
      ]]
    end,
  },
  { -- Adds git releated signs to the gutter, as well as utilities for managing changes
    'lewis6991/gitsigns.nvim',
    opts = {
      -- See `:help gitsigns.txt`
      signs = {
        add = { text = '+' },
        change = { text = '~' },
        delete = { text = '_' },
        topdelete = { text = '‾' },
        changedelete = { text = '~' },
      },
    },
  },

  { -- Theme inspired by Atom
    'navarasu/onedark.nvim',
    priority = 1000,
    config = function()
      vim.cmd.colorscheme 'onedark'
      require('onedark').setup {
      style = 'darker'
      }
      require('onedark').load()
    end,
  },

  { -- Set lualine as statusline
    'nvim-lualine/lualine.nvim',
    -- See `:help lualine.txt`
    opts = {
      options = {
        icons_enabled = false,
        theme = 'onedark',
        component_separators = '|',
        section_separators = '',
      },
    },
  },

  { -- Add indentation guides even on blank lines
  'lukas-reineke/indent-blankline.nvim',
  config = function()
    require("ibl").setup {
      indent = { char = "┊" },
      exclude = {
        filetypes = { "help", "terminal" },
        buftypes = { "terminal" },
      },
    }
  end,
},

  -- "gc" to comment visual regions/lines
  { 'numToStr/Comment.nvim', opts = {} },

  -- Fuzzy Finder (files, lsp, etc)
  { 'nvim-telescope/telescope.nvim', version = '*', dependencies = { 'nvim-lua/plenary.nvim' } },

  -- Fuzzy Finder Algorithm which requires local dependencies to be built.
  -- Only load if `make` is available. Make sure you have the system
  -- requirements installed.
  {
    'nvim-telescope/telescope-fzf-native.nvim',
    -- NOTE: If you are having trouble with this installation,
    --       refer to the README for telescope-fzf-native for more instructions.
    build = 'make',
    cond = function()
      return vim.fn.executable 'make' == 1
    end,
  },
  
  { -- Highlight, edit, and navigate code
  'nvim-treesitter/nvim-treesitter',
  requires = {
    'nvim-treesitter/nvim-treesitter-textobjects',
    'p00f/nvim-ts-rainbow', -- Plugin para resaltar con colores los delimitadores
              },
  config = function()
    require'nvim-treesitter.configs'.setup {
      rainbow = {
        enable = true,
        extended_mode = true, -- Highlight also non-parentheses delimiters, boolean or table: lang -> boolean
        max_file_lines = 1000, -- Do not enable for files with more than n lines, int
      }
    }
  end

  },

  {
  'dccsillag/magma-nvim',
  run = ':UpdateRemotePlugins'
  },
  {
 'kyazdani42/nvim-web-devicons',-- Ussless
 config = function ()
   vim.g.WebDevIconsUnicodeDecorateFolderNodes = 1   
 end,
  },
  {
    'preservim/nerdtree',
  requires = {'ryanoasis/vim-devicons', 'Xuyuanp/nerdtree-git-plugin'},
  config = function()
    -- Configuraciones adicionales de NERDTree aquí
    vim.g.NERDTreeShowLineNumbers = 0 -- Muestra números de línea
    vim.g.NERDTreeHighlightCursorline = 1 -- Resalta la línea del cursor
    vim.g.NERDTreeGitStatusUseNerdFonts = 1 -- Usa fuentes Nerd para los iconos de Git
    vim.g.NERDTreeGitStatusIndicatorMapCustom = {
      Modified = "✹",
      Staged = "✚",
      Untracked = "✭",
      Renamed = "➜",
      Unmerged = "═",
      Deleted = "✖",
      Dirty = "✗",
      Clean = "✔︎",
      Ignored = "☒",
      Unknown = "?"
    } -- Mapa de los iconos de Git
    vim.cmd('autocmd FileType nerdtree setlocal cursorline')
  end,
   -- cmd = 'NERDTreeToggle'
  },    --- My config
  
   { import = 'custom.plugins' },
}, {})

local lspconfig = require('lspconfig')
lspconfig.fortls.setup{}

-- My configurations
 
vim.g.magma_automatically_open_output = false
-- vim.g.magma_image_provider = "ueberzug"
-- Magma configuration
-- Activar el ambiente virtual de Conda o Mamba al iniciar neovim
-- [[ Setting options ]]
-- See `:help vim.o`
vim.o.cursorline = true
-- Set highlight on search
vim.o.hlsearch = true 

-- vim.opt.tabstop = 4 --Aparently that dont usless

vim.opt.shiftwidth = 4

-- Make line numbers default
vim.wo.number = true

-- Enable mouse mode
vim.o.mouse = 'a'

-- Sync clipboard between OS and Neovim.
--  Remove this option if you want your OS clipboard to remain independent.
--  See `:help 'clipboard'`
vim.o.clipboard = 'unnamedplus'

-- Enable break indent
vim.o.breakindent = true

-- Save undo history
vim.o.undofile = true

-- Case insensitive searching UNLESS /C or capital in search
vim.o.ignorecase = true
vim.o.smartcase = true

-- Keep signcolumn on by default
vim.wo.signcolumn = 'yes'

-- Decrease update time
vim.o.updatetime = 250
vim.o.timeout = true
vim.o.timeoutlen = 300

-- Set completeopt to have a better completion experience
vim.o.completeopt = 'menuone,noselect'

-- NOTE: You should make sure your terminal supports this
vim.o.termguicolors = true
-- [[ Basic Keymaps ]]
-- Activar autocompletado de pares de caracteres
vim.cmd([[inoremap ( ()<Left>]])
vim.cmd([[inoremap [ []<Left>]])
vim.cmd([[inoremap { {}<Left>]])
vim.cmd([[inoremap ' ''<Left>]])
vim.cmd([[inoremap " ""<Left>]])
vim.cmd([[inoremap ` ```<Right>]])

--
-- My shortcuts
--
-- Abrir una nueva pestaña
vim.keymap.set("n", "<M-x>", ":tabnew<CR>", {noremap=true})
vim.keymap.set("n", "<M-k>", ":tabnext<CR>", {noremap=true})
vim.keymap.set("n", "<M-j>", ":tabprevious<CR>", {noremap=true})

-- Abrir una nueva ventana
vim.keymap.set("n", "<M-v>",":vnew<CR>", {noremap=true})
vim.keymap.set("n", "<M-H>",":split<CR>", {noremap=true})
vim.keymap.set("n", "<M-l>",":wincmd l<CR>", {noremap=true})
vim.keymap.set("n", "<M-h>",":wincmd h<CR>", {noremap=true})

-- Abrir el gestor de archivos
vim.keymap.set("n", "<M-t>", ":NERDTree<CR>", {noremap=true})
-- Cerrar entorno
vim.keymap.set("n", "<M-Q>", ":q!<CR>", {noremap=true})
vim.keymap.set("n", "<M-q>", ":q<CR>", {noremap=true})

-- Guardar y cerrar 
vim.keymap.set("n", "<M-W>", ":wq!<CR>", {noremap=true})
vim.keymap.set("n", "<M-w>", ":w!<CR>", {noremap=true})
--
--Comentar trozo de codigo
vim.keymap.set("v", "<M-c>",":s/^/", {noremap=true})
vim.keymap.set("v", "<M-u>",":s/^", {noremap=true})

--- INdentar y desindentar
vim.keymap.set("v", "<leader>t",":>4<CR>", {noremap=true})
vim.keymap.set("v", "<leader>u",":<4<CR>", {noremap=true})
--
vim.keymap.set("n", "<M-s>", ":MagmaInit<CR>", {noremap=true})
vim.keymap.set("n", "<M-S>", ":MagmaDeinit<CR>", {noremap=true})
-- vim.keymap.set("n", "<M-e>", ":MagmaEvaluateLine<CR>", {noremap=true})
--vim.keymap.set("n", "<M-s>", ":MagmaLoad", {noremap=true})
--vim.keymap.set("n", "<M-s>", ":MagmaSave", {noremap=true})
-- vim.keymap.set("n", "<M-e>", ":MagmaEvaluateLine<CR>", {noremap=true})
vim.keymap.set("n", "<M-e>", ":MagmaEvaluateLine<CR>", {noremap=true})
vim.keymap.set("v", "<M-b>", ":<C-u>MagmaEvaluateVisual<CR>", {noremap=true})
vim.keymap.set("n", "<M-b>", ":MagmaEvaluateVisual<CR>", {noremap=true})
-- Keymaps for better default experience
-- See `:help vim.keymap.set()`
vim.keymap.set({ 'n', 'v' }, '<Space>', '<Nop>', { silent = true })

-- Remap for dealing with word wrap
vim.keymap.set('n', 'k', "v:count == 0 ? 'gk' : 'k'", { expr = true, silent = true })
vim.keymap.set('n', 'j', "v:count == 0 ? 'gj' : 'j'", { expr = true, silent = true })

-- [[ Highlight on yank ]]
-- See `:help vim.highlight.on_yank()`
local highlight_group = vim.api.nvim_create_augroup('YankHighlight', { clear = true })
vim.api.nvim_create_autocmd('TextYankPost', {
  callback = function()
    vim.highlight.on_yank()
  end,
  group = highlight_group,
  pattern = '*',
})


-------------------------CONFIGURACION PRIVADA

--  -- Cargar la configuración de lspconfig
--  local lspconfig = require'lspconfig'
--  
--  -- Configuración de Fortran LSP
--  lspconfig.fortls.setup{
--    -- Configuración adicional aquí
--  }
-- [[ Configure Telescope ]]
--
-- See `:help telescope` and `:help telescope.setup()`
require('telescope').setup {
  defaults = {
    mappings = {
      i = {
        ['<C-u>'] = false,
        ['<C-d>'] = false,
      },
    },
  },
}

-- Enable telescope fzf native, if installed
pcall(require('telescope').load_extension, 'fzf')

-- See `:help telescope.builtin`
vim.keymap.set('n', '<leader>?', require('telescope.builtin').oldfiles, { desc = '[?] Find recently opened files' })
vim.keymap.set('n', '<leader><space>', require('telescope.builtin').buffers, { desc = '[ ] Find existing buffers' })
vim.keymap.set('n', '<leader>/', function()
  -- You can pass additional configuration to telescope to change theme, layout, etc.
  require('telescope.builtin').current_buffer_fuzzy_find(require('telescope.themes').get_dropdown {
    winblend = 10,
    previewer = false,
  })
end, { desc = '[/] Fuzzily search in current buffer' })

vim.keymap.set('n', '<leader>sf', require('telescope.builtin').find_files, { desc = '[S]earch [F]iles' })
vim.keymap.set('n', '<leader>sh', require('telescope.builtin').help_tags, { desc = '[S]earch [H]elp' })
vim.keymap.set('n', '<leader>sw', require('telescope.builtin').grep_string, { desc = '[S]earch current [W]ord' })
vim.keymap.set('n', '<leader>sg', require('telescope.builtin').live_grep, { desc = '[S]earch by [G]rep' })
vim.keymap.set('n', '<leader>sd', require('telescope.builtin').diagnostics, { desc = '[S]earch [D]iagnostics' })

-- [[ Configure Treesitter ]]
-- See `:help nvim-treesitter`
require('nvim-treesitter.configs').setup {
  -- Add languages to be installed here that you want installed for treesitter
  ensure_installed = { 'c', 'cpp', 'go', 'lua', 'python', 'rust', 'tsx', 'typescript', 'vim' },

  -- Autoinstall languages that are not installed. Defaults to false (but you can change for yourself!)
  auto_install = false,

  highlight = { enable = true },
  indent = { enable = true, disable = { 'python' } },
  incremental_selection = {
    enable = true,
    keymaps = {
      init_selection = '<c-space>',
      node_incremental = '<c-space>',
      scope_incremental = '<c-s>',
      node_decremental = '<M-space>',
    },
  },
  textobjects = {
    select = {
      enable = true,
      lookahead = true, -- Automatically jump forward to textobj, similar to targets.vim
      keymaps = {
        -- You can use the capture groups defined in textobjects.scm
        ['aa'] = '@parameter.outer',
        ['ia'] = '@parameter.inner',
        ['af'] = '@function.outer',
        ['if'] = '@function.inner',
        ['ac'] = '@class.outer',
        ['ic'] = '@class.inner',
      },
    },
    move = {
      enable = true,
      set_jumps = true, -- whether to set jumps in the jumplist
      goto_next_start = {
        [']m'] = '@function.outer',
        [']]'] = '@class.outer',
      },
      goto_next_end = {
        [']M'] = '@function.outer',
        [']['] = '@class.outer',
      },
      goto_previous_start = {
        ['[m'] = '@function.outer',
        ['[['] = '@class.outer',
      },
      goto_previous_end = {
        ['[M'] = '@function.outer',
        ['[]'] = '@class.outer',
      },
    },
    swap = {
      enable = true,
      swap_next = {
        ['<leader>a'] = '@parameter.inner',
      },
      swap_previous = {
        ['<leader>A'] = '@parameter.inner',
      },
    },
  },
}

-- Diagnostic keymaps
vim.keymap.set('n', '[d', vim.diagnostic.goto_prev)
vim.keymap.set('n', ']d', vim.diagnostic.goto_next)
vim.keymap.set('n', '<leader>e', vim.diagnostic.open_float)
vim.keymap.set('n', '<leader>q', vim.diagnostic.setloclist)

-- LSP settings.
--  This function gets run when an LSP connects to a particular buffer.
local on_attach = function(_, bufnr)
  -- NOTE: Remember that lua is a real programming language, and as such it is possible
  -- to define small helper and utility functions so you don't have to repeat yourself
  -- many times.
  --
  -- In this case, we create a function that lets us more easily define mappings specific
  -- for LSP related items. It sets the mode, buffer and description for us each time.
  local nmap = function(keys, func, desc)
    if desc then
      desc = 'LSP: ' .. desc
    end

    vim.keymap.set('n', keys, func, { buffer = bufnr, desc = desc })
  end

  nmap('<leader>rn', vim.lsp.buf.rename, '[R]e[n]ame')
  nmap('<leader>ca', vim.lsp.buf.code_action, '[C]ode [A]ction')

  nmap('gd', vim.lsp.buf.definition, '[G]oto [D]efinition')
  nmap('gr', require('telescope.builtin').lsp_references, '[G]oto [R]eferences')
  nmap('gI', vim.lsp.buf.implementation, '[G]oto [I]mplementation')
  nmap('<leader>D', vim.lsp.buf.type_definition, 'Type [D]efinition')
  nmap('<leader>ds', require('telescope.builtin').lsp_document_symbols, '[D]ocument [S]ymbols')
  nmap('<leader>ws', require('telescope.builtin').lsp_dynamic_workspace_symbols, '[W]orkspace [S]ymbols')

  -- See `:help K` for why this keymap
  nmap('K', vim.lsp.buf.hover, 'Hover Documentation')
  nmap('<C-k>', vim.lsp.buf.signature_help, 'Signature Documentation')

  -- Lesser used LSP functionality
  nmap('gD', vim.lsp.buf.declaration, '[G]oto [D]eclaration')
  nmap('<leader>wa', vim.lsp.buf.add_workspace_folder, '[W]orkspace [A]dd Folder')
  nmap('<leader>wr', vim.lsp.buf.remove_workspace_folder, '[W]orkspace [R]emove Folder')
  nmap('<leader>wl', function()
    print(vim.inspect(vim.lsp.buf.list_workspace_folders()))
  end, '[W]orkspace [L]ist Folders')

  -- Create a command `:Format` local to the LSP buffer
  vim.api.nvim_buf_create_user_command(bufnr, 'Format', function(_)
    vim.lsp.buf.format()
  end, { desc = 'Format current buffer with LSP' })
end

-- Enable the following language servers
--  Feel free to add/remove any LSPs that you want here. They will automatically be installed.
--
--  Add any additional override configuration in the following tables. They will be passed to
--  the `settings` field of the server config. You must look up that documentation yourself.
local servers = {
  -- clangd = {},
  -- gopls = {},
  -- pyright = {},
  -- rust_analyzer = {},
  -- tsserver = {},
    
  lua_ls = {
    Lua = {
      workspace = { checkThirdParty = false },
      telemetry = { enable = false },
    },
  },

}

-- Setup neovim lua configuration
require('neodev').setup()

-- nvim-cmp supports additional completion capabilities, so broadcast that to servers
local capabilities = vim.lsp.protocol.make_client_capabilities()
capabilities = require('cmp_nvim_lsp').default_capabilities(capabilities)

-- Setup mason so it can manage external tooling
require('mason').setup()

-- Ensure the servers above are installed
local mason_lspconfig = require 'mason-lspconfig'

mason_lspconfig.setup {
  ensure_installed = vim.tbl_keys(servers),
}

mason_lspconfig.setup_handlers {
  function(server_name)
    require('lspconfig')[server_name].setup {
      capabilities = capabilities,
      on_attach = on_attach,
      settings = servers[server_name],
    }
  end,
}

-- nvim-cmp setup
local cmp = require 'cmp'
local luasnip = require 'luasnip'

luasnip.config.setup {}

cmp.setup {
  snippet = {
    expand = function(args)
      luasnip.lsp_expand(args.body)
    end,
  },
  mapping = cmp.mapping.preset.insert {
    ['<C-d>'] = cmp.mapping.scroll_docs(-4),
    ['<C-f>'] = cmp.mapping.scroll_docs(4),
    ['<C-Space>'] = cmp.mapping.complete {},
    ['<CR>'] = cmp.mapping.confirm {
      behavior = cmp.ConfirmBehavior.Replace,
      select = true,
    },
    ['<Tab>'] = cmp.mapping(function(fallback)
      if cmp.visible() then
        cmp.select_next_item()
      elseif luasnip.expand_or_jumpable() then
        luasnip.expand_or_jump()
      else
        fallback()
      end
    end, { 'i', 's' }),
    ['<S-Tab>'] = cmp.mapping(function(fallback)
      if cmp.visible() then
        cmp.select_prev_item()
      elseif luasnip.jumpable(-1) then
        luasnip.jump(-1)
      else
        fallback()
      end
    end, { 'i', 's' }),
  },
  sources = {
    { name = 'nvim_lsp' },
    { name = 'luasnip' },
  },
}


-- The line beneath this is called `modeline`. See `:help modeline`
-- vim: ts=2 sts=2 sw=2 et
