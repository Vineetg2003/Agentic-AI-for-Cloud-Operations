-- 1. Select your database
USE agentic_aii;
-- 2. Show all tables (to make sure user_requests exists)
SHOW TABLES;
-- 3. Optional: Show table structure
DESCRIBE user_requests;
-- 4. Insert test data manually
INSERT INTO user_requests (
        timestamp,
        user_input,
        parsed_intent,
        entities,
        action_type,
        confirmation_status,
        execution_status,
        response
    )
VALUES (
        NOW(),
        'Create a VM called test-server',
        'create_vm',
        '{"name": "test-server", "flavor": "S.2"}',
        'create',
        'confirmed',
        'success',
        'VM test-server created with ID vm12345'
    );
-- 5. Query the data to confirm it was inserted
SELECT *
FROM user_requests;