__appname__="PyDataMan"
__module__="main"


from PyQt5.QtGui import *
from PyQt5.QtCore import *
from PyQt5.QtWidgets import *
import sys
from ui_files import mainWindow
import sqlite3
import re
import os
import logging
import csv
import preferences
import utilities
import traceback

appDataPath=os.getcwd() #+"\pyDataman"
appDataPath=os.environ["APPDATA"]+"\\PyDataMan\\"
if not os.path.exists(appDataPath):
    try:
        os.makedirs(appDataPath)
    except Exception:
        appDataPath=os.getcwd()
#print(appDataPath)
logging.basicConfig(filename=appDataPath+"pydataman.log",format="%(asctime)-15s:%(name)-18s-%(levelname)-8s-%(module)-15s-%(funcname)-20s-%(lineno)-6d-%(message)s",level=logging.DEBUG)
logger=logging.getLogger(name="main-gui")


class Main(QMainWindow,mainWindow.Ui_mainwindow):

    dbPath=appDataPath+"pydata.db"
    dbConn=sqlite3.connect(dbPath)

    def __init__(self):
        super(Main, self).__init__()
        self.setupUi(self)
        # try:
        #     lksglklkgn
        # except Exception:
        #     print("hello")
        # logger.debug("application initialized")

        self.dbCursor=self.dbConn.cursor()
        self.dbCursor.execute("""CREATE TABLE IF NOT EXISTS
                            Main(id INTEGER PRIMARY KEY,
                            username TEXT, name TEXT,phone TEXT,address TEXT,status TEXT)""")
        self.dbConn.commit()

        self.settings=QSettings(QSettings.IniFormat,QSettings.UserScope,"PyDataMan","PyDataMan")


        self.addData.clicked.connect(self.add_button_clicked)
        self.removeRow.clicked.connect(self.remove_row_clicked)
        self.actionExport.triggered.connect(self.export_action_triggered)
        self.actionPreferences.triggered.connect(self.preferences_action_triggered)
        self.actionExit.triggered.connect(self.exit_action_triggered)
        self.showToolBar=utilities.str2bool(self.settings.value("showToolbar",True))
        # print(self.showToolBar)

        self.mainToolBar.setVisible(self.showToolBar)

        self.load_initila_settings()


    def load_initila_settings(self):
        """loads the initials settings for the application, setts the main table widths"""
        self.dbCursor.execute("""SELECT * FROM Main""")
        allrows=self.dbCursor.fetchall()

        for row in allrows:
            inx=allrows.index(row)
            self.mainTable.insertRow(inx)
            self.mainTable.setItem(inx, 0, QTableWidgetItem(row[1]))
            self.mainTable.setItem(inx, 1, QTableWidgetItem(row[2]))
            self.mainTable.setItem(inx, 2, QTableWidgetItem(row[3]))
            self.mainTable.setItem(inx, 3, QTableWidgetItem(row[4]))
            self.mainTable.setItem(inx, 4, QTableWidgetItem(row[5]))

    def add_button_clicked(self):
        """calls the vaidate_fields() method, and adds the items to the table"""
        username=self.userName.text()
        first_name=self.firstName.text()
        phone=self.phoneNumber.text()
        address=self.addres.text()
        approved=self.approved.isChecked()

        if not self.validate_fields():
            return False

        currentRowCount=self.mainTable.rowCount()
        self.mainTable.insertRow(currentRowCount)
        self.mainTable.setItem(currentRowCount,0,QTableWidgetItem(username))
        self.mainTable.setItem(currentRowCount, 1, QTableWidgetItem(first_name))
        self.mainTable.setItem(currentRowCount, 2, QTableWidgetItem(phone))
        self.mainTable.setItem(currentRowCount, 3, QTableWidgetItem(address))
        self.mainTable.setItem(currentRowCount, 4, QTableWidgetItem("Approved" if approved else "Not Approved"))

        parameters=(None,username,first_name,phone,address,str(approved))

        self.dbCursor.execute("""INSERT INTO Main VALUES (?,?,?,?,?,?)""",parameters)
        self.dbConn.commit()



    def remove_row_clicked(self):
        """remove the data from table and database"""
        currenRow=self.mainTable.currentRow()

        if currenRow>-1:
            currentUserName=(self.mainTable.item(currenRow,0).text(),)
            self.dbCursor.execute("""DELETE FROM Main WHERE username=?""",currentUserName)
            self.dbConn.commit()
            self.mainTable.removeRow(currenRow)


    def validate_fields(self):
        """validate QLineEdit based on regex"""
        usernames=self.dbCursor.execute("""SELECT username FROM Main""")
        for username in usernames:
            if self.userName.text() in username[0]:
                QMessageBox.warning(self,"warning","Such username already exist!")
                return False
        if not re.match('^[2-9]\d{2}-\d{3}-\d{4}',self.phoneNumber.text()):
            QMessageBox.warning(self,"Warning","Phone number seems incorrect")
            return False
        return True

    def import_action_triggered(self):
        """database import handler"""
        pass

    def export_action_triggered(self):
        """database export handler"""
        self.dbCursor.execute("SELECT * FROM Main")
        rows = self.dbCursor.fetchall()
        #print(rows)
        #dbFile=QFileDialog.getSaveFileName(self,parent=None,str_caption="Export database file",str_directory=".",str_filter="PyDataMan(*.csv)")

        dbFile=QFileDialog.getSaveFileName(self,"Export database file",".","PyDataMan(*.csv)")
        if dbFile[0]:
            try:
                with open(dbFile[0],"w") as csvFile:
                    csvWriter=csv.writer(csvFile,dialect='excel')
                    #print(rows)
                    rowCount=len(rows)
                    for row in rows:
                        csvWriter.writerow(row)
                    QMessageBox.information(self,__appname__,"Succesfuly exported"+str(rowCount)+
                                                   " rows to file\r\n"+str(QDir.toNativeSeparators(dbFile[0])))
            except Exception:
                 QMessageBox.critical(self,__appname__,"Error exporting file")
                 logger.critical("error exporting file the error is dbFile is" + str(dbFile[0]))
                 return

    def preferences_action_triggered(self):
        """fires up the Preferences dialog"""
        dlg=preferences.Preferences(self,showToolbar=self.showToolBar)
        sig=dlg.checkboxsig
        sig.connect(self.showHideToolbar)
        dlg.exec_()

    def showHideToolbar(self,param):
        """show hide mail toolbar"""
        self.mainToolBar.setVisible(param)
        self.settings.setValue("showToolbar",utilities.bool2str(param))


    def about_action_triggered(self):
        pass

    def exit_action_triggered(self):
        self.close()

    def closeEvent(self,event,*args,**kwargs):
        """overides the default close method"""
        result=QMessageBox.question(self,__appname__,"are you sure want to exit",QMessageBox.Yes|QMessageBox.No,QMessageBox.Yes)
        if result==QMessageBox.Yes:
            event.accept()
        else:
            event.ignore()
def unhandled_exception(type,value,exp_traceback):
     exception="".join(traceback.format_exception(type,value,exp_traceback))
     logger.critical(str(exception))
     sys.exit(1)

def main():
    QCoreApplication.setApplicationName("PyDataMan")
    QCoreApplication.setApplicationVersion("0.1")
    QCoreApplication.setOrganizationName("PyDataMan")
    QCoreApplication.setOrganizationDomain("pydataman.com")
    sys.excepthook=unhandled_exception

    app = QApplication(sys.argv)
    form = Main()
    form.show()
    sys.exit(app.exec_())

if __name__ == '__main__':
    main()

