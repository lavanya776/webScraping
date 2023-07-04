import os
import pandas as pd
import requests
from bs4 import BeautifulSoup
from nltk.tokenize import word_tokenize
from nltk.corpus import stopwords
import re
import nltk
import glob

nltk.download('stopwords')
nltk.download('punkt')

df = pd.read_excel('C:/Users/luffy/Downloads/sales data/input.xlsx')
folder_path = 'C:/Users/luffy/Downloads/sales data/StopWords'

stopwords = set(stopwords.words('english'))

files = glob.glob(os.path.join(folder_path, '*.txt'))
for file_path in files:
    with open(file_path, 'r') as file:
        stopwords_list = file.read().splitlines()
    stopwords.update(stopwords_list)


def clean_text(text):
    if text:
        a = BeautifulSoup(text, 'html.parser')
        b = a.get_text(separator=' ')

        clean = b.lower()
        clean = re.sub('[^A-Za-z]', ' ', clean)
        token = word_tokenize(clean)
        token = [word for word in token if word not in stopwords]

        cleanText = ' '.join(token)

        return cleanText
    else:
        return "null"

for index, row in df.iterrows():
    id = row['URL_ID']
    url = row['URL']

    response = requests.get(url)
    page_content = response.text

    a = BeautifulSoup(page_content, 'html.parser')
    article_title = a.find('title').text.strip()
    article_text = a.find('article')

    if article_text:
        article_text1=article_text.text.strip()
    else:
        article_text1=""

    if article_text1:
        with open(f'{id}.txt', 'w',encoding='utf-8') as file:
            file.write(article_text1)

    text1 = clean_text(article_text1)

    positive_score = text1.count('good')
    negative_score = text1.count('bad')
    polarity_score = (positive_score - negative_score) / ((positive_score + negative_score) + 0.000001)
    subjectivity_score = (positive_score + negative_score) / (len(text1.split()) + 0.000001)

    sentences = text1.split('. ')
    average_sentence_length = len(text1.split()) / len(sentences)


    def pronoun(word):
        vowels = 'aeiouAEIOU'
        count = 0
        prev_char = None
        for char in word:
            if char in vowels and (prev_char is None or prev_char not in vowels):
                count += 1
            prev_char = char
        return count

    word_count = 0
    for word in text1.split():
        if pronoun(word) > 2:
            word_count += 1

    percentage_words = word_count / len(text1.split())

    fog_index = 0.4 * (average_sentence_length + percentage_words)

    average= len(text1.split()) / len(sentences)

    pronouns = re.findall(r'\b(I|we|my|ours|us)\b', text1, flags=re.IGNORECASE)
    pronoun_count = len(pronouns)

    total = sum(len(word) for word in text1.split())
    average_word = total / len(text1.split())

    #................//////.......
    print(f'URL ID: {id}')
    print(f'Article Title: {article_title}')
    print(f'Positive Score: {positive_score}')
    print(f'Negative Score: {negative_score}')
    print(f'Polarity Score: {polarity_score}')
    print(f'Subjectivity Score: {subjectivity_score}')
    print(f'Count: {average_sentence_length}')
    print(f'Percentage: {percentage_words}')
    print(f'Count: {fog_index}')
    print(f'Percentage: {average}')
    print(f'Personal Pronoun: {pronoun_count}')
    print(f'Average word length: {average_word}')

    print('-------------------------------------')

    # ........................////////........
    df.loc[index, 'Positive Score'] = positive_score
    df.loc[index, 'Negative Score'] = negative_score
    df.loc[index, 'Polarity Score'] = polarity_score
    df.loc[index, 'Subjectivity Score'] = subjectivity_score
    df.loc[index, 'Count Score'] = average_sentence_length
    df.loc[index, 'Percentage Score'] = percentage_words
    df.loc[index, 'Fog Score'] = fog_index
    df.loc[index, 'Average Score'] = average
    df.loc[index, 'Personal Pronoun Score'] = pronoun_count
    df.loc[index, 'Average word Score'] = average_word

df.to_excel('C:/Users/luffy/Downloads/sales data/output.xlsx', index=False)
