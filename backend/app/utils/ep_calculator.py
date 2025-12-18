# Created: Dec 15, 20:00
# Ver 1.1
# Scripts related to score calculating and ep metrics
# Modified: Dec 16, 20:15, Added EP calculation function

from backend.app.database import scores_collection, difficulties_collection

def calculate_potential(score: int, difficulty: float) -> float:
    ratio = score / 1000000
    potential = difficulty * ratio
    # Rongze Fan: Bouns EP award
    if score > 970000:
        potential *= 1.05
    return round(potential, 3)

# Rongze Fan: Average EP of a player
def calculate_user_ep(uid: str) -> float:
    user_scores = list(scores_collection.find({"uid": uid}))
    if not user_scores:
        return 0.0

    best_by_bid = {}
    for s in user_scores:
        bid = s["bid"]
        if bid not in best_by_bid or s["score"] > best_by_bid[bid]["score"]:
            best_by_bid[bid] = s

    potentials = []
    for s in best_by_bid.values():
        diff = difficulties_collection.find_one({"bid": s["bid"]})
        if diff:
            pot = calculate_potential(s["score"], diff["level"])
            potentials.append(pot)

    potentials.sort(reverse=True)
    best50 = potentials[:50]
    ep = sum(best50) / 50
    return round(ep, 3)

def get_rank_from_accuracy(accuracy: float) -> str:
    if accuracy >= 100:
        return "SS"
    elif accuracy >= 95:
        return "S"
    elif accuracy >= 93:
        return "A"
    elif accuracy >= 87:
        return "B"
    elif accuracy >= 83:
        return "C"
    else:
        return "D"