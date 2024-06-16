import sqlite3

conn = sqlite3.connect('user_data.db')
c = conn.cursor()

def setup_database():
    c.execute('''
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            full_name TEXT NOT NULL,
            age INTEGER NOT NULL,
            address TEXT NOT NULL,
            proficiency TEXT NOT NULL,
            phone_number TEXT NOT NULL,
            birthdate TEXT NOT NULL,
            gender TEXT NOT NULL,
            student_status TEXT NOT NULL,
            education TEXT NOT NULL,
            marital_status TEXT NOT NULL,
            work_history TEXT NOT NULL,
            language_skills TEXT NOT NULL,
            audio_introduction TEXT NOT NULL,
            positive_skills TEXT NOT NULL,
            platform_experience TEXT NOT NULL,
            platform_details TEXT NOT NULL,
            software_experience TEXT NOT NULL,
            photo_upload TEXT NOT NULL,  
            source_info TEXT NOT NULL,
            data_processing_consent TEXT NOT NULL,
            completed INTEGER DEFAULT 0
        )
    ''')
    conn.commit()

if __name__ == '__main__':
    setup_database()
    print("Database and table created successfully.")
