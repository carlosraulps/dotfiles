# ranger custom commands
from __future__ import (absolute_import, division, print_function)

import os
import shutil
import subprocess
from ranger.api.commands import Command


class my_edit(Command):
    """:my_edit <filename>

    Opens a file in the default editor.
    """
    def execute(self):
        if self.arg(1):
            target_filename = self.rest(1)
        else:
            target_filename = self.fm.thisfile.path

        if not os.path.exists(target_filename):
            self.fm.notify("The given file does not exist!", bad=True)
            return

        self.fm.edit_file(target_filename)

    def tab(self, tabnum):
        return self._tab_directory_content()


class mkcd(Command):
    """:mkcd <dirname>

    Creates a directory and navigates into it.
    """
    def execute(self):
        if not self.arg(1):
            self.fm.notify("Usage: mkcd <dirname>", bad=True)
            return

        target_dir = os.path.expanduser(self.rest(1))
        if not os.path.isabs(target_dir):
            target_dir = os.path.join(self.fm.thisdir.path, target_dir)

        try:
            os.makedirs(target_dir, exist_ok=True)
            self.fm.cd(target_dir)
        except OSError as err:
            self.fm.notify("Error creating directory: {}".format(err), bad=True)


class extract(Command):
    """:extract

    Extracts selected archive(s) into current directory.
    """
    def execute(self):
        fail = []
        for f in self.fm.thistab.get_selection():
            path = f.path
            ext = f.extension.lower() if f.extension else ''
            basename = os.path.basename(path)

            if path.endswith(('.tar.gz', '.tgz')):
                cmd = ['tar', '-xzvf', path]
            elif path.endswith(('.tar.bz2', '.tbz2', '.tbz')):
                cmd = ['tar', '-xjvf', path]
            elif path.endswith(('.tar.xz', '.txz')):
                cmd = ['tar', '-xJvf', path]
            elif ext == 'tar':
                cmd = ['tar', '-xvf', path]
            elif ext == 'zip':
                if shutil.which('unzip'):
                    cmd = ['unzip', path]
                elif shutil.which('7z'):
                    cmd = ['7z', 'x', path]
                else:
                    cmd = ['bsdtar', '-xvf', path]
            elif ext == 'rar':
                if shutil.which('unrar'):
                    cmd = ['unrar', 'x', path]
                elif shutil.which('7z'):
                    cmd = ['7z', 'x', path]
                else:
                    fail.append(basename)
                    continue
            elif ext == '7z':
                if shutil.which('7z'):
                    cmd = ['7z', 'x', path]
                else:
                    fail.append(basename)
                    continue
            elif ext in ('gz', 'bz2', 'xz'):
                if shutil.which('7z'):
                    cmd = ['7z', 'x', path]
                else:
                    cmd = ['tar', '-xvf', path]
            else:
                fail.append(basename)
                continue

            self.fm.run(cmd)

        if fail:
            self.fm.notify("Unsupported or missing extractor for: {}".format(', '.join(fail)), bad=True)


class compress(Command):
    """:compress <filename.tar.gz|filename.zip|filename.7z>

    Compresses selected file(s) into an archive.
    """
    def execute(self):
        if not self.arg(1):
            self.fm.notify("Usage: compress <archive_name.tar.gz|zip|7z>", bad=True)
            return

        archive_name = self.rest(1)
        files = [os.path.relpath(f.path, self.fm.thisdir.path) for f in self.fm.thistab.get_selection()]
        if not files:
            self.fm.notify("No files selected to compress!", bad=True)
            return

        if archive_name.endswith('.zip'):
            cmd = ['zip', '-r', archive_name] + files if shutil.which('zip') else ['7z', 'a', archive_name] + files
        elif archive_name.endswith(('.tar.gz', '.tgz')):
            cmd = ['tar', '-czvf', archive_name] + files
        elif archive_name.endswith(('.tar.bz2', '.tbz2')):
            cmd = ['tar', '-cjvf', archive_name] + files
        elif archive_name.endswith(('.tar.xz', '.txz')):
            cmd = ['tar', '-cJvf', archive_name] + files
        elif archive_name.endswith('.tar'):
            cmd = ['tar', '-cvf', archive_name] + files
        elif archive_name.endswith('.7z'):
            cmd = ['7z', 'a', archive_name] + files
        else:
            cmd = ['tar', '-czvf', archive_name + '.tar.gz'] + files

        self.fm.run(cmd)

    def tab(self, tabnum):
        return self._tab_directory_content()


class fzf_select(Command):
    """:fzf_select

    Find a file or directory using fzf and select/cd into it.
    """
    def execute(self):
        if not shutil.which('fzf'):
            self.fm.notify("fzf is not installed!", bad=True)
            return

        if self.fm.settings.show_hidden:
            find_cmd = "find -L . \\( -path '*/.*' -o -fstype 'dev' -o -fstype 'proc' \\) -prune -o -print 2> /dev/null | sed 1d | cut -b3- | fzf +m"
        else:
            find_cmd = "find -L . -maxdepth 5 -not -path '*/.*' 2> /dev/null | sed 1d | cut -b3- | fzf +m"

        fzf = self.fm.execute_command(find_cmd, universal_newlines=True, stdout=subprocess.PIPE)
        stdout, _ = fzf.communicate()
        if fzf.returncode == 0 and stdout.strip():
            selected = os.path.abspath(os.path.join(self.fm.thisdir.path, stdout.strip()))
            if os.path.isdir(selected):
                self.fm.cd(selected)
            else:
                self.fm.select_file(selected)


class fzf_locate(Command):
    """:fzf_locate

    Quickly locate files on system using fzf.
    """
    def execute(self):
        if not shutil.which('fzf'):
            self.fm.notify("fzf is not installed!", bad=True)
            return

        if shutil.which('locate'):
            loc_cmd = "locate /home | fzf --header='Locate file' +m"
        else:
            loc_cmd = "find ~ -maxdepth 4 2>/dev/null | fzf --header='Find file' +m"

        fzf = self.fm.execute_command(loc_cmd, universal_newlines=True, stdout=subprocess.PIPE)
        stdout, _ = fzf.communicate()
        if fzf.returncode == 0 and stdout.strip():
            selected = os.path.abspath(stdout.strip())
            if os.path.isdir(selected):
                self.fm.cd(selected)
            else:
                self.fm.select_file(selected)

