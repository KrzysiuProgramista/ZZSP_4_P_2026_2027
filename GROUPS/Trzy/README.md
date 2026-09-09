# Trzy

Reference directories:
- PISERA_MATEUSZ
- SOBALA_JAKUB
- WASIK_PIOTR
- PICZKOWSKI_OSKAR

# StudySync: Student Study Group & Resource Finder

Problem to Solve Students frequently struggle to find reliable peers for collaborative learning, organize study sessions, and share class-specific resources, which can lead to academic isolation and reduced engagement.

# Stakeholders

Students: Primary users looking for study partners and educational resources.
Teachers/Club Advisors: Supervisors who can moderate content and recommend the platform.
System Administrator: The developer managing database health and user permissions.
# Services & Implementation

User Management: Python backend using Flask or FastAPI to handle secure registration, login, and profile creation.
Matching Algorithm: A custom Python script that analyzes student schedules, subjects, and skill levels to recommend optimal study groups.
Resource Library: File-handling services enabling users to upload, tag, search, and download study notes or practice quizzes.
Coordination Board: A bulletin feature allowing users to post meeting times, virtual links, or library room locations.
# Data Used

User Profile Data: Names, email addresses, grade levels, enrolled courses, and weekly availability time blocks.
Resource Data: Metadata (titles, subject tags, upload dates) and file binaries or paths for PDFs and text documents.
Interaction Data: Group membership lists and posted announcements stored in a relational database (SQLite or PostgreSQL).


