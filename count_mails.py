import os, os.path
import mailparser
import hashlib
import sys
import logging
from os import listdir
from os.path import isfile, join
from database import Database

logger = logging.getLogger()
logger.setLevel(logging.INFO)

handler = logging.StreamHandler(sys.stdout)
handler.setLevel(logging.INFO)
formatter = logging.Formatter("%(asctime)s - %(name)s - %(levelname)s - %(message)s")
handler.setFormatter(formatter)
logger.addHandler(handler)


class Execute(object):
  def __init__(self):
    self.database = Database()
    self.database.create_tables()
    self.message_response = {}
        

  # Parse emails to be inserted into MySQL.
  def extract_and_insert_data(self, mail_dir):
    data = None
    logger.info(os.path.dirname(os.path.abspath(mail_dir)))

    logger.info(len([sub_dir for sub_dir in os.listdir(mail_dir) if os.path.isdir(os.path.join(mail_dir, sub_dir))]))
    total_mails_with_duplicates = 0

    for user_dir in os.listdir(mail_dir):
      user = os.path.join(os.path.join(mail_dir, user_dir))
      logger.info("User directory: {}".format(user))
      for user_mail_dir in os.listdir(user):
        logger.info("User mail directory: {}".format(os.path.join(os.path.join(mail_dir, user_dir, user_mail_dir))))
        for root, dirs, files in os.walk(os.path.join(os.path.join(mail_dir, user_dir, user_mail_dir))):
          for email_file in files:
            logger.info("Email file: {}".format(os.path.join(root, email_file)))
            mail_file = os.path.join(root, email_file)
            mail = mailparser.parse_from_file(mail_file)
            hash_body = hashlib.md5(mail.body)
            row = self.database.parse_mail(mail)
            self.insert_into_database(row)
            total_mails_with_duplicates += 1
    logger.info("Total emails with duplicates: {}".format(total_mails_with_duplicates))


  # Insert parsed data into MySQL.
  def insert_into_database(self, row):
    erow = row.get("message_id"), row.get("from"), row.get(
        "subject"), self.database.convert_date_format(
        row.get("date_created")), row.get("body_md5"), row.get("sub_md5")
    erows = [erow]
    rrows = []
    for to in row.get("to"):
      rrow = row.get("message_id"), row.get(
          "from"), to, 1, 0, 0
      rrows.append(rrow)
    for cc in row.get("cc"):
      rrow = row.get("message_id"), row.get(
          "from"), cc, 0, 1, 0
      rrows.append(rrow)
    for bcc in row.get("bcc"):
      rrow = row.get("message_id"), row.get(
          "from"), bcc, 0, 0, 1
      rrows.append(rrow)
    self.database.insert("email", erows)
    self.database.insert("recipient", rrows)


  def total_number_of_emails(self):
    logger.info("Total number of emails(without duplicates, assuming emails with same MailId as duplicates)")
    for count in self.database.run_query("""SELECT COUNT(*) FROM email;"""):
      logger.info(count)


  def emails_received_per_person(self):
    logger.info("Number of emails received per person")
    for receiver, emails_received in self.database.run_query(
      """
        SELECT receiver, COUNT(r.MessageId) AS emails_received 
        FROM recipient r, email e 
        WHERE e.MessageId = r.MessageId 
        GROUP BY receiver 
        ORDER BY emails_received desc;
      """):
      logger.info("{}, {}".format(receiver, emails_received))


  def fast_responses(self):
    logger.info("Fastest responses")
    logger.info("-----------------")
    for from_, to, sub, email_date, resp_time in self.database.run_query(
      """
        SELECT
          m1.Sender as `FROM`,
          m2.Sender as `TO`,
          m1.Subject as `SUBJECT`,
          m1.DateCreated as `DATE`,
          ABS(TIME_TO_SEC(TIMEDIFF(m1.DateCreated, m2.DateCreated))) as `RESPONSE TIME (seconds)`
        FROM email m1 INNER JOIN email m2
        ON m1.DateCreated IS NOT NULL AND
          m2.DateCreated IS NOT NULL AND
          m1.subject IS NOT NULL AND
          m2.subject IS NOT NULL AND
          m1.SubjectMd5 = m2.SubjectMd5 AND
          m1.Sender <> m2.Sender AND
          LOWER(m2.Subject) LIKE "%re:%"
        GROUP BY m2.BodyMd5
        ORDER BY `RESPONSE TIME (seconds)`
        LIMIT 5;
      """): 
      logger.info("{}, {}, {}, {}, {}".format(from_, to, sub, email_date, resp_time))


  # Make sure the directory of emails can be found.
  def check_for_emails(self):
    if os.path.isdir("maildir"):
      return True
    else:
      logger.error("Unable to find maildir")
      return False


  # Run Full Job
  def execute(self):
    mail_dir = os.getcwd() + "/maildir"
    if self.check_for_emails():
      self.extract_and_insert_data(mail_dir)


if __name__ == "__main__":
  ex = Execute()
  ex.execute()
  ex.total_number_of_emails()
  ex.emails_received_per_person()
  ex.fast_responses()
  


