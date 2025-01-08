"""
submission_autograder.py
------------------------
Licensing Information:  You are free to use or extend these projects for
educational purposes provided that (1) you do not distribute or publish
solutions, (2) you retain this notice, and (3) you provide clear
attribution to UC Berkeley, including a link to http://ai.berkeley.edu.

Attribution Information: The Pacman AI projects were developed at UC Berkeley.
The core projects and autograders were primarily created by John DeNero
(denero@cs.berkeley.edu) and Dan Klein (klein@cs.berkeley.edu).
Student side autograding was added by Brad Miller, Nick Hay, and
Pieter Abbeel (pabbeel@cs.berkeley.edu).
"""

import base64
import bz2

# !/usr/bin/env python
# -*- coding: utf-8 -*-


"""
CS 188 Local Submission Autograder
Written by the CS 188 Staff

==============================================================================
   _____ _              _ 
  / ____| |            | |
 | (___ | |_ ___  _ __ | |
  \___ \| __/ _ \| '_ \| |
  ____) | || (_) | |_) |_|
 |_____/ \__\___/| .__/(_)
                 | |      
                 |_|      

Modifying or tampering with this file is a violation of course policy.
If you're having trouble running the autograder, please contact the staff.
==============================================================================
"""

exec(bz2.decompress(base64.b64decode(
    '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')))
