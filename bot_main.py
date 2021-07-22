from time import sleep
from selenium import webdriver
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.action_chains import ActionChains
from getpass import getpass
import sys, argparse
import keyring

class TwitterBot:
    def __init__(self,username,password,browser='Firefox'):
        #if switch a bunch of browsers
        #else:
        self.browser = webdriver.firefox('webdrivers/geckodriver')
        self.action_chain = ActionChains(self.browser)
        self.username = username
        self.password = password

    def log_in(self):
        self.browser.get('https://twitter.com/login')
        sleep(3)
        username_input = self.browser.find_element_by_name('session[username_or_email]')
        password_input = self.browser.find_element_by_name('session[password]')
        username_input.send_keys(self.username)
        password_input.send_keys(self.password)
        password_input.send_keys(Keys.ENTER)
        sleep(7)

    def post_tweet(self,tweet_text):
        self.action_chain.send_keys('n')
        self.action_chain.send_keys(tweet_text)
        for _ in range(8):
            self.action_chain.send_keys(Keys.TAB)
        self.action_chain.send_keys(Keys.ENTER)

async def post_on_return(process,bot):
    proc = await asyncio.create_subprocess_shell(process,stdout=asyncio.subprocess.PIPE)
    while proc.returncode is None:
        data = await proc.stdout.readline()
        if not data: break
        line = data.decode().rstrip()
        if line.strip():
            bot.post_tweet(line)

parser = argparse.ArgumentParser()
parser.add_argument('-u','--username',action='store',help='Twitter username')
parser.add_argument('-l','--force_login',action='store_true',\
                    help='Ignore password if stored, ask for new authentication.')
parser.add_argument('-o','--overwrite_password',action='store_true',\
                    help='Force new authentication and save new password.')
parser.add_argument('-b','--browser',action='store',help='Browser to use',
                    default='Firefox')
parser.add_argument('tweet_generator',action='store',\
                    help='Path to process that generates tweets')
args = parser.parse_args()
if __name__ == '__main__':
    if not args.username:
        args.username = input("Please enter the Twitter username: ")
    try:
        password = keyring.get_password('pytwitterbot',args.username)
    except:
        password = getpass("Please enter the Twitter password: ")
    ofh = open('accounts.yaml','a+')
    write_password = True
    if args.username in accounts.keys() and not args.force_login \
       and not args.overwrite_password:
        write_password = False
        password = decrypt(accounts[args.username]['password'])
    else:
        password = getpass("Please enter the Twitter password: ")
        if args.force_login and not args.overwrite_password \
           and args.username in accounts.keys():
            write_password = False
    if write_password:
        try:
            keyring.set_password('pytwitterbot',args.username,password)
        except:
            print('Keyring not available')
    bot = TwitterBot(args.username,password,args.browser)
    try:
        bot.log_in()
    except:
        sys.exit("Twitter login failed")

    if sys.platform in ['win32','msys','cygwin']:
        loop = asyncio.ProactorEventLoop()
        asyncio.set_event_loop(loop)
    else:
        loop = asyncio.get_event_loop()

    loop.run_until_complete(post_on_return(args.tweet_generator))
    loop.close()
