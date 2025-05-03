import mysql.connector
from datetime import datetime

# Connect to the MySQL database
def connect():
    return mysql.connector.connect(
        host="localhost",
        user="root",
        password="Vineet2003@",  # Update if needed
        database="agentic_aii"
    )

# Log a user request
def log_user_request(
    user_input,
    parsed_intent,
    entities,
    action_type,
    confirmation_status,
    execution_status,
    response
):
    conn = connect()
    cursor = conn.cursor()
    
    query = """
        INSERT INTO user_requests (
            timestamp,
            user_input,
            parsed_intent,
            entities,
            action_type,
            confirmation_status,
            execution_status,
            response
        ) VALUES (NOW(), %s, %s, %s, %s, %s, %s, %s)
    """
    
    values = (
        user_input,
        parsed_intent,
        entities,
        action_type,
        confirmation_status,
        execution_status,
        response
    )
    
    cursor.execute(query, values)
    conn.commit()
    cursor.close()
    conn.close()
    print(f"[LOGGED] {parsed_intent} → {user_input}")

# Delete a log entry based on exact user input
def delete_log_by_user_input(user_input):
    conn = connect()
    cursor = conn.cursor()

    query = "DELETE FROM user_requests WHERE user_input = %s"
    
    cursor.execute(query, (user_input,))
    conn.commit()
    cursor.close()
    conn.close()
    print(f"[DELETED] Log for user_input: '{user_input}'")

# Example test call for logging a request
if __name__ == "__main__":
    log_user_request(
        user_input="Delete volume data-disk",
        parsed_intent="delete_volume",
        entities='{"name": "data-disk"}',
        action_type="delete",
        confirmation_status="confirmed",
        execution_status="success",
        response="Volume data-disk deleted successfully"
    )

    # Optional: Delete the log (Uncomment to use)
    # delete_log_by_user_input("Delete volume data-disk")
