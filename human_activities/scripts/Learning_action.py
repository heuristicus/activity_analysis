#! /usr/bin/env python

import sys
import rospy
import actionlib
from learn_activities import Offline_ActivityLearning
from human_activities.msg import LearningActivitiesAction, LearningActivitiesResult

class Learning_server(object):
    def __init__(self, name= "LearnHumanActivities"):

        # Start server
        rospy.loginfo("Learning Human Activites action server")
        self._action_name = name
        self._as = actionlib.SimpleActionServer(self._action_name, LearningActivitiesAction,
            execute_cb=self.execute, auto_start=False)
        self._as.start()

        ol = Offline_ActivityLearning(rerun_all=0)
        self.run_cnt = 0

    def execute(self, goal):

        self.run_cnt+=1

        while not self._as.is_preempt_requested():
            ol.initialise_new_day(self.run_cnt)

            """get SOMA2 Objects"""
            ol.get_soma_objects()

            """load skeleton detections over all frames"""
            ol.get_events()

            """encode all the observations using QSRs"""
            ol.encode_qsrs()

            """create histograms with global code book"""
            ol.make_temp_histograms_sequentially()

            ol.make_term_doc_matrix()

            """create tf-idf and LSA classes"""
            ol.learn_lsa_activities()

            """learn a topic model of activity classes"""
            ol.learn_topic_model_activities()

            rospy.loginfo("completed learning phase")
        self._as.set_succeeded(LearningResult())


if __name__ == "__main__":
    rospy.init_node('learning_human_activities_server')

    Learning_server(name = "LearnHumanActivities")
    rospy.spin()
