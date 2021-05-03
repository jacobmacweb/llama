# Copyright (C) 2021 Avery
#
# This file is part of llama.
#
# llama is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# llama is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with llama.  If not, see <http://www.gnu.org/licenses/>.

import os
import re
from pathlib import Path
from typing import Callable, Optional, Union

from llama.components.renderer import Renderer


class Llama:
    def __init__(self, renderers: list = None):
        self.renderers = []
        
        if renderers is not None:
            for renderer in renderers:
                self.set_renderer(*renderer)

    def set_renderer(self, pred_or_ext: Union[str, Callable[[str], bool]], renderer: Renderer):
        """
        Set the renderer for either a filename check predicate or a file
        extension

        Parameters
        ----------
        pred_or_ext : str or callable
            The extension or predicate
        renderer : Renderer
            The renderer to use
        """
        if isinstance(pred_or_ext, str):
            extension = pred_or_ext
            pred_or_ext = lambda filename: filename.endswith("." + extension)

        self.renderers.append([pred_or_ext, renderer])

    def get_renderer(self, filename: str) -> Optional[Renderer]:
        """
        Get the renderer for a filename

        Parameters
        ----------
        filename : str
            The filename

        Returns
        -------
        Renderer
            The renderer, or None if it doesn't exist
        """
        for pred, renderer in self.renderers:
            if pred(filename):
                return renderer

        return None

    def build(self, file_dir: str, target_dir: str, renderer: Renderer):
        """
        Build a given file into the target directory using the given renderer

        Parameters
        ----------
        file_dir : str
            The source file path
        target_dir : str
            The target directory
        renderer : Renderer
            The renderer to use
        """
        Path(target_dir).parent.mkdir(parents=True, exist_ok=True)
        with open(target_dir, "w+") as file:
            file.write(renderer.render(open(file_dir).read()))

    def build_from(self, source_dir: str, target_dir: str, ignore_unknown: bool = False):
        """
        Build from a source directory to a target directory

        Parameters
        ----------
        source_dir : str
            The source directory
        target_dir : str
            The target directory
        ignore_unknown : bool
            Whether to ignore unknown files
        """
        for dir_path, dirnames, filenames in os.walk(source_dir):
            for filename in filenames:
                self.handle_file(filename, dir_path, target_dir)

    def handle_file(self, filename: str, dir_path: str, target_dir: str, ignore_unknown: bool = False):
        """
        Build a file to the target directory using the appropriate renderer

        Parameters
        ----------
        filename : str
            The filename
        dir_path : str
            The directory this file is found in
        target_dir : str
            The target directory for this file
        ignore_unknown : bool
            Whether to ignore unknown extensions
        """
        name, ext = filename.split(".", 1)
        source = Path(dir_path) / filename
        target = Path(target_dir) / Path(dir_path).parent
        renderer = self.get_renderer(filename)
        if renderer:
            target /= (name + "." + renderer.extension)

            self.build(source, target, renderer)
        elif not ignore_unknown:
            target /= (name + "." + ext)

            with open(target, "w+") as file:
                file.write(open(source).read())
