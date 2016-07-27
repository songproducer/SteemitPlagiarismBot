import sys, traceback
from piston.steem import Steem
from piston.steem import Post
import os
import json
import re
import html2text
import requests
from itertools import islice
import difflib
import collections
from collections import OrderedDict
import random

account = 'ChangThisToYourSteemitUsername'
author = 'ChangThisToYourSteemitUsername'
wif = '5YourPostingKeyGoesHere12345678901234567890'
steem = Steem(nobroadcast=False, wif=wif)

#initialise lists to store snippets of the content
captureContentInAList = []
captureContentInTheFinalList = []

percentageDifferenceFormatted = ''
percentageRequired = 0.5
captureContentSnippet = ''
stillTheSamePoster = ''
yacySearchResultDescription = ''
link = ''
limit = 4
theContent= ''
mainLoop = 0
stopLookingForContent = 0
commentedYet=0
query = ''
randomContentSnippets = ''

#begin main loop

def f7(seq):
    seen = set()
    seen_add = seen.add
    return [x for x in seq if not (x in seen or seen_add(x))]
while mainLoop < 1:
    stopLookingForContent = 0
    while commentedYet < 1:
        while stopLookingForContent < 1:

            url = 'http://46.101.159.129:8090/yacysearch.json'

            thePostTitle = steem.get_posts(limit=1,sort='created')

            preformattedTitle = re.search(r'(\@.+?.+[^\>\]])'.format(str(thePostTitle)),str(thePostTitle))
            formattedTitleVar = preformattedTitle.groups(1)

            posterPreformatted = re.search(r'(\@\b.{1,}\b\/)',str(formattedTitleVar))
            posterPre = posterPreformatted.groups(1)
            poster = str(posterPre).replace('(', '').replace(')', '').replace('/','').replace("'",'').replace(",",'')



            try:
                formattedTitle = re.search(r'(\/.+[^\>\]])'.format(str(thePostTitle)),str(thePostTitle))
                titleWithNoSlash = formattedTitle.group(1).replace("/","")
            except AttributeError:
                print ("No slashes in title")

            steemFormattedSlugDetectedPost = str(formattedTitleVar).replace('(', '').replace(')', '').replace("'",'').replace(",",'')
            #turn hyphens to spaces in title
            titleWithNoSpaces = titleWithNoSlash.replace("-"," ")
            #try:
                #print (titleWithNoSpaces)
                    #formattedTitle = preformattedTitle.group(1)
                    #print (html2text.html2text(str(formattedTitle)))
            #except IndexError:
            #    print ('')

            #get new post
            post = steem.get_content(str(preformattedTitle.group(1)))

            #strip new post content of annoying characters
            postFormattedStillHasMarkDown = (html2text.html2text(post["body"]))
            postFormatted = str(postFormattedStillHasMarkDown).replace("*","").replace("#","").replace("\\","").replace(">","").replace("_","").replace('"','').replace('&lt;','').replace('&gt;','').replace('html','').replace('<','')

            #Preprocessing content
            #capture links
            captureLinksString = ''
            captureLinks = re.search(r'\<?(https?:\/\/?\/[^/]+\W?\@?\S+\W?\S+\w)\>?',str(postFormatted))

            #filter out links
            precaptureContent = re.sub(r'\<?(https?:\/\/?\/[^/]+\W?\@?\S+\W?\S+\w)\>?','',str(postFormatted))
            captureContent = re.sub(r'\!|\[|\]|\(|\)','',str(precaptureContent))


            if poster != stillTheSamePoster:

                print ("\nBEGIN POST")
                #Poster details
                print ('Poster: ' + str(poster))
                print ('Post Title: ' + titleWithNoSpaces)
                print ('Content:\n')

                print ('' + captureContent)

                #if there is content, build the Yacy query
                if captureContent != None:

                    try:
                        #initialise captureContentInAList and final list
                        captureContentInAList = []
                        captureContentInTheFinalList = []

                        #get random snippets
                        for m in re.finditer(r"(\b\w+\b.\b\w+\b.\b\w+\b.\b\w+\b)", captureContent):
                            captureContentInAList.append(m.group(0))

                        captureContentListToTuple = tuple(captureContentInAList)
                        #make sure the sentence are long enough
                        for z in captureContentListToTuple:
                            if len((str(z))) > 2:
                                captureContentInTheFinalList.append(str(z))

                        #if not long enough, cause an AttributeError
                            else:
                                captureContentInTheFinalList.append(0)

                        r1 = random.choice(captureContentInTheFinalList)
                        r2 = random.choice(captureContentInTheFinalList)
                        r3 = random.choice(captureContentInTheFinalList)
                        r4 = random.choice(captureContentInTheFinalList)

                        randomContentSnippetList = [r1,r2,r3,r4]

                        #trim the duplicate snippets
                        r1 = f7(randomContentSnippetList[0])
                        r2 = f7(randomContentSnippetList[0])
                        r3 = f7(randomContentSnippetList[0])
                        r4 = f7(randomContentSnippetList[0])


                        #check there are some results
                        if len(captureContent) > 200:
                            if randomContentSnippetList:


                                randomContentSnippets = randomContentSnippetList[0] + ' ' + randomContentSnippetList[1] + ' ' + randomContentSnippetList[2] + ' ' + randomContentSnippetList[3]

                                print ('END OF POST\n')
                                print ('Searching for these random snippets:\n')
                                print (str(randomContentSnippetList[0]))
                                print (str(randomContentSnippetList[1]))
                                print (str(randomContentSnippetList[2]))
                                print (str(randomContentSnippetList[3] +'\n'))
                                query = '"'+randomContentSnippetList[0]+'"'+'"'+randomContentSnippetList[1]+'"'+'"'+randomContentSnippetList[2]+'"'+'"'+randomContentSnippetList[3]+'"'


                                print('Search query: '+ query+'\n')

                                #send the query, get the JSON
                                payload = {'query':query, 'contentdom':'text', 'maximumRecords': '1'}
                                r = requests.get(url, params=payload)
                                #get json into ordered dictionary
                                data = r.json(object_pairs_hook=OrderedDict)
                                #r.encoding = 'ISO-8859-1'

                                #assign top level json variable
                                channels = data[u'channels'][0]
                                try:
                                    link = channels[u'items'][0][u'link']
                                except IndexError:
                                    link = 'none'
                                #start searching
                                if link == 'none':
                                    print ("Query: No results.")
                                else:
                                    yacySearchResultDescriptionPreFormatted = str(html2text.html2text(str(channels[u'items'][0][u'description'])))
                                    yacySearchResultDescription = str(yacySearchResultDescriptionPreFormatted.replace("*",""))

                                    #title = items[0][u'title']
                                    #if seach result is returned display it and the resulting link

                                    print ("Search result found: " + yacySearchResultDescription)
                                    print ("Link: " + str(link)+'\n')

                                    #get detected post
                                    stripDetectedPostLinkToFindSlug = re.search(r'(\@.+?.+[^\>\]])',str(link))
                                    detectedPostSlug = str(stripDetectedPostLinkToFindSlug.group(1))
                                    detectedPostRaw = steem.get_content(detectedPostSlug)

                                    #strip annoying characters
                                    detectedPostStillHasMarkDown = (html2text.html2text(detectedPostRaw["body"]))
                                    detectedPostFormatted = str(detectedPostStillHasMarkDown).replace("*","").replace("#","").replace("\\","").replace(">","").replace("_","").replace('"','').replace("'","").replace('&lt;','').replace('&gt;','').replace('html','').replace('<','')

                                    #filter out links
                                    detectedPostFormattedStillHasLinks = re.sub(r'\<?(https?:\/\/?\/[^/]+\W?\@?\S+\W?\S+\w)\>?','',str(detectedPostFormatted))
                                    detectedPost = re.sub(r'\!|\[|\]|\(|\)','',str(detectedPostFormattedStillHasLinks))

                                    #trim search result link to find its author
                                    searchResultAuthorPreformatted = re.search(r'(\@\b.{1,}\b\/)',str(link))
                                    searchResultAuthorPre = searchResultAuthorPreformatted.groups(1)
                                    searchResultAuthor = str(searchResultAuthorPre).replace('(', '').replace(')', '').replace('/','').replace("'",'').replace(",",'')

                                    print('Search result author: '+searchResultAuthor)
                                    print('Original post author: ' + poster)
                                    #verify if contains duplicate content
                                    percentageDifference = difflib.SequenceMatcher(None,str(captureContent),str(detectedPost)).ratio()
                                    percentageDifferenceFormatted = round(percentageDifference * 100,2)
                                    if searchResultAuthor:
                                        if poster == searchResultAuthor:
                                            print ("Similar content written by the same author. Continuing...")
                                        else:
                                            if percentageDifference < percentageRequired:
                                                print ("Percentage match is only " + str(percentageDifferenceFormatted)+'%')
                                            else:
                                                stopLookingForContent = 1
                                                commentedYet = 0
                        else:
                            query = ''
                            print ('Not enough content.')
                    except AttributeError:
                        print ('Search term is too short.')
                    except IndexError:
                        if len(randomContentSnippets) <15:
                            print ('Not enough content')
                print ('_______________________________')


                #check are we repeating the content?
                stillThePostTitle = steem.get_posts(limit=1,sort='created')
                stillPreformattedTitle = re.search(r'(\@.+?.+[^\>\]])'.format(str(thePostTitle)),str(thePostTitle))
                stillFormattedTitleVar = preformattedTitle.groups(1)

                stillPosterPreformatted = re.search(r'(\@\b.{1,}\b\/)',str(formattedTitleVar))
                stillPosterPre = posterPreformatted.groups(1)
                stillPoster = str(posterPre).replace('(', '').replace(')', '').replace('/','').replace("'",'').replace(",",'')
                stillTheSamePoster = str(stillPoster)

                print ('Waiting for new posts',end="")
            print ('.', end="", flush=True)


    #Found a match!
    try:
        if percentageDifferenceFormatted:
            if commentedYet == 0:
                print ("\nPercentage difference: " + str(percentageDifferenceFormatted),flush=True)
    except IndexError:
        print ('failed, index error')
    except TypeError:
        print ('failed, type error')
    except AttributeError:
        print ('failed, attribute error')


    #make a comment in piston
    post = Post(Steem(), steemFormattedSlugDetectedPost)
    if poster == '@' + author:
        time.sleep(21)
    post.reply("Hi! I have automatically detected similar content from another article:\n " + str(link) + '\nIt is approximately ' + str(percentageDifferenceFormatted) + '%' + ' similar.\nI have not flagged, but want to let manual curators know. Did I get it wrong? Please tell me so I can improve!' ,'', author=author, meta=None)
    commentedYet=1
