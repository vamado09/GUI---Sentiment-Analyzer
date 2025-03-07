#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Tue Dec  6 15:35:28 2022

@author: deleonv
"""

import streamlit as st

import pandas as pd
import numpy as np
import seaborn as sns
import sys
import matplotlib.pyplot as plt
import re
import nltk
nltk.download('stopwords')
nltk.download('punkt')
nltk.download('vader_lexicon')
from nltk.sentiment.vader import SentimentIntensityAnalyzer
np.set_printoptions(precision=2, linewidth=80)

from sklearn import metrics
from sklearn.feature_extraction.text import CountVectorizer
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.linear_model import LogisticRegression
from sklearn.linear_model import SGDClassifier
from sklearn.ensemble import GradientBoostingClassifier
from sklearn.ensemble import RandomForestClassifier


import warnings 
warnings.filterwarnings('ignore')

######################### functions clean text

stop_words = nltk.corpus.stopwords.words('english')

def normalize_document(doc):
    doc = re.sub(r'[^a-zA-Z0-9\s]', '', doc, re.I|re.A)
    doc = doc.lower()
    doc = doc.strip()
    tokens = nltk.word_tokenize(doc)
    filtered_tokens = [token for token in tokens if token not in stop_words] 
    doc = ' '.join(filtered_tokens)
    return doc
  
normalize_corpus = np.vectorize(normalize_document)


########################## df to csv and download generator custome functions:

def convert_df(df):
             return df.to_csv().encode('utf-8')


def generate_download_button(csv_data, filename, file_label):
    st.download_button(label=f"Download {file_label} as CSV",
                           data=csv_data,
                           file_name=f"{filename}.csv")


######################### custome functions TextBlob

from textblob import TextBlob

def polarity(txt):
    try:
        return TextBlob(txt).sentiment.polarity
    except:
        return None

def subjectivity(txt):
  try:
      return TextBlob(txt).sentiment.subjectivity
  except:
        return None

def analyze(x):
        if x < 0:
            return 'negative'
        elif x == 0:
            return 'neutral'
        else:
            return 'positive'


###################################################################### Functions for sentiment VADER analysis:

analyzer = SentimentIntensityAnalyzer()

def vader_sentiment(txt):
  try:
      return analyzer.polarity_scores(txt)['compound']
  except:
      return None


def vader_analysis(sentiment, neg_threshold=-0.05, pos_threshold=0.05):
    if sentiment < neg_threshold:
        label = 'negative'
    elif sentiment > pos_threshold:
        label = 'positive'
    else:
        label = 'neutral'
    return label


#################################################### functions Supervised Learning

def get_metrics(true_labels, predicted_labels):
  st.write('Accuracy:', np.round(metrics.accuracy_score(true_labels, predicted_labels), 4))
  st.write('Precision:',np.round(metrics.precision_score(true_labels, predicted_labels, average = 'weighted'), 4))
  st.write('Recall:',np.round(metrics.recall_score(true_labels, predicted_labels, average = 'weighted'), 4))
  st.write('F1 Score:',np.round(metrics.f1_score(true_labels, predicted_labels, average = 'weighted'), 4))

def train_predict_model(classifier, 
                        train_features, train_labels, 
                        test_features, test_labels):   
    classifier.fit(train_features, train_labels)
    predictions = classifier.predict(test_features) 
    return predictions   


# custom function

def classification_report(true_labels, predicted_labels, classes=[1,0], output_dict=True):
  report = metrics.classification_report(y_true=true_labels, y_pred = predicted_labels, labels = classes, output_dict=True)
  return(report)

def display_confusion_matrix(true_labels, predicted_labels, classes=[1,0]):
    
    total_classes = len(classes)
    level_labels = [total_classes*[0], list(range(total_classes))]

    cm = metrics.confusion_matrix(y_true=true_labels, y_pred=predicted_labels, 
                                  labels=classes)
    cm_frame = pd.DataFrame(data=cm, 
                            columns=pd.MultiIndex(levels=[['Predicted:'], classes], 
                                                  codes=level_labels), 
                            index=pd.MultiIndex(levels=[['Actual:'], classes], 
                                                codes=level_labels)) 
    st.write(cm_frame) 
    

def display_model_performance_metrics(true_labels, predicted_labels, classes=[1,0]):
    st.write('Model Performance metrics:')
    get_metrics(true_labels=true_labels, predicted_labels=predicted_labels)
    st.write('\n')
    st.write('Prediction Confusion Matrix:')
    display_confusion_matrix(true_labels=true_labels, predicted_labels=predicted_labels, 
                             classes=classes)




#################################################### main app.py

st.title('Welcome - Sentiment Analyzer')
st.subheader('Supervised and Unsupervised Learning')

menu = ['Home','About']
choice = st.sidebar.selectbox('Menu', menu)

if choice == 'Home':
  st.subheader('Welcome to the Sentiment Analyzer Streamlit Application')

  sentence = st.text_input('Try the TextBlob sentiment analyzer in a sentence.')
  analysis = TextBlob(sentence)
  analysis = analysis.sentiment
  sent_sentence = polarity(sentence)
  sent_sentence = analyze(sent_sentence)
  st.write('The polarity and subjectivity of your sentence is', {analysis})
  st.write('Here is the sentiment of your sentence:', {sent_sentence})
  st.write('\n')
  st.write('NOTE: If the polarity score is > 0 it means your sentence has a positive sentiment. If the polarity score is < 0 it means it has a negative sentiment (Try typing: I hate you). If the polarity score equals 0 its a neutral sentiment.')
  task = st.selectbox('Select analysis type', ['Inspect CSV','Clean Text' ,'TextBlob', 'VADER', 'Logistic Regression', 'Support Vector Machine', 'Gradient Boosting Classifier', 'Random Forest Classifier'])
  if task == 'Inspect CSV':
      st.header('Natural Language Processing')
      st.subheader('Inspecting your csv file with sentiment column')

      st.write(f'Please upload or drag and drop your csv file.')
      #with st.expander('Value Counts and Bar Graph'):
      csv_file = st.file_uploader('Upload File - Insepct')

      if csv_file:

        df = pd.read_csv(csv_file)
        x = df['sentiment'].value_counts()
        barplot = sns.barplot(x.index,x)
        st.write(x)
        fig = plt.figure(figsize = (14,5))
        sns.barplot(x.index,x)
        st.pyplot(fig)

  if task == 'Clean Text':
      st.header('Natural Language Processing: Text Cleaner')
      st.subheader('Preprocessing your Data')
      st.write('Please upload or drag and drop your csv file to initiate the preprocessing step.')
      st.write('\n')
      st.write('This Text-Cleaner is useful for the TextBlob and VADER Sentiment Analyzers.')
      csv_file = st.file_uploader('Upload File - Preprocessing')
      if csv_file:
        df = pd.read_csv(csv_file)
        df[df.Review.str.strip() == ''].shape[0]
        norm_corpus = normalize_corpus(df['Review'])
        df['Clean Review'] = norm_corpus
        df = df[['Review', 'Clean Review']]

        df.replace(r'^(\s?)+$', np.nan, regex=True)
        df.dropna().reset_index(drop=True)

        df['Clean Review'] = norm_corpus
        df = df[['Review', 'Clean Review']]
        st.write(df.head())

        csv = convert_df(df)
        generate_download_button(csv_data=csv, filename='clean', file_label='clean')

      
      st.write('This Text-Cleaner is useful for the Logistic Regression and Support Vector Machine Analyzers.')
      st.write('Why? Unlike the Unsupervised Models we have (TextBlob and VADER), which calculate 3 sentiments, our Unsupervised Models only calculate 2 sentiments -> positive and negative.')
      csv_file = st.file_uploader('Upload File - Preprocessing(sentiment column)')
      if csv_file:
        df = pd.read_csv(csv_file)
        df[df.Review.str.strip() == ''].shape[0]
        norm_corpus = normalize_corpus(df['Review'])
        df['Clean Review'] = norm_corpus
        df = df[['Review', 'Clean Review', 'sentiment']]

        df.replace(r'^(\s?)+$', np.nan, regex=True)
        df.dropna().reset_index(drop=True)

        df['Clean Review'] = norm_corpus
        df = df[['Clean Review', 'sentiment']]
        st.write(df.head())

        csv = convert_df(df)
        generate_download_button(csv_data=csv, filename='clean_with_sentiment', file_label='clean_with_sentiment')

  if task == 'TextBlob':
      st.subheader('TextBlob Lexicon Model')
      st.write(f'Please upload or drag and drop your clean preprocess data.')
      csv_file = st.file_uploader("Upload File (TextBlob Sentiment)")

      if csv_file:
        df = pd.read_csv(csv_file)
        df['polarity'] = df['Clean Review'].apply(polarity)
        df['subjectivity'] = df['Clean Review'].apply(subjectivity)
        df['sentiment'] = df['polarity'].apply(analyze)
        df = df[['Clean Review', 'polarity', 'subjectivity', 'sentiment']]
        st.write(df.head())

        csv = convert_df(df)
        generate_download_button(csv_data=csv, filename='textblob_analysis', file_label='textblob_analysis')

        x = df['sentiment'].value_counts()
        barplot = sns.barplot(x.index,x)
        st.write(x)
        fig = plt.figure(figsize = (14,5))
        sns.barplot(x.index,x)
        st.pyplot(fig)



  if task == 'VADER':
      st.subheader('VADER Lexicon Model')
      st.write('Please upload or drag and drop your data.')
      st.write('VADER does not require preprocess data. It even takes on emojies!')
      csv_file = st.file_uploader("Upload File")

      if csv_file:
        df = pd.read_csv(csv_file)
        df['compound'] = df['Review'].apply(vader_sentiment)
        df['sentiment'] = df['compound'].apply(vader_analysis)
        df = df[['Review', 'compound', 'sentiment']]
        st.write(df.head())

        csv = convert_df(df)
        generate_download_button(csv_data=csv, filename='vader_analysis', file_label='vader_analysis')

        x = df['sentiment'].value_counts()
        barplot = sns.barplot(x.index,x)
        st.write(x)
        fig = plt.figure(figsize = (14,5))
        sns.barplot(x.index,x)
        st.pyplot(fig)



  if task == 'Support Vector Machine': 
      st.subheader('Supervised Learning: Support Vector Machine')
      st.write('Please upload or drag and drop your csv file.')
      csv_file = st.file_uploader('Upload File - SVM (TF-IDF Model)')
      if csv_file:
        df = pd.read_csv(csv_file)
        df = df[['Clean Review', 'sentiment']].fillna('')
        reviews = np.array(df['Clean Review'])
        sentiments = np.array(df['sentiment'])

        train_reviews = reviews[:35000]
        train_sentiments = sentiments[:35000]
        test_reviews = reviews[35000:]
        test_sentiments = sentiments[35000:]

        norm_train_reviews = normalize_corpus(train_reviews)
        norm_test_reviews = normalize_corpus(test_reviews)

        tv = TfidfVectorizer(use_idf=True, min_df=0.0, max_df=1.0, ngram_range=(1,2), sublinear_tf=True)
        tv_train_features = tv.fit_transform(norm_train_reviews)

        tv_test_features = tv.transform(norm_test_reviews)

        st.write('TFIDF model:> Train features shape:', tv_train_features.shape, ' Test features shape:', tv_test_features.shape)

        svm = SGDClassifier(loss='hinge', max_iter=100)

        svm_tfidf_predictions = train_predict_model(classifier=svm, train_features=tv_train_features, train_labels=train_sentiments, test_features=tv_test_features, test_labels=test_sentiments)

        display_model_performance_metrics(true_labels=test_sentiments, predicted_labels=svm_tfidf_predictions, classes=['positive', 'negative'])

        classification_rep_tfidf = classification_report(true_labels=test_sentiments, predicted_labels=svm_tfidf_predictions, classes=['positive', 'negative'], output_dict = True)

        df_tfidf = pd.DataFrame(classification_rep_tfidf).transpose()
        df_tfidf.at['accuracy', 'precision'] = 0.0
        df_tfidf.at['accuracy', 'recall'] = 0.0

        st.write(df_tfidf)
        csv = convert_df(df_tfidf)
        generate_download_button(csv_data=csv, filename='svm_tfidf', file_label='svm_tfidf')



      csv_file = st.file_uploader('Upload File - SVM (BOW Model)')
      if csv_file:
        df = pd.read_csv(csv_file)
        df = df[['Clean Review', 'sentiment']].fillna('')
        reviews = np.array(df['Clean Review'])
        sentiments = np.array(df['sentiment'])

        train_reviews = reviews[:35000]
        train_sentiments = sentiments[:35000]
        test_reviews = reviews[35000:]
        test_sentiments = sentiments[35000:]

        norm_train_reviews = normalize_corpus(train_reviews)
        norm_test_reviews = normalize_corpus(test_reviews)

        cv = CountVectorizer(binary=False, min_df=0.0, max_df=1.0, ngram_range=(1,2))

        cv_train_features = cv.fit_transform(norm_train_reviews)
        cv_test_features = cv.transform(norm_test_reviews)

        print('BOW model:> Train features shape:', cv_train_features.shape, ' Test features shape:', cv_test_features.shape)

        svm = SGDClassifier(loss='hinge', max_iter=100)

        svm_bow_predictions = train_predict_model(classifier=svm, train_features=cv_train_features, train_labels=train_sentiments, test_features=cv_test_features, test_labels=test_sentiments)

        display_model_performance_metrics(true_labels=test_sentiments, predicted_labels=svm_bow_predictions, classes=['positive', 'negative'])

        classification_rep_bow = classification_report(true_labels=test_sentiments, predicted_labels=svm_bow_predictions, classes=['positive', 'negative'], output_dict = True)

        df_bow = pd.DataFrame(classification_rep_bow).transpose()
        df_bow.at['accuracy', 'precision'] = 0.0
        df_bow.at['accuracy', 'recall'] = 0.0

        st.write(df_bow)
        csv = convert_df(df_bow)
        generate_download_button(csv_data=csv, filename='svm_bow', file_label='svm_bow')


  if task == 'Logistic Regression':
      st.subheader('Supervised Learning: Logistic Regression')
      st.write('Please upload or drag and drop your csv file.')
      csv_file = st.file_uploader('Upload File  - Logistic Regression (TF-IDF Model)')
      if csv_file:
        df = pd.read_csv(csv_file)
        df = df[['Clean Review', 'sentiment']].fillna('')
        reviews = np.array(df['Clean Review'])
        sentiments = np.array(df['sentiment'])

        train_reviews = reviews[:35000]
        train_sentiments = sentiments[:35000]
        test_reviews = reviews[35000:]
        test_sentiments = sentiments[35000:]

        norm_train_reviews = normalize_corpus(train_reviews)
        norm_test_reviews = normalize_corpus(test_reviews)

        tv = TfidfVectorizer(use_idf=True, min_df=0.0, max_df=1.0, ngram_range=(1,2), sublinear_tf=True)
        tv_train_features = tv.fit_transform(norm_train_reviews)

        tv_test_features = tv.transform(norm_test_reviews)

        st.write('TFIDF model:> Train features shape:', tv_train_features.shape, ' Test features shape:', tv_test_features.shape)

        lr = LogisticRegression(penalty='l2', max_iter=500, C=1)

        lr_tfidf_predictions = train_predict_model(classifier=lr, train_features=tv_train_features, train_labels=train_sentiments,test_features=tv_test_features, test_labels=test_sentiments)

        display_model_performance_metrics(true_labels=test_sentiments, predicted_labels=lr_tfidf_predictions, classes=['positive', 'negative'])

        classification_rep_tfidf = classification_report(true_labels=test_sentiments, predicted_labels=lr_tfidf_predictions, classes=['positive', 'negative'], output_dict = True)

        df_tfidf = pd.DataFrame(classification_rep_tfidf).transpose()
        df_tfidf.at['accuracy', 'precision'] = 0.0
        df_tfidf.at['accuracy', 'recall'] = 0.0

        st.write(df_tfidf)
        csv = convert_df(df_tfidf)
        generate_download_button(csv_data=csv, filename='lr_tfidf', file_label='lr_tfidf')




      csv_file = st.file_uploader('Upload File - Logistic Regression (BOW Model)')
      if csv_file:
        df = pd.read_csv(csv_file)
        df = df[['Clean Review', 'sentiment']].fillna('')
        reviews = np.array(df['Clean Review'])
        sentiments = np.array(df['sentiment'])

        train_reviews = reviews[:35000]
        train_sentiments = sentiments[:35000]
        test_reviews = reviews[35000:]
        test_sentiments = sentiments[35000:]

        norm_train_reviews = normalize_corpus(train_reviews)
        norm_test_reviews = normalize_corpus(test_reviews)

        cv = CountVectorizer(binary=False, min_df=0.0, max_df=1.0, ngram_range=(1,2))
        cv_train_features = cv.fit_transform(norm_train_reviews)

        cv_test_features = cv.transform(norm_test_reviews)

        st.write('BOW model:> Train features shape:', cv_train_features.shape, ' Test features shape:', cv_test_features.shape)

        lr = LogisticRegression(penalty='l2', max_iter=500, C=1)

        lr_bow_predictions = train_predict_model(classifier=lr, train_features=cv_train_features, train_labels=train_sentiments,test_features=cv_test_features, test_labels=test_sentiments)

        display_model_performance_metrics(true_labels=test_sentiments, predicted_labels=lr_bow_predictions, classes=['positive', 'negative'])

        classification_rep_bow = classification_report(true_labels=test_sentiments, predicted_labels=lr_bow_predictions, classes=['positive', 'negative'])

        df_bow = pd.DataFrame(classification_rep_bow).transpose()
        df_bow.at['accuracy', 'precision'] = 0.0
        df_bow.at['accuracy', 'recall'] = 0.0

        st.write(df_bow)
        csv = convert_df(df_bow)
        generate_download_button(csv_data=csv, filename='lr_bow', file_label='lr_bow')

  if task == 'Gradient Boosting Classifier':
        st.subheader('Supervised Learning: GradientBoost Classifier')
        st.write('Please upload or drag and drop your csv file.')
        csv_file = st.file_uploader('Upload File  - GradientBoost Classifier (TF-IDF Model)')
        if csv_file:
          df = pd.read_csv(csv_file)
          df = df[['Clean Review', 'sentiment']].fillna('')
          reviews = np.array(df['Clean Review'])
          sentiments = np.array(df['sentiment'])

          train_reviews = reviews[:35000]
          train_sentiments = sentiments[:35000]
          test_reviews = reviews[35000:]
          test_sentiments = sentiments[35000:]

          norm_train_reviews = normalize_corpus(train_reviews)
          norm_test_reviews = normalize_corpus(test_reviews)

          tv = TfidfVectorizer(use_idf=True, min_df=0.0, max_df=1.0, ngram_range=(1,2), sublinear_tf=True)
          tv_train_features = tv.fit_transform(norm_train_reviews)

          tv_test_features = tv.transform(norm_test_reviews)

          st.write('TFIDF model:> Train features shape:', tv_train_features.shape, ' Test features shape:', tv_test_features.shape)

          gbc = GradientBoostingClassifier(n_estimators=10, random_state=42)

          gbc_tfidf_predictions = train_predict_model(classifier=gbc, train_features=tv_train_features, train_labels=train_sentiments, test_features=tv_test_features, test_labels=test_sentiments)

          display_model_performance_metrics(true_labels=test_sentiments, predicted_labels=gbc_tfidf_predictions, classes=['positive', 'negative'])

          classification_rep_tfidf = classification_report(true_labels=test_sentiments, predicted_labels=gbc_tfidf_predictions, classes=['positive', 'negative'], output_dict = True)
       
          df_tfidf = pd.DataFrame(classification_rep_tfidf).transpose()
          df_tfidf.at['accuracy', 'precision'] = 0.0
          df_tfidf.at['accuracy', 'recall'] = 0.0

          st.write(df_tfidf)
          csv = convert_df(df_tfidf)
          generate_download_button(csv_data=csv, filename='gbc_tfidf', file_label='gbc_tfidf')




        csv_file = st.file_uploader('Upload File - GradientBoost Classifier (BOW Model)')
        if csv_file:
          df = pd.read_csv(csv_file)
          df = df[['Clean Review', 'sentiment']].fillna('')
          reviews = np.array(df['Clean Review'])
          sentiments = np.array(df['sentiment'])

          train_reviews = reviews[:35000]
          train_sentiments = sentiments[:35000]
          test_reviews = reviews[35000:]
          test_sentiments = sentiments[35000:]

          norm_train_reviews = normalize_corpus(train_reviews)
          norm_test_reviews = normalize_corpus(test_reviews)

          cv = CountVectorizer(binary=False, min_df=0.0, max_df=1.0, ngram_range=(1,2))
          cv_train_features = cv.fit_transform(norm_train_reviews)

          cv_test_features = cv.transform(norm_test_reviews)

          st.write('BOW model:> Train features shape:', cv_train_features.shape, ' Test features shape:', cv_test_features.shape)

          gbc = GradientBoostingClassifier(n_estimators=10, random_state=42)

          gbc_bow_predictions = train_predict_model(classifier=gbc, train_features=cv_train_features, train_labels=train_sentiments,test_features=cv_test_features, test_labels=test_sentiments)

          display_model_performance_metrics(true_labels=test_sentiments, predicted_labels=gbc_bow_predictions, classes=['positive', 'negative'])

          classification_rep_bow = classification_report(true_labels=test_sentiments, predicted_labels=gbc_bow_predictions, classes=['positive', 'negative'])

          df_bow = pd.DataFrame(classification_rep_bow).transpose()
          df_bow.at['accuracy', 'precision'] = 0.0
          df_bow.at['accuracy', 'recall'] = 0.0

          st.write(df_bow)
          csv = convert_df(df_bow)
          generate_download_button(csv_data=csv, filename='gbc_bow', file_label='gbc_bow')


  if task == 'Random Forest Classifier':
        st.subheader('Supervised Learning: RandomForest Classifier')
        st.write('Please upload or drag and drop your csv file.')
        csv_file = st.file_uploader('Upload File  - RandomForest Classifier (TF-IDF Model)')
        if csv_file:
          df = pd.read_csv(csv_file)
          df = df[['Clean Review', 'sentiment']].fillna('')
          reviews = np.array(df['Clean Review'])
          sentiments = np.array(df['sentiment'])

          train_reviews = reviews[:35000]
          train_sentiments = sentiments[:35000]
          test_reviews = reviews[35000:]
          test_sentiments = sentiments[35000:]

          norm_train_reviews = normalize_corpus(train_reviews)
          norm_test_reviews = normalize_corpus(test_reviews)

          tv = TfidfVectorizer(use_idf=True, min_df=0.0, max_df=1.0, ngram_range=(1,2), sublinear_tf=True)
          tv_train_features = tv.fit_transform(norm_train_reviews)

          tv_test_features = tv.transform(norm_test_reviews)

          st.write('TFIDF model:> Train features shape:', tv_train_features.shape, ' Test features shape:', tv_test_features.shape)
          
          rfc = RandomForestClassifier(n_estimators=10, random_state=42)
          
          rfc_tfidf_predictions = train_predict_model(classifier=rfc, train_features=tv_train_features, train_labels=train_sentiments, test_features=tv_test_features, test_labels=test_sentiments)

          display_model_performance_metrics(true_labels=test_sentiments, predicted_labels=rfc_tfidf_predictions, classes=['positive', 'negative'])

          classification_rep_tfidf = classification_report(true_labels=test_sentiments, predicted_labels=rfc_tfidf_predictions, classes=['positive', 'negative'], output_dict = True)
       
          df_tfidf = pd.DataFrame(classification_rep_tfidf).transpose()
          df_tfidf.at['accuracy', 'precision'] = 0.0
          df_tfidf.at['accuracy', 'recall'] = 0.0

          st.write(df_tfidf)
          csv = convert_df(df_tfidf)
          generate_download_button(csv_data=csv, filename='rfc_tfidf', file_label='rfc_tfidf')




        csv_file = st.file_uploader('Upload File - RandomForest Classifier (BOW Model)')
        if csv_file:
          df = pd.read_csv(csv_file)
          df = df[['Clean Review', 'sentiment']].fillna('')
          reviews = np.array(df['Clean Review'])
          sentiments = np.array(df['sentiment'])

          train_reviews = reviews[:35000]
          train_sentiments = sentiments[:35000]
          test_reviews = reviews[35000:]
          test_sentiments = sentiments[35000:]

          norm_train_reviews = normalize_corpus(train_reviews)
          norm_test_reviews = normalize_corpus(test_reviews)

          cv = CountVectorizer(binary=False, min_df=0.0, max_df=1.0, ngram_range=(1,2))
          cv_train_features = cv.fit_transform(norm_train_reviews)

          cv_test_features = cv.transform(norm_test_reviews)

          st.write('BOW model:> Train features shape:', cv_train_features.shape, ' Test features shape:', cv_test_features.shape)

          rfc = RandomForestClassifier(n_estimators=10, random_state=42)

          rfc_bow_predictions = train_predict_model(classifier=rfc, train_features=cv_train_features, train_labels=train_sentiments,test_features=cv_test_features, test_labels=test_sentiments)

          display_model_performance_metrics(true_labels=test_sentiments, predicted_labels=rfc_bow_predictions, classes=['positive', 'negative'])

          classification_rep_bow = classification_report(true_labels=test_sentiments, predicted_labels=rfc_bow_predictions, classes=['positive', 'negative'])

          df_bow = pd.DataFrame(classification_rep_bow).transpose()
          df_bow.at['accuracy', 'precision'] = 0.0
          df_bow.at['accuracy', 'recall'] = 0.0

          st.write(df_bow)
          csv = convert_df(df_bow)
          generate_download_button(csv_data=csv, filename='rfc_bow', file_label='rfc_bow')



elif choice == 'About':
    st.subheader('About Us')
    st.write('1. Vicente De Leon')
    st.write('Currently a grad student at IU Bloomington focusing on Data Science - Intelligent Systems Engineering domain. The Introduction to NLP in Python class taught me what AI can do in many fields and how important it is to the modern world. This web app shows you a sneek peek of its powerful techniques regarding NLP tasks.')
    st.write('\n')
    st.write('2. Seth Smithson')
    st.write('\n')
    st.write('3. Samaneh Torkzadeh')
    st.write('\n')