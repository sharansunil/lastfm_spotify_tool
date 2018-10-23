import nltk.classify.util 
from nltk.corpus import movie_reviews
from nltk.corpus import stopwords
from nltk.tokenize import word_tokenize
from nltk.corpus import wordnet
from nltk.classify import NaiveBayesClassifier



def create_word_features(words):
	useful_words = [word for word in words if word not in stopwords.words('english')]
	my_dict=dict([word,True] for word in useful_words)
	return my_dict

pos_reviews=[]
neg_reviews=[]

for fileid in movie_reviews.fileids('neg'):
	words=movie_reviews.words(fileid)
	neg_reviews.append((create_word_features(words),"negative"))
for fileid in movie_reviews.fileids('pos'):
	words=movie_reviews.words(fileid)
	pos_reviews.append((create_word_features(words),"positive"))

train_set = neg_reviews[:750] + pos_reviews[:750]
test_set = neg_reviews[750:] + pos_reviews[750:]

classifier = NaiveBayesClassifier.train(train_set)
accuracy = nltk.classify.util.accuracy(classifier,test_set)
accuracy 



