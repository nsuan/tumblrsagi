#-------------------------------------------------------------------------------
# Name:        module1
# Purpose:
#
# Author:      User
#
# Created:     07/01/2015
# Copyright:   (c) User 2015
# Licence:     <your licence>
#-------------------------------------------------------------------------------


import time
import os
import sys
import re
#import mechanize
#import cookielib
import logging
import urllib2
import httplib
import random
import HTMLParser
import json
import shutil
import socket
import string



def setup_logging(log_file_path):
    # Setup logging (Before running any other code)
    # http://inventwithpython.com/blog/2012/04/06/stop-using-print-for-debugging-a-5-minute-quickstart-guide-to-pythons-logging-module/
    assert( len(log_file_path) > 1 )
    assert( type(log_file_path) == type("") )
    global logger
    # Make sure output dir exists
    log_file_folder =  os.path.dirname(log_file_path)
    if log_file_folder is not None:
        if not os.path.exists(log_file_folder):
            os.makedirs(log_file_folder)
    logger = logging.getLogger()
    logger.setLevel(logging.DEBUG)
    formatter = logging.Formatter("%(asctime)s - %(levelname)s - %(message)s")
    fh = logging.FileHandler(log_file_path)
    fh.setLevel(logging.DEBUG)
    fh.setFormatter(formatter)
    logger.addHandler(fh)
    ch = logging.StreamHandler()
    ch.setLevel(logging.DEBUG)
    ch.setFormatter(formatter)
    logger.addHandler(ch)
    logging.debug("Logging started.")
    return


def save_file(filenamein,data,force_save=False):
    assert_is_string(filenamein)
    counter = 0
    while counter <= 10:
        counter += 1
        try:
            if not force_save:
                if os.path.exists(filenamein):
                    logging.debug("file already exists! "+repr(filenamein))
                    return
            sanitizedpath = filenamein# sanitizepath(filenamein)
            foldername = os.path.dirname(sanitizedpath)
            if len(foldername) >= 1:
                if not os.path.isdir(foldername):
                    os.makedirs(foldername)
            file = open(sanitizedpath, "wb")
            file.write(data)
            file.close()
            return
        except IOError, err:
            logging.exception(err)
            logging.error(repr(locals()))
            continue
    logging.critical("Too many failed write attempts!")
    logging.critical(repr(locals()))
    raise(err)


def read_file(path):
    """grab the contents of a file"""
    assert_is_string(path)
    f = open(path, "r")
    data = f.read()
    f.close()
    return data


def add_http(url):
    """Ensure a url starts with http://..."""
    if "http://" in url:
        return url
    elif "https://" in url:
        return url
    else:
        #case //derpicdn.net/img/view/...
        first_two_chars = url[0:2]
        if first_two_chars == "//":
            output_url = "https:"+url
            return output_url
        else:
            logging.error(repr(locals()))
            raise ValueError


def deescape(html):
    # de-escape html
    # http://stackoverflow.com/questions/2360598/how-do-i-unescape-html-entities-in-a-string-in-python-3-1
    deescaped_string = HTMLParser.HTMLParser().unescape(html)
    return deescaped_string





##def get(url):
##    """Simpler url getter"""
##    assert_is_string(url)
##    deescaped_url = deescape(url)
##    url_with_protocol = add_http(deescaped_url)
##    response = urllib2.urlopen(url_with_protocol)
##    html = response.read()
##    return html




def get(url):
    #try to retreive a url. If unable to return None object
    #Example useage:
    #html = get("")
    #if html:
    assert_is_string(url)
    deescaped_url = deescape(url)
    url_with_protocol = add_http(deescaped_url)
    #logging.debug( "getting url ", locals())
    gettuple = getwithinfo(url_with_protocol)
    if gettuple:
        reply, info = gettuple
        return reply
    else:
        return


def getwithinfo(url):
    """Try to retreive a url. If unable to return None objects
    Example useage:
    html = get("")
        if html:
    """
    attemptcount = 0
    max_attempts = 10
    retry_delay = 10
    request_delay = 0
    while attemptcount < max_attempts:
        attemptcount = attemptcount + 1
        if attemptcount > 1:
            delay(retry_delay)
            logging.debug( "Attempt "+repr(attemptcount)+" for URL: "+repr(url) )
        try:
            save_file(os.path.join("debug","get_last_url.txt"), url, True)
            r = urllib2.urlopen(url)
            info = r.info()
            reply = r.read()
            delay(request_delay)
            # Save html responses for debugging
            #print info
            #print info["content-type"]
            if "html" in info["content-type"]:
                #print "saving debug html"
                save_file(os.path.join("debug","get_last_html.htm"), reply, True)
            else:
                save_file(os.path.join("debug","get_last_not_html.txt"), reply, True)
            # Retry if empty response and not last attempt
            if (len(reply) < 1) and (attemptcount < max_attempts):
                logging.error("Reply too short :"+repr(reply))
                continue
            return reply,info
        except urllib2.HTTPError, err:
            logging.debug(repr(err))
            if err.code == 404:
                logging.debug("404 error! "+repr(url))
                return
            elif err.code == 403:
                logging.debug("403 error, ACCESS DENIED! url: "+repr(url))
                return
            elif err.code == 410:
                logging.debug("410 error, GONE")
                return
            else:
                save_file(os.path.join("debug","HTTPError.htm"), err.fp.read(), True)
                continue
        except urllib2.URLError, err:
            logging.debug(repr(err))
            if "unknown url type:" in err.reason:
                return
            else:
                continue
        except httplib.BadStatusLine, err:
            logging.debug(repr(err))
            continue
        except httplib.IncompleteRead, err:
            logging.debug(repr(err))
            continue
        except socket.timeout, err:
            logging.debug(repr( type(err) ) )
            logging.debug(repr(err))
            continue
    logging.critical("Too many repeated fails, exiting.")
    sys.exit()# [19:51] <@CloverTheClever> if it does it more than 10 times, quit/throw an exception upstream




def assert_is_string(object_to_test):
    """Make sure input is either a string or a unicode string"""
    if( (type(object_to_test) == type("")) or (type(object_to_test) == type(u"")) ):
        return
    logging.critical(repr(locals()))
    raise(ValueError)


def delay(basetime,upperrandom=0):
    #replacement for using time.sleep, this adds a random delay to be sneaky
    sleeptime = basetime + random.randint(0,upperrandom)
    #logging.debug("pausing for "+repr(sleeptime)+" ...")
    time.sleep(sleeptime)


def get_current_unix_time():
    """Return the current unix time as an integer"""
    # https://timanovsky.wordpress.com/2009/04/09/get-unix-timestamp-in-java-python-erlang/
    timestamp = int(time.time())
    return timestamp



def merge_dicts(*dict_args):
    # http://stackoverflow.com/questions/38987/how-can-i-merge-two-python-dictionaries-in-a-single-expression
    '''
    Given any number of dicts, shallow copy and merge into a new dict,
    precedence goes to key value pairs in latter dicts.
    '''
    result = {}
    for dictionary in dict_args:
        result.update(dictionary)
    return result


def flatten(sequence,contents=[]):
    """Take a dict, tuple, or list, and flatten it."""
    # Flatten dicts
    if (type(sequence) == type({})):
        for dict_key in sequence.keys():
            field = sequence[dict_key]
            if ( (type(field) == type({})) or (type(field) == type([])) or (type(field) == type((1,2)))):
                contents.append(flatten(field,contents))
            else:
                contents.append(field)
    # Flatten lists and tuples
    elif (
    (type(sequence) == type([])) or
    (type(sequence) == type(()))
    ):
        for item in sequence:
            contents.append(item)
    return contents


def uniquify(seq, idfun=None):
    # List uniquifier from
    # http://www.peterbe.com/plog/uniqifiers-benchmark
   # order preserving
   if idfun is None:
       def idfun(x): return x
   seen = {}
   result = []
   for item in seq:
       marker = idfun(item)
       # in old Python versions:
       # if seen.has_key(marker)
       # but in new ones:
       if marker in seen: continue
       seen[marker] = 1
       result.append(item)
   return result




def main():
    pass

if __name__ == '__main__':
    main()
