import urllib, re
from BeautifulSoup import BeautifulSoup
# if not installed, do easy_install BeautifulSoup
# documentation: http://www.crummy.com/software/BeautifulSoup/documentation.html

# __author__ = 'pashamur'

def fetch_fullname(username):
    # Returns tuple: [firstName, lastName]
    params = urllib.urlencode({'query':username})
    htmldoc = urllib.urlopen("http://web.mit.edu/bin/cgicso?options=general&" + params)
    soup = BeautifulSoup(htmldoc.read())
    data = soup.find('pre') or [1] # put in array with one element in case connection failed
    #data='   name: Drach, Zachary email: <a href="mailto:zdrach@MIT.EDU">zdrach@MIT.EDU</a> address: MacGregor House # F413 year: 1 '
    if len(data) <= 1:
        return None
    else:
        m = re.search("(?<=name: )(\w+), (\w+)", data.contents[0])
        if m == None:
            return None
        name = (str(m.group(2)), str(m.group(1)))  # [firstName, lastName]
        return name

print 'Fetching data for zdrach:'
print fetch_fullname('zdrach')

# print 'Fetching data for pashamur:'
# fetch_mit_userdata('pashamur')

# print 'Fetching data for abcdef:'
# fetch_mit_userdata('abcdef')
