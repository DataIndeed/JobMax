import lxml.html
import requests
import math
from textblob import TextBlob
import nltk
from wordcloud import WordCloud, STOPWORDS
import matplotlib.pyplot as plt
import pandas as pd
import datetime as dt
import hashlib
#nltk.download('punkt')
#nltk.download('averaged_perceptron_tagger')
#nltk.download('brown')
import os, ssl
import boto3



def my_handler(event, context):
    s3_resource = boto3.resource('s3')
    s3_client = boto3.client('s3')
    dynamodb = boto3.resource('dynamodb')

    if (not os.environ.get('PYTHONHTTPVERIFY', '') and getattr(ssl, '_create_unverified_context', None)):
        ssl._create_default_https_context = ssl._create_unverified_context

    #with open('./testfiles/testhtml.htm', 'r') as myfile:
    #    data = myfile.read().replace('\n', '')

    #print data

    search_term = "quantitative developer"
    #url = 'https://www.linkedin.com/jobs/search?keywords=' + search_term + '&location=Canada&f_TP=1&f_TPR=r604800'
    url = 'https://www.linkedin.com/jobs/search?keywords=' + search_term + '&location=Canada'
    r = requests.get(url)
    print(r.text)

    doc = lxml.html.document_fromstring(r.text)
    #print(doc)

    job_result_count_text = doc.xpath("//span[@class='results-context-header__job-count']/text()")
    job_result_count = int(job_result_count_text[0])
    print(job_result_count)

    pages = [i*25 for i in range(math.floor(job_result_count/25))]

    #&start=25
    el_job_all = []
    el_company = []
    el_job_title = []
    el_job_post = []
    el_job_href = []
    el_job_post2 = []
    el_job_href2 = []
    el_job_company = []
    el_job_company_url = []
    el_job_title = []
    el_job_location = []
    el_company = []
    el_job_title = []
    el_job_post = []
    el_job_href = []
    el_job_post2 = []
    el_job_href2 = []
    el_job_company = []
    el_job_company_url = []
    el_job_title = []
    el_job_location = []

    for page in pages:
        url = 'https://www.linkedin.com/jobs/search?keywords=' + search_term + '&location=Canada&start=' + str(page)
        r = requests.get(url)
        doc = lxml.html.document_fromstring(r.text)

        el_company = doc.xpath("//div[@class='artdeco-entity-lockup__subtitle ember-view']/a/text()")
        el_job_title = doc.xpath("//div[@class='full-width artdeco-entity-lockup__title ember-view']/a")

        el_job_post = doc.xpath("//div[@class='flex-grow-1 artdeco-entity-lockup__content ember-view']/div/a/text()")
        el_job_href = doc.xpath("//div[@class='flex-grow-1 artdeco-entity-lockup__content ember-view']/div/a")

        el_job_post2 = doc.xpath("//li[@class='result-card job-result-card result-card--with-hover-state']/a/span/text()")
        el_job_href2 = doc.xpath("//li[@class='result-card job-result-card result-card--with-hover-state']/a")
        el_job_company = doc.xpath("//li[@class='result-card job-result-card result-card--with-hover-state']/div/h4/a/text()")
        el_job_company_url = doc.xpath("//li[@class='result-card job-result-card result-card--with-hover-state']/div/h4/a")
        el_job_title = doc.xpath("//li[@class='result-card job-result-card result-card--with-hover-state']/div/h3/text()")
        el_job_location = doc.xpath("//li[@class='result-card job-result-card result-card--with-hover-state']/div/div/span/text()")

        el_job_all = el_job_all + list(zip([str(dt.datetime.now()) for e in el_job_href2], [abs(hash(e.attrib['href'])) % (10 ** 8) for e in el_job_href2], [e.strip() for e in el_job_title], [e.strip() for e in el_job_location], [e.attrib['href'] for e in el_job_href2], [e.strip() for e in el_job_company], [e.attrib['href'] for e in el_job_company_url]))

    tag_all = []

    all_desc = ''

    for e in list(el_job_all):
        r = requests.get(e[4])
        #print(r.text)
        doc = lxml.html.document_fromstring(r.text)
        desc = ' '.join(doc.xpath("//div[@class='show-more-less-html__markup show-more-less-html__markup--clamp-after-5']/text()"))
        #print(desc)
        blob = TextBlob(desc)
        #print(blob.tags)
        #print(blob.noun_phrases)
        #print(blob.np_counts)
        tag_all = tag_all + blob.tags
        #all_desc = all_desc + desc

    df = pd.DataFrame(tag_all, columns=['word', 'tag'])
    grsum = df.groupby('word').count()
    df_noun = df[df.tag.isin(['NN','NNS','NNP','NNPS'])]
    all_desc = ' '.join(df_noun['word'].tolist())
    grsum = df_noun.groupby('word').count()
    grsum = grsum.sort_values('tag')
    grsum.to_csv('job_keyword_summary_' + search_term + '.csv')
    print(el_job_all)
    df_job = pd.DataFrame(el_job_all, columns=['available_time','job_id', 'job_title', 'location', 'job_url', 'company_name', 'company_url'])
    df_job.to_csv('job_list_' + search_term + '.csv')
    df_job_json = df_job.T.to_dict().values()
    dynamoTable = dynamodb.Table('jobmaxtable')
    for job in df_job_json:
        dynamoTable.put_item(Item=job)

    stopwords = set(STOPWORDS)
    wordcloud = WordCloud(width=800, height=800,
                          background_color='white',
                          stopwords=stopwords,
                          min_font_size=10).generate(all_desc)

    # plot the WordCloud image
    plt.figure(figsize=(8, 8), facecolor=None)
    plt.imshow(wordcloud)
    plt.axis("off")
    plt.tight_layout(pad=0)

    wc_filename="wordcloud_"+search_term+"_"+str(dt.date.today())+".jpg"
    plt.savefig(wc_filename)
    s3_client.upload_file(Filename=wc_filename, Bucket="jobmaxresults", Key=wc_filename)



    #########################################


    #plt.show()

    #for e in el_job_href:
        #print e.attrib['href']

    #for e in el_job_post:
        #print e


    #soup = BeautifulSoup(data, "lxml")
    #for e in el_job_title:
    #    print e.attrib['href']
    #    print e.text.strip()

    #print len(el_job_title)

    #for e in el_company:
    #    print e.strip()

    #print len(el_company)
    #for EachPart in soup.select('a[class*="ember-view job-card-container__link job-card-list__title"]'):
    #    print EachPart.get_text()


#my_event=None
#my_context=None

#my_handler(my_event, my_context)