#-------------------------------------------------------------------------------
# Name:        module1
# Purpose:
#
# Author:      User
#
# Created:     13/06/2015
# Copyright:   (c) User 2015
# Licence:     <your licence>
#-------------------------------------------------------------------------------
import time



def loop():
    """Run in a loop forever"""
    print "Starting loop for get_posts"
    while True:
        # Import each loop to cleanup old objects
        print "running imports"
        import get_posts
        import config
        print "calling get_posts.main()"
        get_posts.main()
        print "finished get_posts.main(), waiting for "+repr(config.get_media_restart_delay)
        time.sleep(config.get_posts_restart_delay)
        continue


def main():
    loop()

if __name__ == '__main__':
    main()