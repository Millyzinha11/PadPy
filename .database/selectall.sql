SELECT id, name, link, short, views,
	DATE_FORMAT(date, '%d/%m/%Y %H:%i') AS datebr,
    DATE_FORMAT(expire, '%d/%m/%Y %H:%i') AS expirebr
FROM redir
WHERE status = 'on'
ORDER BY name, short, date DESC, expire DESC;