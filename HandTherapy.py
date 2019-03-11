################################################################################
# Copyright (C) 2012-2013 Leap Motion, Inc. All rights reserved.               #
# Leap Motion proprietary and confidential. Not for distribution.              #
# Use subject to the terms of the Leap Motion SDK Agreement available at       #
# https://developer.leapmotion.com/sdk_agreement, or another agreement         #
# between Leap Motion and you, your company or other organization.             #
################################################################################

import os, sys, inspect, thread, time, threading
import random

from weka.core.dataset import Instance

src_dir = os.path.dirname(inspect.getfile(inspect.currentframe()))
# Windows and Linux
arch_dir = '../lib'
# Mac
#arch_dir = os.path.abspath(os.path.join(src_dir, '../lib'))

sys.path.insert(0, os.path.abspath(os.path.join(src_dir, arch_dir)))

import Leap

import weka.core.jvm as jvm
from weka.classifiers import Classifier
from weka.core.converters import Loader, Saver
import weka.core.converters as converters
import numpy as np

from gui2 import *

log = open("log.txt", "w")

root = Window("Hand Therapy")
goal_pos = None


class SampleListener(Leap.Listener):
    f = open("gooddata.arff", "a")
    stream = None

    def on_connect(self, controller):
        print "Connected"

    def on_frame(self, controller):
        print "Frame available"
        frame = controller.frame()

        hands = frame.hands
        fingers = frame.fingers
        print "Frame id: %d, timestamp: %d, hands: %d, fingers: %d" % (
            frame.id, frame.timestamp, len(frame.hands), len(
                frame.fingers))
        my_grab_str = -1
        for hand in hands:
            my_grab_str = hand.grab_strength
            self.stream = hand.grab_strength
        root.update_grab(my_grab_str)
        # instance = []
        # for k in range(5):
        #     for finger in fingers:
        #         if finger.type != k:
        #             continue
        #         for i in range(4):
        #             joint_pos = finger.bone(i).center.to_tuple()
        #             for j in range(3):
        #                 instance.append(joint_pos[j])
        # if instance:
        #     instance.append(3)


class Watcher:
    """ A simple class, set to watch its variable. """
    def __init__(self, listener):
        self.oldstream = listener.stream
        self.listener = listener
        self.cls = None
        self.data = None
        self.goal_position = ["open", "closed", "claw"]
        self.goal_idx = 0

    def set_value(self, new_value):
        global grab_str, gui_goal
        print "grab_strength=" + str(new_value)
        grab_str = new_value
        gui_goal = goal_pos
        if new_value == 0 and goal_pos == "open":
            print "GOOD JOB"
        # return self.goal_idx == inst_class

    def inf(self):

        while True:
            if self.oldstream != self.listener.stream:
                self.set_value(self.listener.stream)


def main():
    listener = SampleListener()
    controller = Leap.Controller()

    root.update_grab(0)
    # detector = Watcher(listener)
    #thread2 = threading.Thread(target=detector.inf)
    # thread2.start()
    controller.add_listener(listener)

    #thread2 = threading.Thread(target=root.grab_forever)
    #thread2.start()


    # detector.inf()
    # Keep this process running until Enter is pressed
    print "Press Enter to quit..."

    try:
        sys.stdin.readline()
    except KeyboardInterrupt:
        pass
    finally:
        # Remove the sample listener when done
        controller.remove_listener(listener)


if __name__ == "__main__":
    # root = Window('BioDataSorter')
    # root.geometry(str(WINDOW_WIDTH) + 'x' + str(WINDOW_HEIGHT)
    #               + '+300+300')
    # root.mainloop()

    thread1 = threading.Thread(target=main)
    thread1.start()
    root.mainloop()
