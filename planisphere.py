#!/usr/bin/python3
# planisphere.py
# -*- coding: utf-8 -*-
#
# The python script in this file makes the various parts of a model planisphere.
#
# Copyright (C) 2014-2023 Dominic Ford <https://dcford.org.uk/>
#
# This code is free software; you can redistribute it and/or modify it under
# the terms of the GNU General Public License as published by the Free Software
# Foundation; either version 2 of the License, or (at your option) any later
# version.
#
# You should have received a copy of the GNU General Public License along with
# this file; if not, write to the Free Software Foundation, Inc., 51 Franklin
# Street, Fifth Floor, Boston, MA  02110-1301, USA

# ----------------------------------------------------------------------------

"""
This is the top level script for drawing all the parts needed to build planispheres which work at a range of
different latitudes. They are rendered in PDF, SVG and PNG image formats.

Additionally, we use LaTeX to build a summary document for each latitude, which includes all of the parts needed
to build a planisphere for that latitude, and instructions as to how to put them together.
"""

import os
import subprocess
import time
import shutil

import text
from alt_az import AltAzGrid
from holder import Holder
from settings import fetch_command_line_arguments
from starwheel import StarWheel

# Create output directory
try:
    shutil.rmtree("output")
except:
    pass
os.mkdir("output")

arguments = fetch_command_line_arguments()
theme = arguments['theme']

lats = [int(arguments['latitude'])] if ':' not in arguments['latitude'] else (range(int(arguments['latitude'].split(":")[0]), int(arguments['latitude'].split(":")[1])) if len(arguments['latitude'].split(":")) == 2 else range(int(arguments['latitude'].split(":")[0]), int(arguments['latitude'].split(":")[1]), int(arguments['latitude'].split(":")[2])))

# Render planisphere in all available languages
for language in text.text:

    # Render climates for latitudes at 5-degree spacings from 10 deg -- 85 deg, plus 52N
    for latitude in lats:
        
        # Do not make equatorial planispheres, as they don't really work
        if -10 < latitude < 10:
            continue

        # Boolean flag for which hemiphere we're in
        southern = latitude < 0

        # A dictionary of common substitutions
        subs = {
            "dir_parts": "output",
            "abs_lat": abs(latitude),
            "ns": "S" if southern else "N",
            "lang": language,
            "lang_short": "" if language == "en" else "_{}".format(language)
        }

        settings = {
            'language': language,
            'latitude': latitude,
            'theme': theme
        }

        # Render the various parts of the planisphere
        StarWheel(settings=settings).render_all_formats(
            filename="{dir_parts}/starwheel_{abs_lat:02d}{ns}_{lang}".format(**subs)
        )

        Holder(settings=settings).render_all_formats(
            filename="{dir_parts}/holder_{abs_lat:02d}{ns}_{lang}".format(**subs)
        )

        AltAzGrid(settings=settings).render_all_formats(
            filename="{dir_parts}/alt_az_grid_{abs_lat:02d}{ns}_{lang}".format(**subs)
        )

        # Copy the PDF versions of the components of this astrolabe into LaTeX's working directory, to produce a
        # PDF file containing all the parts of this astrolabe
        shutil.copy("{dir_parts}/starwheel_{abs_lat:02d}{ns}_{lang}.pdf".format(**subs), "doc/tmp/starwheel.pdf")
        shutil.copy("{dir_parts}/holder_{abs_lat:02d}{ns}_{lang}.pdf".format(**subs), "doc/tmp/holder.pdf")
        shutil.copy("{dir_parts}/alt_az_grid_{abs_lat:02d}{ns}_{lang}.pdf".format(**subs), "doc/tmp/altaz.pdf")

        with open("doc/tmp/lat.tex", "wt") as f:
            f.write(r"${abs_lat:d}^\circ${ns}".format(**subs))
