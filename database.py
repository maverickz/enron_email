#!/usr/bin/python

from pymysql.err import InternalError,IntegrityError
from dateutil.parser import parse
import os
import hashlib
import yaml
import pymysql
import logging
import sys

logger = logging.getLogger()
logger.setLevel(logging.DEBUG)

handler = logging.StreamHandler(sys.stdout)
handler.setLevel(logging.DEBUG)
formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
handler.setFormatter(formatter)
logger.addHandler(handler)


class Database(object):
  def __init__(self):
    self.config = os.getcwd() + "/mysql/database.yaml"
    self.config_yaml = self.get_config()

    self.schema = self.config_yaml.get('config').get('schema')
    self.db_host = self.config_yaml.get('config').get('host')
    self.db_user = self.config_yaml.get('config').get('user')
    self.db_pass = self.config_yaml.get('config').get('pass')
    self.db_port = self.config_yaml.get('config').get('port')
    self.conn = pymysql.connect(host=self.db_host,
                                port=self.db_port,
                                user=self.db_user,
                                passwd=self.db_pass,
                                db=self.schema, charset='utf8',
                                autocommit=True)
    self.cursor = self.conn.cursor()

  def get_config(self):
    return yaml.load(open(self.config))

  def create_tables(self):
    for name, ddl in self.config_yaml.get('ddl').items():
      if 'drop' in name:
        logger.info("Dropping table {}: ".format(name))
      elif 'create' in name:
        logger.info("Creating table {}: ".format(name))
      try:
        self.cursor.execute(ddl)
      except InternalError as e:
        logger.error(e)

  def insert(self, table=None, rows=None):
    if rows is None or table is None:
      logger.error("Table {} not found".format(table))
      return False
    if table is 'email':
      for row in rows:
        try:
          self.cursor.execute("INSERT IGNORE INTO email(MessageId, Sender, Subject, DateCreated, BodyMd5, SubjectMd5) VALUES (%s,%s,%s,%s,%s,%s)",row)
        except IntegrityError as e:
          logger.error(e)
    elif table is 'recipient':
      for row in rows:
        try:
          self.cursor.execute("INSERT INTO recipient(MessageId, Sender, Receiver, isTo, isCc, isBcc) VALUES (%s,%s,%s,%s,%s,%s)",row)
        except IntegrityError as e:
          logger.error(e)
    else:
      logger.error("FAILURE")
      return False

  def run_query(self, query=None, n=None):
    if query is None:
      return None
    self.cursor.execute(query)
    if n is None:
      return self.cursor.fetchall()
    elif n == 1:
      return self.cursor.fetchone()
    else:
      return self.cursor.fetchmany(5)

  def convert_date_format(self,dt=None):
    # datetime is in UTC
    if dt:
      return dt.strftime("%Y-%m-%d %H:%M:%S")
    else:
      return None

  def parse_mail(self, mail):
      row = {}

      row['to'] = sorted([elem[1] for elem in mail.to])
      row['cc'] = sorted([elem[1] for elem in mail.cc])
      row['from'] = mail.from_[0][1]
      row['bcc'] = sorted([elem[1] for elem in mail.bcc])
      row['subject'] = mail.subject
      row['message_id'] = mail.message_id
      row['date_created'] = mail.date
      row['body_md5'] = hashlib.md5(mail.body).hexdigest() if mail.body else None
      row['sub_md5'] = hashlib.md5(
          mail.subject.encode('utf-8').lower().replace("re:", "").strip()).hexdigest() if mail.subject else None
      logger.info("DB row: {}".format(row))
      return row
