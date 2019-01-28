#!/bin/sh

# Ensure that mysql is running locally on port 3306
# Create `test` user as outlined under `query/test_user_creation.sql
# Create a new database `enron`

wget https://www.cs.cmu.edu/~./enron/enron_mail_20150507.tar.gz && \
tar xvzf enron_mail_20150507.tar.gz && \
rm -rf enron_mail_20150507.tar.gz && \
python count_mails1.py
