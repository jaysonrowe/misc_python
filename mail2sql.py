#!/usr/bin/env python
# mail2sql.py - J Knowler, 10-10-2008 v1.0
# Purpose:
# Read a postfix/sendmail email file from STDIN, parse it and output to a MySQL database.
# Errors and warnings are reported via email and logged to STDOUT
#
# Usage:
# cat emailfile | mail2sql.py
# * Note: can be piped to via a .procmailrc file
#
# --
# -- MySQL Table structure for table `msg`
# --
#
# CREATE TABLE `msg` (
#  `id` int(11) NOT NULL auto_increment,
#  `bindata` longblob NOT NULL,
#  `msgfrom` text NOT NULL,
#  `msgto` text NOT NULL,
#  `msgsubj` text NOT NULL,
#  `msgdate` datetime NOT NULL,
#  PRIMARY KEY  (`id`)
# ) ENGINE=MyISAM AUTO_INCREMENT=165 DEFAULT CHARSET=latin1 COMMENT='email archive ' AUTO_INCREMENT=1 ;

# Import in the libs we need
import sys, time, email, email.Message, email.Errors, email.Utils, smtplib, MySQLdb

#
# Define User Variables
admin_email = "sysadmin@xxxxxxxx.com"
report_errors_to_email = "someone@xxxxxxxx.com"
smtp_server = "mail.xxxxxxxx.com"
mysql_server = "localhost"
mysql_database = "archives"
mysql_table = "msg"
mysql_user = "xxxxxx"
mysql_password = "xxxxxx"

#
# Funtion to send error messages via email
def mail(serverURL=None, sender='', to='', subject='', text=''):
    message = email.Message.Message()
    message["To"]      = to
    message["From"]    = sender
    message["Subject"] = subject
    message.set_payload(text)
    mailServer = smtplib.SMTP(serverURL)
    mailServer.sendmail(sender, to, message.as_string())
    mailServer.quit()

#
# ---- Start of MAIN script ----
#

#
#
# Parse the mail with error checking
try:
    emailmsg = email.message_from_string(raw_msg)
except email.Errors.MessageError, val:
    warn("Message parse error: %s" % (str(val)))
    mail(smtp_server, admin_email, report_errors_to_email, \
        "mail2sql Parsing Error", \
        "Message parse error: %s" % (str(val)))

#
# Extract database Fields from mail
msgfrom = MySQLdb.escape_string(emailmsg['From'])
msgto =  MySQLdb.escape_string(emailmsg['To'])
msgsubj = MySQLdb.escape_string(emailmsg['Subject'])

#
# Convert email Date/Time to MySQL compatible DateTime type
msgdate = time.strftime('%Y_%m_%d.%T', email.Utils.parsedate(emailmsg['date']))

#
# Connect to MySQL and check for errors
try:
    db=MySQLdb.connect(user=mysql_user,passwd=mysql_password,db=mysql_database)
except MySQLdb.Error, e:
    print "MySQLdb CONNECT Error %d: %s" % (e.args[0], e.args[1])
    mail(smtp_server, admin_email, report_errors_to_email, \
        "mail2sql Database Connection Error", \
        "MySQLdb CONNECT Error %d: %s" % (e.args[0], e.args[1]))
    sys.exit (1)

#
# Setup the Database Cursor
c=db.cursor()

# Insert Data into MYSQL(copy of entire raw email is stored as a BLOB in MySQL)
# with error checking
sql = "INSERT INTO %s (bindata, msgfrom, msgto, msgsubj, msgdate) \
    VALUES('%s','%s','%s','%s','%s')" % \
    (mysql_table, MySQLdb.escape_string(raw_msg), msgfrom, msgto, msgsubj, msgdate)
try:
    c.execute(sql)
except MySQLdb.Error, e:
    print "MySQLdb INSERT Error %d: %s" % (e.args[0], e.args[1])
    mail(smtp_server, admin_email, report_errors_to_email, \
        "mail2sql MySQL Database INSERT Error", \
        "MySQLdb INSERT Error %d: %s" % (e.args[0], e.args[1]))
    sys.exit (1)

# Clean up
c.close ()
db.commit()
db.close ()

# --- End of Script ---