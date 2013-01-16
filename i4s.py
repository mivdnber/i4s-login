## Copyright (C) 2013 Michiel Van den Berghe
##
## Permission is hereby granted, free of charge, to any person obtaining a copy
## of this software and associated documentation files (the "Software"), to deal
## in the Software without restriction, including without limitation the rights
## to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
## copies of the Software, and to permit persons to whom the Software is
## furnished to do so, subject to the following conditions:
##
## The above copyright notice and this permission notice shall be included in
## all copies or substantial portions of the Software.
##
## THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
## IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
## FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
## AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
## LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
## OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
## SOFTWARE
##
## Contains a Python function to log in to Internet 4 Students, a Ghent based
## internet provider offering - at least in this building - horribly unstable
## connections to student homes. As the login page is slow and annoying with
## useless popups, I created this little script to log in from CLI. Their main
## site is http://www.i4s.be/. Don't open if you're even slighly epileptic.
##
## Note that everything is sent over clear HTTP, a massive security hole I4S
## doesn't care to fix, so use at your own risk. I suspect many captive portal
## systems work in a similar way, so I thought I'd share the code.
##
## If run as python i4s.py <username> <password>, it should log you in!

import sys, time
import urllib2 as url
from urllib import urlencode
from bs4 import BeautifulSoup

# Might have to change these
apip, apport = '192.168.182.1', '3990'
i4surl = 'http://go.i4s.be/'

class I4SError(Exception):
    def __init__(self, message):
        self.message = message

class LoginError(I4SError):
    def __init__(self):
        I4SError.__init__(self, 'Login failed')

class CrapError(I4SError):
    def __init__(self):
        I4SError.__init__(self, 'I4S is total crap and is down.')

def login(username, password):
    '''Log in to I4S using username and password. Returns True if you weren't
    already logged in, raises CrapError if I4S is down and raises LoginError if
    your credentials are wrong.'''
    prelogin = url.urlopen('http://%s:%s/prelogin' % (apip, apport))
    content = prelogin.read()
    soup = BeautifulSoup(content)

    # get login page params. These include the challenge.
    params = {elem['name']: elem['value'] for elem in soup.findAll('input', {'type': 'hidden'})}
    params['uid'] = username
    params['pwd'] = password
    # yes, these are necessary!
    params['save_login'] = 'on'
    params['login'] = 'Login'

    request = url.Request(i4surl + '?' + urlencode(params))
    request.add_header('Referer', prelogin.geturl())
    try:
        response = url.urlopen(request)
        content = response.read()
        if 'failed' in content:
            raise LoginError()
        if 'Already' in content:
            return False
        return True
    except url.HTTPError as e:
        raise CrapError()

def main():
    if len(sys.argv) != 3 :
        print 'Usage: python i4s.py <username> <password>'
        raw_input()
    else:
        _, user, password = sys.argv
        try:
            print 'Logging in user %s...' % user,
            if login(user, password):
                print ' done!'
            else:
                print " which wasn't necessary at all!"
            time.sleep(3)
        except CrapError:
            print 'I4S seems to be down. Bummer!'
            raw_input('Press enter to exit...')
        except LoginError:
            print 'Login failed for user %s. Check your credentials!' % user
            raw_input('Press enter to exit...')

if __name__ == '__main__':
    main()
