from time import sleep
from selenium import webdriver
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.action_chains import ActionChains
from getpass import getpass
from cryptography.fernet import Fernet
import sys, argparse, yaml, asyncio
import keyring

class TwitterBot:
    def __init__(self,username,password,browser='Firefox'):
        if browser == 'Android':
            self.browser = webdriver.Android('webdrivers')
        elif browser == 'BlackBerry':
            self.browser = webdriver.BlackBerry('webdrivers')
        elif browser == 'Chrome':
            self.browser = webdriver.Chrome('webdrivers')
        elif browser == 'Edge':
            self.browser = webdriver.Edge('webdrivers')
        elif browser == 'Ie':
            self.browser = webdriver.Ie('webdrivers')
        elif browser == 'Opera':
            self.browser = webdriver.Opera('webdrivers')
        elif browser == 'PhantomJS':
            self.browser = webdriver.PhantomJS('webdrivers')
        elif browser == 'Safari':
            self.browser = webdriver.Safari('webdrivers')
        elif browser == 'WebKitGTK':
            self.browser = webdriver.WebKitGTK('webdrivers')
        else:
            self.browser = webdriver.Firefox('webdrivers')
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

async def post_on_return(process,bot,test):
    proc = await asyncio.create_subprocess_shell(process,stdout=asyncio.subprocess.PIPE)
    while proc.returncode is None:
        data = await proc.stdout.readuntil(b'\f')
        if not data: break
        chunk = data.decode().rstrip()
        if chunk.strip():
            if test:
                print("TEST OUTPUT: tweet\n"+chunk)
            else:
                bot.post_tweet(chunk)

parser = argparse.ArgumentParser()
parser.add_argument('-u','--username',action='store',help='Twitter username')
parser.add_argument('-l','--force_login',action='store_true',\
                    help='Ignore password if stored, ask for new authentication.')
parser.add_argument('-o','--overwrite_password',action='store_true',\
                    help='Force new authentication and save new password.')
parser.add_argument('-b','--browser',action='store',help='Browser to use',\
                    default='Firefox')
parser.add_argument('-x','--no_unsafe_write',action='store_true',\
                    help='Never write passwords to disk (even encrypted).')
parser.add_argument('-t','--test_run', action='store_true',help='Test only, do not tweet.')
parser.add_argument('tweet_generator',action='store',\
                    help='Path to process that generates tweets')
args = parser.parse_args()
if __name__ == '__main__':
    if args.force_login and args.overwrite_password:
        sys.exit("--force_login and --overwrite_password cannot be used in the same\
                 session.")
    if not args.username:
        args.username = input("Please enter the Twitter username: ")
    write_password = args.overwrite_password
    try:
        password = keyring.get_password('pytwitterbot',args.username)
        if not password:
            raise NotImplementedError
        print("Got from keyring")
    except (keyring.errors.KeyringError, NotImplementedError) as e:
        try:
            if args.force_login or args.overwrite_password:
                raise NotImplementedError
            with open('settings','rb') as rbfh, open('users.yaml') as rfh:
                all_users = yaml.safe_load(rfh)
                pw_token_str = all_users[args.username]
                key = rbfh.read()
            f = Fernet(key)
            password = f.decrypt(pw_token_str.encode()).decode()
            print("Got from users.yaml")
        except:
            print("Getting pw manually")
            write_password = not args.force_login
            password = getpass("Please enter the Twitter password: ")
    if write_password:
        try:
            keyring.set_password('pytwitterbot',args.username,password)
        except:
            print('Keyring not available')
            if args.no_unsafe_write:
                print('no_unsafe_write is set, credentials not saved.')
            else:
                try:
                    with open('settings','rb') as rbfh:
                        binkey = rbfh.read()
                    f = fernet(binkey)
                    token = f.encrypt(password.encode())
                    with open('users.yaml','a') as afh:
                        yaml.safe_dump({args.username: token.decode()},afh)
                except FileNotFoundError:
                    print('Creating keyfile')
                    key = Fernet.generate_key()
                    with open('settings','wb') as wbfh:
                        wbfh.write(key)
                    f = Fernet(key)
                    token = f.encrypt(password.encode())
                    with open('users.yaml','w') as wfh:
                        yaml.safe_dump({args.username: token.decode()},wfh)
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

    loop.run_until_complete(post_on_return(args.tweet_generator,bot,args.test_run))
    loop.close()
