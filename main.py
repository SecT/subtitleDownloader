#use with python3

from html.parser import HTMLParser
import urllib.request

from time import sleep


#Configuration
domain = 'https://www.opensubtitles.org/pl/ssearch/sublanguageid-'
lang = 'pol'
langShort = 'pl'
showId = '488581'
mainUrl = domain+lang+'/idmovie-'+showId

limit = 1

pageDownloadDelay = 1  # [s] in order to avoid overloading the server
###


def processEpisodeUrl(url):
	#check if correct episodeUrl
	if url[-7:].isnumeric():
		episodeId = url[-7:]
		outputUrl = 'https://www.opensubtitles.org/'+langShort+'/search/sublanguageid-'+lang+'/imdbid-'+episodeId
		return outputUrl

def processSubtitlePageUrl(url):
	outputUrl = 'https://www.opensubtitles.org/'+langShort+'/subtitles/'
	
	prefixLength = len('/'+langShort+'/subtitles/')
	
	subtitlePageSuffix =  url[prefixLength:] #/pl/subtitles/  +  6921128/the-crown-wolferton-splash-pl    
	outputUrl = outputUrl + subtitlePageSuffix
	return outputUrl

def isSubtitleUrl(url):
		if url[:8] == 'https://':
			return True
		return False
	
class MyHTMLParser(HTMLParser):

	#Initializing lists
	lsStartTags = list()
	lsEndTags = list()
	lsStartEndTags = list()
	lsComments = list()

	episodeUrls = list()
	subtitlePageUrls = list()
	
	subtitleUrl = ''

	def handle_starttag(self, startTag, attrs):
		self.lsStartTags.append(startTag)
	
		if startTag == 'a' and len(attrs) > 1:
			if attrs[0][0] == 'itemprop' and attrs[0][1] == 'url' and attrs[1][0] == 'title':
				rawEpisodeUrl = attrs[2][1]
				#print(episodeUrl)
				episodeUrl = processEpisodeUrl(rawEpisodeUrl)
				if episodeUrl != None:
					self.episodeUrls.append(episodeUrl)
				#print(episodeUrl)

			if attrs[0][0] == 'class' and attrs[0][1] == 'bnone':
				subtitlePageUrl = attrs[3][1]
				
				subtitlePageUrl = processSubtitlePageUrl(subtitlePageUrl)
				self.subtitlePageUrls.append(subtitlePageUrl)
			
			if attrs[0][0] == 'class' and attrs[0][1] == 'none':
				if isSubtitleUrl(attrs[1][1]):
					self.subtitleUrl = attrs[1][1]
			
	def handle_endtag(self, endTag):
		self.lsEndTags.append(endTag)
	
	def handle_startendtag(self,startendTag, attrs):
		self.lsStartEndTags.append(startendTag)
	
	def handle_comment(self,data):
		self.lsComments.append(data)



def getPageContents(url):
	page = urllib.request.urlopen(url)
	return page


##########################################################################################


isProcessingStopped = False

######Get episode list
page = getPageContents(mainUrl)

parser = MyHTMLParser()

parser.feed(str(page.read()))

parser.reset()
######


#######Get subtitle pages list
#Example episode Url: ('https://www.opensubtitles.org/pl/search/sublanguageid-pol/imdbid-5483578')

print('Obtain subtitle page urls')

subtitlePageUrls = list()

for episode in parser.episodeUrls:
	
	page = getPageContents(episode)

	parser.feed(str(page.read()))
	
	subtitlePageUrls = subtitlePageUrls + parser.subtitlePageUrls
	
	if len(subtitlePageUrls) > limit:
		print('Stopped processing due to the limit set: '+ str(limit))
		isProcessingStopped = True
		break
	
	parser.reset()
	sleep(pageDownloadDelay)
#######

print('Finished obtaining subtitle page urls')

#######

subtitles = list()


for subtitlePage in subtitlePageUrls:
	page = getPageContents(subtitlePage)
	parser.feed(str(page.read()))
	
	subtitles.append(parser.subtitleUrl)
	sleep(pageDownloadDelay)

print('Finished obtaining subtitle files urls')

print(subtitles)

if isProcessingStopped:
	print("NOTE: Not all subtitles have been downloaded because of the limit set")


proceedWithDownload = input("Found "+str(len(subtitles))+" for download. Proceed? y/n ")

if proceedWithDownload == 'y':
	###########################
	#Download the found subtitles

	#Temporarily only open the urls in a web browser
	import webbrowser

	for subtitle in subtitles:
		webbrowser.open(subtitle)
	####

