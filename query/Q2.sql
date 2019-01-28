SELECT receiver, COUNT(r.MessageId) AS emails_received 
FROM recipient r, email e 
WHERE e.MessageId = r.MessageId 
GROUP BY receiver 
ORDER BY emails_received desc;