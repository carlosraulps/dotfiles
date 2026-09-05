-- Options are automatically loaded before lazy.nvim startup
-- Default options that are always set: https://github.com/LazyVim/LazyVim/blob/main/lua/lazyvim/config/options.lua
-- Add any additional options here

-- System clipboard integration
vim.opt.clipboard = "unnamedplus"

-- Text wrapper: Soft wrap lines so all text fits in the terminal window
vim.opt.wrap = true
vim.opt.linebreak = true -- Wrap lines at word boundaries (never split words in half)
vim.opt.breakindent = true -- Visually align wrapped lines with parent indentation level
vim.opt.showbreak = "↳ " -- Clean visual indicator for wrapped lines
