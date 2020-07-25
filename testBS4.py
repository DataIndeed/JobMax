from bs4 import BeautifulSoup
import lxml.html

with open('./testfiles/testhtml.htm', 'r') as myfile:
    data = myfile.read().replace('\n', '')

doc = lxml.html.document_fromstring(data)

el = doc.xpath("//div[@class='full-width artdeco-entity-lockup__title ember-view']/a/text()")
#soup = BeautifulSoup(data, "lxml")
for e in el:
    print e.strip()

#for EachPart in soup.select('a[class*="ember-view job-card-container__link job-card-list__title"]'):
#    print EachPart.get_text()
