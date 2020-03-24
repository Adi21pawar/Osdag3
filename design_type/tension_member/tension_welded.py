from design_type.connection.shear_connection import ShearConnection
from PyQt5.QtWidgets import QMessageBox
from PyQt5 import QtCore, QtGui, QtWidgets
from utils.common.component import Bolt, Plate, Weld
# from gui.ui_summary_popup import Ui_Dialog
from utils.common.component import *
# from cad.common_logic import CommonDesignLogic
from utils.common.material import *
from Common import *
from utils.common.load import Load
import yaml
from design_report.reportGenerator import save_html
import os
import shutil
import logging
from PyQt5.QtCore import QFile, pyqtSignal, QTextStream, Qt, QIODevice
from PyQt5.QtCore import QRegExp
from PyQt5.QtGui import QBrush
from PyQt5.QtGui import QColor
from PyQt5.QtGui import QDoubleValidator, QIntValidator, QPixmap, QPalette
from PyQt5.QtGui import QTextCharFormat
from PyQt5.QtGui import QTextCursor
from PyQt5.QtWidgets import QMainWindow, QDialog, QFontDialog, QApplication, QFileDialog, QColorDialog,QMessageBox
import pickle
import pdfkit
import configparser
from main import Main
import cairosvg
from io import StringIO

#from ...gui.newnew import Ui_Form
#newnew_object = Ui_Form()

# connectivity = "column_flange_beam_web"
# supporting_member_section = "HB 400"
# fy = 250.0
# fu = 410.0
# shear_force = 100.0
# axial_force=100.0
# bolt_diameter = 24.0
# bolt_type = "friction_grip"
# bolt_grade = 8.8
# plate_thickness = 10.0
# weld_size = 6
# material_grade = "E 250 (Fe 410 W)B"
# material = Material(material_grade)


class Tension_welded(Main):

    def __init__(self):
        super(Tension_welded, self).__init__()


        self.design_status = False

    def set_osdaglogger(key):

        """
        Function to set Logger for Tension Module
        """

        # @author Arsil Zunzunia
        global logger
        logger = logging.getLogger('osdag')

        logger.setLevel(logging.DEBUG)
        handler = logging.StreamHandler()
        # handler.setLevel(logging.DEBUG)
        formatter = logging.Formatter(fmt='%(asctime)s - %(name)s - %(levelname)s - %(message)s', datefmt='%H:%M:%S')

        handler.setFormatter(formatter)
        logger.addHandler(handler)
        handler = logging.FileHandler('logging_text.log')

        # handler.setLevel(logging.DEBUG)
        formatter = logging.Formatter(fmt='%(asctime)s - %(name)s - %(levelname)s - %(message)s', datefmt='%H:%M:%S')
        handler.setFormatter(formatter)
        logger.addHandler(handler)
        # handler.setLevel(logging.INFO)
        # formatter = logging.Formatter(fmt='%(asctime)s - %(name)s - %(levelname)s - %(message)s', datefmt='%H:%M:%S')
        # handler.setFormatter(formatter)
        # logger.addHandler(handler)
        handler = OurLog(key)
        # handler.setLevel(logging.DEBUG)
        formatter = logging.Formatter(fmt='%(asctime)s - %(name)s - %(levelname)s - %(message)s', datefmt='%H:%M:%S')
        handler.setFormatter(formatter)
        logger.addHandler(handler)

    def module_name(self):
        return KEY_DISP_TENSION_WELDED

    def customized_input(self):

        c_lst = []

        t1 = (KEY_SECSIZE, self.fn_profile_section)
        c_lst.append(t1)
        t2 = (KEY_GRD, self.grdval_customized)
        c_lst.append(t2)
        t3 = (KEY_D, self.diam_bolt_customized)
        c_lst.append(t3)
        t4 = (KEY_PLATETHK, self.plate_thick_customized)
        c_lst.append(t4)
        t5 = (KEY_SEC_PROFILE, self.fn_conn_type)
        c_lst.append(t5)

        return c_lst

    def fn_profile_section(self):
        print(self,"2")
        if self == 'Beams':
            return connectdb("Beams", call_type="popup")
        elif self == 'Columns':
            return connectdb("Columns", call_type= "popup")
        elif self in ['Angles', 'Back to Back Angles', 'Star Angles']:
            return connectdb("Angles", call_type= "popup")
        elif self in ['Channels', 'Back to Back Channels']:
            return connectdb("Channels", call_type= "popup")

    def input_value_changed(self):

        lst = []

        t1 = (KEY_SEC_PROFILE, KEY_LOCATION, TYPE_COMBOBOX, self.fn_conn_type)
        lst.append(t1)

        t2 = (KEY_SEC_PROFILE, KEY_SECSIZE, TYPE_COMBOBOX_CUSTOMIZED, self.fn_profile_section)
        lst.append(t2)

        return lst

    def fn_conn_type(self):
        print(self,"1")
        if self in ['Angles', 'Back to Back Angles', 'Star Angles']:
            b = VALUES_LOCATION_1
        elif self in ["Channels", "Back to Back Channels"]:
            b = VALUES_LOCATION_2
        return b

    def tab_list(self):
        tabs = []

        t1 = (KEY_DISP_COLSEC, TYPE_TAB_1, self.tab_column_section)
        tabs.append(t1)

        t2 = (KEY_DISP_BEAMSEC, TYPE_TAB_1, self.tab_beam_section)
        tabs.append(t2)

        t3 = (DISP_TITLE_ANGLE, TYPE_TAB_1, self.tab_angle_section)
        tabs.append(t3)

        t4 = ("Bolt", TYPE_TAB_2, self.bolt_values)
        tabs.append(t4)

        t5 = ("Weld", TYPE_TAB_2, self.weld_values)
        tabs.append(t5)

        t6 = ("Detailing", TYPE_TAB_2, self.detailing_values)
        tabs.append(t6)

        t7 = ("Design", TYPE_TAB_2, self.design_values)
        tabs.append(t7)

        return tabs

    @staticmethod
    def tab_column_section():
        supporting_section = []

        t34 = (KEY_SUPTNGSEC, KEY_DISP_COLSEC, TYPE_COMBOBOX, [])
        supporting_section.append(t34)

        t1 = (KEY_SUPTNGSEC_DESIGNATION, KEY_DISP_SUPTNGSEC_DESIGNATION, TYPE_TEXTBOX, None)
        supporting_section.append(t1)

        t2 = (None, KEY_DISP_MECH_PROP, TYPE_TITLE, None)
        supporting_section.append(t2)

        t3 = (KEY_SUPTNGSEC_FU, KEY_DISP_SUPTNGSEC_FU, TYPE_TEXTBOX, None)
        supporting_section.append(t3)

        t4 = (KEY_SUPTNGSEC_FY, KEY_DISP_SUPTNGSEC_FY, TYPE_TEXTBOX, None)
        supporting_section.append(t4)

        t5 = (None, KEY_DISP_DIMENSIONS, TYPE_TITLE, None)
        supporting_section.append(t5)

        t6 = (KEY_SUPTNGSEC_DEPTH, KEY_DISP_SUPTNGSEC_DEPTH, TYPE_TEXTBOX, None)
        supporting_section.append(t6)

        t7 = (KEY_SUPTNGSEC_FLANGE_W, KEY_DISP_SUPTNGSEC_FLANGE_W, TYPE_TEXTBOX, None)
        supporting_section.append(t7)

        t8 = (KEY_SUPTNGSEC_FLANGE_T, KEY_DISP_SUPTNGSEC_FLANGE_T, TYPE_TEXTBOX, None)
        supporting_section.append(t8)

        t9 = (KEY_SUPTNGSEC_WEB_T, KEY_DISP_SUPTNGSEC_WEB_T, TYPE_TEXTBOX, None)
        supporting_section.append(t9)

        t10 = (KEY_SUPTNGSEC_FLANGE_S, KEY_DISP_SUPTNGSEC_FLANGE_S, TYPE_TEXTBOX, None)
        supporting_section.append(t10)

        t11 = (KEY_SUPTNGSEC_ROOT_R, KEY_DISP_SUPTNGSEC_ROOT_R, TYPE_TEXTBOX, None)
        supporting_section.append(t11)

        t12 = (KEY_SUPTNGSEC_TOE_R, KEY_DISP_SUPTNGSEC_TOE_R, TYPE_TEXTBOX, None)
        supporting_section.append(t12)

        t13 = (None, None, TYPE_BREAK, None)
        supporting_section.append(t13)

        t35 = (None, None, TYPE_ENTER, None)
        supporting_section.append(t35)

        t14 = (KEY_SUPTNGSEC_TYPE, KEY_DISP_SUPTNGSEC_TYPE, TYPE_COMBOBOX, ['Rolled', 'Welded'])
        supporting_section.append(t14)

        t18 = (None, None, TYPE_ENTER, None)
        supporting_section.append(t18)

        t15 = (KEY_SUPTNGSEC_MOD_OF_ELAST, KEY_SUPTNGSEC_DISP_MOD_OF_ELAST, TYPE_TEXTBOX, None)
        supporting_section.append(t15)

        t16 = (KEY_SUPTNGSEC_MOD_OF_RIGID, KEY_SUPTNGSEC_DISP_MOD_OF_RIGID, TYPE_TEXTBOX, None)
        supporting_section.append(t16)

        t17 = (None, KEY_DISP_SEC_PROP, TYPE_TITLE, None)
        supporting_section.append(t17)

        t18 = (KEY_SUPTNGSEC_MASS, KEY_DISP_SUPTNGSEC_MASS, TYPE_TEXTBOX, None)
        supporting_section.append(t18)

        t19 = (KEY_SUPTNGSEC_SEC_AREA, KEY_DISP_SUPTNGSEC_SEC_AREA, TYPE_TEXTBOX, None)
        supporting_section.append(t19)

        t20 = (KEY_SUPTNGSEC_MOA_LZ, KEY_DISP_SUPTNGSEC_MOA_LZ, TYPE_TEXTBOX, None)
        supporting_section.append(t20)

        t21 = (KEY_SUPTNGSEC_MOA_LY, KEY_DISP_SUPTNGSEC_MOA_LY, TYPE_TEXTBOX, None)
        supporting_section.append(t21)

        t22 = (KEY_SUPTNGSEC_ROG_RZ, KEY_DISP_SUPTNGSEC_ROG_RZ, TYPE_TEXTBOX, None)
        supporting_section.append(t22)

        t23 = (KEY_SUPTNGSEC_ROG_RY, KEY_DISP_SUPTNGSEC_ROG_RY, TYPE_TEXTBOX, None)
        supporting_section.append(t23)

        t24 = (KEY_SUPTNGSEC_EM_ZZ, KEY_DISP_SUPTNGSEC_EM_ZZ, TYPE_TEXTBOX, None)
        supporting_section.append(t24)

        t25 = (KEY_SUPTNGSEC_EM_ZY, KEY_DISP_SUPTNGSEC_EM_ZY, TYPE_TEXTBOX, None)
        supporting_section.append(t25)

        t26 = (KEY_SUPTNGSEC_PM_ZPZ, KEY_DISP_SUPTNGSEC_PM_ZPZ, TYPE_TEXTBOX, None)
        supporting_section.append(t26)

        t27 = (KEY_SUPTNGSEC_PM_ZPY, KEY_DISP_SUPTNGSEC_PM_ZPY, TYPE_TEXTBOX, None)
        supporting_section.append(t27)

        t28 = (None, None, TYPE_BREAK, None)
        supporting_section.append(t28)

        t36 = (None, None, TYPE_ENTER, None)
        supporting_section.append(t36)

        t29 = (KEY_SUPTNGSEC_SOURCE, KEY_DISP_SUPTNGSEC_SOURCE, TYPE_TEXTBOX, None)
        supporting_section.append(t29)

        t30 = (None, None, TYPE_ENTER, None)
        supporting_section.append(t30)

        t31 = (KEY_SUPTNGSEC_POISSON_RATIO, KEY_DISP_SUPTNGSEC_POISSON_RATIO, TYPE_TEXTBOX, None)
        supporting_section.append(t31)

        t32 = (KEY_SUPTNGSEC_THERMAL_EXP, KEY_DISP_SUPTNGSEC_THERMAL_EXP, TYPE_TEXTBOX, None)
        supporting_section.append(t32)

        t33 = (KEY_IMAGE, None, TYPE_IMAGE, None, None)
        supporting_section.append(t33)

        return supporting_section

    @staticmethod
    def tab_beam_section():
        supported_section = []

        t34 = (KEY_SUPTDSEC, KEY_DISP_BEAMSEC, TYPE_COMBOBOX, [])
        supported_section.append(t34)

        t1 = (KEY_SUPTDSEC_DESIGNATION, KEY_DISP_SUPTDSEC_DESIGNATION, TYPE_TEXTBOX, None)
        supported_section.append(t1)

        t2 = (None, KEY_DISP_MECH_PROP, TYPE_TITLE, None)
        supported_section.append(t2)

        t3 = (KEY_SUPTDSEC_FU, KEY_DISP_SUPTDSEC_FU, TYPE_TEXTBOX, None)
        supported_section.append(t3)

        t4 = (KEY_SUPTDSEC_FY, KEY_DISP_SUPTDSEC_FY, TYPE_TEXTBOX, None)
        supported_section.append(t4)

        t5 = (None, KEY_DISP_DIMENSIONS, TYPE_TITLE, None)
        supported_section.append(t5)

        t6 = (KEY_SUPTDSEC_DEPTH, KEY_DISP_SUPTDSEC_DEPTH, TYPE_TEXTBOX, None)
        supported_section.append(t6)

        t7 = (KEY_SUPTDSEC_FLANGE_W, KEY_DISP_SUPTDSEC_FLANGE_W, TYPE_TEXTBOX, None)
        supported_section.append(t7)

        t8 = (KEY_SUPTDSEC_FLANGE_T, KEY_DISP_SUPTDSEC_FLANGE_T, TYPE_TEXTBOX, None)
        supported_section.append(t8)

        t9 = (KEY_SUPTDSEC_WEB_T, KEY_DISP_SUPTDSEC_WEB_T, TYPE_TEXTBOX, None)
        supported_section.append(t9)

        t10 = (KEY_SUPTDSEC_FLANGE_S, KEY_DISP_SUPTDSEC_FLANGE_S, TYPE_TEXTBOX, None)
        supported_section.append(t10)

        t11 = (KEY_SUPTDSEC_ROOT_R, KEY_DISP_SUPTDSEC_ROOT_R, TYPE_TEXTBOX, None)
        supported_section.append(t11)

        t12 = (KEY_SUPTDSEC_TOE_R, KEY_DISP_SUPTDSEC_TOE_R, TYPE_TEXTBOX, None)
        supported_section.append(t12)

        t13 = (None, None, TYPE_BREAK, None)
        supported_section.append(t13)

        t35 = (None, None, TYPE_ENTER, None)
        supported_section.append(t35)

        t14 = (KEY_SUPTDSEC_TYPE, KEY_DISP_SUPTDSEC_TYPE, TYPE_COMBOBOX, ['Rolled', 'Welded'])
        supported_section.append(t14)

        t18 = (None, None, TYPE_ENTER, None)
        supported_section.append(t18)

        t15 = (KEY_SUPTDSEC_MOD_OF_ELAST, KEY_SUPTDSEC_DISP_MOD_OF_ELAST, TYPE_TEXTBOX, None)
        supported_section.append(t15)

        t16 = (KEY_SUPTDSEC_MOD_OF_RIGID, KEY_SUPTDSEC_DISP_MOD_OF_RIGID, TYPE_TEXTBOX, None)
        supported_section.append(t16)

        t17 = (None, KEY_DISP_SEC_PROP, TYPE_TITLE, None)
        supported_section.append(t17)

        t18 = (KEY_SUPTDSEC_MASS, KEY_DISP_SUPTDSEC_MASS, TYPE_TEXTBOX, None)
        supported_section.append(t18)

        t19 = (KEY_SUPTDSEC_SEC_AREA, KEY_DISP_SUPTDSEC_SEC_AREA, TYPE_TEXTBOX, None)
        supported_section.append(t19)

        t20 = (KEY_SUPTDSEC_MOA_LZ, KEY_DISP_SUPTDSEC_MOA_LZ, TYPE_TEXTBOX, None)
        supported_section.append(t20)

        t21 = (KEY_SUPTDSEC_MOA_LY, KEY_DISP_SUPTDSEC_MOA_LY, TYPE_TEXTBOX, None)
        supported_section.append(t21)

        t22 = (KEY_SUPTDSEC_ROG_RZ, KEY_DISP_SUPTDSEC_ROG_RZ, TYPE_TEXTBOX, None)
        supported_section.append(t22)

        t23 = (KEY_SUPTDSEC_ROG_RY, KEY_DISP_SUPTDSEC_ROG_RY, TYPE_TEXTBOX, None)
        supported_section.append(t23)

        t24 = (KEY_SUPTDSEC_EM_ZZ, KEY_DISP_SUPTDSEC_EM_ZZ, TYPE_TEXTBOX, None)
        supported_section.append(t24)

        t25 = (KEY_SUPTDSEC_EM_ZY, KEY_DISP_SUPTDSEC_EM_ZY, TYPE_TEXTBOX, None)
        supported_section.append(t25)

        t26 = (KEY_SUPTDSEC_PM_ZPZ, KEY_DISP_SUPTDSEC_PM_ZPZ, TYPE_TEXTBOX, None)
        supported_section.append(t26)

        t27 = (KEY_SUPTDSEC_PM_ZPY, KEY_DISP_SUPTDSEC_PM_ZPY, TYPE_TEXTBOX, None)
        supported_section.append(t27)

        t28 = (None, None, TYPE_BREAK, None)
        supported_section.append(t28)

        t36 = (None, None, TYPE_ENTER, None)
        supported_section.append(t36)

        t29 = (KEY_SUPTDSEC_SOURCE, KEY_DISP_SUPTDSEC_SOURCE, TYPE_TEXTBOX, None)
        supported_section.append(t29)

        t30 = (None, None, TYPE_ENTER, None)
        supported_section.append(t30)

        t31 = (KEY_SUPTDSEC_POISSON_RATIO, KEY_DISP_SUPTDSEC_POISSON_RATIO, TYPE_TEXTBOX, None)
        supported_section.append(t31)

        t32 = (KEY_SUPTDSEC_THERMAL_EXP, KEY_DISP_SUPTDSEC_THERMAL_EXP, TYPE_TEXTBOX, None)
        supported_section.append(t32)

        t33 = (KEY_IMAGE, None, TYPE_IMAGE, None, None)
        supported_section.append(t33)

        return supported_section

    @staticmethod
    def tab_angle_section():
        angle_section = []

        t34 = (KEY_SUPTDSEC, KEY_DISP_BEAMSEC, TYPE_COMBOBOX, [])
        angle_section.append(t34)

        t1 = (KEY_SUPTDSEC_DESIGNATION, KEY_DISP_SUPTDSEC_DESIGNATION, TYPE_TEXTBOX, None)
        angle_section.append(t1)

        t2 = (None, KEY_DISP_MECH_PROP, TYPE_TITLE, None)
        angle_section.append(t2)

        t3 = (KEY_SUPTDSEC_FU, KEY_DISP_SUPTDSEC_FU, TYPE_TEXTBOX, None)
        angle_section.append(t3)

        t4 = (KEY_SUPTDSEC_FY, KEY_DISP_SUPTDSEC_FY, TYPE_TEXTBOX, None)
        angle_section.append(t4)

        t5 = (None, KEY_DISP_DIMENSIONS, TYPE_TITLE, None)
        angle_section.append(t5)

        t6 = (KEY_SUPTDSEC_DEPTH, KEY_DISP_SUPTDSEC_DEPTH, TYPE_TEXTBOX, None)
        angle_section.append(t6)

        t7 = (KEY_SUPTDSEC_FLANGE_W, KEY_DISP_SUPTDSEC_FLANGE_W, TYPE_TEXTBOX, None)
        angle_section.append(t7)

        t8 = (KEY_SUPTDSEC_FLANGE_T, KEY_DISP_SUPTDSEC_FLANGE_T, TYPE_TEXTBOX, None)
        angle_section.append(t8)

        t9 = (KEY_SUPTDSEC_WEB_T, KEY_DISP_SUPTDSEC_WEB_T, TYPE_TEXTBOX, None)
        angle_section.append(t9)

        t10 = (KEY_SUPTDSEC_FLANGE_S, KEY_DISP_SUPTDSEC_FLANGE_S, TYPE_TEXTBOX, None)
        angle_section.append(t10)

        t11 = (KEY_SUPTDSEC_ROOT_R, KEY_DISP_SUPTDSEC_ROOT_R, TYPE_TEXTBOX, None)
        angle_section.append(t11)

        t12 = (KEY_SUPTDSEC_TOE_R, KEY_DISP_SUPTDSEC_TOE_R, TYPE_TEXTBOX, None)
        angle_section.append(t12)

        t13 = (None, None, TYPE_BREAK, None)
        angle_section.append(t13)

        t35 = (None, None, TYPE_ENTER, None)
        angle_section.append(t35)

        t14 = (KEY_SUPTDSEC_TYPE, KEY_DISP_SUPTDSEC_TYPE, TYPE_COMBOBOX, ['Rolled', 'Welded'])
        angle_section.append(t14)

        t18 = (None, None, TYPE_ENTER, None)
        angle_section.append(t18)

        t15 = (KEY_SUPTDSEC_MOD_OF_ELAST, KEY_SUPTDSEC_DISP_MOD_OF_ELAST, TYPE_TEXTBOX, None)
        angle_section.append(t15)

        t16 = (KEY_SUPTDSEC_MOD_OF_RIGID, KEY_SUPTDSEC_DISP_MOD_OF_RIGID, TYPE_TEXTBOX, None)
        angle_section.append(t16)

        t17 = (None, KEY_DISP_SEC_PROP, TYPE_TITLE, None)
        angle_section.append(t17)

        t18 = (KEY_SUPTDSEC_MASS, KEY_DISP_SUPTDSEC_MASS, TYPE_TEXTBOX, None)
        angle_section.append(t18)

        t19 = (KEY_SUPTDSEC_SEC_AREA, KEY_DISP_SUPTDSEC_SEC_AREA, TYPE_TEXTBOX, None)
        angle_section.append(t19)

        t20 = (KEY_SUPTDSEC_MOA_LZ, KEY_DISP_SUPTDSEC_MOA_LZ, TYPE_TEXTBOX, None)
        angle_section.append(t20)

        t21 = (KEY_SUPTDSEC_MOA_LY, KEY_DISP_SUPTDSEC_MOA_LY, TYPE_TEXTBOX, None)
        angle_section.append(t21)

        t22 = (KEY_SUPTDSEC_ROG_RZ, KEY_DISP_SUPTDSEC_ROG_RZ, TYPE_TEXTBOX, None)
        angle_section.append(t22)

        t23 = (KEY_SUPTDSEC_ROG_RY, KEY_DISP_SUPTDSEC_ROG_RY, TYPE_TEXTBOX, None)
        angle_section.append(t23)

        t24 = (KEY_SUPTDSEC_EM_ZZ, KEY_DISP_SUPTDSEC_EM_ZZ, TYPE_TEXTBOX, None)
        angle_section.append(t24)

        t25 = (KEY_SUPTDSEC_EM_ZY, KEY_DISP_SUPTDSEC_EM_ZY, TYPE_TEXTBOX, None)
        angle_section.append(t25)

        t26 = (KEY_SUPTDSEC_PM_ZPZ, KEY_DISP_SUPTDSEC_PM_ZPZ, TYPE_TEXTBOX, None)
        angle_section.append(t26)

        t27 = (KEY_SUPTDSEC_PM_ZPY, KEY_DISP_SUPTDSEC_PM_ZPY, TYPE_TEXTBOX, None)
        angle_section.append(t27)

        t28 = (None, None, TYPE_BREAK, None)
        angle_section.append(t28)

        t36 = (None, None, TYPE_ENTER, None)
        angle_section.append(t36)

        t29 = (KEY_SUPTDSEC_SOURCE, KEY_DISP_SUPTDSEC_SOURCE, TYPE_TEXTBOX, None)
        angle_section.append(t29)

        t30 = (None, None, TYPE_ENTER, None)
        angle_section.append(t30)

        t31 = (KEY_SUPTDSEC_POISSON_RATIO, KEY_DISP_SUPTDSEC_POISSON_RATIO, TYPE_TEXTBOX, None)
        angle_section.append(t31)

        t32 = (KEY_SUPTDSEC_THERMAL_EXP, KEY_DISP_SUPTDSEC_THERMAL_EXP, TYPE_TEXTBOX, None)
        angle_section.append(t32)

        t33 = (KEY_IMAGE, None, TYPE_IMAGE, None, None)
        angle_section.append(t33)

        return angle_section

    @staticmethod
    def bolt_values():

        bolt = []

        t1 = (KEY_DP_BOLT_TYPE, KEY_DISP_TYP, TYPE_COMBOBOX, ['Pretensioned', 'Non-pretensioned'])
        bolt.append(t1)

        t2 = (KEY_DP_BOLT_HOLE_TYPE, KEY_DISP_DP_BOLT_HOLE_TYPE, TYPE_COMBOBOX, ['Standard', 'Over-sized'])
        bolt.append(t2)

        t3 = (KEY_DP_BOLT_MATERIAL_G_O, KEY_DISP_DP_BOLT_MATERIAL_G_O, TYPE_TEXTBOX, '410')
        bolt.append(t3)

        t4 = (None, None, TYPE_ENTER, None)
        bolt.append(t4)

        t5 = (None, KEY_DISP_DP_BOLT_DESIGN_PARA, TYPE_TITLE, None)
        bolt.append(t5)

        t6 = (KEY_DP_BOLT_SLIP_FACTOR, KEY_DISP_DP_BOLT_SLIP_FACTOR, TYPE_COMBOBOX, ['0.2', '0.5', '0.1', '0.25', '0.3',
                                                                                     '0.33', '0.48', '0.52', '0.55'])
        bolt.append(t6)

        t7 = (None, None, TYPE_ENTER, None)
        bolt.append(t7)

        t8 = (None, "NOTE : If slip is permitted under the design load, design the bolt as"
                    "<br>a bearing bolt and select corresponding bolt grade.", TYPE_NOTE, None)
        bolt.append(t8)

        t9 = ["textBrowser", "", TYPE_TEXT_BROWSER, BOLT_DESCRIPTION]
        bolt.append(t9)

        return bolt

    @staticmethod
    def weld_values():

        weld = []

        t1 = (KEY_DP_WELD_FAB, KEY_DISP_DP_WELD_FAB, TYPE_COMBOBOX, KEY_DP_WELD_FAB_VALUES)
        weld.append(t1)

        t2 = (KEY_DP_WELD_MATERIAL_G_O, KEY_DISP_DP_WELD_MATERIAL_G_O, TYPE_TEXTBOX, '410')
        weld.append(t2)

        t3 = ["textBrowser", "", TYPE_TEXT_BROWSER, WELD_DESCRIPTION]
        weld.append(t3)

        return weld

    @staticmethod
    def detailing_values():
        detailing = []

        t1 = (KEY_DP_DETAILING_EDGE_TYPE, KEY_DISP_DP_DETAILING_EDGE_TYPE, TYPE_COMBOBOX, [
            'a - Sheared or hand flame cut', 'b - Rolled, machine-flame cut, sawn and planed'])
        detailing.append(t1)

        t2 = (KEY_DP_DETAILING_GAP, KEY_DISP_DP_DETAILING_GAP, TYPE_TEXTBOX, '10')
        detailing.append(t2)

        t3 = (KEY_DP_DETAILING_CORROSIVE_INFLUENCES, KEY_DISP_DP_DETAILING_CORROSIVE_INFLUENCES, TYPE_COMBOBOX,
              ['No', 'Yes'])
        detailing.append(t3)

        t4 = ["textBrowser", "", TYPE_TEXT_BROWSER, DETAILING_DESCRIPTION]
        detailing.append(t4)

        return detailing

    @staticmethod
    def design_values():

        design = []

        t1 = (KEY_DP_DESIGN_METHOD, KEY_DISP_DP_DESIGN_METHOD, TYPE_COMBOBOX, ['Limit State Design',
                                                                               'Limit State (Capacity based) Design',
                                                                               'Working Stress Design'])
        design.append(t1)

        return design

    def input_values(self, existingvalues={}):

        '''
        Fuction to return a list of tuples to be displayed as the UI.(Input Dock)
        '''

        # @author: Amir, Umair
        self.module = KEY_DISP_TENSION_WELDED
        self.connection = "Welded"

        options_list = []

        # if KEY_SECTION in existingvalues:
        #     existingvalue_key_section = existingvalues[KEY_SECTION]
        # else:
        #     existingvalue_key_section = ''

        # if KEY_SUPTNGSEC in existingvalues:
        #    existingvalue_key_suptngsec = existingvalues[KEY_SUPTNGSEC]
        # else:
        #     existingvalue_key_suptngsec = ''
        #
        # if KEY_SUPTDSEC in existingvalues:
        #     existingvalue_key_suptdsec = existingvalues[KEY_SUPTDSEC]
        # else:
        #     existingvalue_key_suptdsec = ''

        if KEY_LOCATION in existingvalues:
            existingvalue_key_location = existingvalues[KEY_LOCATION]
        else:
            existingvalue_key_location = ''

        if KEY_SEC_PROFILE in existingvalues:
            existingvalue_key_sec_profile = existingvalues[KEY_SEC_PROFILE]
        else:
            existingvalue_key_sec_profile = ''

        if KEY_SECSIZE in existingvalues:
            existingvalue_key_sec_size = existingvalues[KEY_SECSIZE]
        else:
            existingvalue_key_sec_size = ''

        if KEY_MATERIAL in existingvalues:
            existingvalue_key_mtrl = existingvalues[KEY_MATERIAL]
        else:
            existingvalue_key_mtrl = ''

        if KEY_LENGTH in existingvalues:
            existingvalue_key_length = existingvalues[KEY_LENGTH]
        else:
            existingvalue_key_length = ''

        # if KEY_SHEAR in existingvalues:
        #     existingvalue_key_versh = existingvalues[KEY_SHEAR]
        # else:
        #     existingvalue_key_versh = ''

        if KEY_AXIAL in existingvalues:
            existingvalue_key_axial = existingvalues[KEY_AXIAL]
        else:
            existingvalue_key_axial = ''

        if KEY_D in existingvalues:
            existingvalue_key_d = existingvalues[KEY_D]
        else:
            existingvalue_key_d = ''

        if KEY_TYP in existingvalues:
            existingvalue_key_typ = existingvalues[KEY_TYP]
        else:
            existingvalue_key_typ = ''

        if KEY_GRD in existingvalues:
            existingvalue_key_grd = existingvalues[KEY_GRD]
        else:
            existingvalue_key_grd = ''

        # if KEY_PLATETHK in existingvalues:
        #     existingvalue_key_platethk = existingvalues[KEY_PLATETHK]
        # else:
        #     existingvalue_key_platethk = ''

        t16 = (KEY_MODULE, KEY_DISP_TENSION_WELDED, TYPE_MODULE, None, None)
        options_list.append(t16)

        t1 = (None, DISP_TITLE_CM, TYPE_TITLE, None, None)
        options_list.append(t1)

        t2 = (KEY_SEC_PROFILE, KEY_DISP_SEC_PROFILE, TYPE_COMBOBOX, existingvalue_key_sec_profile, VALUES_SEC_PROFILE_2)
        options_list.append(t2)

        t15 = (KEY_IMAGE, None, TYPE_IMAGE, None, "./ResourceFiles/images/fin_cf_bw.png")
        options_list.append(t15)

        t3 = (KEY_LOCATION, KEY_DISP_LOCATION, TYPE_COMBOBOX, existingvalue_key_location, VALUES_LOCATION_1)
        options_list.append(t3)

        t4 = (KEY_SECSIZE, KEY_DISP_SECSIZE, TYPE_COMBOBOX_CUSTOMIZED, existingvalue_key_sec_size, ['All','Customized'])
        options_list.append(t4)

        t5 = (KEY_MATERIAL, KEY_DISP_MATERIAL, TYPE_COMBOBOX, existingvalue_key_mtrl, VALUES_MATERIAL)
        options_list.append(t5)

        t5 = (KEY_LENGTH, KEY_DISP_LENGTH, TYPE_TEXTBOX, existingvalue_key_length, None)
        options_list.append(t5)

        t6 = (None, DISP_TITLE_FSL, TYPE_TITLE, None, None)
        options_list.append(t6)

        # t7 = (KEY_SHEAR, KEY_DISP_SHEAR, TYPE_TEXTBOX, existingvalue_key_versh, None)
        # options_list.append(t7)

        t7 = (KEY_AXIAL, KEY_DISP_AXIAL, TYPE_TEXTBOX, existingvalue_key_axial, None)
        options_list.append(t7)

        # t8 = (None, DISP_TITLE_BOLT, TYPE_TITLE, None, None)
        # options_list.append(t8)
        #
        # t10 = (KEY_D, KEY_DISP_D, TYPE_COMBOBOX_CUSTOMIZED, existingvalue_key_d, VALUES_D)
        # options_list.append(t10)
        #
        # t11 = (KEY_TYP, KEY_DISP_TYP, TYPE_COMBOBOX, existingvalue_key_typ, VALUES_TYP)
        # options_list.append(t11)
        #
        # t12 = (KEY_GRD, KEY_DISP_GRD, TYPE_COMBOBOX_CUSTOMIZED, existingvalue_key_grd, VALUES_GRD)
        # options_list.append(t12)

        # t13 = (None, DISP_TITLE_PLATE, TYPE_TITLE, None, None)
        # options_list.append(t13)

        # t14 = (KEY_PLATETHK, KEY_DISP_PLATETHK, TYPE_COMBOBOX_CUSTOMIZED, existingvalue_key_platethk, VALUES_PLATETHK)
        # options_list.append(t14)

        return options_list

    def spacing(self, status):

        spacing = []

        t9 = (KEY_OUT_PITCH, KEY_OUT_DISP_PITCH, TYPE_TEXTBOX, self.plate.pitch_provided if status else '')
        spacing.append(t9)

        t10 = (KEY_OUT_END_DIST, KEY_OUT_DISP_END_DIST, TYPE_TEXTBOX, self.plate.end_dist_provided if status else '')
        spacing.append(t10)

        t11 = (KEY_OUT_GAUGE, KEY_OUT_DISP_GAUGE, TYPE_TEXTBOX, self.plate.gauge_provided if status else '')
        spacing.append(t11)

        t12 = (KEY_OUT_EDGE_DIST, KEY_OUT_DISP_EDGE_DIST, TYPE_TEXTBOX, self.plate.edge_dist_provided if status else '')
        spacing.append(t12)

        return spacing

    def output_values(self, flag):
        '''
        Fuction to return a list of tuples to be displayed as the UI.(Output Dock)
        '''

        # @author: Umair

        out_list = []

        t1 = (None, DISP_TITLE_TENSION_SECTION, TYPE_TITLE, None)
        out_list.append(t1)

        t2 = (KEY_DESIGNATION, KEY_DISP_DESIGNATION, TYPE_TEXTBOX,
              self.section_size_1.designation if flag else '')
        out_list.append(t2)

        t3 = (KEY_TENSION_YIELDCAPACITY, KEY_DISP_TENSION_YIELDCAPACITY, TYPE_TEXTBOX, self.section_size_1.tension_yielding_capacity if flag else '')
        out_list.append(t3)

        t4 = (KEY_TENSION_RUPTURECAPACITY, KEY_DISP_TENSION_RUPTURECAPACITY, TYPE_TEXTBOX,
              self.section_size_1.tension_rupture_capacity if flag else '')
        out_list.append(t4)

        t5 = (KEY_TENSION_BLOCKSHEARCAPACITY, KEY_DISP_TENSION_BLOCKSHEARCAPACITY, TYPE_TEXTBOX,
              self.section_size_1.block_shear_capacity_axial if flag else '')
        out_list.append(t5)

        t6 = (KEY_TENSION_CAPACITY, KEY_DISP_TENSION_CAPACITY, TYPE_TEXTBOX,
              self.section_size_1.tension_capacity if flag else '')
        out_list.append(t6)

        t6 = (KEY_SLENDER, KEY_DISP_SLENDER, TYPE_TEXTBOX,
              self.section_size_1.slenderness if flag else '')
        out_list.append(t6)

        t7 = (KEY_EFFICIENCY, KEY_DISP_EFFICIENCY, TYPE_TEXTBOX,
               self.efficiency if flag else '')
        out_list.append(t7)

        t8 = (None, DISP_TITLE_WELD_CAPACITY, TYPE_TITLE, None)
        out_list.append(t8)

        t9 = (KEY_OUT_WELD_SIZE, KEY_OUT_DISP_WELD_SIZE, TYPE_TEXTBOX, self.weld.size if flag else '')
        out_list.append(t9)

        t10 = (KEY_OUT_WELD_STRENGTH, KEY_OUT_DISP_WELD_STRENGTH, TYPE_TEXTBOX, round(self.weld.strength,2) if flag else '')

        out_list.append(t10)

        t11 = (KEY_OUT_WELD_STRESS, KEY_OUT_DISP_WELD_STRESS, TYPE_TEXTBOX, round(self.weld.stress,2) if flag else '')
        out_list.append(t11)

        # bolt_bearing_capacity_disp = ''
        # if flag is True:
        #     if self.bolt.bolt_bearing_capacity is not VALUE_NOT_APPLICABLE:
        #         bolt_bearing_capacity_disp = round(self.bolt.bolt_bearing_capacity / 1000, 2)
        #         pass
        #     else:
        #         bolt_bearing_capacity_disp = self.bolt.bolt_bearing_capacity

        t5 = (KEY_OUT_WELD_LENGTH, KEY_OUT_DISP_WELD_LENGTH, TYPE_TEXTBOX, self.weld.length if flag else '')
        out_list.append(t5)

        t13 = (KEY_OUT_WELD_LENGTH_EFF, KEY_OUT_DISP_WELD_LENGTH_EFF, TYPE_TEXTBOX, self.weld.effective if flag else '')
        out_list.append(t13)

        # t14 = (KEY_OUT_BOLT_FORCE, KEY_OUT_DISP_BOLT_FORCE, TYPE_TEXTBOX, round(self.plate.bolt_force / 1000, 2) if flag else '')
        # out_list.append(t14)
        #
        # t15 = (KEY_OUT_BOLT_LINE, KEY_OUT_DISP_BOLT_LINE, TYPE_TEXTBOX, self.plate.bolt_line if flag else '')
        # out_list.append(t15)
        #
        # t16 = (KEY_OUT_BOLTS_ONE_LINE, KEY_OUT_DISP_BOLTS_ONE_LINE, TYPE_TEXTBOX, self.plate.bolts_one_line if flag else '')
        # out_list.append(t16)
        #
        # t17 = (KEY_OUT_SPACING, KEY_OUT_DISP_SPACING, TYPE_OUT_BUTTON, ['Spacing Details', self.spacing])
        # out_list.append(t17)

        t18 = (None, DISP_TITLE_PLATE, TYPE_TITLE, None)
        out_list.append(t18)

        t19 = (KEY_OUT_PLATETHK, KEY_OUT_DISP_PLATETHK, TYPE_TEXTBOX, self.plate.thickness_provided if flag else '')
        out_list.append(t19)

        t20 = (KEY_OUT_PLATE_HEIGHT, KEY_OUT_DISP_PLATE_HEIGHT, TYPE_TEXTBOX, self.plate.height if flag else '')
        out_list.append(t20)

        t21 = (KEY_OUT_PLATE_LENGTH, KEY_OUT_DISP_PLATE_LENGTH, TYPE_TEXTBOX, self.plate.length if flag else '')
        out_list.append(t21)

        return out_list

    # def loadDesign_inputs(self, window, op_list, data, new):
    #     fileName, _ = QFileDialog.getOpenFileName(window, "Open Design", os.path.join(str(' '), ''), "InputFiles(*.osi)")
    #     if not fileName:
    #         return
    #     try:
    #         in_file = str(fileName)
    #         with open(in_file, 'r') as fileObject:
    #             uiObj = yaml.load(fileObject)
    #         module = uiObj[KEY_MODULE]
    #
    #         if module == KEY_DISP_FINPLATE:
    #             self.setDictToUserInputs(window, uiObj, op_list, data, new)
    #         else:
    #             QMessageBox.information(window, "Information",
    #                                 "Please load the appropriate Input")
    #
    #             return
    #     except IOError:
    #         QMessageBox.information(window, "Unable to open file",
    #                                 "There was an error opening \"%s\"" % fileName)
    #         return
    #
    #     # Function for loading inputs from a file to Ui
    #
    # '''
    # @author: Umair
    # '''
    #
    # def setDictToUserInputs(self, uiObj, op_list, data, new):
    #     for op in op_list:
    #         key_str = op[0]
    #         key = self.dockWidgetContents.findChild(QtWidgets.QWidget, key_str)
    #         if op[2] == TYPE_COMBOBOX:
    #             index = key.findText(uiObj[key_str], QtCore.Qt.MatchFixedString)
    #             if index >= 0:
    #                 key.setCurrentIndex(index)
    #         elif op[2] == TYPE_TEXTBOX:
    #             key.setText(uiObj[key_str])
    #         elif op[2] == TYPE_COMBOBOX_CUSTOMIZED:
    #             for n in new:
    #                 if n[0] == key_str:
    #                     if uiObj[key_str] != n[1]():
    #                         data[key_str + "_customized"] = uiObj[key_str]
    #                         key.setCurrentIndex(1)
    #                     else:
    #                         pass
    #         else:
    #             pass

    # def func_for_validation(self, window, design_dictionary):
    #     self.design_status = False
    #     flag = False
    #     flag1 = False
    #     option_list = self.input_values(self)
    #     missing_fields_list = []
    #     for option in option_list:
    #         if option[2] == TYPE_TEXTBOX:
    #             if design_dictionary[option[0]] == '':
    #                 missing_fields_list.append(option[1])
    #         elif option[2] == TYPE_COMBOBOX and option[0] != KEY_CONN:
    #             val = option[4]
    #             if design_dictionary[option[0]] == val[0]:
    #                 missing_fields_list.append(option[1])
    #         elif option[2] == TYPE_COMBOBOX_CUSTOMIZED:
    #             if design_dictionary[option[0]] == []:
    #                 missing_fields_list.append(option[1])
    #         # elif option[2] == TYPE_MODULE:
    #         #     if design_dictionary[option[0]] == "Fin Plate":
    #
    #     # if design_dictionary[KEY_CONN] == 'Beam-Beam':
    #     #     primary = design_dictionary[KEY_SUPTNGSEC]
    #     #     secondary = design_dictionary[KEY_SUPTDSEC]
    #     #     conn = sqlite3.connect(PATH_TO_DATABASE)
    #     #     cursor = conn.execute("SELECT D FROM BEAMS WHERE Designation = ( ? ) ", (primary,))
    #     #     lst = []
    #     #     rows = cursor.fetchall()
    #     #     for row in rows:
    #     #         lst.append(row)
    #     #     p_val = lst[0][0]
    #     #     cursor2 = conn.execute("SELECT D FROM BEAMS WHERE Designation = ( ? )", (secondary,))
    #     #     lst1 = []
    #     #     rows1 = cursor2.fetchall()
    #     #     for row1 in rows1:
    #     #         lst1.append(row1)
    #     #     s_val = lst1[0][0]
    #     #     if p_val <= s_val:
    #     #         QMessageBox.about(window, 'Information',
    #     #                           "Secondary beam depth is higher than clear depth of primary beam web "
    #     #                           "(No provision in Osdag till now)")
    #     #     else:
    #     #         flag1 = True
    #     # else:
    #     #     flag1 = True
    #
    #     if len(missing_fields_list) > 0:
    #         QMessageBox.information(window, "Information",
    #                                 self.generate_missing_fields_error_string(self, missing_fields_list))
    #         # flag = False
    #     else:
    #         flag = True
    #
    #     if flag and flag1:
    #         self.set_input_values(self, design_dictionary)
    #     else:
    #         pass

    def func_for_validation(self, window, design_dictionary):
        self.design_status = False

        flag = False
        option_list = self.input_values(self)
        missing_fields_list = []
        for option in option_list:
            if option[2] == TYPE_TEXTBOX:
                if design_dictionary[option[0]] == '':
                    missing_fields_list.append(option[1])
            elif option[2] == TYPE_COMBOBOX and option[0] not in [KEY_SEC_PROFILE, KEY_LOCATION, KEY_END1, KEY_END2]:
                val = option[4]
                if design_dictionary[option[0]] == val[0]:
                    missing_fields_list.append(option[1])

        if len(missing_fields_list) > 0:
            QMessageBox.information(window, "Information",
                                    self.generate_missing_fields_error_string(self, missing_fields_list))
            # flag = False
        else:
            flag = True

        if flag:
            self.set_input_values(self, design_dictionary)
            print(design_dictionary)
        else:
            pass



    def generate_missing_fields_error_string(self, missing_fields_list):
        """
        Args:
            missing_fields_list: list of fields that are not selected or entered
        Returns:
            error string that has to be displayed
        """
        # The base string which should be displayed
        information = "Please input the following required field"
        if len(missing_fields_list) > 1:
            # Adds 's' to the above sentence if there are multiple missing input fields
            information += "s"
        information += ": "
        # Loops through the list of the missing fields and adds each field to the above sentence with a comma

        for item in missing_fields_list:
            information = information + item + ", "

        # Removes the last comma
        information = information[:-2]
        information += "."

        return information

    def warn_text(self):
      
        """
        Function to give logger warning when any old value is selected from Column and Beams table.
        """

        # @author Arsil Zunzunia
        global logger
        red_list = red_list_function()
        if self.supported_section.designation in red_list or self.supporting_section.designation in red_list:
            logger.warning(
                " : You are using a section (in red color) that is not available in latest version of IS 808")
            logger.info(
                " : You are using a section (in red color) that is not available in latest version of IS 808")

    def set_input_values(self, design_dictionary):

        super(Tension_welded,self).set_input_values(self, design_dictionary)
        self.module = design_dictionary[KEY_MODULE]
        self.sizelist = design_dictionary[KEY_SECSIZE]
        self.sec_profile = design_dictionary[KEY_SEC_PROFILE]
        self.plate_thickness = [3,4,6,8,10,12,16,20,24,28,30,32,36,40]
        # print(self.sizelist)
        self.length = float(design_dictionary[KEY_LENGTH])
        # print(self.bolt)
        self.load = Load(shear_force=None, axial_force=design_dictionary.get(KEY_AXIAL))
        self.efficiency = 0.0

        self.plate = Plate(thickness=self.plate_thickness,
                           material_grade=design_dictionary[KEY_MATERIAL])
        self.weld = Weld(material_grade=design_dictionary[KEY_MATERIAL],
                         material_g_o=design_dictionary[KEY_DP_WELD_MATERIAL_G_O],
                         fabrication=design_dictionary[KEY_DP_WELD_FAB])

        print("input values are set. Doing preliminary member checks")
        # self.i = 0

        self.initial_member_capacity(self,design_dictionary)


    def select_section(self, design_dictionary, selectedsize):
        if design_dictionary[KEY_SEC_PROFILE] in ['Angles', 'Back to Back Angles', 'Star Angles']:
            self.section_size = Angle(designation=selectedsize, material_grade=design_dictionary[KEY_MATERIAL])
        elif design_dictionary[KEY_SEC_PROFILE] in ['Channels', 'Back to Back Channels']:
            self.section_size = Channel(designation=selectedsize, material_grade=design_dictionary[KEY_MATERIAL])
        else:
            pass

        return self.section_size

    def max_force_length(self, design_dictionary):
        if design_dictionary[KEY_SEC_PROFILE] == 'Angles':
            # print (Angle)
            self.section_size_max = Angle(designation = "200 200 X 25", material_grade=design_dictionary[KEY_MATERIAL])
            self.section_size_max.tension_member_yielding(A_g = (self.section_size_max.area) , F_y = self.section_size_max.fy)
            self.max_member_force = self.section_size_max.tension_yielding_capacity
            self.section_size_max.min_rad_gyration_calc(key = design_dictionary[KEY_SEC_PROFILE],subkey = design_dictionary[KEY_LOCATION],mom_inertia_y = 0.0 ,mom_inertia_z = 0.0 ,rad_y = self.section_size_max.rad_of_gy_y , rad_z = self.section_size_max.rad_of_gy_z, rad_u =self.section_size_max.rad_of_gy_u, rad_v=self.section_size_max.rad_of_gy_v, area = self.section_size_max.area,Cg_1= 0.0,Cg_2= 0.0,thickness=0.0)
            self.max_length = 400 * self.section_size_max.min_radius_gyration

        elif design_dictionary[KEY_SEC_PROFILE] in ['Back to Back Angles', 'Star Angles']:
            self.section_size_max = Angle(designation="200 200 X 25", material_grade=design_dictionary[KEY_MATERIAL])
            self.section_size_max.tension_member_yielding(A_g=(self.section_size_max.area),
                                                          F_y=self.section_size_max.fy)
            self.max_member_force = self.section_size_max.tension_yielding_capacity * 2
            self.section_size_max.min_rad_gyration_calc(key=design_dictionary[KEY_SEC_PROFILE],subkey = design_dictionary[KEY_LOCATION],
                                                        mom_inertia_y=self.section_size_max.mom_inertia_y,
                                                        mom_inertia_z=self.section_size_max.mom_inertia_z,
                                                        rad_y=self.section_size_max.rad_of_gy_y,
                                                        rad_z=self.section_size_max.rad_of_gy_z, rad_u =self.section_size_max.rad_of_gy_u, rad_v=self.section_size_max.rad_of_gy_v,
                                                        area=self.section_size_max.area, Cg_1=self.section_size_max.Cy,Cg_2=self.section_size_max.Cz,
                                                        thickness=0.0)
            self.max_length = 400 * self.section_size_max.min_radius_gyration



        elif design_dictionary[KEY_SEC_PROFILE] == 'Channels':
            self.section_size_max = Channel(designation="MCP 400", material_grade=design_dictionary[KEY_MATERIAL])
            # self.area = self.section_size_max.area
            self.section_size_max.tension_member_yielding(A_g = (self.section_size_max.area) , F_y = self.section_size_max.fy)
            self.max_member_force = self.section_size_max.tension_yielding_capacity
            self.section_size_max.min_rad_gyration_calc(key = design_dictionary[KEY_SEC_PROFILE],subkey = design_dictionary[KEY_LOCATION],mom_inertia_y = self.section_size_max.mom_inertia_y,mom_inertia_z = self.section_size_max.mom_inertia_z,rad_y = self.section_size_max.rad_of_gy_y , rad_z = self.section_size_max.rad_of_gy_z,area = self.section_size_max.area,Cg_1 = self.section_size_max.Cy, Cg_2=0.0,thickness=0.0)
            self.max_length = 400 * self.section_size_max.min_radius_gyration

        elif design_dictionary[KEY_SEC_PROFILE] ==  'Back to Back Channels':
            self.section_size_max = Channel(designation="MCP 400", material_grade=design_dictionary[KEY_MATERIAL])
            # self.area = self.section_size_max.area
            self.section_size_max.tension_member_yielding(A_g = (self.section_size_max.area) , F_y = self.section_size_max.fy)
            self.max_member_force  = 2 * self.section_size_max.tension_yielding_capacity
            self.section_size_max.min_rad_gyration_calc(key = design_dictionary[KEY_SEC_PROFILE],subkey = design_dictionary[KEY_LOCATION],mom_inertia_y = self.section_size_max.mom_inertia_y,mom_inertia_z = self.section_size_max.mom_inertia_z,rad_y = self.section_size_max.rad_of_gy_y , rad_z = self.section_size_max.rad_of_gy_z,area = self.section_size_max.area,Cg_1 = self.section_size_max.Cy, Cg_2=0.0,thickness=0.0)
            # Iyy = (self.section_size_max.mom_inertia_y + (self.section_size_max.area * (self.section_size_max.Cg) * (
            #             self.section_size_max.Cg))) * 2
            # Izz = 2 * self.section_size_max.mom_inertia_z
            # I = min(Iyy, Izz)
            # self.rad_gyration = math.sqrt(I / (self.section_size_max.area))
            self.max_length = 400 * self.section_size_max.min_radius_gyration

        return self.max_member_force,self.max_length


    def initial_member_capacity(self,design_dictionary,previous_size = None):
        min_yield = 0

        [max_force,length] = self.max_force_length(self, design_dictionary)
        for selectedsize in self.sizelist:
            print(selectedsize)
            self.section_size = self.select_section(self,design_dictionary,selectedsize)
            print(self.section_size)
            if design_dictionary[KEY_LOCATION] == "Long Leg":
               if self.section_size.max_leg < self.section_size.root_radius + self.section_size.thickness + (2 *25):
                   continue
            elif design_dictionary[KEY_LOCATION] == 'Short Leg':
                if self.section_size.min_leg < self.section_size.root_radius + self.section_size.thickness + (2 * 25):
                    continue
            if design_dictionary[KEY_SEC_PROFILE] =='Channels':
                self.max_plate_height = self.section_size.max_plate_height()
                if self.max_plate_height < (2 * 30) + (2 * 25):
                    continue
                else:
                    self.cross_area = self.section_size.area
                # self.section_size.min_rad_gyration_calc((self.section_size.rad_of_gy_y),(self.section_size.rad_of_gy_z))
                # radius_gyration = self.section_size.min_radius_gyration

            elif design_dictionary[KEY_SEC_PROFILE] == 'Back to Back Channels':
                self.max_plate_height = self.section_size.max_plate_height()
                if self.max_plate_height < (2 * 30) + (2 * 25):
                    continue
                else:
                    self.cross_area = self.section_size.area * 2

            elif design_dictionary[KEY_SEC_PROFILE] =='Angles':
                self.cross_area = self.section_size.area

            else:
                self.cross_area = self.section_size.area * 2

                # self.section_size.min_rad_gyration_bbchannel_calc(mom_inertia_y=self.section_size.mom_inertia_y,
                #                                                       area=self.section_size.area,
                #                                                       Cg=self.section_size.Cg,
                #                                                       mom_inertia_z=self.section_size.mom_inertia_z,
                #                                                       thickness=0.0)
                # radius_gyration = self.section_size.min_rad_gyration_bbchannel



            if previous_size != None:
                self.section_size_prev = self.select_section(self, design_dictionary, previous_size)
                if design_dictionary[KEY_SEC_PROFILE] in ['Channels','Angles']:
                    self.cross_area_prev = self.section_size_prev.area
                elif design_dictionary[KEY_SEC_PROFILE] in ['Back to Back Channels','Star Angles','Back to Back Angles']:
                    self.cross_area_prev = self.section_size_prev.area * 2
                else:
                    pass
            else:
                self.cross_area_prev = 0

            if self.cross_area > self.cross_area_prev or previous_size == None:
                self.section_size.tension_member_yielding(A_g = self.cross_area , F_y =self.section_size.fy)
                self.K = 1.0
                # print(self.section_size.rad_of_gy_z)
                if design_dictionary[KEY_SEC_PROFILE] in ['Angles','Star Angles','Back to Back Angles']:
                    # print(selectedsize)
                    self.section_size.min_rad_gyration_calc(key=design_dictionary[KEY_SEC_PROFILE],subkey = design_dictionary[KEY_LOCATION],
                                                                mom_inertia_y=self.section_size.mom_inertia_y,
                                                                mom_inertia_z=self.section_size.mom_inertia_z,
                                                            rad_y=self.section_size.rad_of_gy_y,rad_z=self.section_size.rad_of_gy_z, rad_u =self.section_size.rad_of_gy_u, rad_v=self.section_size.rad_of_gy_v,
                                                                area=self.section_size.area,
                                                                Cg_1=self.section_size.Cy, Cg_2=self.section_size.Cz,thickness=0.0)
                else:
                    self.section_size.min_rad_gyration_calc(key=design_dictionary[KEY_SEC_PROFILE],
                                                            subkey=design_dictionary[KEY_LOCATION],
                                                            mom_inertia_y=self.section_size.mom_inertia_y,
                                                            mom_inertia_z=self.section_size.mom_inertia_z,
                                                            rad_y=self.section_size.rad_of_gy_y,
                                                            rad_z=self.section_size.rad_of_gy_z,
                                                            area=self.section_size.area,
                                                            Cg_1=self.section_size.Cy, Cg_2=0,
                                                            thickness=0.0)

                self.section_size.design_check_for_slenderness(K=self.K, L=design_dictionary[KEY_LENGTH],r=self.section_size.min_radius_gyration)
                    # print(self.section_size.tension_yielding_capacity)

                if (self.section_size.tension_yielding_capacity > self.load.axial_force) and self.section_size.slenderness < 400:
                    min_yield_current = self.section_size.tension_yielding_capacity
                    if min_yield == 0:
                        min_yield = min_yield_current
                        self.section_size_1 = self.select_section(self, design_dictionary, selectedsize)
                        self.section_size_1.tension_member_yielding(A_g=self.cross_area, F_y=self.section_size.fy)

                        if design_dictionary[KEY_SEC_PROFILE] in ['Angles', 'Star Angles', 'Back to Back Angles']:
                            self.section_size_1.min_rad_gyration_calc(key=design_dictionary[KEY_SEC_PROFILE],subkey = design_dictionary[KEY_LOCATION],
                                                                    mom_inertia_y=self.section_size_1.mom_inertia_y,
                                                                    mom_inertia_z=self.section_size_1.mom_inertia_z,
                                                                      rad_y=self.section_size_1.rad_of_gy_y,rad_z= self.section_size_1.rad_of_gy_z,rad_u=self.section_size_1.rad_of_gy_u,rad_v= self.section_size_1.rad_of_gy_v,
                                                                    area=self.section_size_1.area,
                                                                    Cg_1=self.section_size_1.Cy, Cg_2=self.section_size_1.Cz, thickness=0.0)
                        else:
                            self.section_size.min_rad_gyration_calc(key=design_dictionary[KEY_SEC_PROFILE],
                                                                    subkey=design_dictionary[KEY_LOCATION],
                                                                    mom_inertia_y=self.section_size.mom_inertia_y,
                                                                    mom_inertia_z=self.section_size.mom_inertia_z,
                                                                    rad_y=self.section_size.rad_of_gy_y,
                                                                    rad_z=self.section_size.rad_of_gy_z,
                                                                    area=self.section_size.area,
                                                                    Cg_1=self.section_size.Cy, Cg_2=0,
                                                                    thickness=0.0)

                        self.section_size_1.design_check_for_slenderness(K=self.K, L=design_dictionary[KEY_LENGTH],
                                                                   r=self.section_size_1.min_radius_gyration)

                    elif min_yield_current <= min_yield:
                        min_yield = min_yield_current
                        self.section_size_1 = self.select_section(self, design_dictionary, selectedsize)
                        self.section_size_1.tension_member_yielding(A_g=self.cross_area, F_y=self.section_size.fy)
                        if design_dictionary[KEY_SEC_PROFILE] in ['Angles', 'Star Angles', 'Back to Back Angles']:
                            self.section_size_1.min_rad_gyration_calc(key=design_dictionary[KEY_SEC_PROFILE],
                                                                      subkey=design_dictionary[KEY_LOCATION],
                                                                      mom_inertia_y=self.section_size_1.mom_inertia_y,
                                                                      mom_inertia_z=self.section_size_1.mom_inertia_z,
                                                                      rad_y=self.section_size_1.rad_of_gy_y,
                                                                      rad_z=self.section_size_1.rad_of_gy_z,
                                                                      rad_u=self.section_size_1.rad_of_gy_u,
                                                                      rad_v=self.section_size_1.rad_of_gy_v,
                                                                      area=self.section_size_1.area,
                                                                      Cg_1=self.section_size_1.Cy,
                                                                      Cg_2=self.section_size_1.Cz, thickness=0.0)
                        else:
                            self.section_size.min_rad_gyration_calc(key=design_dictionary[KEY_SEC_PROFILE],
                                                                    subkey=design_dictionary[KEY_LOCATION],
                                                                    mom_inertia_y=self.section_size.mom_inertia_y,
                                                                    mom_inertia_z=self.section_size.mom_inertia_z,
                                                                    rad_y=self.section_size.rad_of_gy_y,
                                                                    rad_z=self.section_size.rad_of_gy_z,
                                                                    area=self.section_size.area,
                                                                    Cg_1=self.section_size.Cy, Cg_2=0,
                                                                    thickness=0.0)
                    self.section_size_1.design_check_for_slenderness(K=self.K, L=design_dictionary[KEY_LENGTH],
                                                                     r=self.section_size_1.min_radius_gyration)

                    # print(self.section_size_1.slenderness)
                elif (self.load.axial_force > max_force) :
                    self.design_status = False
                    logger.error(" : Tension force exceeds tension capacity of maximum available member size")
                    break

                elif self.length > length:
                    self.design_status = False
                    logger.error(" : Member fails in slenderness")
                    break

                else:
                    pass

        if (self.load.axial_force > max_force) or self.length > length:
            pass
        else:
            print("pass")
            self.design_status = True
            self.select_weld(self, design_dictionary)



    def closest(self, lst, K):

        return lst[min(range(len(lst)), key=lambda i: abs(lst[i] - K))]

    def select_weld(self,design_dictionary):
        if design_dictionary[KEY_SEC_PROFILE] in ["Channels", 'Back to Back Channels']:
            self.min_plate_height = self.section_size_1.min_plate_height()
            self.max_plate_height = self.section_size_1.max_plate_height()
        elif design_dictionary[KEY_LOCATION] == 'Long Leg':
            self.min_plate_height = self.section_size_1.max_leg - self.section_size_1.root_radius - self.section_size_1.thickness
            self.max_plate_height = self.section_size_1.max_leg - self.section_size_1.root_radius - self.section_size_1.thickness
        elif design_dictionary[KEY_LOCATION] == 'Short Leg':
            self.min_plate_height = self.section_size_1.min_leg - self.section_size_1.root_radius - self.section_size_1.thickness
            self.max_plate_height = self.section_size_1.min_leg - self.section_size_1.root_radius - self.section_size_1.thickness


            # self.res_force = math.sqrt(self.load.shear_force ** 2 + self.load.axial_force ** 2) * 1000
        self.res_force = self.load.axial_force*1000
        # if current_thick == None:
        if design_dictionary[KEY_SEC_PROFILE] in ["Channels", 'Back to Back Channels']:
            bolts_required_previous = 2
            self.thick = self.section_size_1.web_thickness
            self.plate.thickness_provided = self.closest(self, self.plate_thickness, self.thick)
        else:
            bolts_required_previous = 1
            self.thick = self.section_size_1.thickness
            self.plate.thickness_provided = self.closest(self, self.plate_thickness, self.thick)
    # else:
        #     self.plate.thickness_provided = current_thick

        self.weld.weld_size(plate_thickness = self.plate.thickness_provided, member_thickness= self.thick)

        self.get_weld_strength(self,connecting_fu= [self.section_size_1.fu,self.plate.fu], weld_fabrication = self.weld.fabrication , t_weld = self.weld.size, force = (self.load.axial_force*1000))
        if design_dictionary[KEY_SEC_PROFILE] == "Channels":
            web_weld = self.section_size_1.depth - 2 * self.weld.size
            flange_weld = round_up(((self.weld.effective - web_weld)/2),5,50)
            self.weld.length = round_up((web_weld + 2 * flange_weld),5,100)

        elif design_dictionary[KEY_SEC_PROFILE] == 'Back to Back Channels':
            web_weld = 2 * (self.section_size_1.depth - 2 * self.weld.size)
            flange_weld = round_up(((self.weld.effective - web_weld)/4),5,50)
            self.weld.length = round_up((web_weld + 4*flange_weld),5,100)

        elif design_dictionary[KEY_SEC_PROFILE] in ["Star Angles", "Back to Back Angles"] and design_dictionary[KEY_LOCATION] == "Long Leg":
            web_weld = 2 * (self.section_size_1.max_leg - 2 * self.weld.size)
            flange_weld = round_up(((self.weld.effective - web_weld) / 4), 5, 50)
            self.weld.length = round_up((web_weld + 4 * flange_weld),5,100)

        elif design_dictionary[KEY_SEC_PROFILE] in ["Star Angles", "Back to Back Angles"] and design_dictionary[KEY_LOCATION] == "Short Leg":
            web_weld = 2 * (self.section_size_1.min_leg - 2 * self.weld.size)
            flange_weld = round_up(((self.weld.effective - web_weld) / 4), 5, 50)
            self.weld.length = round_up((web_weld + 4 * flange_weld),5,100)

        elif design_dictionary[KEY_SEC_PROFILE] == "Angles" and design_dictionary[KEY_LOCATION] == "Long Leg":
            web_weld = (self.section_size_1.max_leg - 2 * self.weld.size)
            flange_weld = round_up(((self.weld.effective - web_weld) / 2), 5, 50)
            self.weld.length = round_up((web_weld + 2 * flange_weld),5,100)

        else:
            web_weld = (self.section_size_1.min_leg - 2 * self.weld.size)
            flange_weld = round_up(((self.weld.effective - web_weld) / 2), 5, 50)
            self.weld.length = round_up((web_weld + 2 * flange_weld),5,100)

        self.weld.get_weld_stress(weld_axial = self.load.axial_force, l_weld = self.weld.effective)

        if self.weld.strength> self.weld.stress:
            self.design_status = True
            self.member_check(self,design_dictionary)
        else:
            self.design_status = False


    def get_weld_strength(self,connecting_fu, weld_fabrication, t_weld, force, weld_angle = 90):
        f_wd = IS800_2007.cl_10_5_7_1_1_fillet_weld_design_stress(connecting_fu, weld_fabrication)
        throat_tk = IS800_2007.cl_10_5_3_2_fillet_weld_effective_throat_thickness(t_weld, weld_angle)
        weld_strength = f_wd * throat_tk
        L_eff = round_up((force/weld_strength),5,100)
        Btw = IS800_2007.cl_10_5_7_3_weld_long_joint(L_eff, throat_tk)
        if L_eff > 150 * throat_tk:
            f_wd = Btw * f_wd
            throat_tk = IS800_2007.cl_10_5_3_2_fillet_weld_effective_throat_thickness(t_weld, weld_angle)
            weld_strength = f_wd * throat_tk
            L_eff = round_up((force / weld_strength), 5, 100)
        else:
            pass

        self.weld.strength =  weld_strength
        self.weld.effective = L_eff




    def member_check(self,design_dictionary):

        if design_dictionary[KEY_LOCATION] == 'Long Leg':
            w = self.section_size_1.min_leg
            shear_lag = w
            L_c = self.weld.length - self.section_size_1.min_leg - 2 * self.weld.size
            A_go = self.section_size_1.min_leg * self.section_size_1.thickness
            A_nc = (self.section_size_1.max_leg * self.section_size_1.thickness)
            t = self.section_size_1.thickness

        elif design_dictionary[KEY_LOCATION] == 'Short Leg':
            w = self.section_size_1.max_leg
            shear_lag = w
            L_c = self.weld.length - self.section_size_1.max_leg - 2 * self.weld.size
            A_go = self.section_size_1.max_leg * self.section_size_1.thickness
            A_nc = (self.section_size_1.min_leg * self.section_size_1.thickness)
            t = self.section_size_1.thickness

        elif design_dictionary[KEY_SEC_PROFILE] in ["Channels", 'Back to Back Channels']:
            w = self.section_size_1.flange_width
            shear_lag = w
            L_c = self.weld.length - self.section_size_1.depth - 2 * self.weld.size
            A_go = self.section_size_1.flange_width * self.section_size_1.flange_thickness*2
            A_nc = (self.section_size_1.depth * self.section_size_1.web_thickness)
            t = self.section_size_1.web_thickness
        # if design_dictionary[KEY_SEC_PROFILE] in ["Channels", 'Back to Back Channels']:
        #     self.section_size_1.tension_rupture(A_n= member_An,F_u= self.section_size_1.fu)
        # else:
        self.section_size_1.tension_member_design_due_to_rupture_of_critical_section( A_nc = A_nc , A_go = A_go, F_u = self.section_size_1.fu, F_y = self.section_size_1.fy, L_c = L_c, w = w, b_s = shear_lag, t = t)

        if design_dictionary[KEY_SEC_PROFILE] in ["Back to Back Angles", "Star Angles", "Back to Back Channels"]:
            self.section_size_1.tension_rupture_capacity = 2 * self.section_size_1.tension_rupture_capacity
        elif design_dictionary[KEY_SEC_PROFILE] in ["Angles","Channels"]:
            self.section_size_1.tension_rupture_capacity = self.section_size_1.tension_rupture_capacity
        else:
            pass

        # self.section_size_1.tension_blockshear_area_input (A_vg = A_vg, A_vn = A_vn, A_tg = A_tg, A_tn = A_tn, f_u = self.section_size_1.fu, f_y = self.section_size_1.fy)
        self. K = 1
        self.section_size_1.design_check_for_slenderness(K = self.K, L = design_dictionary[KEY_LENGTH], r = self.section_size_1.min_radius_gyration)
        self.section_size_1.tension_capacity = min (self.section_size_1.tension_yielding_capacity, self.section_size_1.tension_rupture_capacity)

        self.member_recheck(self, design_dictionary)

    def member_recheck(self,design_dictionary):

        if self.section_size_1.slenderness < 400:
            self.design_status = True
        else:
            self.design_status = False

        if self.section_size_1.tension_capacity > self.load.axial_force:
            self.efficiency = round((self.load.axial_force / self.section_size_1.tension_capacity), 2)
            self.get_plate_thickness(self,design_dictionary)
            self.design_status = True
        else:
            print("recheck")
            previous_size = self.section_size_1.designation
            self.initial_member_capacity(self, design_dictionary, previous_size)

    def get_plate_thickness(self,design_dictionary):

        self.plate_last = self.plate.thickness[-1]

        if design_dictionary[KEY_SEC_PROFILE] in ["Channels", 'Back to Back Channels']:
            # bolts_required_previous = 2
            self.thick = self.section_size_1.web_thickness
            self.plate.thickness_provided = self.closest(self, self.plate_thickness, self.thick)
        else:
            # bolts_required_previous = 1
            self.thick = self.section_size_1.thickness
            self.plate.thickness_provided = self.closest(self, self.plate_thickness, self.thick)

        self.thickness_possible = [i for i in self.plate.thickness if i >= self.thick]
        self.plate_thick_weld = self.thickness_possible[-1]

        for self.plate.thickness_provided in self.thickness_possible:
            if design_dictionary[KEY_SEC_PROFILE] in ["Channels", 'Back to Back Channels']:
                self.plate.tension_yielding(length = self.section_size_1.depth, thickness = self.plate.thickness_provided, fy = self.plate.fy)
                self.net_area = self.section_size_1.depth * self.plate.thickness_provided

            else:
                if design_dictionary[KEY_LOCATION] == 'Long Leg':
                    self.plate.tension_yielding(length = self.section_size_1.max_leg, thickness = self.plate.thickness_provided, fy = self.plate.fy)
                    self.net_area = self.section_size_1.max_leg * self.plate.thickness_provided
                else:
                    self.plate.tension_yielding(length = self.section_size_1.min_leg, thickness = self.plate.thickness_provided, fy = self.plate.fy)
                    self.net_area = self.section_size_1.min_leg * self.plate.thickness_provided

            self.plate.tension_rupture(A_n = self.net_area, F_u = self.plate.fu)
            # if (design_dictionary[KEY_SEC_PROFILE] == "Channels" or design_dictionary[KEY_SEC_PROFILE] =="Back to Back Channels") and design_dictionary[KEY_LOCATION] == "Web":
            #     if self.plate.bolts_one_line >= 2:
            if design_dictionary[KEY_SEC_PROFILE] == "Channels":
                A_vg = (self.weld.length - (self.section_size_1.depth - 2 * self.weld.size) + 4 * self.weld.size)*self.plate.thickness_provided
                A_vn = A_vg
                A_tg = self.section_size_1.depth * self.plate.thickness_provided
                A_tn = A_tg
                self.plate.length = (self.weld.length - (self.section_size_1.depth - 2 * self.weld.size) + 4 * self.weld.size)/2
                self.plate.height = self.section_size_1.depth

            elif design_dictionary[KEY_SEC_PROFILE] == "Back to Back Channels":
                A_vg = ((self.weld.length - 2 * (self.section_size_1.depth - 2 * self.weld.size)) + 8 * self.weld.size) * self.plate.thickness_provided
                A_vn = A_vg
                A_tg = self.section_size_1.depth * self.plate.thickness_provided
                A_tn = A_tg
                self.plate.length = ((self.weld.length - 2 * (self.section_size_1.depth - 2 * self.weld.size)) + 8 * self.weld.size)/4
                self.plate.height = self.section_size_1.depth

            elif design_dictionary[KEY_SEC_PROFILE] in ["Star Angles", "Back to Back Angles"] and design_dictionary[KEY_LOCATION]== "Long Leg":
                A_vg =  ((self.weld.length - 2 * (self.section_size_1.max_leg - 2 * self.weld.size)) + 8 * self.weld.size) * self.plate.thickness_provided
                A_vn = A_vg
                A_tg = self.section_size_1.max_leg * self.plate.thickness_provided
                A_tn = A_tg
                self.plate.length = ((self.weld.length - 2 * (self.section_size_1.max_leg - 2 * self.weld.size)) + 8 * self.weld.size)/4
                self.plate.height = self.section_size_1.max_leg

            elif design_dictionary[KEY_SEC_PROFILE] in ["Star Angles", "Back to Back Angles"] and design_dictionary[KEY_LOCATION] == "Short Leg":
                A_vg = ((self.weld.length - 2 * (self.section_size_1.min_leg - 2 * self.weld.size)) + 8 * self.weld.size) * self.plate.thickness_provided
                A_vn = A_vg
                A_tg = self.section_size_1.min_leg * self.plate.thickness_provided
                A_tn = A_tg
                self.plate.length = ((self.weld.length - 2 * (self.section_size_1.min_leg - 2 * self.weld.size)) + 8 * self.weld.size) / 4
                self.plate.height = self.section_size_1.max_leg

            elif design_dictionary[KEY_SEC_PROFILE]== "Angles" and design_dictionary[KEY_LOCATION]== "Long Leg":
                A_vg =  ((self.weld.length - (self.section_size_1.max_leg - 2 * self.weld.size)) + 4 * self.weld.size) * self.plate.thickness_provided
                A_vn = A_vg
                A_tg = self.section_size_1.max_leg * self.plate.thickness_provided
                A_tn = A_tg
                self.plate.length = ((self.weld.length - (self.section_size_1.max_leg - 2 * self.weld.size)) + 4 * self.weld.size) / 2
                self.plate.height = self.section_size_1.max_leg
            else:
                A_vg = ((self.weld.length - (self.section_size_1.min_leg - 2 * self.weld.size)) + 4 * self.weld.size) * self.plate.thickness_provided
                A_vn = A_vg
                A_tg = self.section_size_1.min_leg * self.plate.thickness_provided
                A_tn = A_tg
                self.plate.length = ((self.weld.length - (self.section_size_1.min_leg - 2 * self.weld.size)) + 4 * self.weld.size) / 2
                self.plate.height = self.section_size_1.min_leg

            self.plate.tension_blockshear_area_input(A_vg = A_vg, A_vn = A_vn, A_tg = A_tg, A_tn = A_tn, f_u = self.plate.fu, f_y = self.plate.fy)
            self.plate_tension_capacity = min(self.plate.tension_yielding_capacity,self.plate.tension_rupture_capacity,self.plate.block_shear_capacity)

            if self.plate_tension_capacity > self.load.axial_force:
                self.design_status = True
                break

                # if self.plate.thickness_provided == self.plate_thick_weld:
                #     self.design_status = True
                #     break
                # else:
                #     self.select_weld(self,design_dictionary,self.plate.thickness_provided)

            elif (self.plate_tension_capacity < self.load.axial_force) and self.plate.thickness_provided == self.plate_last:
                self.design_status = False
                logger.error("Plate thickness is not sufficient")
            else:
                pass


#     def save_design(self,ui,popup_summary):
#
#
#         self.report_input =  {'Connection':{"Connection Title" : 'Finplate', 'Connection Type': 'Shear Connection'},"Connection Category":{"Connectivity": 'Column flange-Beam web', "Beam Connection":"Bolted", "Column Connection": "Welded"},"Loading":{'ShearForce(kN) - Vs': 140},"Components":{"Column Section": 'UC 305 x 305 x 97',"Column Material":"E250(Fe410W)A", "Column(N/mm2)-Fuc":410, "Column(N/mm2)-Fyc":250,"Column Details": "","Beam Section": "MB 500", "Beam Material":"E250(Fe410W)A", "Beam(N/mm2)-Fub":410, "Beam(N/mm2)-Fyb":250, "Beam Details": "","Plate Section" : '300 x 100 x 12',  'Thickness(mm)-tp': 12.0, 'Depth(mm)-dp': 300.0, 'Width(mm)-wp': 118.0, 'externalmoment(kN) - md': 8.96, "Weld": "", "Weld Type":"Double Fillet", "Size(mm)-ws": 12, 'Type_of_weld': 'Shop weld', 'Safety_Factor- ': 1.25, 'Weld(kN) - Fuw ': 410, 'WeldStrength - wst': 1590.715 , "EffectiveWeldLength(mm) - efl": 276.0 ,"Bolts":"",'Diameter (mm) - d': 24 , 'Grade': 8.8 ,
#                     'Bolt Type': 'Friction Grip Bolt','Bolt Hole Type': 'Standard', 'Bolt Hole Clearance - bc': 2,'Slip Factor - sf': 0.3, 'k_b': 0.519,"Number of effective interface - ne":1, "Factor for clearance- Kh":1,"Minimum Bolt Tension - F0": 50, "Bolt Fu - Fubo": 800, "Bolt Fy - Fybo": 400, "Bolt Numbers - nb": 3, "Bolts per Row - rb": 1, "Bolts per Column - cb": 1, "Gauge (mm) - g": 0, "Pitch(mm) - p": 100, 'colflangethk(mm) - cft ': 15.4, 'colrootradius(mm) - crr': 15.2,'End Distance(mm) - en': 54.0, 'Edge Distance(mm) - eg': 54.0, 'Type of Edge': 'a - Sheared or hand flame cut', 'Min_Edge/end_dist': 1.7, 'gap': 10.0,'is_env_corrosive': 'No'}}
#
#         self.report_supporting = {'Mass': self.supporting_section.mass,
#                                   'Area(cm2) - A': self.supporting_section.area,
#                                   'D(mm)': self.supporting_section.depth,
#                                   'B(mm)': self.supporting_section.flange_width,
#                                   't(mm)': self.supporting_section.web_thickness,
#                                   'T(mm)': self.supporting_section.flange_thickness,
#                                   'FlangeSlope': self.supporting_section.flange_slope,
#                                   'R1(mm)': self.supporting_section.root_radius,
#                                   'R2(mm)': self.supporting_section.toe_radius,
#                                   'Iz(cm4)': self.supporting_section.mom_inertia_z,
#                                   'Iy(cm4)': self.supporting_section.mom_inertia_y,
#                                   'rz(cm)': self.supporting_section.rad_of_gy_z,
#                                   'ry(cm)': self.supporting_section.rad_of_gy_y,
#                                   'Zz(cm3)': self.supporting_section.elast_sec_mod_z,
#                                   'Zy(cm3)': self.supporting_section.elast_sec_mod_y,
#                                   'Zpz(cm3)': self.supporting_section.plast_sec_mod_z,
#                                   'Zpy(cm3)': self.supporting_section.elast_sec_mod_y}
#
#         self.report_supported = {'Mass': 86.9, 'Area(cm2) - A': 111.0, 'D(mm)': 500.0, 'B(mm)': 180.0, 't(mm)': 10.2,
#                                                     'T(mm)': 17.2, 'FlangeSlope': 98, 'R1(mm)': 17.0, 'R2(mm)': 8.5, 'Iz(cm4)': 45228.0,
#                                                     'Iy(cm4)': 1320.0, 'rz(cm)': 20.2, 'ry(cm)': 3.5, 'Zz(cm3)': 1809.1, 'Zy(cm3)': 147.0,
#                                                     'Zpz(cm3)': 2074.8, 'Zpy(cm3)': 266.7}
#         self.report_result = {"thinnerplate": 10.2,
#             'Bolt': {'status': True, 'shearcapacity': 47.443, 'bearingcapacity': 1.0, 'boltcapacity': 47.443,
#                      'numofbolts': 3, 'boltgrpcapacity': 142.33, 'numofrow': 3, 'numofcol': 1, 'pitch': 96.0,
#                      'edge': 54.0, 'enddist': 54.0, 'gauge': 0.0, 'bolt_fu': 800.0, 'bolt_dia': 24, 'k_b': 0.519,
#                      'beam_w_t': 10.2, 'web_plate_t': 12.0, 'beam_fu': 410.0, 'shearforce': 140.0, 'dia_hole': 26},
#             'FlangeBolt':{'MaxPitchF': 50},
#             'Weld': {'thickness': 10, 'thicknessprovided': 12.0, 'resultantshear': 434.557, 'weldstrength': 1590.715,
#                      'weld_fu': 410.0, 'effectiveWeldlength': 276.0},
#             'Plate': {'minHeight': 300.0, 'minWidth': 118.0, 'plateedge': 64.0, 'externalmoment': 8.96,
#                       'momentcapacity': 49.091, 'height': 300.0, 'width': 118.0, 'blockshear': 439.837,
#                       'web_plate_fy': 250.0, 'platethk': 12.0, 'beamdepth': 500.0, 'beamrootradius': 17.0,
#                       'colrootradius': 15.2, 'beamflangethk': 17.2, 'colflangethk': 15.4}}
#
#         self.report_check = ["bolt_shear_capacity", "bolt_bearing_capacity", "bolt_capacity", "No_of_bolts", "No_of_Rows",
#                         "No_of_Columns", "Thinner_Plate", "Bolt_Pitch", "Bolt_Gauge", "End_distance", "Edge_distance", "Block_Shear",
#                         "Plate_thickness", "Plate_height", "Plate_Width", "Plate_Moment_Capacity", "Effective_weld_length",
#                         "Weld_Strength"]
#
#
#         folder = self.select_workspace_folder(self)
#         filename = os.path.join(str(folder), "images_html", "Html_Report.html")
#         file_name = str(filename)
#         ui.call_designreport(self,file_name, popup_summary, folder)
#
#         # Creates PDF
#         config = configparser.ConfigParser()
#         config.readfp(open(r'Osdag.config'))
#         wkhtmltopdf_path = config.get('wkhtml_path', 'path1')
#
#         config = pdfkit.configuration(wkhtmltopdf=wkhtmltopdf_path)
#
#         options = {
#             'margin-bottom': '10mm',
#             'footer-right': '[page]'
#         }
#         file_type = "PDF(*.pdf)"
#         fname, _ = QFileDialog.getSaveFileName(None, "Save File As", folder + "/", file_type)
#         fname = str(fname)
#         flag = True
#         if fname == '':
#             flag = False
#             return flag
#         else:
#             pdfkit.from_file(filename, fname, configuration=config, options=options)
#             QMessageBox.about(None, 'Information', "Report Saved")
#
#         # with open("filename", 'w') as out_file:
#         #     yaml.dump(fin_plate_input, out_file)
#
#     def select_workspace_folder(self):
#         # This function prompts the user to select the workspace folder and returns the name of the workspace folder
#         config = configparser.ConfigParser()
#         config.read_file(open(r'Osdag.config'))
#         desktop_path = config.get("desktop_path", "path1")
#         folder = QFileDialog.getExistingDirectory(None, "Select Workspace Folder (Don't use spaces in the folder name)",
#                                                   desktop_path)
#         return folder
#
#
#     def call_3DModel(self,ui,bgcolor):
#         '''
#         This routine responsible for displaying 3D Cad model
#         :param flag: boolean
#         :return:
#         '''
#         if ui.btn3D.isChecked:
#             ui.chkBxCol.setChecked(Qt.Unchecked)
#             ui.chkBxBeam.setChecked(Qt.Unchecked)
#             ui.chkBxFinplate.setChecked(Qt.Unchecked)
#         ui.commLogicObj.display_3DModel("Model",bgcolor)
#
#     def call_3DBeam(self,ui,bgcolor):
#         '''
#         Creating and displaying 3D Beam
#         '''
#         ui.chkBxBeam.setChecked(Qt.Checked)
#         if ui.chkBxBeam.isChecked():
#             ui.chkBxCol.setChecked(Qt.Unchecked)
#             ui.chkBxFinplate.setChecked(Qt.Unchecked)
#             ui.btn3D.setChecked(Qt.Unchecked)
#             ui.mytabWidget.setCurrentIndex(0)
#
#         ui.commLogicObj.display_3DModel("Beam", bgcolor)
#
#     def call_3DColumn(self, ui, bgcolor):
#         '''
#         '''
#         ui.chkBxCol.setChecked(Qt.Checked)
#         if ui.chkBxCol.isChecked():
#             ui.chkBxBeam.setChecked(Qt.Unchecked)
#             ui.chkBxFinplate.setChecked(Qt.Unchecked)
#             ui.btn3D.setChecked(Qt.Unchecked)
#             ui.mytabWidget.setCurrentIndex(0)
#         ui.commLogicObj.display_3DModel("Column", bgcolor)
#
#     def call_3DFinplate(self,ui,bgcolor):
#         '''
#         Displaying FinPlate in 3D
#         '''
#         ui.chkBxFinplate.setChecked(Qt.Checked)
#         if ui.chkBxFinplate.isChecked():
#             ui.chkBxBeam.setChecked(Qt.Unchecked)
#             ui.chkBxCol.setChecked(Qt.Unchecked)
#             ui.mytabWidget.setCurrentIndex(0)
#             ui.btn3D.setChecked(Qt.Unchecked)
#
#         ui.commLogicObj.display_3DModel("Plate", bgcolor)
#
#     def unchecked_allChkBox(self,ui):
#         '''
#         This routine is responsible for unchecking all checkboxes in GUI
#         '''
#
#         ui.btn3D.setChecked(Qt.Unchecked)
#         ui.chkBxBeam.setChecked(Qt.Unchecked)
#         ui.chkBxCol.setChecked(Qt.Unchecked)
#         ui.chkBxFinplate.setChecked(Qt.Unchecked)
#
#     def showColorDialog(self,ui):
#
#         col = QColorDialog.getColor()
#         colorTup = col.getRgb()
#         r = colorTup[0]
#         g = colorTup[1]
#         b = colorTup[2]
#         ui.display.set_bg_gradient_color([r, g, b], [255, 255, 255])
#
#     def generate_3D_Cad_image(self,ui,folder):
#
#         # folder = self.select_workspace_folder(self)
#
#         # status = self.resultObj['Bolt']['status']
#         if self.design_status is True:
#             self.call_3DModel(self, ui,"gradient_bg")
#             data = os.path.join(str(folder), "images_html", "3D_Model.png")
#             ui.display.ExportToImage(data)
#             ui.display.FitAll()
#             return data
#
#         else:
#             pass
#
#
# # For Command Line
#
#
# # from ast import literal_eval
# #
# # path = input("Enter the file location: ")
# # with open(path, 'r') as f:
# #     data = f.read()
# #     d = literal_eval(data)
# #     FinPlateConnection.set_input_values(FinPlateConnection(), d, False)