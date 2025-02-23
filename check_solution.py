from itertools import combinations

def load_data(file_path):
    with open(file_path, 'r') as f:
        lines = f.read().strip().split('\n')

    n = int(lines[0])
    photos = []
    for i, line in enumerate(lines[1:]):
        parts = line.split()
        orientation = parts[0]
        tags = set(parts[2:])
        photos.append((i, orientation, tags))

    return photos

def calculate_interest(tags1, tags2):
    common = len(tags1 & tags2)
    only_in_1 = len(tags1 - tags2)
    only_in_2 = len(tags2 - tags1)
    return min(common, only_in_1, only_in_2)

def check_solution(photos, solution_path):
    # Load the solution
    with open(solution_path, 'r') as f:
        lines = f.read().strip().split('\n')

    num_slides = int(lines[0])
    slides = []
    for line in lines[1:]:
        parts = line.split()
        if len(parts) == 1:
            slides.append((int(parts[0]),))
        else:
            slides.append((int(parts[0]), int(parts[1])))

    # Check si chaque photo est utilisée qu'une seule fois
    used_photos = set()
    for slide in slides:
        for photo in slide:
            if photo in used_photos:
                return False, "Some photos are used more than once."
            used_photos.add(photo)

    if len(used_photos) != len(photos):
        return False, "Not all photos are used."

    # Check si la transition est optimale
    total_interest = 0
    for (slide1, slide2) in zip(slides, slides[1:]):
        tags1 = set()
        tags2 = set()
        for photo_id in slide1:
            tags1.update(photos[photo_id][2])
        for photo_id in slide2:
            tags2.update(photos[photo_id][2])
        total_interest += calculate_interest(tags1, tags2)

    return True, f"Solution is valid with total interest: {total_interest}"

# Charger data et check solution
dataset_path = "data/c_example.txt"
solution_path = "slideshow.sol"
photos = load_data(dataset_path)
is_valid, message = check_solution(photos, solution_path)

print(message)
