INSERT INTO logs (user_id, action, module, details, ip_address, created_at) VALUES
(1, 'LOGIN', 'auth', '{"status": "success", "method": "password"}', '192.168.1.1', NOW()),
(1, 'CREATE', 'job', '{"job_id": 24, "title": "数据分析师"}', '192.168.1.1', NOW()),
(1, 'UPDATE', 'job', '{"job_id": 24, "field": "salary_range", "old": "15k-25k", "new": "20k-35k"}', '192.168.1.1', NOW()),
(1, 'DELETE', 'job', '{"job_id": 20, "title": "iOS开发工程师"}', '192.168.1.1', NOW()),
(2, 'LOGIN', 'auth', '{"status": "failed", "reason": "wrong password"}', '192.168.1.2', NOW());