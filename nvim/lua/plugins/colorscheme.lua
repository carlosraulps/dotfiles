return {
  -- Add OneDark Pro plugin
  {
    "olimorris/onedarkpro.nvim",
    priority = 1000, -- Ensure it loads first on startup
    opts = {
      styles = {
        comments = "italic",
        keywords = "bold,italic",
        functions = "italic",
        conditionals = "italic",
      },
      options = {
        transparency = false,
        terminal_colors = true,
        highlight_inactive_windows = true,
      },
    },
  },

  -- Configure LazyVim to use OneDark Pro
  {
    "LazyVim/LazyVim",
    opts = {
      colorscheme = "onedark_dark",
    },
  },
}
