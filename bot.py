import discord, time
from pyquery import PyQuery as pq

intents = discord.Intents.default()
intents.message_content = True

client = discord.Client(intents=intents)

cache = {}

def cached():
    global cache
    if not cache.get('data') or cache.get('age', 0) + 3600 < time.time():
        try:
            newdata = pq(url="https://meteo.arso.gov.si/uploads/probase/www/fproduct/text/sl/fcast_si_text.html")
            cache['data'] = newdata
        except:
            pass
        cache['age'] = time.time()
    return cache['data']

def getvreme(what='short'): # or long or full
    d = cached()
    if what == 'long':
        long = ''
        p = d("h2").next().next().next()
        while True:
            el = p[0]
            if el.tag != 'p':
                break
            long += '\n' + str(bytes(el.text, 'latin1'), 'utf-8')
            p = p.next()
        return long
    elif what == 'full':
        full = ''
        p = d("h2:first")
        while True:
            el = p[0]
            if el.tag not in ('h2', 'p'):
                break
            full += '\n' + str(bytes(el.text, 'latin1'), 'utf-8')
            p = p.next()
        return full
    elif what == 'short':
        return str(bytes(d("p:first")[0].text, 'latin1'), 'utf-8')
    else:
        return 'ne vem kaj je to ' + what

@client.event
async def on_ready():
    print(f'We have logged in as {client.user}')

@client.event
async def on_message(message):
    if message.author == client.user:
        return

    if message.content.lower().startswith('vreme') and len(message.content.split()) < 3:
        try:
            what = message.content.split()[1]
        except IndexError:
            what = 'short'
        await message.channel.send('```' + getvreme(what) + '```')

    if message.content.lower().startswith('radar') and len(message.content.split()) < 2:
        await message.channel.send('https://meteo.arso.gov.si/uploads/probase/www/observ/radar/si0-rm-anim.gif')

client.run(settings.TOKEN)

