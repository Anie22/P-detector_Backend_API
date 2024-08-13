import nltk
from nltk.tokenize import word_tokenize
from nltk.corpus import stopwords
from collections import Counter
import math

# nltk.download('punkt')
# nltk.download('stopwords')
# nltk.download('punkt_tab')

def cosine_similarity(vec1, vec2):
    intersection = set(vec1.keys()) & set(vec2.keys())
    numerator = sum([vec1[x] * vec2[x] for x in intersection])

    sum1 = sum([vec1[x] ** 2 for x in vec1.keys()])
    sum2 = sum([vec2[x] ** 2 for x in vec2.keys()])
    denominator = math.sqrt(sum1) * math.sqrt(sum2)

    if not denominator:
        return 0.0
    else:
        return float(numerator) / denominator

def text_to_vector(text):
    words = word_tokenize(text)
    return Counter(words)

def check_plagiarism(file1_path, file2_path):
    try:
        with open(file1_path, 'r', encoding='utf-8', errors='ignore') as file1, \
             open(file2_path, 'r', encoding='utf-8', errors='ignore') as file2:
            file1_data = file1.read().lower()
            file2_data = file2.read().lower()

            stop_words = set(stopwords.words('english'))
            words1 = [word for word in word_tokenize(file1_data) if word.isalnum() and word not in stop_words]
            words2 = [word for word in word_tokenize(file2_data) if word.isalnum() and word not in stop_words]

            vector1 = text_to_vector(" ".join(words1))
            vector2 = text_to_vector(" ".join(words2))

            similarity = cosine_similarity(vector1, vector2)
            return similarity * 100
    except Exception as e:
        raise Exception(f"An error occurred while processing files: {e}")