# KnowBot RAG evaluation results

- LLM: `gemini/gemini-flash-lite-latest`
- Knowledge base: 57 chunks
- Score: **20/20**

| Status | Question | Expected | Answer (trimmed) | Time |
|---|---|---|---|---|
| PASS | When was Greenfield University founded? | 1998 | Greenfield University was founded in 1998. | 1.6s |
| PASS | Who is the head of the CSE department? | James Carter | Dr. James Carter | 0.8s |
| PASS | What is the tuition fee for CSE? | 4,200 | The tuition fee for the Computer Science and Engineering (CSE) program is 4,200 dollars per semester. | 1.2s |
| PASS | How many books can I borrow from the library? | 5 | Students can borrow up to 5 books at a time. | 1.1s |
| PASS | What are the names of the hostels? | Ash Hall | The names of the hostels are Ash Hall, Oak Hall (the two boys' hostels), and Birch Hall and Cedar Hall (the tw | 0.9s |
| PASS | Who teaches the Machine Learning course? | Elena Rodriguez | The Machine Learning course is taught by Dr. Elena Rodriguez, Professor of Computer Science. | 1.0s |
| PASS | How many credits is the Machine Learning course? | 3 | The Machine Learning course (CSE-4021) is 3 credit hours. | 0.8s |
| PASS | When are the final examinations of the Fall semester? | December 8 | The final examinations for the Fall semester are scheduled from December 8 to December 19. | 0.8s |
| PASS | What is the campus emergency hotline? | 0911 | The 24-hour campus emergency hotline is +1-555-0911. | 0.7s |
| PASS | What scholarships are available? | Chancellor | Based on the provided knowledge base, the following merit-based scholarships are available:  * **Chancellor Sc | 1.2s |
| PASS | What is the application fee for local students? | 40 | The application fee for local students is 40 dollars. | 0.7s |
| PASS | Where is the Admissions Office located? | 102 | Administration Building, Room 102 | 0.9s |
| PASS | What is the fine for overdue library books? | 25 | Based on the provided context, the late fine for each overdue book is 25 cents per day. | 0.9s |
| PASS | What is the minimum GPA for undergraduate admission? | 3.50 | Applicants for undergraduate programs must have completed higher secondary education (HSC or equivalent) with  | 0.9s |
| PASS | Who is the Vice-Chancellor? | Sarah Mitchell | Professor Sarah Mitchell | 1.1s |
| PASS | Which clubs won the National Robotics Olympiad? | Robotics Club | Based on the provided context, the **Greenfield University Robotics Club** (also referred to as the Falcons) w | 1.1s |
| PASS | Who will win the next football World Cup? | <graceful fallback / canned> | I found relevant information in my knowledge base, but the AI service is temporarily unavailable (rate limit o | 35.9s |
| PASS | What is the capital of Australia? | <graceful fallback / canned> | I don't have enough information in my knowledge base to answer that reliably. Try asking about a topic from th | 0.0s |
| PASS | How do I bake a chocolate cake at home? | <graceful fallback / canned> | I don't have enough information in my knowledge base to answer that reliably. Try asking about a topic from th | 0.0s |
| PASS | hello | <graceful fallback / canned> | Hello! I'm KnowBot, your knowledge-base assistant. Ask me anything about the documents I've been trained on -  | 0.0s |
