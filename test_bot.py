from app import get_answer

tests = [
    "hello",
    "fees kitni hai",
    "how to apply for scholarship",
    "library kab khulti hai",
    "exam kab hai",
    "placement cell kya hai",
    "make a 7-day exam study plan",
    "explain inheritance in java",
    "placement interview questions",
    "what is quantum physics",
]

for t in tests:
    answer, tag, score = get_answer(t)
    print(f"Q: {t}\n   Topic: {tag} | Score: {score}\n   A: {answer[:70]}...\n")
