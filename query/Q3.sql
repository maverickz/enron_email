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