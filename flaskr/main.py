import pandas as pd
import random
from . import poem_generator as pg
from . import object_detection as od

def parse_poem_csv():
    df = pd.read_csv("flaskr/PoetryFoundationData.csv")
    indexes = []
    for i in range(10):
        rand_idx = random.randint(0, 13855)
        if rand_idx not in indexes:
            indexes.append(rand_idx)
    for idx in indexes:
        title = df['Title'][idx]
        title = title.strip()
        if '/' in title:
            continue
        filename = "-".join(title.split())
        file_path = f'flaskr/inspiring_poems/{filename}.txt'
        new_file = open(file_path, 'w')
        poem = df['Poem'][idx]
        new_file.write(poem)
        new_file.close()

def main():
    num_sentences = 5

    themes = od.detect_objects_in_images()
    if themes == None:
        return ("temp", "*NO IMAGES*")

    generator = pg.PoemGenerator()

    # read inspiring poem files
    generator.read_poem_files_to_strings()

    # parse inspiring poems
    generator.parse_inspiring_poems()

    # parse themes
    generator.parse_themes(themes)

    # generate poem
    poem = generator.generate_poem(num_sentences, themes)

    themed_poem = generator.improve_poem_themes(poem)

    avg_pol, avg_sub = generator.evaluate_sentiment(themed_poem)

    goal_pol = (avg_pol + 0.01) * 1.05
    goal_sub = (avg_sub + 0.01) * 1.05

    updated_poem = generator.improve_poem_sentiment\
                            (themed_poem, goal_pol, goal_sub)

    final_poem = generator.reformat_poem(updated_poem)
    final_text = final_poem.text
    final_name = final_poem.name
    return (final_name, final_text)