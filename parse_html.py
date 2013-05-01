import re
import requests
import csv
import sys
from bs4 import BeautifulSoup
import json

# Extract year string from year
def extract_year(str):
	# look for '1927'
	match = re.search(r'1\d{3}', str)
	if match:
		return match.group(0)

	# not found? look for '192-'
	match = re.search(r'1\d{2}-', str)
	if match:
		return match.group(0).replace('-', '5') #for 192- return 1925
	
	# ok, '19--' then
	match = re.search(r'1\d{1}--', str)
	if match:
		return match.group(0).replace('-', '0') #for 19-- return 1900

	# screw that BS
	return None
    	

# Get data from a single map details page
def get_details(url):
	i = requests.get(url)
	bs = BeautifulSoup(i.text)
	image_url = bs.find('img', {'class':'imgthumb'}).parent.get('href')

	notes = [] ; headline = '' ; text = '' ; year = '' ; caption = ''

	y = bs.find(text="Imprint").find_next('td').text
	year = extract_year(y)

	t = bs.find(text="Title")
	if t is not None:
		headline = t.find_next('td').text.split('[')[0]

	for n in bs.find_all(text="Note"):
		notes.append(n.find_next('td').text)

	if len(notes) == 1:
		text = notes[0]

	elif len(notes) > 1:
		caption = notes.pop(0) + '  ' + caption
		# headline = notes.pop(0)
		text = '<br/><br/>'.join(notes)

	return image_url, headline, text, caption, year


# START HERE

json_data = {
	"timeline" : {
		"headline" 	: "Ancient Maps of Jerusalem",
		"type"		: "default",
		"date"		: []
	}
}

r = requests.get('http://www.jnul.huji.ac.il/dl/maps/jer/html/date.html')
soup = BeautifulSoup(r.text)

data = soup.find("table", cols="5")
imgs = data.find_all('img', {'class':'imgthumb'});

# writer = csv.writer(sys.stdout, quoting=csv.QUOTE_ALL)
# writer.writerow(('Start Date', 'End Date', 'Headline', 'Text', 'Media', 'Media Credit', 'Media Caption', 'Media Thumbnail'))

for i in imgs:
	thumbnail = i.get('src')

	details_url = 'http://www.jnul.huji.ac.il/dl/maps/jer/html/' + i.find_parent("a").get('href')

	image_url, headline, text, caption, year = get_details(details_url)

	credit =  'National Library of Israel'

	# writer.writerow((year, year, headline.encode('utf-8'), text.encode('utf-8'), image_url, credit, caption.encode('utf-8'), thumbnail))

	json_data['timeline']['date'].append ({
        "startDate"	: year,
        "headline"	: headline.encode('utf-8'),
        "text"		: text.encode('utf-8'),
        "asset":
        {
            "media"		: image_url,
            "thumbnail" : thumbnail,
            "credit"	: credit,
            "caption"	: caption.encode('utf-8')
        }
	})


data = json.dumps(json_data)

print "data =  %s" % data

