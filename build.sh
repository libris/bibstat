#!/bin/sh
cd build
# Minify Stylesheets
r.js -o css.build.js
# Minify main.js and dependency third party scripts
r.js -o js.buildmain.js
# Minify main_survey.js and dependency third party scripts
r.js -o js.buildsurvey.js
