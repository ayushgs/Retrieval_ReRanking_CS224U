import scrapy
import pickle
from scrapy.crawler import CrawlerProcess
from bs4 import BeautifulSoup

# read in the doc urls
prefix = 'dev' # could also change to train

doc_id_list = pickle.load(open("{}_doc_id_list.p".format(prefix), "rb"))
doc_dict = pickle.load(open("{}_doc_dict.p".format(prefix), "rb"))
assert len(doc_id_list) > 0
assert len(doc_dict) > 0

doc_id_content = {} #dict maps from doc id to the contents in the doc. The content is saved as a list of vocab_ids
vocab_dict = {} #mapping from vocab term to id
vocab_id_list = [] #list where id maps to the vocab term (0 indexed)
vocab_frequency = {} #number of times each vocab term appears in the vocab of documents
parse_failures = 0

class DocumentSpider(scrapy.Spider):
    name = "documents"
    start_urls = doc_id_list

    def parse(self, response):
        soup = BeautifulSoup(response.text, 'html.parser')
        body = soup.find('body')
        title = soup.find('title')

        # get the original url we requested
        if response.request.meta.get('redirect_urls'):
            url = response.request.meta['redirect_urls'][0]
        else:
            url = response.request.url

        def get_content(part):
            if part is None:
                global parse_failures
                parse_failures += 1
                return []

            content_list = []
            for word in part.text.split():
                word = word.strip().lower()
                if not word.isalnum():
                    continue

                vocab_frequency[word] = vocab_frequency.get(word, 0) + 1

                if word not in vocab_dict:
                    vocab_id_list.append(word)
                    vocab_dict[word] = len(vocab_id_list) - 1

                word_id = vocab_dict[word]
                content_list.append(word_id)
            return content_list

        content = (get_content(title), get_content(body))
        doc_id_content[doc_dict[url]] = content

process = CrawlerProcess()
process.crawl(DocumentSpider)
process.start() # the script will block here until the crawling is finished

# save the data!
pickle.dump(doc_id_content, open("{}_doc_id_content.p".format(prefix), "wb" ))
pickle.dump(vocab_dict, open("{}_vocab_dict.p".format(prefix), "wb" ))
pickle.dump(vocab_id_list, open("{}_vocab_id_list.p".format(prefix), "wb" ))
pickle.dump(vocab_frequency, open("{}_vocab_frequency.p".format(prefix), "wb" ))
print("Parse failures:", parse_failures)

