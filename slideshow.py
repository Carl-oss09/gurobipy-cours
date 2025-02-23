from gurobipy import Model, GRB
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

def build_model(photos):
    model = Model("PhotoSlideshow")

    # Separate photos by orientation
    horizontal_photos = [p for p in photos if p[1] == 'H']
    vertical_photos = [p for p in photos if p[1] == 'V']

    # Combine vertical photos into potential slides
    vertical_pairs = list(combinations(vertical_photos, 2))

    # Create slides (horizontal + vertical pairs)
    slides = [(p[0], p[2]) for p in horizontal_photos] + [
        ((p1[0], p2[0]), p1[2] | p2[2]) for p1, p2 in vertical_pairs
    ]

    # Transition scores
    transitions = {}
    for (i, slide1), (j, slide2) in combinations(enumerate(slides), 2):
        tags1 = slide1[1]
        tags2 = slide2[1]
        transitions[(i, j)] = calculate_interest(tags1, tags2)

    # Variables
    x = model.addVars(transitions.keys(), vtype=GRB.BINARY, name="x")

    # Objective
    model.setObjective(
        sum(x[i, j] * score for (i, j), score in transitions.items()), GRB.MAXIMIZE
    )

    # Constraints
    used_photos = {p[0] for p in photos}
    for p in used_photos:
        model.addConstr(
            sum(
                x[i, j] for (i, j) in transitions
                if (isinstance(slides[i][0], int) and p == slides[i][0]) or
                   (isinstance(slides[i][0], tuple) and p in slides[i][0]) or
                   (isinstance(slides[j][0], int) and p == slides[j][0]) or
                   (isinstance(slides[j][0], tuple) and p in slides[j][0])
            ) <= 1,
            name=f"Photo_{p}_used_once"
        )

    return model, slides

def save_solution(model, slides, output_path):
    model.optimize()

    if model.Status == GRB.OPTIMAL:
        with open(output_path, 'w') as f:
            solution_slides = []
            for v in model.getVars():
                if v.X > 0.5:  # Selected transition
                    i, j = map(int, v.VarName.split('[')[1][:-1].split(','))
                    solution_slides.append(i)

            f.write(f"{len(solution_slides)}\n")
            for slide in solution_slides:
                if isinstance(slides[slide][0], int):
                    f.write(f"{slides[slide][0]}\n")
                else:
                    f.write(f"{slides[slide][0][0]} {slides[slide][0][1]}\n")

if __name__ == "__main__":
    dataset_path = "data/c_example.txt" 
    photos = load_data(dataset_path)
    model, slides = build_model(photos)
    save_solution(model, slides, "slideshow.sol")
