Instructions on running the code:
	- Ensure that mysql is running locally on port 3306
	- Create `test` user as outlined under `query/test_user_creation.sql`
	- Create a new database `enron`
	- sh run.sh

Assumptions:
	- Emails with different MailIds are assumed to be unique
	- Mail chains are identified by similarity in Subject and doesn't account for changes in Subject when a user responds
	  to the same email thread
